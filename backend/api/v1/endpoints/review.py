"""Human review queue endpoints."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import json

from ....core.cache import cache
from ....core.database import db_manager
from ....models.application import Application, ApplicationTimeline
from ....engine.email.sender import EmailSender

router = APIRouter(prefix="/review", tags=["review"])


class ReviewItem(BaseModel):
    """Review queue item."""

    id: str
    type: str  # standard, senior, ambiguous, resume_failed, follow_up, email_reply
    application_id: int
    created_at: str
    data: dict
    status: str = "pending"


class ReviewAction(BaseModel):
    """Action to take on review item."""

    approved: bool
    modified_data: Optional[dict] = None
    notes: Optional[str] = None


@router.get("/queue")
async def get_review_queue(
    types: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=100)
):
    """Get items awaiting human review."""

    all_items = []

    if types:
        review_types = [t.strip() for t in types.split(",")]
    else:
        review_types = [
            "standard",
            "senior",
            "ambiguous",
            "resume_failed",
            "follow_up",
            "email_reply",
        ]

    for review_type in review_types:
        queue_key = f"review_queue:{review_type}"
        item_ids = await cache.lrange(queue_key, 0, -1)

        for item_id in item_ids[:limit]:
            item_key = f"review:{review_type}:{item_id}"
            item_json = await cache.get(item_key)
            if item_json:
                item_data = json.loads(item_json) if isinstance(item_json, str) else {}
                item_data["id"] = f"{review_type}:{item_id}"
                item_data["type"] = review_type
                all_items.append(item_data)

    # Sort by created_at (newest first)
    all_items.sort(key=lambda x: x.get("created_at", ""), reverse=True)

    return all_items[:limit]


@router.get("/queue/counts")
async def get_review_counts():
    """Get count of items in each review queue."""

    review_types = [
        "standard",
        "senior",
        "ambiguous",
        "resume_failed",
        "follow_up",
        "email_reply",
    ]
    counts = {}

    for review_type in review_types:
        queue_key = f"review_queue:{review_type}"
        count = await cache.llen(queue_key)
        counts[review_type] = count

    return counts


@router.post("/{item_id}/approve")
async def approve_item(item_id: str, action: ReviewAction):
    """Approve a review item."""

    # Parse item ID (format: "type:id")
    parts = item_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    review_type, item_id_value = parts

    # Get item data
    item_key = f"review:{review_type}:{item_id_value}"
    item_json = await cache.get(item_key)

    if not item_json:
        raise HTTPException(status_code=404, detail="Review item not found")

    item_data = json.loads(item_json) if isinstance(item_json, str) else {}

    # Remove from queue
    queue_key = f"review_queue:{review_type}"
    await cache.lrem(queue_key, 0, item_id_value)

    # Process based on type
    if review_type == "follow_up":
        await _process_follow_up_approval(item_data, action)
    elif review_type == "email_reply":
        await _process_reply_approval(item_data, action)
    else:
        await _process_application_approval(item_data, action)

    # Delete the item
    await cache.delete(item_key)

    return {"status": "approved", "item_id": item_id}


@router.post("/{item_id}/reject")
async def reject_item(item_id: str, action: ReviewAction):
    """Reject a review item."""

    # Parse item ID
    parts = item_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid item ID format")

    review_type, item_id_value = parts

    # Get item data
    item_key = f"review:{review_type}:{item_id_value}"
    item_json = await cache.get(item_key)

    if not item_json:
        raise HTTPException(status_code=404, detail="Review item not found")

    item_data = json.loads(item_json) if isinstance(item_json, str) else {}

    # Remove from queue
    queue_key = f"review_queue:{review_type}"
    await cache.lrem(queue_key, 0, item_id_value)

    # Log rejection
    async with db_manager.session() as session:
        timeline = ApplicationTimeline(
            application_id=item_data.get("application_id"),
            event_type="review_rejected",
            description=f"Review rejected: {action.notes or 'No reason given'}",
            extra_data={"review_type": review_type, "notes": action.notes},
        )

        session.add(timeline)
        await session.commit()

    # Delete the item
    await cache.delete(item_key)

    return {"status": "rejected", "item_id": item_id}


async def _process_application_approval(item_data: dict, action: ReviewAction):
    """Process approval of an application."""

    application_id = item_data.get("application_id")
    email_data = item_data.get("data", {}).get("email", {})

    # Use modified data if provided
    if action.modified_data:
        email_data = action.modified_data.get("email", email_data)

    # Send the email
    sender = EmailSender()
    result = await sender.send_email(
        to_email=email_data.get("to_email"),
        subject=email_data.get(
            "email_subject", email_data.get("subject", "Application")
        ),
        body=email_data.get("email_body", email_data.get("body", "")),
        application_id=application_id,
    )

    if result["success"]:
        # Update application status
        async with db_manager.session() as session:
            app = await session.get(Application, application_id)
            if app:
                app.status = "applied"
                app.applied_at = datetime.now()

                timeline = ApplicationTimeline(
                    application_id=application_id,
                    event_type="application_sent",
                    description="Application submitted after human approval",
                    ai_generated=False,
                )
                session.add(timeline)

                await session.commit()


async def _process_follow_up_approval(item_data: dict, action: ReviewAction):
    """Process approval of a follow-up email."""

    application_id = item_data.get("application_id")
    follow_up_data = action.modified_data or item_data.get("follow_up", {})

    # Send the follow-up
    sender = EmailSender()
    result = await sender.send_email(
        to_email=follow_up_data.get("to_email"),
        subject=follow_up_data.get("subject", "Follow-up"),
        body=follow_up_data.get("body", ""),
        application_id=application_id,
    )

    if result["success"]:
        async with db_manager.session() as session:
            app = await session.get(Application, application_id)
            if app:
                app.last_activity_at = datetime.now()

                timeline = ApplicationTimeline(
                    application_id=application_id,
                    event_type="follow_up_sent",
                    description="Follow-up sent after human approval",
                    ai_generated=False,
                )
                session.add(timeline)
                await session.commit()


async def _process_reply_approval(item_data: dict, action: ReviewAction):
    """Process approval of a reply to a recruiter."""

    application_id = item_data.get("application_id")
    reply_data = action.modified_data or item_data

    # Send the reply
    sender = EmailSender()
    result = await sender.send_email(
        to_email=reply_data.get("from_email"),
        subject=f"Re: {reply_data.get('subject', '')}",
        body=reply_data.get("suggested_response", ""),
        application_id=application_id,
    )

    if result["success"]:
        async with db_manager.session() as session:
            app = await session.get(Application, application_id)
            if app:
                app.last_activity_at = datetime.now()

                timeline = ApplicationTimeline(
                    application_id=application_id,
                    event_type="reply_sent",
                    description="Reply sent to recruiter",
                    ai_generated=False,
                )
                session.add(timeline)
                await session.commit()
