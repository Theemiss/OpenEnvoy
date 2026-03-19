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


class Email(Base):
    """Email tracking."""

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[Optional[int]] = mapped_column(ForeignKey("application.id"))

    # Email metadata
    message_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    thread_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Direction
    direction: Mapped[str] = mapped_column(String(10))  # outbound, inbound

    # Addresses
    from_email: Mapped[str] = mapped_column(String(255))
    to_email: Mapped[str] = mapped_column(String(255))
    cc: Mapped[Optional[list]] = mapped_column(JSON)
    bcc: Mapped[Optional[list]] = mapped_column(JSON)

    # Content
    subject: Mapped[str] = mapped_column(String(255))
    body_text: Mapped[str] = mapped_column(Text)
    body_html: Mapped[Optional[str]] = mapped_column(Text)

    # Classification (for inbound)
    classification: Mapped[Optional[str]] = mapped_column(
        String(50)
    )  # interview, rejection, info_request, other
    classification_confidence: Mapped[Optional[float]] = mapped_column(Float)

    # Status
    status: Mapped[str] = mapped_column(
        String(50), default="pending", index=True
    )  # pending, sent, delivered, opened, replied, failed
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # For AI-generated
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    model_used: Mapped[Optional[str]] = mapped_column(String(50))
    prompt_used: Mapped[Optional[str]] = mapped_column(Text)

    # Tracking
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    application: Mapped[Optional["Application"]] = relationship(back_populates="emails")

    # Indexes
    __table_args__ = (
        Index("ix_email_application_direction", "application_id", "direction"),
    )


class EmailTemplate(Base):
    """Email templates for follow-ups."""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    subject_template: Mapped[str] = mapped_column(String(255))
    body_template: Mapped[str] = mapped_column(Text)

    trigger_type: Mapped[str] = mapped_column(
        String(50)
    )  # after_application, after_interview, etc.
    trigger_days: Mapped[int] = mapped_column(Integer, default=5)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    usage_count: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[Optional[float]] = mapped_column(Float)  # Response rate

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
