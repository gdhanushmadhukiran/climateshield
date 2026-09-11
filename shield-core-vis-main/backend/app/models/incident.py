"""Incident model."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class IncidentModel(Base, TimestampMixin):
    __tablename__ = "incidents"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    ref = Column(String(50), unique=True, nullable=False, index=True)  # e.g. INC-2418
    title = Column(String(200), nullable=False)
    hazard_type = Column(String(50), nullable=False)
    zone_id = Column(String(50), ForeignKey("zones.id"), nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="WARNING")  # INFO, ADVISORY, WARNING, EMERGENCY
    status = Column(String(20), nullable=False, default="OPEN")  # OPEN, ACKNOWLEDGED, IN_RESPONSE, RESOLVED
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    reported_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    zone = relationship("RiskZoneModel", back_populates="incidents")
