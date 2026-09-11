"""Forecast and Forecast Point models."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import generate_uuid


class ForecastModel(Base):
    __tablename__ = "forecasts"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    zone_id = Column(String(50), ForeignKey("zones.id"), nullable=False, index=True)
    hazard = Column(String(50), nullable=False, default="FLOOD")
    model = Column(String(100), nullable=False, default="HYBRID_PHYSICS_STAT")
    horizon_hours = Column(Integer, nullable=False, default=12)
    issued_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    points = relationship("ForecastPointModel", back_populates="forecast", cascade="all, delete-orphan")


class ForecastPointModel(Base):
    __tablename__ = "forecast_points"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    forecast_id = Column(String(50), ForeignKey("forecasts.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    value = Column(Integer, nullable=False)
    lower = Column(Integer, nullable=False)
    upper = Column(Integer, nullable=False)
    confidence = Column(Integer, nullable=False)

    forecast = relationship("ForecastModel", back_populates="points")
