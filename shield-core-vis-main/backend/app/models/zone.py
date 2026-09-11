"""Risk Zone model."""

from sqlalchemy import Column, String, Integer, Float, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class RiskZoneModel(Base, TimestampMixin):
    __tablename__ = "zones"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    population = Column(Integer, nullable=False)
    area_km2 = Column(Float, nullable=False)
    dominant_hazard = Column(String(50), nullable=False)
    centroid_lat = Column(Float, nullable=False)
    centroid_lng = Column(Float, nullable=False)
    polygon_geojson = Column(Text, nullable=False)  # JSON string of [[lng, lat], ...]

    # Relationships
    risk_scores = relationship("RiskScoreModel", back_populates="zone", cascade="all, delete-orphan")
    assets = relationship("AssetModel", back_populates="zone")
    incidents = relationship("IncidentModel", back_populates="zone")
    sensors = relationship("SensorNodeModel", back_populates="zone")
