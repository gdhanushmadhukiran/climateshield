"""Alert model."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from app.core.database import Base
from app.models.base import generate_uuid


class AlertModel(Base):
    __tablename__ = "alerts"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    ref = Column(String(50), unique=True, nullable=False, index=True)
    severity = Column(String(20), nullable=False, default="WARNING")
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    channels = Column(String(255), nullable=False, default="SMS,PUSH")  # Comma-separated or JSON string
    delivery_status = Column(String(50), nullable=False, default="DELIVERED")
    acknowledged = Column(Boolean, nullable=False, default=False)
    acknowledged_by = Column(String(100), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    zone_id = Column(String(50), ForeignKey("zones.id"), nullable=True, index=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
