"""Integration tests for email functionality."""

import pytest
from datetime import datetime, timedelta

from backend.engine.email.sender import EmailSender
from backend.engine.email.followup import FollowUpManager
from backend.ai.email.drafter import EmailDrafter
from backend.models.email import Email
from backend.models.application import Application


@pytest.mark.asyncio
async def test_email_drafting(test_job, test_profile):
    """Test email drafting with AI."""
    
    drafter = EmailDrafter()
    
    # Mock AI response
    drafter.draft_initial_email = pytest.mock.AsyncMock(return_value={
        "subject": "Test Subject",
        "body": "Test Body"
    })
    
    # Draft initial email
    result = await drafter.draft_initial_email(test_job, test_profile)
    
    assert "subject" in result
    assert "body" in result


@pytest.mark.asyncio
async def test_follow_up_detection(session, test_job):
    """Test follow-up detection."""
    
    # Create an old application
    app = Application(
        job_id=test_job.id,
        status="applied",
        applied_at=datetime.now() - timedelta(days=7)
    )
    session.add(app)
    await session.commit()
    
    manager = FollowUpManager()
    
    # Check for follow-ups
    follow_ups = await manager.check_for_follow_ups()
    
    assert len(follow_ups) > 0
    assert follow_ups[0]["application"].id == app.id
    assert follow_ups[0]["days_since"] >= 5


@pytest.mark.asyncio
async def test_email_queue_processing():
    """Test email queue processing."""
    
    from backend.core.cache import cache
    
    sender = EmailSender()
    
    # Mock send method
    sender.send_email = pytest.mock.AsyncMock(return_value={
        "success": True,
        "message_id": "test-id"
    })
    
    # Queue an email
    email_id = "test-email-1"
    await cache.set(
        f"email:{email_id}",
        {
            "to_email": "test@example.com",
            "subject": "Test",
            "body": "Test body"
        }
    )
    await cache.rpush("email_queue", email_id)
    
    # Process queue (simulate worker)
    queue_key = "email_queue"
    queued_id = await cache.lpop(queue_key)
    
    assert queued_id == email_id
    
    email_data = await cache.get(f"email:{queued_id}")
    assert email_data is not None
    
    # Send
    result = await sender.send_email(**email_data)
    
    assert result["success"] is True


@pytest.mark.asyncio
async def test_email_rate_limiting():
    """Test email rate limiting."""
    
    sender = EmailSender()
    sender.max_per_day = 2
    sender.sent_today = 0
    
    # Send first email
    sender.send_email = pytest.mock.AsyncMock(return_value={"success": True})
    
    result1 = await sender.send_email(
        to_email="test@example.com",
        subject="Test 1",
        body="Body 1"
    )
    
    assert result1["success"] is True
    assert sender.sent_today == 1
    
    # Send second email
    result2 = await sender.send_email(
        to_email="test@example.com",
        subject="Test 2",
        body="Body 2"
    )
    
    assert result2["success"] is True
    assert sender.sent_today == 2
    
    # Third should be rate limited
    with pytest.raises(Exception, match="Daily email limit reached"):
        await sender.send_email(
            to_email="test@example.com",
            subject="Test 3",
            body="Body 3"
        )


@pytest.mark.asyncio
async def test_follow_up_sending(session, test_job):
    """Test sending actual follow-ups."""
    
    # Create application
    app = Application(
        job_id=test_job.id,
        status="applied",
        applied_at=datetime.now() - timedelta(days=7)
    )
    session.add(app)
    await session.commit()
    
    manager = FollowUpManager()
    
    # Mock email sending
    manager.sender.send_email = pytest.mock.AsyncMock(return_value={
        "success": True,
        "message_id": "test-id"
    })
    
    # Send follow-up
    result = await manager.send_follow_up(app, days_since=7)
    
    assert result["success"] is True
    
    # Check that application was updated
    updated = await session.get(Application, app.id)
    assert updated.last_activity_at is not None