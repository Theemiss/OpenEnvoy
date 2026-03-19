"""Jobs API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ....core.database import db_manager, get_db
from ....models.job import Job
from ....schemas.job import JobResponse, JobListResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    job_type: Optional[str] = None,
    location: Optional[str] = None,
    min_score: Optional[float] = Query(None, ge=0, le=100),
    sort_by: str = Query(
        "scraped_at", regex="^(scraped_at|relevance_score|company|title)$"
    ),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    session: AsyncSession = Depends(get_db),
):
    """List jobs with filtering and pagination."""

    # Build query
    query = select(Job).where(Job.is_active == True)

    # Apply filters
    if search:
        query = query.where(
            Job.title.ilike(f"%{search}%")
            | Job.company.ilike(f"%{search}%")
            | Job.description.ilike(f"%{search}%")
        )

    if job_type:
        query = query.where(Job.job_type == job_type)

    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))

    if min_score:
        query = query.where(Job.relevance_score >= min_score)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    result = await session.execute(count_query)
    total = result.scalar() or 0

    # Apply sorting
    if sort_order == "desc":
        query = query.order_by(getattr(Job, sort_by).desc())
    else:
        query = query.order_by(getattr(Job, sort_by))

    # Apply pagination
    query = query.offset(skip).limit(limit)

    # Execute
    result = await session.execute(query)
    jobs = result.scalars().all()

    return JobListResponse(
        items=[JobResponse.model_validate(job) for job in jobs],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int, session: AsyncSession = Depends(get_db)
):
    """Get job by ID."""
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobResponse.model_validate(job)


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: int,
    job_update: dict,
    session: AsyncSession = Depends(get_db),
):
    """Update job."""
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    for key, value in job_update.items():
        if hasattr(job, key):
            setattr(job, key, value)

    await session.commit()
    await session.refresh(job)

    return JobResponse.model_validate(job)


@router.delete("/{job_id}")
async def delete_job(
    job_id: int, session: AsyncSession = Depends(get_db)
):
    """Soft delete job."""
    job = await session.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.is_active = False
    await session.commit()

    return {"message": "Job deleted successfully"}
