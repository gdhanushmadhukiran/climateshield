"""Sensor observation historical query endpoint."""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.sensor import SensorObservationModel, SensorNodeModel
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/sensors", tags=["Sensors"])


class ObservationRecord(BaseModel):
    id: str
    sensor_id: str
    observed_at: str
    metric: str
    value: float
    unit: str
    quality: str
    is_simulated: bool


@router.get(
    "/{sensor_id}/observations",
    response_model=List[ObservationRecord],
    summary="Get bounded historical observations for a sensor node",
)
def get_sensor_observations(
    sensor_id: str,
    metric: Optional[str] = Query(None, description="Filter by metric (water_level, rainfall, temperature)"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Record offset"),
    db: Session = Depends(get_db),
):
    sensor = (
        db.query(SensorNodeModel)
        .filter((SensorNodeModel.id == sensor_id) | (SensorNodeModel.code == sensor_id))
        .first()
    )
    if not sensor:
        raise EntityNotFoundException("SensorNode", sensor_id)

    query = db.query(SensorObservationModel).filter(SensorObservationModel.sensor_id == sensor.id)
    if metric:
        query = query.filter(SensorObservationModel.metric == metric)

    observations = (
        query.order_by(SensorObservationModel.observed_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return [
        ObservationRecord(
            id=obs.id,
            sensor_id=obs.sensor_id,
            observed_at=obs.observed_at.isoformat(),
            metric=obs.metric,
            value=obs.value,
            unit=obs.unit,
            quality=obs.quality,
            is_simulated=obs.is_simulated,
        )
        for obs in observations
    ]
