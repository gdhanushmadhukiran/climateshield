"""Incidents endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.incident_service import IncidentService
from app.schemas.incident import IncidentResponse, IncidentStatusUpdateRequest

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("", response_model=List[IncidentResponse], summary="List active incidents")
def get_incidents(db: Session = Depends(get_db)):
    service = IncidentService(db)
    return service.get_all()


@router.post("/{incident_id}/status", response_model=IncidentResponse, summary="Update incident response status")
def update_incident_status(
    incident_id: str,
    payload: IncidentStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    service = IncidentService(db)
    return service.update_status(incident_id, payload.status)
