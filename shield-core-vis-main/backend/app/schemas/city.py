"""City response schemas."""

from pydantic import BaseModel, ConfigDict
from app.schemas.common import Coordinates


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    state: str = "Andhra Pradesh"
    country: str = "India"
    timezone: str = "Asia/Kolkata"
    coordinates: Coordinates
    population: int = 2400000
    areaKm2: float = 540.0
    criticalAssetsCount: int = 42
    riskScore: int = 74
