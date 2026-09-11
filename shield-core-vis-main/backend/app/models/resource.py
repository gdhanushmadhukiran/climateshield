"""Response Resource model for emergency logistics."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, ForeignKey
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class ResourceModel(Base, TimestampMixin):
    __tablename__ = "response_resources"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)  # PUMP, RESCUE, BARRIER, POWER, MEDICAL, CREW
    status = Column(String(30), nullable=False, default="AVAILABLE")  # AVAILABLE, DEPLOYED, IN_TRANSIT, MAINTENANCE
    depot_name = Column(String(150), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    hourly_cost = Column(Float, nullable=False, default=150.0)
    mobilization_minutes = Column(Integer, nullable=False, default=15)
    assigned_zone_id = Column(String(50), ForeignKey("zones.id"), nullable=True)
    assigned_incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=True)
