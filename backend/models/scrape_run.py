"""Scrape run model for tracking job scan status."""

from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Integer, Text, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..core.database import Base


class ScrapeRunStatus(str, Enum):
    """Scrape run status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScrapeRun(Base):
    """Track job scrape scan runs."""

    id: Mapped[int] = mapped_column(primary_key=True)

    # Status tracking
    status: Mapped[str] = mapped_column(
        String(20), default=ScrapeRunStatus.PENDING.value, index=True
    )

    # Results per source
    results: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    # e.g. {"linkedin": 12, "adzuna": 45, "remotive": 8}

    # Aggregate stats
    total_jobs_found: Mapped[int] = mapped_column(Integer, default=0)
    total_jobs_saved: Mapped[int] = mapped_column(Integer, default=0)

    # Timing
    started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Trigger info
    trigger_type: Mapped[str] = mapped_column(
        String(20),
        default="manual",  # "manual" or "scheduled"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (Index("ix_scraperun_status_created", "status", "created_at"),)
