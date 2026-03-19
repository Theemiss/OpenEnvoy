"""AI model configuration schemas."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AIModelConfigBase(BaseModel):
    """Base AI model config schema."""

    name: str
    provider: str
    model_name: str
    tier: str = "cheap"


class AIModelConfigCreate(AIModelConfigBase):
    """Create AI model config."""

    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    is_default: bool = False


class AIModelConfigUpdate(BaseModel):
    """Update AI model config."""

    name: Optional[str] = None
    provider: Optional[str] = None
    model_name: Optional[str] = None
    tier: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None


class AIModelConfigResponse(AIModelConfigBase):
    """AI model config response."""

    id: int
    temperature: Optional[float]
    max_tokens: Optional[int]
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AIModelConfigListResponse(BaseModel):
    """List of AI model configs."""

    items: List[AIModelConfigResponse]
    total: int
