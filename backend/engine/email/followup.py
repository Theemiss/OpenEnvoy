"""Automated follow-up system."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from ...core.database import db_manager
from ...models.application import Application
from ...models.email import Email, EmailTemplate
from ...ai.email.drafter import EmailDrafter
from ...engine.email.sender import EmailSender
from ...core.cache import cache

logger = logging.getLogger(__name__)


class FollowUpManager:
    """Manage automated follow-up emails."""
    
    def __init__(self):
        self.drafter = EmailDrafter()
        self.sender = EmailSender()
    
    async def check_for_follow_ups(self) -> List[Dict[str, Any]]:
        """Check which applications need follow-ups."""
        
        async with db_manager.session() as session:
            from sqlalchemy import select, and_
            
            # Find applications that:
            # - Are in 'applied' status
            # - Haven't had a follow-up yet
            # - Are at least 5 days old
            cutoff = datetime.now() - timedelta(days=5)
            
            stmt = select(Application).where(
                and_(
                    Application.status == "applied",
                    Application.applied_at <= cutoff,
                    Application.last_activity_at == None
                )
            ).order_by(Application.applied_at)
            
            result = await session.execute(stmt)
            applications = result.scalars().all()
            
            follow_ups = []
            
            for app in applications:
                # Check if follow-up already sent
                email_stmt = select(Email).where(
                    and_(
                        Email.application_id == app.id,
                        Email.subject.ilike("%follow%")
                    )
                )
                email_result = await session.execute(email_stmt)
                existing = email_result.scalar_one_or_none()
                
                if not existing:
                    days_since = (datetime.now() - app.applied_at).days
                    follow_ups.append({
                        "application": app,
                        "days_since": days_since
                    })
            
            return follow_ups
    
    async def send_follow_up(self, application: Application, 
                              days_since: int) -> Dict[str, Any]:
        """Send a follow-up for an application."""
        
        logger.info(f"Sending follow-up for application {application.id}, {days_since} days")
        
        # Get template
        template = await self._get_follow_up_template(days_since)
        
        # Draft follow-up
        follow_up = await self.drafter.draft_follow_up(application, days_since)
        
        # Send email
        result = await self.sender.send_email(
            to_email=self._get_recruiter_email(application),  # You'd need to extract this
            subject=follow_up.get("subject", template.subject_template),
            body=follow_up.get("body", template.body_template),
            application_id=application.id
        )
        
        if result["success"]:
            logger.info(f"Follow-up sent for application {application.id}")
            
            # Update application
            async with db_manager.session() as session:
                app = await session.get(Application, application.id)
                if app:
                    app.last_activity_at = datetime.now()
                    await session.commit()
            
            # Track in Redis
            await cache.set(
                f"followup:{application.id}",
                {
                    "sent_at": datetime.now().isoformat(),
                    "days_since": days_since
                },
                ttl=2592000  # 30 days
            )
        
        return result
    
    async def send_batch_follow_ups(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Send follow-ups for multiple applications."""
        
        follow_ups = await self.check_for_follow_ups()
        
        # Sort by oldest first
        follow_ups.sort(key=lambda x: x["days_since"], reverse=True)
        
        results = []
        for item in follow_ups[:limit]:
            try:
                result = await self.send_follow_up(item["application"], item["days_since"])
                results.append({
                    "application_id": item["application"].id,
                    "success": result["success"],
                    "message_id": result.get("message_id")
                })
                
                # Space them out
                await asyncio.sleep(60)  # 1 minute between follow-ups
                
            except Exception as e:
                logger.error(f"Follow-up failed for {item['application'].id}: {str(e)}")
                results.append({
                    "application_id": item["application"].id,
                    "success": False,
                    "error": str(e)
                })
        
        return results
    
    async def _get_follow_up_template(self, days_since: int) -> EmailTemplate:
        """Get appropriate template based on days since application."""
        
        async with db_manager.session() as session:
            from sqlalchemy import select
            
            # Try to find template for this timeframe
            if days_since <= 7:
                trigger = "after_application"
            elif days_since <= 14:
                trigger = "second_followup"
            else:
                trigger = "final_followup"
            
            stmt = select(EmailTemplate).where(
                EmailTemplate.trigger_type == trigger,
                EmailTemplate.is_active == True
            )
            result = await session.execute(stmt)
            template = result.scalar_one_or_none()
            
            if template:
                return template
            
            # Return default
            return EmailTemplate(
                name="Default Follow-up",
                subject_template="Follow-up on {job_title} application",
                body_template="""Dear Hiring Manager,

I hope this email finds you well. I'm writing to follow up on my application for the {job_title} position, which I submitted {days_since} days ago.

I remain very interested in this opportunity and would welcome the chance to discuss how my skills could benefit your team.

Thank you for your consideration.

Best regards,
{name}""",
                trigger_type="after_application",
                trigger_days=5,
                is_active=True
            )
    
    def _get_recruiter_email(self, application: Application) -> str:
        """Extract recruiter email from application data."""
        # This would need to be implemented based on how you store this
        # For now, return a placeholder
        if application.emails:
            for email in application.emails:
                if email.direction == "outbound":
                    return email.to_email
        
        # Try to extract from job
        if application.job and application.job.company:
            # Would need company email mapping
            pass
        
        return "recruiter@example.com"  # Placeholder
    
    async def cancel_follow_ups(self, application_id: int):
        """Cancel scheduled follow-ups for an application."""
        # Remove from queue
        await cache.delete(f"followup:{application_id}")
        
        # Mark as cancelled in database
        async with db_manager.session() as session:
            from sqlalchemy import update
            from ...models.application import ApplicationTimeline
            
            stmt = update(ApplicationTimeline).where(
                ApplicationTimeline.application_id == application_id,
                ApplicationTimeline.event_type == "followup_scheduled"
            ).values(
                event_type="followup_cancelled"
            )
            
            await session.execute(stmt)
            await session.commit()