"""Email schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EmailBase(BaseModel):
    """Base email schema."""
    
    to_email: str
    subject: str
    body_text: str
    body_html: Optional[str] = None


class EmailCreate(EmailBase):
    """Create email schema."""
    
    application_id: Optional[int] = None
    from_email: str = "me"
    cc: Optional[List[str]] = None
    bcc: Optional[List[str]] = None


class EmailResponse(EmailBase):
    """Email response schema."""
    
    id: int
    application_id: Optional[int]
    message_id: Optional[str]
    thread_id: Optional[str]
    direction: str
    from_email: str
    cc: Optional[List[str]]
    bcc: Optional[List[str]]
    classification: Optional[str]
    classification_confidence: Optional[float]
    status: str
    sent_at: Optional[datetime]
    opened_at: Optional[datetime]
    ai_generated: bool
    model_used: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailDraftRequest(BaseModel):
    """Request to draft an email."""
    
    job_id: int
    profile_id: int
    email_type: str = Field(..., pattern="^(initial|follow_up|cover|thank_you)$")
    additional_context: Optional[dict] = None


class EmailDraftResponse(BaseModel):
    """Response from email drafting."""
    
    subject: str
    body: str
    generated_at: str
    model_used: str


class EmailSendRequest(BaseModel):
    """Request to send an email."""
    
    to_email: str
    subject: str
    body: str
    html_body: Optional[str] = None
    application_id: Optional[int] = None
    schedule_at: Optional[datetime] = None  # For future scheduling