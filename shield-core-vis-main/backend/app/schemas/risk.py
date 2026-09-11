"""Risk score and zone schemas."""

from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.common import Coordinates, GeoJSONPolygon


class RiskDriverResponse(BaseModel):
    id: str
    label: str
    contribution: float
    value: str
    metricValue: Optional[float] = None
    unit: Optional[str] = None
    trend: str = "STABLE"


class RiskScoreResponse(BaseModel):
    city: Optional[str] = "Visakhapatnam"
    value: int
    level: str
    confidence: int
    velocityPerHour: float
    observedAt: str
    quality: str


class RiskZoneResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    code: str
    population: int
    areaKm2: float
    dominantHazard: str
    risk: RiskScoreResponse
    drivers: List[RiskDriverResponse]
    centroid: Coordinates
    polygon: Union[List[List[float]], GeoJSONPolygon]


class RiskExplanationResponse(BaseModel):
    zone_id: str
    engine_version: str
    generated_at: str
    answers: Dict[str, Any]


class HazardMatrixItem(BaseModel):
    zone_id: str
    zone_code: str
    zone_name: str
    dominant_hazard: str
    composite_risk: int
    hazards: Dict[str, float]
    compounding_active: bool


class HazardMatrixResponse(BaseModel):
    engine_version: str
    evaluated_at: str
    matrix: List[HazardMatrixItem]


class RecalculateRiskResponse(BaseModel):
    engine_version: str
    timestamp: str
    zones_evaluated: int
    zone_results: Dict[str, Any]
    cascade_summary: Dict[str, Any]

