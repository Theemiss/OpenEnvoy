"""Email endpoints."""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ....core.database import db_manager, get_db
from ....models.email import Email
from ....schemas.email import (
    EmailResponse,
    EmailSendRequest,
    EmailDraftRequest,
    EmailDraftResponse,
)
from ....engine.email.sender import EmailSender
from ....ai.email.drafter import EmailDrafter
from ....core.cache import cache
from ....models.job import Job
from ....models.profile import Profile
from ....models.application import Application

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("", response_model=List[EmailResponse])
async def list_emails(
    application_id: Optional[int] = None,
    direction: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List emails."""
    query = select(Email)

    if application_id:
        query = query.where(Email.application_id == application_id)

    if direction:
        query = query.where(Email.direction == direction)

    query = query.order_by(Email.created_at.desc()).limit(limit)

    result = await session.execute(query)
    emails = result.scalars().all()

    return [EmailResponse.model_validate(e) for e in emails]


@router.get("/queue/status")
async def queue_status():
    """Get email queue status."""
    queue_size = await cache.llen("email_queue")

    return {"queue_size": queue_size, "processing": queue_size > 0}


@router.post("/draft", response_model=EmailDraftResponse)
async def draft_email(
    request: EmailDraftRequest,
):
    """Draft an email."""
    drafter = EmailDrafter()

    result = {}
    if request.email_type == "initial":
        result = await drafter.draft_initial_email(None, None)
    elif request.email_type == "follow_up":
        result = await drafter.draft_follow_up(None, days_since=5)
    elif request.email_type == "cover":
        result = await drafter.draft_cover_letter(None, None)
    elif request.email_type == "thank_you":
        result = await drafter.draft_thank_you(None, None)
    else:
        raise HTTPException(status_code=400, detail="Invalid email type")

    return EmailDraftResponse(
        subject=result.get("subject", ""),
        body=result.get("body", result.get("cover_letter", "")),
        generated_at=result.get("generated_at", datetime.now().isoformat()),
        model_used=result.get("model", "gpt-4o-mini"),
    )


@router.post("/send")
async def send_email(request: EmailSendRequest):
    """Send an email."""
    sender = EmailSender()

    result = await sender.send_email(
        to_email=request.to_email,
        subject=request.subject,
        body=request.body,
        html_body=request.html_body,
        application_id=request.application_id,
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500, detail=result.get("error", "Failed to send email")
        )

    return {
        "success": True,
        "message_id": result.get("message_id"),
        "email_id": result.get("email_id"),
    }


@router.post("/queue")
async def queue_email(request: EmailSendRequest):
    """Queue an email for later sending."""
    import uuid
    import json

    email_id = str(uuid.uuid4())

    await cache.set(
        f"email:{email_id}",
        json.dumps(
            {
                "to_email": request.to_email,
                "subject": request.subject,
                "body": request.body,
                "html_body": request.html_body,
                "application_id": request.application_id,
            }
        ),
        ttl=604800,
    )

    await cache.rpush("email_queue", email_id)

    return {"email_id": email_id, "status": "queued"}


@router.get("/{email_id}", response_model=EmailResponse)
async def get_email(email_id: int, session: AsyncSession = Depends(get_db)):
    """Get email by ID."""
    email = await session.get(Email, email_id)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    return EmailResponse.model_validate(email)
