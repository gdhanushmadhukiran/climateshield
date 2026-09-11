"""River Node topology model."""

from sqlalchemy import Column, String, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class RiverNodeModel(Base):
    __tablename__ = "river_nodes"

    sensor_id = Column(String(50), ForeignKey("sensor_nodes.id", ondelete="CASCADE"), primary_key=True)
    segment = Column(String(20), nullable=False)  # UPSTREAM, MIDSTREAM, DOWNSTREAM
    threshold_m = Column(Float, nullable=False)
    travel_time_min = Column(Integer, nullable=False, default=0)
    downstream_node_id = Column(String(50), nullable=True)

    sensor = relationship("SensorNodeModel", back_populates="river_node")
