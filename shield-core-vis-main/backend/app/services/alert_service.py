"""Alert service."""

from typing import List
from sqlalchemy.orm import Session
from app.repositories.alert_repo import AlertRepository
from app.schemas.alert import AlertResponse
from app.core.exceptions import EntityNotFoundException


class AlertService:
    def __init__(self, db: Session):
        self.repo = AlertRepository(db)

    def get_all(self) -> List[AlertResponse]:
        alerts = self.repo.get_all()
        return [self._format_alert(a) for a in alerts]

    def acknowledge(self, alert_id: str, operator_id: str) -> AlertResponse:
        alert = self.repo.get_by_id(alert_id)
        if not alert:
            raise EntityNotFoundException("Alert", alert_id)

        updated = self.repo.acknowledge(alert, operator_id)
        return self._format_alert(updated)

    def _format_alert(self, a) -> AlertResponse:
        channels_list = [c.strip() for c in a.channels.split(",") if c.strip()]
        return AlertResponse(
            id=a.id,
            ref=a.ref,
            severity=a.severity,
            title=a.title,
            message=a.message,
            channels=channels_list,
            deliveryStatus=a.delivery_status,
            acknowledged=a.acknowledged,
            acknowledgedBy=a.acknowledged_by,
            acknowledgedAt=a.acknowledged_at.isoformat() if a.acknowledged_at else None,
            zoneId=a.zone_id,
            createdAt=a.created_at.isoformat(),
        )
