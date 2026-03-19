"""Pydantic schemas for API."""

from .job import JobResponse, JobListResponse, JobFilterParams
from .profile import ProfileResponse, ProfileUpdate, ExperienceSchema
from .resume import ResumeResponse, ResumeCreate
from .email import EmailResponse, EmailCreate
from .application import ApplicationResponse, ApplicationCreate, ApplicationUpdate, ApplicationStats

__all__ = [
    "JobResponse",
    "JobListResponse",
    "JobFilterParams",
    "ProfileResponse",
    "ProfileUpdate",
    "ExperienceSchema",
    "ResumeResponse",
    "ResumeCreate",
    "EmailResponse",
    "EmailCreate",
    "ApplicationResponse",
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationStats",
]
