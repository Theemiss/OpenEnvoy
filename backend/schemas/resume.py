"""Resume schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ResumeBase(BaseModel):
    """Base resume schema."""
    
    version: str
    name: str
    is_canonical: bool = False
    file_type: str
    content_json: Dict[str, Any]


class ResumeCreate(ResumeBase):
    """Create resume schema."""
    
    profile_id: int
    job_id: Optional[int] = None


class ResumeResponse(ResumeBase):
    """Resume response schema."""
    
    id: int
    profile_id: int
    job_id: Optional[int]
    file_path: str
    file_size: int
    model_used: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ResumeAdaptationRequest(BaseModel):
    """Request for resume adaptation."""
    
    job_id: int
    profile_id: int


class ResumeAdaptationResponse(BaseModel):
    """Response from resume adaptation."""
    
    adapted_resume: Dict[str, Any]
    changes_made: str
    targeted_skills: List[str]
    confidence: int
    generated_at: str
    resume_id: Optional[int]