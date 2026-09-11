"""Action Recommendation and Operational Plan models."""

from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.base import TimestampMixin, generate_uuid


class ActionRecommendationModel(Base, TimestampMixin):
    __tablename__ = "action_recommendations"

    id = Column(String(50), primary_key=True, default=generate_uuid)
    action = Column(String(250), nullable=False)
    rationale = Column(Text, nullable=False)
    zone_id = Column(String(50), ForeignKey("zones.id"), nullable=False, index=True)
    asset_id = Column(String(50), ForeignKey("assets.id"), nullable=True)
    priority = Column(String(10), nullable=False, default="P1")  # P1, P2, P3
    expected_risk_reduction = Column(Integer, nullable=False, default=15)
    confidence = Column(Integer, nullable=False, default=85)
    cost = Column(String(50), nullable=False, default="~$5,000")
    eta_minutes = Column(Integer, nullable=False, default=30)
    status = Column(String(30), nullable=False, default="PENDING")  # PENDING, APPROVED, DISPATCHED, COMPLETED, REJECTED
    cascade_edge_mitigated = Column(String(100), nullable=True)
    resources_required = Column(Text, nullable=True)  # JSON string of resource descriptions/IDs
    assigned_resource_id = Column(String(50), ForeignKey("response_resources.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String(100), nullable=True)
    dispatched_incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=True)

    # Relationships
    zone = relationship("RiskZoneModel")
    asset = relationship("AssetModel")
    assigned_resource = relationship("ResourceModel")
    dispatched_incident = relationship("IncidentModel")
