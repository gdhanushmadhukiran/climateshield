"""Alert repository."""

from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.alert import AlertModel


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[AlertModel]:
        return self.db.query(AlertModel).order_by(AlertModel.created_at.desc()).all()

    def get_by_id(self, alert_id: str) -> Optional[AlertModel]:
        return (
            self.db.query(AlertModel)
            .filter((AlertModel.id == alert_id) | (AlertModel.ref == alert_id))
            .first()
        )

    def acknowledge(self, alert: AlertModel, operator_id: str) -> AlertModel:
        alert.acknowledged = True
        alert.acknowledged_by = operator_id
        alert.acknowledged_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(alert)
        return alert
