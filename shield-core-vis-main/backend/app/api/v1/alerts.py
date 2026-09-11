"""Alerts endpoints."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.alert_service import AlertService
from app.schemas.alert import AlertResponse, AlertAcknowledgeRequest

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[AlertResponse], summary="List active climate alerts")
def get_alerts(db: Session = Depends(get_db)):
    service = AlertService(db)
    return service.get_all()


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse, summary="Acknowledge alert as operator")
def acknowledge_alert(
    alert_id: str,
    payload: AlertAcknowledgeRequest,
    db: Session = Depends(get_db),
):
    service = AlertService(db)
    return service.acknowledge(alert_id, payload.operatorId)
