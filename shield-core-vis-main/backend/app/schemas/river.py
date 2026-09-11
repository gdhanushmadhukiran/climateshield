"""River sensor node schemas."""

from typing import Optional
from pydantic import BaseModel, ConfigDict


class RiverNodeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str = "RN-01"
    name: str
    segment: str  # UPSTREAM, MIDSTREAM, DOWNSTREAM
    waterLevelM: float
    thresholdM: float
    rateOfRiseMPerHour: float = 0.0
    timeToThresholdMinutes: Optional[float] = None
    travelTimeMinutes: int
    status: str
    dataQuality: str = "FRESH"
    batteryPercent: int
    signalPercent: int
    lastPacketAt: str
    downstreamNodeId: Optional[str] = None
