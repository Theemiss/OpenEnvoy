from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_async_session
from backend.engine.tracking.history import ApplicationHistory
from backend.models.application import Application
from backend.models.email import Email
from backend.schemas.analytics import (
    OverviewResponse,
    ResponseRateItem,
    SourceBreakdownItem,
    TrendDataItem,
    TimelineItem,
)

# This router is mounted under /api/v1/analytics by backend/api/v1/__init__.py
analytics_router = APIRouter()


@analytics_router.get(
    "/overview",
    response_model=OverviewResponse,
    summary="Analytics overview",
    description="Dashboard overview stats: total applications, response rate, interview rate",
)
async def overview(db: AsyncSession = Depends(get_async_session)) -> OverviewResponse:
    """Dashboard overview stats: total applications, response rate, interview rate."""
    stats = {}
    if hasattr(ApplicationHistory, "get_statistics"):
        try:
            stats = await ApplicationHistory.get_statistics(db)  # type: ignore[call-arg]
        except Exception:
            stats = {}

    if not isinstance(stats, dict):
        stats = {}

    total = int(stats.get("total_applications", 0))
    response_rate = float(stats.get("response_rate", 0.0))
    interview_rate = float(stats.get("interview_rate", 0.0))

    return OverviewResponse(
        total_applications=total,
        response_rate=response_rate,
        interview_rate=interview_rate,
    )


@analytics_router.get(
    "/response-rates",
    response_model=List[ResponseRateItem],
    summary="Response rate over time",
    description="Response rate over time, grouped by week",
)
async def response_rates(db: AsyncSession = Depends(get_async_session)) -> List[ResponseRateItem]:
    """Response rate over time, grouped by week."""
    results: List[ResponseRateItem] = []

    # First, try to fetch pre-aggregated series from ApplicationHistory if available
    if hasattr(ApplicationHistory, "get_statistics"):
        try:
            stats = await ApplicationHistory.get_statistics(db)  # type: ignore[call-arg]
            if isinstance(stats, dict) and "response_rate_by_period" in stats:
                for rec in stats["response_rate_by_period"]:
                    period = str(rec.get("period"))
                    rate = float(rec.get("rate", 0.0))
                    results.append(ResponseRateItem(period=period, rate=rate))
                return results
        except Exception:
            pass

    # Fallback: compute from Email data grouped by week
    q = (
        select(
            func.date_trunc("week", Email.sent_at).label("week"),
            func.sum(case((Email.classification == "responded", 1), else_=0)).label("responded"),
            func.count(Email.id).label("total"),
        )
        .group_by("week")
        .order_by("week")
    )
    res = await db.execute(q)
    for row in res:
        week = str(row.week)
        responded = int(row.responded) if row.responded is not None else 0
        total = int(row.total) if row.total is not None else 0
        rate = (responded / total) if total > 0 else 0.0
        results.append(ResponseRateItem(period=week, rate=rate))
    return results


@analytics_router.get(
    "/source-breakdown",
    response_model=List[SourceBreakdownItem],
    summary="Applications by source",
    description="Breakdown of applications by their source",
)
async def source_breakdown(db: AsyncSession = Depends(get_async_session)) -> List[SourceBreakdownItem]:
    """Breakdown of applications by source."""
    items: List[SourceBreakdownItem] = []
    if not hasattr(Application, "source"):
        return items
    q = select(Application.source, func.count(Application.id).label("count")).group_by(Application.source).order_by(func.count(Application.id).desc())
    res = await db.execute(q)
    for row in res:
        source = getattr(row, "source", None)
        count = int(getattr(row, "count", 0))
        if source is None:
            source = "unknown"
        items.append(SourceBreakdownItem(source=source, count=count))
    return items


@analytics_router.get(
    "/trends",
    response_model=List[TrendDataItem],
    summary="Trending metrics",
    description="Weekly trends for applications and response rate",
)
async def trends(db: AsyncSession = Depends(get_async_session)) -> List[TrendDataItem]:
    """Trending metrics: weekly applications and response rate."""
    # Applications per week
    apps_q = select(
        func.date_trunc("week", Application.applied_at).label("week"),
        func.count(Application.id).label("applications"),
    ).group_by("week").order_by("week")
    apps_res = await db.execute(apps_q)
    apps_by_week = {str(r.week): int(r.applications) for r in apps_res}

    # Responses per week (from EmailClassification 'responded')
    resp_q = select(
        func.date_trunc("week", Email.sent_at).label("week"),
        func.count(Email.id).label("responded"),
    ).where(Email.classification == "responded").group_by("week").order_by("week")
    resp_res = await db.execute(resp_q)
    resp_by_week = {str(r.week): int(r.responded) for r in resp_res}

    weeks = sorted(set(list(apps_by_week.keys()) + list(resp_by_week.keys())))
    items: List[TrendDataItem] = []
    for w in weeks:
        apps = apps_by_week.get(w, 0)
        responded = resp_by_week.get(w, 0)
        rate = (responded / apps) if apps > 0 else 0.0
        items.append(TrendDataItem(period=w, applications=apps, response_rate=rate))
    return items


@analytics_router.get(
    "/timeline",
    response_model=List[TimelineItem],
    summary="Recent activity timeline",
    description="Recent activity events combining applications and email events",
)
async def timeline(db: AsyncSession = Depends(get_async_session)) -> List[TimelineItem]:
    """Recent activity timeline (latest events from applications and emails)."""
    timeline_items: List[TimelineItem] = []

    # Latest applications
    app_q = select(Application.id, Application.created_at, Application.status, Application.applied_at).order_by(Application.created_at.desc()).limit(6)
    apps = await db.execute(app_q)
    for a in apps:
        ts = getattr(a, "created_at", None) or getattr(a, "applied_at", None)
        ts_str = str(ts) if ts is not None else ""
        event = f"Application {getattr(a, 'id', '')} status={getattr(a, 'status', '')}"
        timeline_items.append(TimelineItem(timestamp=ts_str, event=event))

    # Latest emails
    email_q = select(Email.id, Email.sent_at, Email.direction, Email.classification).order_by(Email.sent_at.desc()).limit(6)
    emails = await db.execute(email_q)
    for e in emails:
        ts = getattr(e, "sent_at", None)
        ts_str = str(ts) if ts is not None else ""
        direction = getattr(e, "direction", "unknown")
        classification = getattr(e, "classification", "")
        event = f"Email {getattr(e, 'id', '')} dir={direction} cls={classification}"
        timeline_items.append(TimelineItem(timestamp=ts_str, event=event))

    # Sort by timestamp descending if possible
    timeline_items.sort(key=lambda x: x.timestamp, reverse=True)
    return timeline_items
