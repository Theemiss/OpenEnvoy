"""API endpoints."""

from .jobs import router as jobs_router
from .applications import router as applications_router
from .profile import router as profile_router
from .emails import router as emails_router
from .review import router as review_router
from .feedback import router as feedback_router
from .ai_costs import router as ai_costs_router
from .auth import router as auth_router
from .ai_configs import router as ai_configs_router
from .scans import router as scans_router

__all__ = [
    "jobs_router",
    "applications_router",
    "profile_router",
    "emails_router",
    "review_router",
    "feedback_router",
    "ai_costs_router",
    "auth_router",
    "ai_configs_router",
    "scans_router",
]