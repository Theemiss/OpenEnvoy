"""Application history tracking."""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from ...core.database import db_manager
from ...models.application import Application


class ApplicationHistory:
    """Track and analyze application history."""
    
    async def get_history(self, days: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get application history."""
        async with db_manager.session() as session:
            from sqlalchemy import select
            
            query = select(Application)
            
            if days:
                cutoff = datetime.now() - timedelta(days=days)
                query = query.where(Application.created_at >= cutoff)
            
            query = query.order_by(Application.created_at.desc())
            
            result = await session.execute(query)
            applications = result.scalars().all()
            
            return [self._format_application(a) for a in applications]
    
    async def get_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Get application statistics."""
        history = await self.get_history(days)
        
        if not history:
            return {}
        
        total = len(history)
        by_status = {}
        response_times = []
        
        for app in history:
            # Count by status
            status = app.get("status")
            by_status[status] = by_status.get(status, 0) + 1
            
            # Calculate response time if available
            if app.get("applied_at") and app.get("first_response_at"):
                response_time = (
                    datetime.fromisoformat(app["first_response_at"]) -
                    datetime.fromisoformat(app["applied_at"])
                ).total_seconds() / 3600  # Hours
                response_times.append(response_time)
        
        # Calculate rates
        responded = sum(by_status.get(s, 0) for s in 
                       ["interviewing", "rejected", "offered", "accepted"])
        
        interviewed = sum(by_status.get(s, 0) for s in 
                         ["interviewing", "offered", "accepted"])
        
        return {
            "period_days": days,
            "total_applications": total,
            "by_status": by_status,
            "response_rate": round(responded / total * 100, 1) if total > 0 else 0,
            "interview_rate": round(interviewed / total * 100, 1) if total > 0 else 0,
            "avg_response_time_hours": round(sum(response_times) / len(response_times), 1) if response_times else None
        }
    
    def _format_application(self, app: Application) -> Dict[str, Any]:
        """Format application for history."""
        # Find first response
        first_response = None
        if app.emails:
            inbound = [e for e in app.emails if e.direction == "inbound"]
            if inbound:
                first_response = min(inbound, key=lambda e: e.sent_at or datetime.max)
        
        return {
            "id": app.id,
            "job_id": app.job_id,
            "job_title": app.job.title if app.job else None,
            "company": app.job.company if app.job else None,
            "status": app.status,
            "applied_at": app.applied_at.isoformat() if app.applied_at else None,
            "first_response_at": first_response.sent_at.isoformat() if first_response else None,
            "first_response_type": first_response.classification if first_response else None,
            "relevance_score": app.relevance_score,
            "created_at": app.created_at.isoformat()
        }