"""Incident repository."""

from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.incident import IncidentModel


class IncidentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[IncidentModel]:
        return self.db.query(IncidentModel).order_by(IncidentModel.reported_at.desc()).all()

    def get_by_id(self, incident_id: str) -> Optional[IncidentModel]:
        return (
            self.db.query(IncidentModel)
            .filter((IncidentModel.id == incident_id) | (IncidentModel.ref == incident_id))
            .first()
        )

    def update_status(self, incident: IncidentModel, new_status: str) -> IncidentModel:
        incident.status = new_status
        self.db.commit()
        self.db.refresh(incident)
        return incident
