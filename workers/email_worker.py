#!/usr/bin/env python3
"""Email worker for sending and monitoring."""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.engine.email.sender import EmailSender
from backend.engine.email.monitor import EmailMonitor
from backend.engine.email.followup import FollowUpManager
from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.core.alerting import alert_manager
from backend.core.cache import cache

logger = logging.getLogger(__name__)


async def process_email_queue():
    """Process emails waiting in queue."""
    sender = EmailSender()
    
    # Get pending emails from Redis
    queue_key = "email_queue"
    email_ids = await cache.lrange(queue_key, 0, 10)  # Process up to 10 at a time
    
    if not email_ids:
        return 0
    
    results = []
    for email_id in email_ids:
        try:
            # Get email data
            email_data = await cache.get(f"email:{email_id}")
            if not email_data:
                await cache.lrem(queue_key, 1, email_id)
                continue
            
            # Send email
            result = await sender.send_email(**email_data)
            
            if result["success"]:
                await cache.lrem(queue_key, 1, email_id)
                await cache.delete(f"email:{email_id}")
                results.append({"id": email_id, "status": "sent"})
            else:
                # Increment retry count
                retry_key = f"email_retry:{email_id}"
                retries = await cache.incr(retry_key)
                
                if retries >= 3:
                    # Max retries exceeded, remove from queue
                    await cache.lrem(queue_key, 1, email_id)
                    await cache.delete(f"email:{email_id}")
                    
                    await alert_manager.send_alert(
                        title="Email Failed",
                        message=f"Email {email_id} failed after 3 retries",
                        severity="warning",
                        metadata={"error": result.get("error")}
                    )
            
        except Exception as e:
            logger.error(f"Error processing email {email_id}: {str(e)}")
    
    return len(results)


async def check_follow_ups():
    """Check and send follow-ups."""
    manager = FollowUpManager()
    
    try:
        results = await manager.send_batch_follow_ups(limit=5)
        
        if results:
            logger.info(f"Sent {len(results)} follow-ups")
            
            # Alert on successful follow-ups
            successful = [r for r in results if r.get("success")]
            if successful:
                await alert_manager.send_alert(
                    title="Follow-ups Sent",
                    message=f"Sent {len(successful)} follow-up emails",
                    severity="info",
                    metadata={"results": successful}
                )
        
        return len(results)
        
    except Exception as e:
        logger.error(f"Error checking follow-ups: {str(e)}")
        return 0


async def monitor_inbox():
    """Monitor for new email replies."""
    monitor = EmailMonitor()
    
    try:
        replies = await monitor.check_new_replies()
        
        if replies:
            logger.info(f"Found {len(replies)} new replies")
            
            # Process replies that need attention
            for reply in replies:
                if reply.get("classification", {}).get("requires_human"):
                    await alert_manager.send_alert(
                        title="New Email Reply",
                        message=f"Reply from {reply.get('from_email')}: {reply.get('subject')}",
                        severity="info",
                        metadata={"reply": reply}
                    )
        
        return len(replies)
        
    except Exception as e:
        logger.error(f"Error monitoring inbox: {str(e)}")
        return 0


async def main():
    """Main email worker loop."""
    setup_logging("email_worker")
    
    logger.info("Starting email worker")
    
    while True:
        try:
            # Process email queue (every minute)
            sent = await process_email_queue()
            if sent:
                logger.info(f"Processed {sent} emails from queue")
            
            # Check for follow-ups (every 6 hours)
            current_hour = asyncio.get_event_loop().time() // 3600
            if current_hour % 6 == 0:  # Every 6 hours
                follow_ups = await check_follow_ups()
                if follow_ups:
                    logger.info(f"Sent {follow_ups} follow-ups")
            
            # Monitor inbox (every 15 minutes)
            current_minute = asyncio.get_event_loop().time() // 60
            if current_minute % 15 == 0:  # Every 15 minutes
                replies = await monitor_inbox()
                if replies:
                    logger.info(f"Found {replies} new replies")
            
        except Exception as e:
            logger.error(f"Unhandled error in email worker: {str(e)}")
        
        await asyncio.sleep(60)  # Check every minute


if __name__ == "__main__":
    asyncio.run(main())