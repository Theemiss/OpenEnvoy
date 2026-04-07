"""Webhook endpoints for external integrations (email notifications, etc.)."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel

from ....core.database import db_manager
from ....ai.classification.reply_classifier import ReplyClassifier
from ....engine.email.gmail import GmailClient
from .monitor import EmailMonitor

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class EmailWebhookPayload(BaseModel):
    message_id: str
    thread_id: Optional[str] = None
    subject: str
    from_email: str
    to_email: str
    body_text: str
    date: Optional[str] = None


class WebhookResponse(BaseModel):
    success: bool
    message: str
    application_id: Optional[int] = None
    classification: Optional[dict] = None


async def process_webhook_email(payload: EmailWebhookPayload) -> WebhookResponse:
    """Process incoming email webhook."""
    classifier = ReplyClassifier()

    try:
        classification = await classifier.classify_reply(
            body=payload.body_text,
            subject=payload.subject,
            from_email=payload.from_email
        )
    except Exception as e:
        classification = {
            "category": "OTHER",
            "confidence": 0,
            "error": str(e)
        }

    async with db_manager.session() as session:
        from sqlalchemy import select
        from ....models.email import Email
        from ....models.application import Application

        stmt = select(Email).where(Email.message_id == payload.message_id)
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing:
            return WebhookResponse(
                success=True,
                message="Email already processed",
                application_id=existing.application_id,
                classification=classification
            )

        application_id = None
        if payload.thread_id:
            thread_stmt = select(Email).where(Email.thread_id == payload.thread_id)
            thread_result = await session.execute(thread_stmt)
            existing_thread = thread_result.scalar_one_or_none()
            if existing_thread:
                application_id = existing_thread.application_id

        email_record = Email(
            application_id=application_id,
            message_id=payload.message_id,
            thread_id=payload.thread_id,
            direction="inbound",
            from_email=payload.from_email,
            to_email=payload.to_email,
            subject=payload.subject,
            body_text=payload.body_text[:10000],
            classification=classification.get("category"),
            classification_confidence=classification.get("confidence"),
            status="received",
            sent_at=datetime.now()
        )

        session.add(email_record)

        if application_id:
            app = await session.get(Application, application_id)
            if app:
                category = classification.get("category")
                if category == "interview":
                    app.status = "interviewing"
                elif category == "rejection":
                    app.status = "rejected"
                elif category == "info_request":
                    app.status = "needs_info"
                app.last_activity_at = datetime.now()

                if classification.get("requires_human"):
                    from ....engine.workflow.temporal.activities import queue_for_human_review
                    await queue_for_human_review(
                        application_id=application_id,
                        review_type="email_reply",
                        data={
                            "email": {
                                "message_id": payload.message_id,
                                "subject": payload.subject,
                                "from_email": payload.from_email,
                                "body_text": payload.body_text
                            },
                            "classification": classification
                        }
                    )

        await session.commit()

        return WebhookResponse(
            success=True,
            message="Email processed successfully",
            application_id=application_id,
            classification=classification
        )


@router.post("/email", response_model=WebhookResponse)
async def receive_email_webhook(
    payload: EmailWebhookPayload,
    background_tasks: BackgroundTasks
):
    """Receive email webhook from external service (e.g., SendGrid, Mailgun)."""
    background_tasks.add_task(process_webhook_email, payload)

    return WebhookResponse(
        success=True,
        message="Webhook received, processing in background"
    )


@router.post("/email/sync")
async def sync_gmail_inbox():
    """Trigger Gmail inbox sync (for manual sync button)."""
    try:
        monitor = EmailMonitor()
        replies = await monitor.check_new_replies(since_minutes=60 * 24)

        return {
            "success": True,
            "replies_found": len(replies),
            "message": f"Found {len(replies)} new replies"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def webhook_status():
    """Get webhook configuration status."""
    from ....core.config import settings

    return {
        "webhook_url": f"/api/v1/webhooks/email",
        "gmail_configured": bool(settings.GMAIL_CREDENTIALS_FILE),
        "imap_configured": bool(settings.IMAP_HOST and settings.IMAP_USERNAME),
        "supported_providers": ["Gmail API", "IMAP", "SendGrid", "Mailgun"]
    }
