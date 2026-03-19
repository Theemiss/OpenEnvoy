"""Temporal client setup and management."""

import asyncio
from typing import Optional, Dict, Any
from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker
from temporalio import workflow

from ....core.config import settings
from . import activities
from .workflows import JobProcessingWorkflow, BatchJobProcessingWorkflow


class TemporalClient:
    """Temporal client wrapper."""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.worker: Optional[Worker] = None
        self.task_queue = "job-processing-queue"
    
    async def connect(self):
        """Connect to Temporal server."""
        if self.client:
            return
        
        # Build connection config
        kwargs = {
            "target_host": "localhost:7233",  # Default Temporal port
            "namespace": "default",
        }
        
        # Add TLS if configured
        if settings.TEMPORAL_TLS_CERT and settings.TEMPORAL_TLS_KEY:
            kwargs["tls"] = TLSConfig(
                client_cert=settings.TEMPORAL_TLS_CERT.encode(),
                client_private_key=settings.TEMPORAL_TLS_KEY.encode()
            )
        
        self.client = await Client.connect(**kwargs)
        
        workflow.logger.info("Connected to Temporal server")
    
    async def start_worker(self):
        """Start a worker to process workflows."""
        if not self.client:
            await self.connect()
        
        # Import workflows and activities
        from .workflows import JobProcessingWorkflow, BatchJobProcessingWorkflow
        
        self.worker = Worker(
            self.client,
            task_queue=self.task_queue,
            workflows=[JobProcessingWorkflow, BatchJobProcessingWorkflow],
            activities=[
                activities.fetch_unprocessed_jobs,
                activities.apply_rule_filters,
                activities.score_job_relevance,
                activities.generate_tailored_resume,
                activities.draft_application_email,
                activities.create_application_record,
                activities.queue_for_human_review,
                activities.mark_job_processed,
            ],
        )
        
        # Start worker in background
        asyncio.create_task(self.worker.run())
        
        workflow.logger.info(f"Worker started on queue: {self.task_queue}")
    
    async def start_job_processing(self, profile_id: int, batch_size: int = 20) -> str:
        """Start a batch job processing workflow."""
        if not self.client:
            await self.connect()
        
        handle = await self.client.start_workflow(
            "BatchJobProcessingWorkflow",
            profile_id,
            batch_size,
            id=f"batch-{asyncio.get_event_loop().time()}",
            task_queue=self.task_queue,
        )
        
        workflow.logger.info(f"Started batch workflow: {handle.id}")
        return handle.id
    
    async def schedule_periodic_scraping(self, interval_hours: int = 4):
        """Schedule periodic scraping workflow."""
        if not self.client:
            await self.connect()
        
        # This would use Temporal schedules in a real implementation
        # For now, we'll just start one manually
        
        handle = await self.client.start_workflow(
            "ScheduledScrapingWorkflow",
            id=f"scrape-schedule-{asyncio.get_event_loop().time()}",
            task_queue="scraping-queue",
        )
        
        return handle.id
    
    async def close(self):
        """Close the client."""
        if self.worker:
            self.worker.shutdown()
        
        if self.client:
            # Client doesn't need explicit closing
            pass


temporal_client = TemporalClient()