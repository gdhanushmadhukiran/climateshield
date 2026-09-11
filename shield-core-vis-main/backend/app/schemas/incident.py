"""Incident schemas."""

from pydantic import BaseModel, ConfigDict, field_validator
from app.schemas.common import Coordinates


VALID_INCIDENT_STATUSES = {"OPEN", "ACKNOWLEDGED", "IN_RESPONSE", "RESOLVED"}


class IncidentStatusUpdateRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        upper = v.upper()
        if upper not in VALID_INCIDENT_STATUSES:
            raise ValueError(f"Status must be one of {VALID_INCIDENT_STATUSES}")
        return upper


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ref: str
    title: str
    hazard: str
    zoneId: str
    severity: str
    status: str
    reportedAt: str
    coordinates: Coordinates
