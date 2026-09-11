"""Alert schemas."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class AlertAcknowledgeRequest(BaseModel):
    operatorId: str = "demo-operator"


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ref: str
    severity: str
    title: str
    message: str
    channels: List[str]
    deliveryStatus: str
    acknowledged: bool
    acknowledgedBy: Optional[str] = None
    acknowledgedAt: Optional[str] = None
    zoneId: Optional[str] = None
    createdAt: str
