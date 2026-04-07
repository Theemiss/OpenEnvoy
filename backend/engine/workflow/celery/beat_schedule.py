"""
Celery Beat schedule configuration for OpenEnvoy backend.

This module defines the beat_schedule dictionary and the CELERY_BEAT_SCHEDULE
constant used by the Celery beat scheduler to periodically trigger background
tasks for job scraping, follow-up checks, and email reply checks.

Notes:
- Imports follow the project's existing Celery pattern (celery.shared_task usage
  in backend/engine/workflow/celery/tasks.py and config-driven time intervals
  from backend.core.config).
- Timezone-aware schedules rely on CELERY_TIMEZONE from the config (default to
  UTC if not available).
- The scrape interval aligns with SCRAPE_INTERVAL_HOURS from config (4 hours by
  default) to schedule scrape_jobs_task.
"""
from __future__ import annotations

from typing import Dict, Any

from celery.schedules import crontab

# Import timing/config defaults from the project's settings.
# If the configuration cannot be imported (e.g., during static analysis),
# fall back to sensible defaults.
try:
    from backend.core.config import SCRAPE_INTERVAL_HOURS, CELERY_TIMEZONE  # type: ignore
except Exception:  # pragma: no cover
    SCRAPE_INTERVAL_HOURS = 4
    CELERY_TIMEZONE = "UTC"

# The beat_schedule maps Celery beat entries to their corresponding task
# descriptors. Each entry includes:
# - task: Python import path to the Celery task function
# - schedule: crontab schedule (timezone-aware)
# - args: optional positional arguments (unused in this configuration)
# - kwargs: optional keyword arguments (unused in this configuration)
beat_schedule: Dict[str, Dict[str, Any]] = {
    # Slice: scrape jobs on a regular interval. Uses SCRAPE_INTERVAL_HOURS to
    # determine the cadence (e.g., 4 hours).
    "scrape_jobs_task": {
        "task": "backend.engine.workflow.celery.tasks.scrape_jobs_task",
        "schedule": crontab(minute=0, hour=f"*/{SCRAPE_INTERVAL_HOURS}", timezone=CELERY_TIMEZONE),
        # No additional args
        "args": (),
        "kwargs": {},
    },
    # Slice: check for newly follow-ups every 6 hours.
    "check_followups_task": {
        "task": "backend.engine.workflow.celery.tasks.check_followups_task",
        "schedule": crontab(minute=0, hour="*/6", timezone=CELERY_TIMEZONE),
        "args": (),
        "kwargs": {},
    },
    # Slice: monitor and process email replies every 15 minutes.
    "check_email_replies_task": {
        "task": "backend.engine.workflow.celery.tasks.check_email_replies_task",
        "schedule": crontab(minute="*/15", hour="*", timezone=CELERY_TIMEZONE),
        "args": (),
        "kwargs": {},
    },
}

# Backwards-compatible alias used by Celery when loading configuration.
CELERY_BEAT_SCHEDULE: Dict[str, Dict[str, Any]] = beat_schedule

__all__ = ["beat_schedule", "CELERY_BEAT_SCHEDULE"]
