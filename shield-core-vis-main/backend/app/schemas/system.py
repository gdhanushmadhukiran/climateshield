"""System health and liveness schemas."""

from typing import Dict
from pydantic import BaseModel


class LivenessResponse(BaseModel):
    status: str = "ok"


class SystemHealthResponse(BaseModel):
    overallPercent: int
    mode: str
    services: Dict[str, str]
    checkedAt: str
