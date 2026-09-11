"""Data Source model."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, Float, DateTime
from app.core.database import Base


class DataSourceModel(Base):
    __tablename__ = "data_sources"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    source_type = Column(String(50), nullable=False)  # WEATHER, SATELLITE, GIS, IOT, MODEL, DATABASE
    status = Column(String(20), nullable=False, default="HEALTHY")
    latency_ms = Column(Integer, nullable=False, default=120)
    reliability = Column(Float, nullable=False, default=99.5)
    last_updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
