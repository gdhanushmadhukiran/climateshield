"""City repository."""

from typing import Optional
from sqlalchemy.orm import Session
from app.models.city import CityModel


class CityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_city(self, city_id: Optional[str] = None) -> Optional[CityModel]:
        if city_id:
            return self.db.query(CityModel).filter(CityModel.id == city_id).first()
        return self.db.query(CityModel).first()
