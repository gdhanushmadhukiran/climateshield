"""Forecast schemas."""

from typing import List
from pydantic import BaseModel, ConfigDict


class ForecastPointResponse(BaseModel):
    timestamp: str
    value: int
    lower: int
    upper: int
    confidence: int


class ForecastResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    zoneId: str
    hazard: str
    horizonHours: int
    issuedAt: str
    model: str
    points: List[ForecastPointResponse]
