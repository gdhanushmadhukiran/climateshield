"""Cascade Network Graph models."""

from sqlalchemy import Column, String, Integer, Float
from app.core.database import Base
from app.models.base import generate_uuid


class CascadeNodeModel(Base):
    __tablename__ = "cascade_nodes"

    id = Column(String(50), primary_key=True)
    label = Column(String(100), nullable=False)
    kind = Column(String(50), nullable=False)  # HAZARD, SYSTEM, ASSET, SERVICE, POPULATION
    risk = Column(String(20), nullable=False, default="MODERATE")  # LOW, MODERATE, HIGH, CRITICAL


class CascadeEdgeModel(Base):
    __tablename__ = "cascade_edges"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    from_node_id = Column(String(50), nullable=False, index=True)
    to_node_id = Column(String(50), nullable=False, index=True)
    likelihood = Column(Float, nullable=False)  # 0 - 100
    lag_minutes = Column(Integer, nullable=False, default=0)
