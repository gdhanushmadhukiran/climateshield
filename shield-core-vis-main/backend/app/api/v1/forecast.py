"""Forecast trajectory endpoint."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.repositories.forecast_repo import ForecastRepository
from app.schemas.forecast import ForecastResponse, ForecastPointResponse
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.get("/trajectory", response_model=ForecastResponse, summary="Get predicted risk trajectory points")
def get_forecast_trajectory(
    zoneId: str = Query("zone-a", description="Risk zone ID"),
    horizon: int = Query(12, description="Forecast horizon in hours"),
    db: Session = Depends(get_db),
):
    repo = ForecastRepository(db)
    fc = repo.get_forecast(zoneId, horizon)
    if not fc:
        raise EntityNotFoundException("Forecast", zoneId)

    points = [
        ForecastPointResponse(
            timestamp=p.timestamp.isoformat(),
            value=p.value,
            lower=p.lower,
            upper=p.upper,
            confidence=p.confidence,
        )
        for p in fc.points
    ]

    return ForecastResponse(
        id=fc.id,
        zoneId=fc.zone_id,
        hazard=fc.hazard,
        horizonHours=fc.horizon_hours,
        issuedAt=fc.issued_at.isoformat(),
        model=fc.model,
        points=points,
    )
