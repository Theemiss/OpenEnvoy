from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Text, DateTime, Integer, Boolean, Float, 
    JSON, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Job(Base):
    """Job posting model."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(50))  # linkedin, adzuna, etc.
    source_id: Mapped[Optional[str]] = mapped_column(String(255))  # External ID
    url: Mapped[str] = mapped_column(String(1024), unique=True, index=True)
    
    # Core job data
    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    company_url: Mapped[Optional[str]] = mapped_column(String(1024))
    company_logo: Mapped[Optional[str]] = mapped_column(String(1024))
    location: Mapped[Optional[str]] = mapped_column(String(255))
    salary_min: Mapped[Optional[int]] = mapped_column(Integer)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer)
    salary_currency: Mapped[Optional[str]] = mapped_column(String(3))
    job_type: Mapped[Optional[str]] = mapped_column(String(50))  # full-time, contract, etc.
    experience_level: Mapped[Optional[str]] = mapped_column(String(50))  # entry, mid, senior
    
    # Content
    description: Mapped[str] = mapped_column(Text)
    description_html: Mapped[Optional[str]] = mapped_column(Text)
    requirements: Mapped[Optional[list]] = mapped_column(JSON)  # Extracted requirements
    benefits: Mapped[Optional[list]] = mapped_column(JSON)
    skills: Mapped[Optional[list]] = mapped_column(JSON)  # Extracted skills
    
    # Metadata
    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Processing state
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    process_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[Optional[str]] = mapped_column(Text)
    
    # AI-related fields
    relevance_score: Mapped[Optional[float]] = mapped_column(Float)
    score_reasoning: Mapped[Optional[str]] = mapped_column(Text)
    score_model: Mapped[Optional[str]] = mapped_column(String(50))
    embedding: Mapped[Optional[list]] = mapped_column(JSON)  # For similarity search
    
    # Relationships
    applications: Mapped[list["Application"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_job_company_title", "company", "title"),
        Index("ix_job_source_posted", "source", "posted_at"),
        Index("ix_job_active_score", "is_active", "relevance_score"),
    )


class JobCache(Base):
    """Cache for job processing results."""
    
    id: Mapped[int] = mapped_column(primary_key=True)
    cache_key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    job_id: Mapped[Optional[int]] = mapped_column(ForeignKey("job.id"))
    cache_type: Mapped[str] = mapped_column(String(50))  # score, cv, email
    input_hash: Mapped[str] = mapped_column(String(64))  # SHA256 of inputs
    output_data: Mapped[dict] = mapped_column(JSON)
    model_used: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    __table_args__ = (
        UniqueConstraint("cache_key", "cache_type", name="uq_cache_key_type"),
    )