"""API v1 package."""

from fastapi import APIRouter

from .endpoints import (
    jobs_router,
    applications_router,
    profile_router,
    emails_router,
    review_router,
    feedback_router,
    ai_costs_router,
    auth_router,
    ai_configs_router,
    scans_router,
    ai_tasks_router,
    webhooks_router,
)

# Analytics router registration
from .endpoints.analytics import analytics_router
api_router = APIRouter()

api_router.include_router(jobs_router)
api_router.include_router(applications_router)
api_router.include_router(profile_router)
api_router.include_router(ai_configs_router)
api_router.include_router(scans_router)
api_router.include_router(emails_router)
api_router.include_router(review_router)
api_router.include_router(feedback_router)
api_router.include_router(ai_costs_router)
api_router.include_router(auth_router)
api_router.include_router(ai_tasks_router)
api_router.include_router(webhooks_router)
api_router.include_router(analytics_router, prefix="/analytics")

__all__ = ["api_router"]
