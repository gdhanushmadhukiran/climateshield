"""Data source schemas."""

from pydantic import BaseModel, ConfigDict, Field


class DataSourceResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)

    id: str
    name: str
    type: str = Field(..., alias="sourceType")
    status: str
    latencyMs: int
    reliability: float
    lastUpdatedAt: str
