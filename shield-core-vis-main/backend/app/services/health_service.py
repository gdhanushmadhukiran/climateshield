"""System health service."""

from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.schemas.system import SystemHealthResponse


class HealthService:
    def __init__(self, db: Session):
        self.db = db

    def check_health(self) -> SystemHealthResponse:
        # Check actual database connectivity
        db_status = "HEALTHY"
        try:
            self.db.execute(text("SELECT 1"))
        except Exception:
            db_status = "DEGRADED"

        services = {
            "weather": settings.WEATHER_SERVICE_STATUS,
            "gis": settings.GIS_SERVICE_STATUS,
            "iot": settings.IOT_SERVICE_STATUS,
            "risk": settings.RISK_SERVICE_STATUS,
            "alerts": "HEALTHY",
            "db": db_status,
        }

        # Calculate overall percent
        healthy_count = sum(1 for status in services.values() if status in ("HEALTHY", "ACTIVE"))
        overall = round((healthy_count / len(services)) * 100)

        return SystemHealthResponse(
            overallPercent=overall,
            mode=settings.ENV.upper(),
            services=services,
            checkedAt=datetime.now(timezone.utc).isoformat(),
        )
