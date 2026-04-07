"""Temporal workflow definitions for job automation."""

import asyncio
from datetime import timedelta
from typing import List, Dict, Any, Optional

from temporalio import workflow

# Import activity interfaces
with workflow.unsafe.imports_passed_through():
    from .activities import (
        fetch_unprocessed_jobs,
        apply_rule_filters,
        score_job_relevance,
        generate_tailored_resume,
        draft_application_email,
        create_application_record,
        queue_for_human_review,
        mark_job_processed,
        run_scraping_pipeline,
        queue_scraped_jobs_for_processing,
    )


@workflow.defn
class JobProcessingWorkflow:
    """Main workflow for processing a single job."""
    
    @workflow.run
    async def run(self, job_data: Dict[str, Any], profile_id: int) -> Dict[str, Any]:
        """Process a single job through the pipeline."""
        
        workflow.logger.info(f"Processing job {job_data['id']}")
        
        # Step 1: Apply rule filters
        filter_result = await workflow.execute_activity(
            apply_rule_filters,
            job_data,
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        if not filter_result["passed"]:
            workflow.logger.info(f"Job {job_data['id']} failed filters: {filter_result['reasons']}")
            await workflow.execute_activity(
                mark_job_processed,
                job_data["id"],
                success=True,
                error=f"Filtered out: {filter_result['reasons']}"
            )
            return {
                "job_id": job_data["id"],
                "status": "filtered_out",
                "reasons": filter_result["reasons"],
                "filter_score": filter_result["score"]
            }
        
        # Step 2: Score with AI
        score_result = await workflow.execute_activity(
            score_job_relevance,
            job_data,
            profile_id,
            start_to_close_timeout=timedelta(minutes=2)
        )
        
        if "error" in score_result:
            workflow.logger.error(f"Scoring failed for job {job_data['id']}: {score_result['error']}")
            await workflow.execute_activity(
                mark_job_processed,
                job_data["id"],
                success=False,
                error=score_result["error"]
            )
            return {
                "job_id": job_data["id"],
                "status": "scoring_failed",
                "error": score_result["error"]
            }
        
        # Check if score meets threshold
        if score_result["score"] < 70:
            workflow.logger.info(f"Job {job_data['id']} score {score_result['score']} below threshold")
            await workflow.execute_activity(
                mark_job_processed,
                job_data["id"],
                success=True,
                error=f"Score {score_result['score']} below threshold"
            )
            return {
                "job_id": job_data["id"],
                "status": "low_score",
                "score": score_result["score"],
                "reasoning": score_result.get("reasoning", "")
            }
        
        # Step 3: Generate tailored resume
        resume_result = await workflow.execute_activity(
            generate_tailored_resume,
            job_data,
            profile_id,
            score_result,
            start_to_close_timeout=timedelta(minutes=3)
        )
        
        if "error" in resume_result:
            workflow.logger.error(f"Resume generation failed for job {job_data['id']}: {resume_result['error']}")
            # Continue without tailored resume? Use canonical?
            resume_result = {"resume_id": None, "error": resume_result["error"]}
        
        # Step 4: Draft email
        email_result = await workflow.execute_activity(
            draft_application_email,
            job_data,
            profile_id,
            resume_result,
            start_to_close_timeout=timedelta(minutes=2)
        )
        
        # Step 5: Create application record
        application_id = await workflow.execute_activity(
            create_application_record,
            job_data,
            profile_id,
            score_result,
            resume_result,
            email_result,
            start_to_close_timeout=timedelta(seconds=30)
        )
        
        # Step 6: Queue for human review if needed
        review_type = "standard"
        
        # Check if senior role
        if "senior" in job_data["title"].lower() or "lead" in job_data["title"].lower():
            review_type = "senior"
        
        # Check if ambiguous score
        if 40 <= score_result["score"] <= 70:
            review_type = "ambiguous"
        
        # Check if resume generation failed
        if "error" in resume_result:
            review_type = "resume_failed"
        
        await workflow.execute_activity(
            queue_for_human_review,
            application_id,
            review_type,
            {
                "job": job_data,
                "score": score_result,
                "resume": resume_result,
                "email": email_result
            },
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        # Step 7: Mark job as processed
        await workflow.execute_activity(
            mark_job_processed,
            job_data["id"],
            success=True
        )
        
        workflow.logger.info(f"Job {job_data['id']} processed successfully, application {application_id}")
        
        return {
            "job_id": job_data["id"],
            "status": "processed",
            "application_id": application_id,
            "score": score_result["score"],
            "review_type": review_type
        }


@workflow.defn
class BatchJobProcessingWorkflow:
    """Workflow for processing multiple jobs in batch."""
    
    @workflow.run
    async def run(self, profile_id: int, batch_size: int = 20) -> Dict[str, Any]:
        """Process multiple jobs in batch."""
        
        workflow.logger.info(f"Starting batch processing for profile {profile_id}")
        
        # Fetch unprocessed jobs
        jobs = await workflow.execute_activity(
            fetch_unprocessed_jobs,
            batch_size,
            start_to_close_timeout=timedelta(minutes=2)
        )
        
        if not jobs:
            workflow.logger.info("No unprocessed jobs found")
            return {
                "status": "no_jobs",
                "processed_count": 0
            }
        
        workflow.logger.info(f"Found {len(jobs)} jobs to process")
        
        # Process each job in parallel
        processed = []
        failed = []
        
        # Use child workflows for parallel processing
        child_workflows = []
        for job in jobs:
            child = workflow.start_child_workflow(
                JobProcessingWorkflow.run,
                job,
                profile_id,
                id=f"job-{job['id']}-{workflow.info().workflow_id}",
                task_queue="job-processing-queue"
            )
            child_workflows.append(child)
        
        # Wait for all to complete
        results = await asyncio.gather(*child_workflows, return_exceptions=True)
        
        # Process results
        for job, result in zip(jobs, results):
            if isinstance(result, Exception):
                workflow.logger.error(f"Job {job['id']} failed: {result}")
                failed.append({"job_id": job["id"], "error": str(result)})
            else:
                processed.append(result)
        
        return {
            "status": "completed",
            "total_jobs": len(jobs),
            "processed_count": len(processed),
            "failed_count": len(failed),
            "results": processed,
            "failures": failed
        }


@workflow.defn
class ScrapingWorkflow:
    """Workflow for running the scraping pipeline."""
    
    @workflow.run
    async def run(self, sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Run scraping pipeline and queue jobs for processing."""
        
        workflow.logger.info(f"Starting scraping workflow for sources: {sources or 'all'}")
        
        scrape_result = await workflow.execute_activity(
            run_scraping_pipeline,
            sources,
            start_to_close_timeout=timedelta(minutes=30)
        )
        
        queued_count = 0
        if scrape_result.get("success") and scrape_result.get("total_new_jobs", 0) > 0:
            queued_count = await workflow.execute_activity(
                queue_scraped_jobs_for_processing,
                start_to_close_timeout=timedelta(minutes=5)
            )
        
        return {
            "scrape_result": scrape_result,
            "jobs_queued": queued_count,
            "timestamp": workflow.now().isoformat()
        }


@workflow.defn
class ScheduledScrapingWorkflow:
    """Workflow that runs on a schedule to trigger scraping."""
    
    @workflow.run
    async def run(self, profile_id: int = 1) -> Dict[str, Any]:
        """Run scheduled scraping with automatic job processing."""
        
        workflow.logger.info("Starting scheduled scraping workflow")
        
        scrape_result = await workflow.execute_activity(
            run_scraping_pipeline,
            None,
            start_to_close_timeout=timedelta(minutes=30)
        )
        
        if scrape_result.get("total_new_jobs", 0) > 0:
            workflow.logger.info(f"Found {scrape_result['total_new_jobs']} new jobs, starting batch processing")
            
            batch_result = await workflow.execute_child_workflow(
                BatchJobProcessingWorkflow.run,
                profile_id,
                batch_size=50,
                id=f"batch-{workflow.now().strftime('%Y%m%d-%H%M%S')}",
                task_queue="job-processing-queue"
            )
        else:
            batch_result = {"status": "no_jobs", "processed_count": 0}
        
        return {
            "scrape_result": scrape_result,
            "batch_result": batch_result,
            "timestamp": workflow.now().isoformat()
        }


@workflow.defn
class FollowUpWorkflow:
    """Workflow for sending follow-up emails."""
    
    @workflow.run
    async def run(self, application_id: int, days_since: int) -> Dict[str, Any]:
        """Send follow-up for an application."""
        
        workflow.logger.info(f"Sending follow-up for application {application_id}")
        
        # Get application data
        async with db_manager.session() as session:
            from ....models.application import Application
            from ....models.email import Email
            
            app = await session.get(Application, application_id)
            if not app:
                raise ValueError(f"Application {application_id} not found")
            
            # Check if already responded
            if app.status not in ["applied", "draft"]:
                workflow.logger.info(f"Application {application_id} already has response, skipping follow-up")
                return {"status": "skipped", "reason": "already_responded"}
            
            # Check if follow-up already sent
            from sqlalchemy import select
            stmt = select(Email).where(
                Email.application_id == application_id,
                Email.subject.ilike("%follow%")
            )
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                workflow.logger.info(f"Follow-up already sent for application {application_id}")
                return {"status": "skipped", "reason": "already_sent"}
        
        # Draft follow-up
        from ....ai.email.drafter import EmailDrafter
        drafter = EmailDrafter()
        
        follow_up = await drafter.draft_follow_up(app, days_since)
        
        # Queue for sending (with human review)
        from .activities import queue_for_human_review
        await workflow.execute_activity(
            queue_for_human_review,
            application_id,
            "follow_up",
            {
                "application_id": application_id,
                "follow_up": follow_up,
                "days_since": days_since
            },
            start_to_close_timeout=timedelta(seconds=10)
        )
        
        return {
            "status": "queued",
            "application_id": application_id,
            "follow_up_drafted": True
        }