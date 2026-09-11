"""Risk repository."""

from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.models.risk import RiskScoreModel, RiskDriverModel


class RiskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_latest_scores(self) -> List[RiskScoreModel]:
        return (
            self.db.query(RiskScoreModel)
            .options(joinedload(RiskScoreModel.drivers))
            .order_by(RiskScoreModel.observed_at.desc())
            .all()
        )

    def get_latest_score_for_zone(self, zone_id: str) -> Optional[RiskScoreModel]:
        return (
            self.db.query(RiskScoreModel)
            .options(joinedload(RiskScoreModel.drivers))
            .filter(RiskScoreModel.zone_id == zone_id)
            .order_by(RiskScoreModel.observed_at.desc())
            .first()
        )
