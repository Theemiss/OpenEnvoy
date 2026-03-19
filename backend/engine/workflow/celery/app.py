"""Celery application configuration."""

from celery import Celery
from kombu import Queue, Exchange

from ....core.config import settings

# Create Celery app
celery_app = Celery(
    "job_automation",
    broker=str(settings.REDIS_URL),
    backend=str(settings.REDIS_URL)
)

# Configure queues
celery_app.conf.task_queues = [
    Queue(
        'job_processing',
        Exchange('job_processing'),
        routing_key='job.#'
    ),
    Queue(
        'scoring',
        Exchange('scoring'),
        routing_key='score.#'
    ),
    Queue(
        'email',
        Exchange('email'),
        routing_key='email.#'
    )
]

# Task routing
celery_app.conf.task_routes = {
    'process_job_task': {'queue': 'job_processing'},
    'score_job_task': {'queue': 'scoring'},
    'generate_resume_task': {'queue': 'job_processing'},
    'send_email_task': {'queue': 'email'},
}

# Task settings
celery_app.conf.task_serializer = 'json'
celery_app.conf.result_serializer = 'json'
celery_app.conf.accept_content = ['json']
celery_app.conf.task_track_started = True
celery_app.conf.task_time_limit = 300  # 5 minutes
celery_app.conf.task_soft_time_limit = 240  # 4 minutes

# Beat schedule (periodic tasks)
celery_app.conf.beat_schedule = {
    'scrape-jobs': {
        'task': 'scrape_jobs_task',
        'schedule': 3600.0 * settings.SCRAPE_INTERVAL_HOURS,
    },
    'check-followups': {
        'task': 'check_followups_task',
        'schedule': 3600.0 * 6,  # Every 6 hours
    },
    'check-email-replies': {
        'task': 'check_email_replies_task',
        'schedule': 900.0,  # Every 15 minutes
    },
}

# Load task modules
celery_app.autodiscover_tasks(['backend.engine.workflow.celery.tasks'])