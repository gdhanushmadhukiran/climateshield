"""Telemetry ingestion HTTP endpoint."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.telemetry import TelemetryPayload, TelemetryIngestResponse
from app.services.telemetry_service import TelemetryService

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


@router.post(
    "/ingest",
    response_model=TelemetryIngestResponse,
    status_code=status.HTTP_200_OK,
    summary="Ingest validated sensor telemetry (HTTP fallback / edge gateway)",
)
def ingest_telemetry(payload: TelemetryPayload, db: Session = Depends(get_db)):
    service = TelemetryService(db)
    return service.process_telemetry(payload)
