"""Application logging and tracking."""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from ...core.database import db_manager
from ...models.application import Application, ApplicationTimeline

logger = logging.getLogger(__name__)


class ApplicationLogger:
    """Log application events and milestones."""

    async def log_event(
        self,
        application_id: int,
        event_type: str,
        description: str,
        extra_data: Optional[Dict] = None,
        ai_generated: bool = False,
        model_used: Optional[str] = None,
    ):
        """Log an application event."""

        async with db_manager.session() as session:
            timeline = ApplicationTimeline(
                application_id=application_id,
                event_type=event_type,
                event_date=datetime.now(),
                description=description,
                ai_generated=ai_generated,
                model_used=model_used,
                extra_data=extra_data,
            )

            session.add(timeline)
            await session.commit()

            logger.info(f"Logged event {event_type} for application {application_id}")

    async def log_score(
        self, application_id: int, score: float, reasoning: str, model: str
    ):
        """Log scoring event."""
        await self.log_event(
            application_id=application_id,
            event_type="scored",
            description=f"Job scored {score}: {reasoning[:100]}",
            extra_data={"score": score, "reasoning": reasoning},
            ai_generated=True,
            model_used=model,
        )

    async def log_application_sent(
        self, application_id: int, email_id: Optional[int] = None
    ):
        """Log application sent."""
        await self.log_event(
            application_id=application_id,
            event_type="submitted",
            description="Application submitted",
            extra_data={"email_id": email_id},
        )

    async def log_response_received(
        self, application_id: int, response_type: str, email_id: int
    ):
        """Log response received."""
        await self.log_event(
            application_id=application_id,
            event_type="response",
            description=f"Received {response_type} response",
            extra_data={"response_type": response_type, "email_id": email_id},
        )

    async def log_interview_scheduled(
        self, application_id: int, interview_date: datetime, interview_type: str
    ):
        """Log interview scheduled."""
        await self.log_event(
            application_id=application_id,
            event_type="interview_scheduled",
            description=f"Interview scheduled: {interview_type}",
            extra_data={
                "interview_date": interview_date.isoformat(),
                "interview_type": interview_type,
            },
        )

    async def log_follow_up_sent(
        self, application_id: int, follow_up_number: int, email_id: int
    ):
        """Log follow-up sent."""
        await self.log_event(
            application_id=application_id,
            event_type="follow_up",
            description=f"Follow-up #{follow_up_number} sent",
            extra_data={"follow_up_number": follow_up_number, "email_id": email_id},
        )

    async def get_timeline(self, application_id: int) -> List[Dict[str, Any]]:
        """Get timeline for an application."""
        async with db_manager.session() as session:
            from sqlalchemy import select

            stmt = (
                select(ApplicationTimeline)
                .where(ApplicationTimeline.application_id == application_id)
                .order_by(ApplicationTimeline.event_date)
            )

            result = await session.execute(stmt)
            events = result.scalars().all()

            return [
                {
                    "event_type": e.event_type,
                    "event_date": e.event_date,
                    "description": e.description,
                    "ai_generated": e.ai_generated,
                    "extra_data": e.extra_data,
                }
                for e in events
            ]
