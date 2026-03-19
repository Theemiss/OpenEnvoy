"""Feedback and insights endpoints."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ....core.database import db_manager, get_db
from ....models.application import Application, ApplicationTimeline
from ....ai.cost_tracker import AICostTracker, CostOptimizationAdvisor

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.get("/report")
async def get_feedback_report(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db),
):
    """Get application feedback report."""
    cutoff = datetime.now() - timedelta(days=days)

    # Application stats
    total_result = await session.execute(
        select(func.count(Application.id)).where(Application.created_at >= cutoff)
    )
    total = total_result.scalar() or 0

    # Status breakdown
    status_result = await session.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.created_at >= cutoff)
        .group_by(Application.status)
    )
    by_status = {row[0]: row[1] for row in status_result.all()}

    # Timeline events
    events_result = await session.execute(
        select(ApplicationTimeline.event_type, func.count(ApplicationTimeline.id))
        .where(ApplicationTimeline.event_date >= cutoff)
        .group_by(ApplicationTimeline.event_type)
    )
    events = {row[0]: row[1] for row in events_result.all()}

    # Calculate response rate
    applied = by_status.get("applied", 0)
    response_rate = round((applied / total) * 100, 1) if total > 0 else 0.0

    # Interview rate
    interviewing = by_status.get("interviewing", 0) + by_status.get("offered", 0)
    interview_rate = round((interviewing / total) * 100, 1) if total > 0 else 0.0

    return {
        "period_days": days,
        "total_applications": total,
        "by_status": by_status,
        "response_rate": response_rate,
        "interview_rate": interview_rate,
        "events": events,
        "generated_at": datetime.now().isoformat(),
    }


@router.get("/insights")
async def get_insights(
    days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db),
):
    """Get AI-generated insights from application data."""
    cutoff = datetime.now() - timedelta(days=days)

    # Recent applications
    result = await session.execute(
        select(Application)
        .where(Application.created_at >= cutoff)
        .order_by(Application.created_at.desc())
        .limit(100)
    )
    applications = result.scalars().all()

    # Calculate insights
    insights = []

    if not applications:
        insights.append({
            "type": "info",
            "message": "No applications in the selected period. Start applying to see insights!"
        })
        return {"insights": insights}

    # Insight 1: Check submission rate
    submitted = sum(1 for a in applications if a.status != "draft")
    if submitted > 0:
        insights.append({
            "type": "success",
            "message": f"{submitted} of {len(applications)} applications have been submitted."
        })
    else:
        insights.append({
            "type": "warning",
            "message": "You have draft applications waiting to be submitted."
        })

    # Insight 2: Interview rate
    interviewing = sum(1 for a in applications if a.status in ["interviewing", "offered", "accepted"])
    if interviewing > 0:
        rate = round((interviewing / len(applications)) * 100, 1)
        insights.append({
            "type": "success",
            "message": f"{rate}% of applications led to interviews. Keep going!"
        })

    # Insight 3: High-scoring jobs
    high_score = [a for a in applications if a.relevance_score and a.relevance_score >= 70]
    if high_score:
        insights.append({
            "type": "info",
            "message": f"You've applied to {len(high_score)} highly relevant positions (score 70+)."
        })

    # Insight 4: Check for stalled applications
    stalled = [
        a for a in applications
        if a.status == "applied"
        and a.last_activity_at
        and (datetime.now() - a.last_activity_at).days > 14
    ]
    if stalled:
        insights.append({
            "type": "action",
            "message": f"You have {len(stalled)} applications with no activity for 2+ weeks. Consider follow-ups."
        })

    return {"insights": insights}
