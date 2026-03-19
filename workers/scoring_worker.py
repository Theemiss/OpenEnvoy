#!/usr/bin/env python3
"""Scoring worker for AI job relevance scoring."""

import asyncio
import json
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.ai.scoring.two_tier import JobScorer
from backend.ai.cost_tracker import AICostTracker, AICallRecord
from backend.core.database import db_manager
from backend.core.config import settings
from backend.core.logging import setup_logging
from backend.core.cache import cache
from backend.core.alerting import alert_manager
from backend.models.job import Job
from backend.models.profile import Profile

logger = logging.getLogger(__name__)


async def get_next_job_for_scoring():
    """Get next job from queue for scoring."""
    # Get job ID from queue
    job_id = await cache.lpop("job_queue")
    if not job_id:
        return None
    
    # Get job from database
    async with db_manager.session() as session:
        from sqlalchemy import select
        job = await session.get(Job, int(job_id))
        
        if not job or not job.is_active:
            return None
        
        return job


async def score_job(job: Job, profile_id: int = 1):
    """Score a single job."""
    scorer = JobScorer()
    tracker = AICostTracker()
    
    # Get profile
    async with db_manager.session() as session:
        profile = await session.get(Profile, profile_id)
        if not profile:
            logger.error(f"Profile {profile_id} not found")
            return None
    
    try:
        logger.info(f"Scoring job {job.id}: {job.title} at {job.company}")
        
        # Score the job
        result = await scorer.score_job(job, profile)
        
        # Track cost
        await tracker.record_call(AICallRecord(
            timestamp=result.get("scored_at"),
            model=result.get("model_used", "unknown"),
            operation="scoring",
            prompt_tokens=result.get("usage", {}).get("prompt_tokens", 0),
            completion_tokens=result.get("usage", {}).get("completion_tokens", 0),
            total_tokens=result.get("usage", {}).get("total_tokens", 0),
            cost=result.get("cost", 0),
            latency=result.get("latency", 0),
            job_id=job.id,
            success=True
        ))
        
        # Update job in database
        async with db_manager.session() as session:
            job = await session.get(Job, job.id)
            if job:
                job.relevance_score = result.get("score")
                job.score_reasoning = result.get("reasoning")
                job.score_model = result.get("model_used")
                await session.commit()
        
        logger.info(f"Job {job.id} scored: {result.get('score')} (using {result.get('model_used')})")
        
        # If score is high enough, queue for resume generation
        if result.get("score", 0) >= 70:
            await cache.rpush("resume_queue", job.id)
            logger.info(f"Job {job.id} queued for resume generation")
        
        return result
        
    except Exception as e:
        logger.error(f"Error scoring job {job.id}: {str(e)}")
        
        # Track failed call
        await tracker.record_call(AICallRecord(
            timestamp=datetime.now(),
            model="unknown",
            operation="scoring",
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            cost=0,
            latency=0,
            job_id=job.id,
            success=False,
            error=str(e)
        ))
        
        # Increment attempt count
        async with db_manager.session() as session:
            job = await session.get(Job, job.id)
            if job:
                job.process_attempts += 1
                job.last_error = str(e)[:500]
                await session.commit()
        
        return None


async def main():
    """Main scoring worker loop."""
    setup_logging("scoring_worker")
    
    logger.info("Starting scoring worker")
    
    # Get active profile ID (could be configured)
    profile_id = 1
    
    # Warm up cache if needed
    await cache.ping()
    
    consecutive_errors = 0
    
    while True:
        try:
            # Get next job
            job = await get_next_job_for_scoring()
            
            if job:
                # Score it
                result = await score_job(job, profile_id)
                
                if result:
                    consecutive_errors = 0
                else:
                    consecutive_errors += 1
                
                # Small delay between scores
                await asyncio.sleep(2)
            else:
                # No jobs in queue, wait a bit
                logger.debug("No jobs in queue, waiting...")
                await asyncio.sleep(30)
                consecutive_errors = 0
            
            # Alert if too many consecutive errors
            if consecutive_errors >= 5:
                await alert_manager.send_alert(
                    title="Scoring Worker Errors",
                    message=f"{consecutive_errors} consecutive scoring failures",
                    severity="warning"
                )
            
        except Exception as e:
            logger.error(f"Unhandled error in scoring worker: {str(e)}")
            consecutive_errors += 1
            await asyncio.sleep(10)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())