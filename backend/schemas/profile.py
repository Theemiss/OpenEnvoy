"""Profile schemas."""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class ExperienceSchema(BaseModel):
    """Work experience schema."""

    company: str
    title: str
    location: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_current: bool = False
    description: str
    achievements: List[str] = []
    skills_used: List[str] = []


class EducationSchema(BaseModel):
    """Education schema."""

    institution: str
    degree: str
    field: str
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    achievements: List[str] = []


class ProjectSchema(BaseModel):
    """Project schema."""

    name: str
    description: str
    url: Optional[str] = None
    technologies: List[str] = []
    highlights: List[str] = []
    stars: Optional[int] = 0


class ProfileBase(BaseModel):
    """Base profile schema."""

    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    location: Optional[str] = None
    title: str
    summary: str
    skills: List[str] = []
    languages: List[str] = []
    tools: List[str] = []
    domains: List[str] = []


class ProfileCreate(ProfileBase):
    """Create profile schema."""

    pass


class ProfileUpdate(BaseModel):
    """Update profile schema."""

    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    domains: Optional[List[str]] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None




class ProfileResponse(ProfileBase):
    """Profile response schema."""

    id: int
    version: int
    is_active: bool
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    source: str

    class Config:
        from_attributes = True
