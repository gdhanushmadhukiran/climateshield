"""City model."""

from sqlalchemy import Column, String, Float
from app.core.database import Base
from app.models.base import TimestampMixin


class CityModel(Base, TimestampMixin):
    __tablename__ = "cities"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    country = Column(String(100), nullable=False, default="India")
    timezone = Column(String(50), nullable=False, default="Asia/Kolkata")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
