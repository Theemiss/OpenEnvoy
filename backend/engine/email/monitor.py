"""Email monitoring for replies."""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ...core.config import settings
from ...core.database import db_manager
from ...ai.classification.reply_classifier import ReplyClassifier
from .gmail import GmailClient

logger = logging.getLogger(__name__)


class EmailMonitor:
    """Monitor email inbox for replies."""
    
    def __init__(self):
        self.classifier = ReplyClassifier()
        self.gmail = GmailClient() if settings.GMAIL_CREDENTIALS_FILE else None
    
    async def check_new_replies(self, since_minutes: int = 60) -> List[Dict[str, Any]]:
        """Check for new email replies."""
        
        if not self.gmail:
            logger.warning("Gmail not configured, skipping inbox check")
            return []
        
        try:
            replies = await self.gmail.check_new_replies(since_minutes)
            
            # Process each reply
            for reply in replies:
                await self._process_reply(reply)
            
            return replies
            
        except Exception as e:
            logger.error(f"Error checking replies: {str(e)}")
            return []
    
    async def _process_reply(self, reply: Dict[str, Any]):
        """Process a single reply."""
        
        # Find associated application
        application_id = await self._find_application(reply)
        
        if application_id:
            # Update application status
            await self._update_application_status(
                application_id,
                reply.get("classification", {})
            )
            
            # Queue for human review if needed
            if reply.get("classification", {}).get("requires_human"):
                from ...engine.workflow.temporal.activities import queue_for_human_review
                
                await queue_for_human_review(
                    application_id=application_id,
                    review_type="email_reply",
                    data=reply
                )
    
    async def _find_application(self, reply: Dict[str, Any]) -> Optional[int]:
        """Find application ID from email reply."""
        async with db_manager.session() as session:
            from sqlalchemy import select
            from ...models.email import Email
            
            # Look for thread match
            stmt = select(Email).where(Email.thread_id == reply.get("thread_id"))
            result = await session.execute(stmt)
            email = result.scalar_one_or_none()
            
            if email and email.application_id:
                return email.application_id
            
            return None
    
    async def _update_application_status(self, application_id: int,
                                          classification: Dict[str, Any]):
        """Update application status based on reply classification."""
        async with db_manager.session() as session:
            from ...models.application import Application
            
            app = await session.get(Application, application_id)
            if not app:
                return
            
            category = classification.get("category")
            
            if category == "interview":
                app.status = "interviewing"
            elif category == "rejection":
                app.status = "rejected"
            elif category == "offer":
                app.status = "offered"
            elif category == "info_request":
                app.status = "needs_info"
            
            app.last_activity_at = datetime.now()
            await session.commit()
    
    async def monitor_continuously(self, interval_minutes: int = 15):
        """Continuously monitor for new emails."""
        while True:
            try:
                replies = await self.check_new_replies(interval_minutes)
                
                if replies:
                    logger.info(f"Found {len(replies)} new replies")
                
                await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in email monitoring: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error