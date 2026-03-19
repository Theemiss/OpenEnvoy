"""Job scan schemas."""

from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime


class ScanRunCreate(BaseModel):
    """Trigger a new scan."""

    trigger_type: str = "manual"


class ScanRunResponse(BaseModel):
    """Response after triggering a scan."""

    id: int
    status: str
    trigger_type: str
    created_at: datetime

    class Config:
        from_attributes = True


class ScanRunDetailResponse(BaseModel):
    """Full scan run details."""

    id: int
    status: str
    trigger_type: str
    results: Dict[str, int]
    total_jobs_found: int
    total_jobs_saved: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ScanStatusResponse(BaseModel):
    """Current scan status (for polling)."""

    is_running: bool
    last_run_id: Optional[int]
    last_run_at: Optional[datetime]
    last_run_status: Optional[str]
    next_run_in_seconds: Optional[int]
    recent_results: Optional[Dict[str, int]]
