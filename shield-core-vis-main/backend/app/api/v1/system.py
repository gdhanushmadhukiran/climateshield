"""System health and liveness endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.health_service import HealthService
from app.schemas.system import SystemHealthResponse, LivenessResponse

router = APIRouter(tags=["System"])


@router.get("/health", response_model=LivenessResponse, summary="Root liveness check without DB requirement")
def liveness():
    return LivenessResponse(status="ok")


@router.get("/system/health", response_model=SystemHealthResponse, summary="Deep subsystem health check verifying DB connectivity")
def system_health(db: Session = Depends(get_db)):
    service = HealthService(db)
    return service.check_health()
