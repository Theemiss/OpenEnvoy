"""Job schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class JobBase(BaseModel):
    """Base job schema."""
    
    title: str
    company: str
    description: str
    location: Optional[str] = None
    url: str
    source: str


class JobCreate(JobBase):
    """Create job schema."""
    
    source_id: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = "USD"
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    posted_at: Optional[datetime] = None


class JobUpdate(BaseModel):
    """Update job schema."""
    
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_type: Optional[str] = None
    experience_level: Optional[str] = None
    is_active: Optional[bool] = None
    relevance_score: Optional[float] = None


class JobResponse(JobBase):
    """Job response schema."""
    
    id: int
    source_id: Optional[str]
    salary_min: Optional[int]
    salary_max: Optional[int]
    salary_currency: Optional[str]
    job_type: Optional[str]
    experience_level: Optional[str]
    skills: Optional[List[str]]
    posted_at: Optional[datetime]
    scraped_at: datetime
    is_active: bool
    relevance_score: Optional[float]
    score_reasoning: Optional[str]
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Job list response schema."""
    
    items: List[JobResponse]
    total: int
    skip: int
    limit: int


class JobFilterParams(BaseModel):
    """Job filter parameters."""
    
    search: Optional[str] = None
    job_type: Optional[str] = None
    location: Optional[str] = None
    min_score: Optional[float] = Field(None, ge=0, le=100)
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)