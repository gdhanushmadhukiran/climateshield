"""Common Pydantic models and GeoJSON types."""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class Coordinates(BaseModel):
    lat: float
    lng: float


class GeoJSONPolygon(BaseModel):
    type: str = "Polygon"
    coordinates: List[List[List[float]]] = Field(
        ...,
        description="Nested polygon coordinates array: [[[lng, lat], ...]]"
    )


class APIErrorDetail(BaseModel):
    code: str
    message: str
    request_id: str
    details: Optional[Dict[str, Any]] = None


class APIErrorResponse(BaseModel):
    error: APIErrorDetail
