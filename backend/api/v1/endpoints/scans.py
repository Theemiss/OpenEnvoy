"""Job scan endpoints - trigger and monitor scrapes."""

import asyncio
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from ....core.database import get_db
from ....models.scrape_run import ScrapeRun, ScrapeRunStatus
from ....models.job import Job
from ....schemas.scan_run import (
    ScanRunCreate,
    ScanRunResponse,
    ScanRunDetailResponse,
    ScanStatusResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/jobs", tags=["jobs-scan"])


async def _run_scraping_pipeline(scrape_run_id: int):
    """Background task that runs the scraping pipeline."""
    from ....core.database import db_manager
    from ....scrapers.pipeline import ScrapingPipeline

    async with db_manager.session() as session:
        scrape_run = await session.get(ScrapeRun, scrape_run_id)
        if not scrape_run:
            return

        scrape_run.status = ScrapeRunStatus.RUNNING.value
        scrape_run.started_at = datetime.utcnow()
        await session.commit()

        try:
            pipeline = ScrapingPipeline()
            results = await pipeline.run_all()

            # Calculate totals
            total_found = sum(results.values())

            # Get saved count
            saved_count_query = (
                select(func.count())
                .select_from(Job)
                .where(Job.scraped_at >= scrape_run.started_at)
            )
            result = await session.execute(saved_count_query)
            saved_count = result.scalar() or 0

            scrape_run.results = results
            scrape_run.total_jobs_found = total_found
            scrape_run.total_jobs_saved = saved_count
            scrape_run.status = ScrapeRunStatus.COMPLETED.value
            scrape_run.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error(f"Scrape failed: {e}")
            scrape_run.status = ScrapeRunStatus.FAILED.value
            scrape_run.error_message = str(e)
            scrape_run.completed_at = datetime.utcnow()

        await session.commit()


@router.post("/scan", response_model=ScanRunResponse)
async def trigger_scan(
    body: ScanRunCreate = ScanRunCreate(),
    session: AsyncSession = Depends(get_db),
):
    """Trigger a manual job scan."""

    # Create scan run record
    scrape_run = ScrapeRun(
        status=ScrapeRunStatus.PENDING.value,
        trigger_type=body.trigger_type,
    )
    session.add(scrape_run)
    await session.commit()
    await session.refresh(scrape_run)

    # Run scraping in background
    asyncio.create_task(_run_scraping_pipeline(scrape_run.id))

    return ScanRunResponse.model_validate(scrape_run)


@router.get("/scan/{scan_id}", response_model=ScanRunDetailResponse)
async def get_scan_status(
    scan_id: int,
    session: AsyncSession = Depends(get_db),
):
    """Get status of a specific scan run."""
    scrape_run = await session.get(ScrapeRun, scan_id)
    if not scrape_run:
        raise HTTPException(status_code=404, detail="Scan not found")

    return ScanRunDetailResponse.model_validate(scrape_run)


@router.get("/scan", response_model=ScanStatusResponse)
async def get_current_scan_status(
    session: AsyncSession = Depends(get_db),
):
    """Get the current/latest scan status."""
    # Get most recent scan
    query = select(ScrapeRun).order_by(desc(ScrapeRun.created_at)).limit(1)
    result = await session.execute(query)
    last_run = result.scalar_one_or_none()

    # Check if any scan is currently running
    running_query = select(ScrapeRun.id).where(
        ScrapeRun.status == ScrapeRunStatus.RUNNING.value
    )
    running_result = await session.execute(running_query)
    is_running = running_result.scalar_one_or_none() is not None

    # Count queued jobs (jobs scraped in last 24h but not processed)
    recent_jobs_query = (
        select(func.count())
        .select_from(Job)
        .where(
            Job.is_active == True,
            Job.is_processed == False,
        )
    )
    recent_result = await session.execute(recent_jobs_query)
    queued_jobs = recent_result.scalar() or 0

    return ScanStatusResponse(
        is_running=is_running,
        last_run_id=last_run.id if last_run else None,
        last_run_at=last_run.created_at if last_run else None,
        last_run_status=last_run.status if last_run else None,
        recent_results=last_run.results if last_run else None,
        next_run_in_seconds=None,  # Manual scan only
    )
