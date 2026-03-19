"""AI model configuration per profile."""
from datetime import datetime
from typing import Optional
from enum import Enum

from sqlalchemy import String, Integer, Boolean, Float, ForeignKey, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from ..core.database import Base


class AIModelTier(str, Enum):
    """AI model tier/category."""

    CHEAP = "cheap"  # gpt-4o-mini, claude-haiku - fast/cheap tasks
    PREMIUM = "premium"  # gpt-4o, claude-sonnet - complex tasks
    FREE = "free"  # Ollama, OpenRouter free models


class AIModelProvider(str, Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"


class AIModelConfig(Base):
    """AI model configuration per profile."""

    __tablename__ = "ai_model_config"

    id: Mapped[int] = mapped_column(primary_key=True)
    profile_id: Mapped[int] = mapped_column(
        ForeignKey("profile.id", ondelete="CASCADE"), index=True
    )

    # Identity
    name: Mapped[str] = mapped_column(String(100))  # e.g. "My GPT-4 Setup"
    provider: Mapped[str] = mapped_column(String(50))  # openai, anthropic, etc.
    model_name: Mapped[str] = mapped_column(String(100))  # gpt-4o-mini, etc.

    # Tier for task routing
    tier: Mapped[str] = mapped_column(
        String(20), default=AIModelTier.CHEAP.value, index=True
    )

    # Optional settings
    temperature: Mapped[Optional[float]] = mapped_column(Float, default=0.7)
    max_tokens: Mapped[Optional[int]] = mapped_column(Integer, default=1000)

    # Override API key (optional - if user wants to use their own)
    api_key_override: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # State
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("ix_aimodelconfig_profile_tier", "profile_id", "tier"),
        Index("ix_aimodelconfig_profile_default", "profile_id", "is_default"),
    )
