"""Asset response schemas."""

from pydantic import BaseModel, ConfigDict
from app.schemas.common import Coordinates


class AssetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    zoneId: str
    criticality: str
    coordinates: Coordinates
    status: str
