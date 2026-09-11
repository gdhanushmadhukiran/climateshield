"""Risk endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.risk_service import RiskService
from app.schemas.risk import (
    RiskScoreResponse,
    RiskZoneResponse,
    RiskExplanationResponse,
    HazardMatrixResponse,
    RecalculateRiskResponse,
)
from app.engine.coordinator import RiskIntelligenceCoordinator
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/risk", tags=["Risk"])


@router.get("/current", response_model=RiskScoreResponse, summary="Get current aggregate city risk score")
def get_current_risk(db: Session = Depends(get_db)):
    service = RiskService(db)
    return service.get_city_risk()


@router.get("/zones", response_model=List[RiskZoneResponse], summary="List all risk zones with GeoJSON polygons")
def get_risk_zones(
    hazard: Optional[str] = Query(None, description="Filter by dominant hazard"),
    db: Session = Depends(get_db),
):
    service = RiskService(db)
    return service.get_zones(hazard)


@router.post("/recalculate", response_model=RecalculateRiskResponse, summary="Trigger deterministic multi-hazard risk engine recalculation")
def recalculate_risk(db: Session = Depends(get_db)):
    coordinator = RiskIntelligenceCoordinator(db)
    return coordinator.recalculate_all_zones()


@router.get("/matrix", response_model=HazardMatrixResponse, summary="Get multi-hazard interaction matrix")
def get_hazard_matrix(db: Session = Depends(get_db)):
    coordinator = RiskIntelligenceCoordinator(db)
    return coordinator.get_hazard_matrix()


@router.get("/explain/{zone_id}", response_model=RiskExplanationResponse, summary="Get 10-point explainability report for a risk zone")
def explain_risk_zone(zone_id: str, db: Session = Depends(get_db)):
    coordinator = RiskIntelligenceCoordinator(db)
    result = coordinator.explain_zone(zone_id)
    if not result:
        raise EntityNotFoundException("RiskZone", zone_id)
    return result


@router.get("/zones/{zone_id}", response_model=RiskZoneResponse, summary="Get specific risk zone by ID")
def get_risk_zone(zone_id: str, db: Session = Depends(get_db)):
    service = RiskService(db)
    return service.get_zone_by_id(zone_id)

