"""Feedback data collection from applications and responses."""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

from ..core.database import db_manager
from ..models.application import Application
from ..models.email import Email
from ..core.cache import cache

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """Collect feedback data from application outcomes."""
    
    def __init__(self):
        self.stats_key = "feedback:stats"
    
    async def collect_application_outcomes(self, days: int = 30) -> Dict[str, Any]:
        """Collect outcomes for applications in the last N days."""
        
        cutoff = datetime.now() - timedelta(days=days)
        
        async with db_manager.session() as session:
            from sqlalchemy import select, func
            
            # Get applications with their emails
            stmt = select(Application).where(
                Application.created_at >= cutoff,
                Application.status.in_(["interviewing", "rejected", "offered", "accepted"])
            )
            
            result = await session.execute(stmt)
            applications = result.scalars().all()
            
            outcomes = []
            for app in applications:
                # Get emails for this application
                email_stmt = select(Email).where(Email.application_id == app.id)
                email_result = await session.execute(email_stmt)
                emails = email_result.scalars().all()
                
                # Get the initial application email (first outbound)
                initial_email = next(
                    (e for e in emails if e.direction == "outbound" and e.ai_generated),
                    None
                )
                
                # Get the response (first inbound after application)
                response = next(
                    (e for e in emails if e.direction == "inbound" and 
                     e.sent_at > (app.applied_at or app.created_at)),
                    None
                )
                
                outcomes.append({
                    "application_id": app.id,
                    "job_id": app.job_id,
                    "job_title": app.job.title if app.job else None,
                    "company": app.job.company if app.job else None,
                    "status": app.status,
                    "relevance_score": app.relevance_score,
                    "applied_at": app.applied_at,
                    "response_time": (response.sent_at - app.applied_at).total_seconds() / 3600 
                                    if response and app.applied_at else None,
                    "response_type": response.classification if response else None,
                    "email_subject": initial_email.subject if initial_email else None,
                    "email_body_preview": initial_email.body_text[:200] if initial_email else None
                })
            
            # Cache the results
            await cache.set(
                f"{self.stats_key}:outcomes:{days}",
                outcomes,
                ttl=3600  # 1 hour
            )
            
            return outcomes
    
    async def calculate_response_rates(self, days: int = 30) -> Dict[str, Any]:
        """Calculate response rates by various dimensions."""
        
        outcomes = await self.collect_application_outcomes(days)
        
        if not outcomes:
            return {}
        
        # Overall stats
        total = len(outcomes)
        responded = sum(1 for o in outcomes if o["response_type"])
        interviewed = sum(1 for o in outcomes if o["status"] == "interviewing")
        rejected = sum(1 for o in outcomes if o["status"] == "rejected")
        offered = sum(1 for o in outcomes if o["status"] in ["offered", "accepted"])
        
        # By score range
        score_ranges = {
            "90-100": [],
            "80-89": [],
            "70-79": [],
            "60-69": [],
            "below_60": []
        }
        
        for o in outcomes:
            score = o["relevance_score"] or 0
            if score >= 90:
                score_ranges["90-100"].append(o)
            elif score >= 80:
                score_ranges["80-89"].append(o)
            elif score >= 70:
                score_ranges["70-79"].append(o)
            elif score >= 60:
                score_ranges["60-69"].append(o)
            else:
                score_ranges["below_60"].append(o)
        
        # Calculate rates by score range
        score_performance = {}
        for range_name, apps in score_ranges.items():
            if apps:
                range_total = len(apps)
                range_responded = sum(1 for a in apps if a["response_type"])
                range_interviewed = sum(1 for a in apps if a["status"] == "interviewing")
                
                score_performance[range_name] = {
                    "count": range_total,
                    "response_rate": round(range_responded / range_total * 100, 1),
                    "interview_rate": round(range_interviewed / range_total * 100, 1)
                }
        
        # By company
        company_stats = defaultdict(lambda: {"count": 0, "responded": 0, "interviewed": 0})
        for o in outcomes:
            if o["company"]:
                company = o["company"]
                company_stats[company]["count"] += 1
                if o["response_type"]:
                    company_stats[company]["responded"] += 1
                if o["status"] == "interviewing":
                    company_stats[company]["interviewed"] += 1
        
        # Calculate rates for companies with multiple applications
        company_rates = []
        for company, stats in company_stats.items():
            if stats["count"] >= 2:
                company_rates.append({
                    "company": company,
                    "count": stats["count"],
                    "response_rate": round(stats["responded"] / stats["count"] * 100, 1),
                    "interview_rate": round(stats["interviewed"] / stats["count"] * 100, 1)
                })
        
        # Sort by count
        company_rates.sort(key=lambda x: x["count"], reverse=True)
        
        # By response type
        response_types = Counter(o["response_type"] for o in outcomes if o["response_type"])
        
        return {
            "period_days": days,
            "total_applications": total,
            "overall": {
                "response_rate": round(responded / total * 100, 1) if total > 0 else 0,
                "interview_rate": round(interviewed / total * 100, 1) if total > 0 else 0,
                "offer_rate": round(offered / total * 100, 1) if total > 0 else 0,
                "rejection_rate": round(rejected / total * 100, 1) if total > 0 else 0
            },
            "by_score": score_performance,
            "top_companies": company_rates[:10],
            "response_types": dict(response_types)
        }
    
    async def analyze_email_performance(self, days: int = 30) -> Dict[str, Any]:
        """Analyze which email styles perform best."""
        
        outcomes = await self.collect_application_outcomes(days)
        
        # Group by email subject patterns
        email_patterns = defaultdict(lambda: {"count": 0, "responded": 0})
        
        for o in outcomes:
            if o["email_subject"]:
                # Simple categorization - can be improved
                subject = o["email_subject"].lower()
                
                if "interested" in subject:
                    pattern = "interested"
                elif "application" in subject:
                    pattern = "standard"
                elif "hello" in subject or "hi" in subject:
                    pattern = "casual"
                elif "passionate" in subject:
                    pattern = "passionate"
                else:
                    pattern = "other"
                
                email_patterns[pattern]["count"] += 1
                if o["response_type"]:
                    email_patterns[pattern]["responded"] += 1
        
        # Calculate rates
        pattern_rates = []
        for pattern, stats in email_patterns.items():
            if stats["count"] >= 3:
                pattern_rates.append({
                    "pattern": pattern,
                    "count": stats["count"],
                    "response_rate": round(stats["responded"] / stats["count"] * 100, 1)
                })
        
        return {
            "email_patterns": sorted(pattern_rates, key=lambda x: x["response_rate"], reverse=True)
        }
    
    async def get_feedback_summary(self) -> Dict[str, Any]:
        """Get comprehensive feedback summary."""
        
        # Get data for different time periods
        week_data = await self.calculate_response_rates(7)
        month_data = await self.calculate_response_rates(30)
        email_data = await self.analyze_email_performance(30)
        
        # Get trending
        if week_data and month_data:
            trend = {
                "response_rate_change": round(
                    week_data["overall"]["response_rate"] - 
                    (month_data["overall"]["response_rate"] or 0), 1
                ),
                "interview_rate_change": round(
                    week_data["overall"]["interview_rate"] - 
                    (month_data["overall"]["interview_rate"] or 0), 1
                )
            }
        else:
            trend = {}
        
        return {
            "last_7_days": week_data,
            "last_30_days": month_data,
            "trends": trend,
            "email_performance": email_data,
            "generated_at": datetime.now().isoformat()
        }