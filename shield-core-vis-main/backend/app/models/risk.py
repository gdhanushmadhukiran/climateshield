"""Risk Score and Risk Driver models."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import generate_uuid


class RiskScoreModel(Base):
    __tablename__ = "risk_scores"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    zone_id = Column(String(50), ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True)
    value = Column(Integer, nullable=False)
    level = Column(String(20), nullable=False, default="HIGH")
    confidence = Column(Integer, nullable=False, default=90)
    velocity_per_hour = Column(Float, nullable=False, default=0.0)
    data_quality = Column(String(20), nullable=False, default="FRESH")
    observed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    zone = relationship("RiskZoneModel", back_populates="risk_scores")
    drivers = relationship("RiskDriverModel", back_populates="risk_score", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_risk_scores_zone_observed", "zone_id", "observed_at"),
    )


class RiskDriverModel(Base):
    __tablename__ = "risk_drivers"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    risk_score_id = Column(String(50), ForeignKey("risk_scores.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    contribution = Column(Float, nullable=False)
    trend = Column(String(20), nullable=False, default="STABLE")
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    risk_score = relationship("RiskScoreModel", back_populates="drivers")
