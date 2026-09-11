"""Cascade network graph schemas."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CascadeNodeResponse(BaseModel):
    id: str
    label: str
    kind: str
    risk: str


class CascadeEdgeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: Optional[str] = None
    from_: str = Field(..., alias="from")
    to: str
    likelihood: float
    lagMinutes: int


class CascadeGraphResponse(BaseModel):
    nodes: List[CascadeNodeResponse]
    edges: List[CascadeEdgeResponse]
