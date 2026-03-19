"""Celery task definitions."""

from celery import shared_task
import logging
import asyncio

from ....core.database import db_manager
from ....models.job import Job
from ....models.profile import Profile
from ....scrapers.pipeline import ScrapingPipeline
from ....ai.scoring.two_tier import JobScorer
from ....ai.resume_adaptation.generator import ResumeAdapter
from ....engine.email.sender import EmailSender
from ....engine.email.followup import FollowUpManager
from ....engine.email.monitor import EmailMonitor

logger = logging.getLogger(__name__)


@shared_task(name="scrape_jobs_task")
def scrape_jobs_task():
    """Periodic task to scrape jobs."""
    async def _run():
        pipeline = ScrapingPipeline()
        try:
            results = await pipeline.run_all()
            queued = await pipeline.process_new_jobs()
            logger.info(f"Scraped jobs: {results}, queued: {queued}")
            return {"scraped": results, "queued": queued}
        finally:
            await pipeline.close()
    
    return asyncio.run(_run())


@shared_task(name="process_job_task")
def process_job_task(job_id: int, profile_id: int = 1):
    """Process a single job through the pipeline."""
    async def _run():
        async with db_manager.session() as session:
            job = await session.get(Job, job_id)
            profile = await session.get(Profile, profile_id)
            
            if not job or not profile:
                logger.error(f"Job {job_id} or profile {profile_id} not found")
                return None
            
            # Score job
            scorer = JobScorer()
            score_result = await scorer.score_job(job, profile)
            
            if score_result.get("score", 0) >= 70:
                # Generate resume
                adapter = ResumeAdapter()
                resume_result = await adapter.generate_tailored_resume(job, profile)
                
                # Draft email
                from ....ai.email.drafter import EmailDrafter
                drafter = EmailDrafter()
                email_result = await drafter.draft_initial_email(job, profile)
                
                # Create application
                from ....models.application import Application
                app = Application(
                    job_id=job_id,
                    status="draft",
                    relevance_score=score_result.get("score")
                )
                session.add(app)
                await session.commit()
                
                return {
                    "job_id": job_id,
                    "score": score_result.get("score"),
                    "resume_generated": True,
                    "application_id": app.id
                }
            
            return {
                "job_id": job_id,
                "score": score_result.get("score"),
                "action": "skip"
            }
    
    return asyncio.run(_run())


@shared_task(name="score_job_task")
def score_job_task(job_id: int, profile_id: int = 1):
    """Score a job (subset of process_job_task)."""
    async def _run():
        async with db_manager.session() as session:
            job = await session.get(Job, job_id)
            profile = await session.get(Profile, profile_id)
            
            if not job or not profile:
                return None
            
            scorer = JobScorer()
            result = await scorer.score_job(job, profile)
            
            # Update job
            job.relevance_score = result.get("score")
            job.score_reasoning = result.get("reasoning")
            await session.commit()
            
            return result
    
    return asyncio.run(_run())


@shared_task(name="generate_resume_task")
def generate_resume_task(job_id: int, profile_id: int = 1):
    """Generate tailored resume for a job."""
    async def _run():
        async with db_manager.session() as session:
            job = await session.get(Job, job_id)
            profile = await session.get(Profile, profile_id)
            
            if not job or not profile:
                return None
            
            adapter = ResumeAdapter()
            result = await adapter.generate_tailored_resume(job, profile)
            
            # Save resume
            resume_id = await adapter.save_tailored_resume(result, job, profile)
            
            return {
                "job_id": job_id,
                "resume_id": resume_id,
                "changes": result.get("changes_made")
            }
    
    return asyncio.run(_run())


@shared_task(name="send_email_task")
def send_email_task(email_data: dict):
    """Send an email."""
    async def _run():
        sender = EmailSender()
        result = await sender.send_email(**email_data)
        return result
    
    return asyncio.run(_run())


@shared_task(name="check_followups_task")
def check_followups_task():
    """Check and send follow-up emails."""
    async def _run():
        manager = FollowUpManager()
        results = await manager.send_batch_follow_ups(limit=10)
        return {"followups_sent": len(results), "results": results}
    
    return asyncio.run(_run())


@shared_task(name="check_email_replies_task")
def check_email_replies_task():
    """Check for new email replies."""
    async def _run():
        monitor = EmailMonitor()
        replies = await monitor.check_new_replies()
        return {"replies_found": len(replies)}
    
    return asyncio.run(_run())