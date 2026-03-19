"""Applications API endpoints."""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ....core.database import db_manager, get_db
from ....models.job import Job
from ....models.resume import Resume
from ....models.application import Application, ApplicationTimeline
from ....schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
    ApplicationStats,
)
from ....engine.email.sender import EmailSender

router = APIRouter(prefix="/applications", tags=["applications"])


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    """List applications with optional filtering."""
    query = select(Application)

    if status:
        query = query.where(Application.status == status)

    query = query.order_by(Application.updated_at.desc()).offset(skip).limit(limit)
    result = await session.execute(query)
    applications = result.scalars().all()

    return [ApplicationResponse.model_validate(a) for a in applications]


@router.get("/stats/summary", response_model=ApplicationStats)
async def get_application_stats(
    period_days: int = Query(30, ge=1, le=365),
    session: AsyncSession = Depends(get_db),
):
    """Get application statistics."""
    from datetime import timedelta

    cutoff = datetime.now() - timedelta(days=period_days)

    # Total count
    count_query = select(func.count(Application.id)).where(
        Application.created_at >= cutoff
    )
    result = await session.execute(count_query)
    total = result.scalar() or 0

    # Count by status
    status_query = select(
        Application.status, func.count(Application.id)
    ).where(Application.created_at >= cutoff).group_by(Application.status)
    result = await session.execute(status_query)
    by_status = {row[0]: row[1] for row in result.all()}

    # Response rate
    applied_query = select(func.count(Application.id)).where(
        Application.created_at >= cutoff, Application.applied_at.isnot(None)
    )
    result = await session.execute(applied_query)
    applied_count = result.scalar() or 0
    response_rate = round((applied_count / total) * 100, 1) if total > 0 else 0.0

    # Interview rate
    interview_query = select(func.count(Application.id)).where(
        Application.created_at >= cutoff,
        Application.status.in_(["interviewing", "offered", "accepted"]),
    )
    result = await session.execute(interview_query)
    interview_count = result.scalar() or 0
    interview_rate = round((interview_count / total) * 100, 1) if total > 0 else 0.0

    return ApplicationStats(
        period_days=period_days,
        total_applications=total,
        by_status=by_status,
        response_rate=response_rate,
        interview_rate=interview_rate,
    )


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get application by ID."""
    app = await session.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    return ApplicationResponse.model_validate(app)


@router.post("", response_model=ApplicationResponse)
async def create_application(
    application_create: ApplicationCreate,
    session: AsyncSession = Depends(get_db),
):
    """Create a new application."""
    job = await session.get(Job, application_create.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    existing = await session.execute(
        select(Application).where(Application.job_id == application_create.job_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400, detail="Application for this job already exists"
        )

    if application_create.resume_id:
        resume = await session.get(Resume, application_create.resume_id)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

    app = Application(
        job_id=application_create.job_id,
        resume_id=application_create.resume_id,
        status="draft",
    )
    session.add(app)
    await session.commit()
    await session.refresh(app)

    timeline = ApplicationTimeline(
        application_id=app.id,
        event_type="application_created",
        description="Application draft created",
        ai_generated=False,
    )
    session.add(timeline)
    await session.commit()

    return ApplicationResponse.model_validate(app)


@router.patch("/{application_id}", response_model=ApplicationResponse)
async def update_application(
    application_id: int,
    application_update: ApplicationUpdate,
    session: AsyncSession = Depends(get_db),
):
    """Update an application."""
    app = await session.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    update_data = application_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(app, key, value)

    app.updated_at = datetime.now()
    await session.commit()
    await session.refresh(app)

    return ApplicationResponse.model_validate(app)


@router.post("/{application_id}/submit")
async def submit_application(
    application_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Submit an application (send email)."""
    app = await session.get(Application, application_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    if app.status == "applied":
        raise HTTPException(status_code=400, detail="Application already submitted")

    job = app.job

    sender = EmailSender()
    result = await sender.send_email(
        to_email="recruiter@example.com",
        subject=f"Application for {job.title}",
        body=f"Please find my application for the {job.title} position at {job.company}.",
        application_id=app.id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to send"))

    app.status = "applied"
    app.applied_at = datetime.now()
    app.application_method = "email"
    app.last_activity_at = datetime.now()

    timeline = ApplicationTimeline(
        application_id=app.id,
        event_type="application_sent",
        description="Application submitted via email",
        ai_generated=False,
    )
    session.add(timeline)
    await session.commit()

    return {"status": "submitted", "message_id": result.get("message_id")}
