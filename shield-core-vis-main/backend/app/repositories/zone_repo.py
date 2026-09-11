"""Risk zone repository."""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.models.zone import RiskZoneModel
from app.models.risk import RiskScoreModel


class ZoneRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, hazard: Optional[str] = None) -> List[RiskZoneModel]:
        query = self.db.query(RiskZoneModel).options(
            joinedload(RiskZoneModel.risk_scores).joinedload(RiskScoreModel.drivers)
        )
        if hazard:
            query = query.filter(RiskZoneModel.dominant_hazard == hazard.upper())
        return query.all()

    def get_by_id(self, zone_id: str) -> Optional[RiskZoneModel]:
        return (
            self.db.query(RiskZoneModel)
            .options(
                joinedload(RiskZoneModel.risk_scores).joinedload(RiskScoreModel.drivers)
            )
            .filter(RiskZoneModel.id == zone_id)
            .first()
        )
