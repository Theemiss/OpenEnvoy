"""Workflow orchestration package.

This package provides workflow management for long-running processes
using either Temporal.io or Celery as the backend.
"""

from typing import Optional
from ...core.config import settings

# Determine which workflow engine to use
USE_TEMPORAL = settings.USE_TEMPORAL if hasattr(settings, 'USE_TEMPORAL') else False

if USE_TEMPORAL:
    try:
        from .temporal import (
            JobProcessingWorkflow,
            BatchJobProcessingWorkflow,
            ScheduledScrapingWorkflow,
            FollowUpWorkflow,
            temporal_client
        )
        
        __all__ = [
            "JobProcessingWorkflow",
            "BatchJobProcessingWorkflow",
            "ScheduledScrapingWorkflow",
            "FollowUpWorkflow",
            "temporal_client"
        ]
    except ImportError:
        # Fall back to Celery
        from .celery import (
            celery_app,
            process_job_task,
            score_job_task,
            generate_resume_task,
            send_email_task
        )
        
        __all__ = [
            "celery_app",
            "process_job_task",
            "score_job_task",
            "generate_resume_task",
            "send_email_task"
        ]
else:
    # Use Celery by default
    from .celery import (
        celery_app,
        process_job_task,
        score_job_task,
        generate_resume_task,
        send_email_task
    )
    
    __all__ = [
        "celery_app",
        "process_job_task",
        "score_job_task",
        "generate_resume_task",
        "send_email_task"
    ]