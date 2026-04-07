from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List


class OverviewResponse(BaseModel):
    total_applications: int = Field(0, description="Total number of applications tracked in the system.")
    response_rate: float = Field(0.0, description="Overall response rate (0.0 - 1.0).")
    interview_rate: float = Field(0.0, description="Overall interview rate (0.0 - 1.0).")


class ResponseRateItem(BaseModel):
    period: str = Field(..., description="Time period label (e.g. ISO week or date).")
    rate: float = Field(..., description="Response rate for the given period.")


class SourceBreakdownItem(BaseModel):
    source: str = Field(..., description="Source of the application (e.g. LinkedIn, Website).")
    count: int = Field(..., description="Number of applications from this source.")


class TrendDataItem(BaseModel):
    period: str = Field(..., description="Time period for the trend (e.g. week label).")
    applications: int = Field(..., description="Number of applications in the period.")
    response_rate: float = Field(..., description="Response rate for the period.")


class TimelineItem(BaseModel):
    timestamp: str = Field(..., description="ISO timestamp of the event.")
    event: str = Field(..., description="Descriptive event text for the timeline.")
