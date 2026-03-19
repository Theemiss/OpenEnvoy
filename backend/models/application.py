from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    Text,
    DateTime,
    Integer,
    Boolean,
    Float,
    JSON,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Application(Base):
    """Job application tracking."""

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job.id"))
    resume_id: Mapped[Optional[int]] = mapped_column(ForeignKey("resume.id"))

    # Application details
    status: Mapped[str] = mapped_column(
        String(50), default="draft", index=True
    )  # draft, applied, interviewing, rejected, offered, accepted, withdrawn

    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    application_method: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # email, portal, linkedin

    # AI scores
    relevance_score: Mapped[Optional[float]] = mapped_column(Float)
    match_score: Mapped[Optional[float]] = mapped_column(Float)  # More detailed match

    # Timeline
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Relationships
    job: Mapped["Job"] = relationship(back_populates="applications")
    resume: Mapped[Optional["Resume"]] = relationship()
    emails: Mapped[list["Email"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    timeline: Mapped[list["ApplicationTimeline"]] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (Index("ix_application_status_updated", "status", "updated_at"),)


class ApplicationTimeline(Base):
    """Timeline events for an application."""

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("application.id"))

    event_type: Mapped[str] = mapped_column(
        String(50)
    )  # applied, response, interview, etc.
    event_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    description: Mapped[Optional[str]] = mapped_column(Text)

    # For AI-related events
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    model_used: Mapped[Optional[str]] = mapped_column(String(50))
    prompt_used: Mapped[Optional[str]] = mapped_column(Text)

    # Structured data (renamed from 'metadata' to avoid SQLAlchemy reserved name conflict)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    application: Mapped["Application"] = relationship(back_populates="timeline")
