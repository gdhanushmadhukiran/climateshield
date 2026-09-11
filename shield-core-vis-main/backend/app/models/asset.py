"""Critical Asset model."""

from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class AssetModel(Base, TimestampMixin):
    __tablename__ = "assets"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    name = Column(String(150), nullable=False)
    asset_type = Column(String(50), nullable=False)  # HOSPITAL, EMERGENCY, BRIDGE, WATER, POWER, etc.
    criticality = Column(String(20), nullable=False, default="TIER_1")  # TIER_1, TIER_2, TIER_3
    zone_id = Column(String(50), ForeignKey("zones.id"), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default="OPERATIONAL")

    zone = relationship("RiskZoneModel", back_populates="assets")
