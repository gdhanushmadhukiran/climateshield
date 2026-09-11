"""Incident service."""

from typing import List
from sqlalchemy.orm import Session
from app.repositories.incident_repo import IncidentRepository
from app.schemas.incident import IncidentResponse
from app.schemas.common import Coordinates
from app.core.exceptions import EntityNotFoundException, InvalidStateTransitionException


class IncidentService:
    def __init__(self, db: Session):
        self.repo = IncidentRepository(db)

    def get_all(self) -> List[IncidentResponse]:
        incidents = self.repo.get_all()
        return [
            IncidentResponse(
                id=inc.id,
                ref=inc.ref,
                title=inc.title,
                hazard=inc.hazard_type,
                zoneId=inc.zone_id,
                severity=inc.severity,
                status=inc.status,
                reportedAt=inc.reported_at.isoformat(),
                coordinates=Coordinates(lat=inc.latitude, lng=inc.longitude),
            )
            for inc in incidents
        ]

    def update_status(self, incident_id: str, new_status: str) -> IncidentResponse:
        inc = self.repo.get_by_id(incident_id)
        if not inc:
            raise EntityNotFoundException("Incident", incident_id)

        current = inc.status.upper()
        target = new_status.upper()

        if current == "RESOLVED" and target == "OPEN":
            raise InvalidStateTransitionException(current, target)

        updated = self.repo.update_status(inc, target)
        return IncidentResponse(
            id=updated.id,
            ref=updated.ref,
            title=updated.title,
            hazard=updated.hazard_type,
            zoneId=updated.zone_id,
            severity=updated.severity,
            status=updated.status,
            reportedAt=updated.reported_at.isoformat(),
            coordinates=Coordinates(lat=updated.latitude, lng=updated.longitude),
        )
