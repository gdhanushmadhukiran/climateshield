"""Sensor Node and Sensor Observation models."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class SensorNodeModel(Base, TimestampMixin):
    __tablename__ = "sensor_nodes"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    zone_id = Column(String(50), ForeignKey("zones.id"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="HEALTHY")
    battery_pct = Column(Integer, nullable=False, default=100)
    signal_pct = Column(Integer, nullable=False, default=100)
    last_packet_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    zone = relationship("RiskZoneModel", back_populates="sensors")
    observations = relationship("SensorObservationModel", back_populates="sensor", cascade="all, delete-orphan")
    river_node = relationship("RiverNodeModel", back_populates="sensor", uselist=False)


class SensorObservationModel(Base):
    __tablename__ = "sensor_observations"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    sensor_id = Column(String(50), ForeignKey("sensor_nodes.id", ondelete="CASCADE"), nullable=False, index=True)
    observed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    metric = Column(String(50), nullable=False)  # water_level, rainfall, temperature, discharge
    value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)    # m, mm, C, m3/s
    quality = Column(String(20), nullable=False, default="FRESH")
    is_simulated = Column(Boolean, nullable=False, default=False)
    message_id = Column(String(100), nullable=True, index=True)
    received_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    sensor = relationship("SensorNodeModel", back_populates="observations")

    __table_args__ = (
        Index("ix_sensor_obs_sensor_metric_time", "sensor_id", "metric", "observed_at"),
    )


class ProcessedMessageModel(Base):
    """Message deduplication log to prevent duplicate ingestion."""
    __tablename__ = "processed_messages"

    message_id = Column(String(100), primary_key=True)
    node_code = Column(String(50), nullable=False, index=True)
    received_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status = Column(String(20), nullable=False, default="PROCESSED")
