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
)

api_router = APIRouter()

api_router.include_router(jobs_router)
api_router.include_router(applications_router)
api_router.include_router(profile_router)
api_router.include_router(emails_router)
api_router.include_router(review_router)
api_router.include_router(feedback_router)
api_router.include_router(ai_costs_router)

__all__ = ["api_router"]
