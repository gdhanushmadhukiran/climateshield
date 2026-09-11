"""ClimateShield Schemas Package."""

from app.schemas.common import Coordinates, GeoJSONPolygon, APIErrorResponse
from app.schemas.city import CityResponse
from app.schemas.risk import RiskScoreResponse, RiskZoneResponse, RiskDriverResponse
from app.schemas.asset import AssetResponse
from app.schemas.incident import IncidentResponse, IncidentStatusUpdateRequest
from app.schemas.alert import AlertResponse, AlertAcknowledgeRequest
from app.schemas.river import RiverNodeResponse
from app.schemas.forecast import ForecastResponse, ForecastPointResponse
from app.schemas.cascade import CascadeGraphResponse, CascadeNodeResponse, CascadeEdgeResponse
from app.schemas.data_source import DataSourceResponse
from app.schemas.system import SystemHealthResponse, LivenessResponse
from app.schemas.optimization import RecommendationResponse

__all__ = [
    "Coordinates",
    "GeoJSONPolygon",
    "APIErrorResponse",
    "CityResponse",
    "RiskScoreResponse",
    "RiskZoneResponse",
    "RiskDriverResponse",
    "AssetResponse",
    "IncidentResponse",
    "IncidentStatusUpdateRequest",
    "AlertResponse",
    "AlertAcknowledgeRequest",
    "RiverNodeResponse",
    "ForecastResponse",
    "ForecastPointResponse",
    "CascadeGraphResponse",
    "CascadeNodeResponse",
    "CascadeEdgeResponse",
    "DataSourceResponse",
    "SystemHealthResponse",
    "LivenessResponse",
    "RecommendationResponse",
]
