"""Application schemas."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ApplicationBase(BaseModel):
    """Base application schema."""

    job_id: int
    resume_id: Optional[int] = None


class ApplicationCreate(ApplicationBase):
    """Create application schema."""

    pass


class ApplicationUpdate(BaseModel):
    """Update application schema."""

    status: Optional[str] = None
    resume_id: Optional[int] = None
    match_score: Optional[float] = None


class ApplicationResponse(ApplicationBase):
    """Application response schema."""

    id: int
    status: str
    applied_at: Optional[datetime] = None
    application_method: Optional[str] = None
    relevance_score: Optional[float] = None
    match_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    last_activity_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplicationStats(BaseModel):
    """Application statistics schema."""

    period_days: int = 30
    total_applications: int = 0
    by_status: dict = {}
    response_rate: float = 0.0
    interview_rate: float = 0.0
    avg_response_time_hours: Optional[float] = None
