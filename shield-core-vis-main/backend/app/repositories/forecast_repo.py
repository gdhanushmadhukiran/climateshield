"""Forecast repository."""

from typing import Optional
from sqlalchemy.orm import Session, joinedload
from app.models.forecast import ForecastModel


class ForecastRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_forecast(self, zone_id: str = "zone-a", horizon: int = 12) -> Optional[ForecastModel]:
        return (
            self.db.query(ForecastModel)
            .options(joinedload(ForecastModel.points))
            .filter(ForecastModel.zone_id == zone_id)
            .order_by(ForecastModel.created_at.desc())
            .first()
        )
