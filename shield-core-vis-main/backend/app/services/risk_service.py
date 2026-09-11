"""Risk service."""

import json
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.zone_repo import ZoneRepository
from app.repositories.risk_repo import RiskRepository
from app.schemas.risk import RiskScoreResponse, RiskZoneResponse, RiskDriverResponse
from app.schemas.common import Coordinates
from app.core.exceptions import EntityNotFoundException


class RiskService:
    def __init__(self, db: Session):
        self.zone_repo = ZoneRepository(db)
        self.risk_repo = RiskRepository(db)

    def get_city_risk(self) -> RiskScoreResponse:
        zones = self.zone_repo.get_all()
        if not zones:
            return RiskScoreResponse(
                city="Visakhapatnam",
                value=72,
                level="HIGH",
                confidence=91,
                velocityPerHour=5.4,
                observedAt=datetime.now(timezone.utc).isoformat(),
                quality="FRESH",
            )

        total_pop = sum(z.population for z in zones) or 1
        weighted_val = 0.0
        conf_sum = 0
        vel_sum = 0.0
        latest_obs = datetime.now(timezone.utc).isoformat()
        quality = "FRESH"
        level = "HIGH"

        count = 0
        for z in zones:
            if z.risk_scores:
                latest = z.risk_scores[0]
                weighted_val += latest.value * z.population
                conf_sum += latest.confidence
                vel_sum += latest.velocity_per_hour
                latest_obs = latest.observed_at.isoformat()
                quality = latest.data_quality
                level = latest.level
                count += 1

        val = round(weighted_val / total_pop) if count > 0 else 72
        conf = round(conf_sum / count) if count > 0 else 91
        vel = round(vel_sum / count, 1) if count > 0 else 5.4

        return RiskScoreResponse(
            city="Visakhapatnam",
            value=val,
            level=level,
            confidence=conf,
            velocityPerHour=vel,
            observedAt=latest_obs,
            quality=quality,
        )

    def get_zones(self, hazard: Optional[str] = None) -> List[RiskZoneResponse]:
        zones = self.zone_repo.get_all(hazard)
        return [self._format_zone(z) for z in zones]

    def get_zone_by_id(self, zone_id: str) -> RiskZoneResponse:
        zone = self.zone_repo.get_by_id(zone_id)
        if not zone:
            raise EntityNotFoundException("RiskZone", zone_id)
        return self._format_zone(zone)

    def _format_zone(self, zone) -> RiskZoneResponse:
        latest_score = zone.risk_scores[0] if zone.risk_scores else None
        score_resp = RiskScoreResponse(
            city="Visakhapatnam",
            value=latest_score.value if latest_score else 65,
            level=latest_score.level if latest_score else "MODERATE",
            confidence=latest_score.confidence if latest_score else 88,
            velocityPerHour=latest_score.velocity_per_hour if latest_score else 2.0,
            observedAt=latest_score.observed_at.isoformat() if latest_score else datetime.now(timezone.utc).isoformat(),
            quality=latest_score.data_quality if latest_score else "FRESH",
        )

        drivers_resp = []
        if latest_score and latest_score.drivers:
            for d in latest_score.drivers:
                drivers_resp.append(
                    RiskDriverResponse(
                        id=d.id,
                        label=d.metric_name,
                        contribution=d.contribution,
                        value=f"{d.metric_value} {d.unit}",
                        metricValue=d.metric_value,
                        unit=d.unit,
                        trend=d.trend,
                    )
                )

        try:
            poly_coords = json.loads(zone.polygon_geojson)
        except Exception:
            poly_coords = [[83.2, 17.7], [83.22, 17.7], [83.22, 17.72], [83.2, 17.72], [83.2, 17.7]]

        return RiskZoneResponse(
            id=zone.id,
            name=zone.name,
            code=zone.code,
            population=zone.population,
            areaKm2=zone.area_km2,
            dominantHazard=zone.dominant_hazard,
            risk=score_resp,
            drivers=drivers_resp,
            centroid=Coordinates(lat=zone.centroid_lat, lng=zone.centroid_lng),
            polygon=poly_coords,
        )
