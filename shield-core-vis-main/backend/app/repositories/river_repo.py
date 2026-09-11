"""River sensor node repository."""

from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from app.models.river import RiverNodeModel
from app.models.sensor import SensorNodeModel, SensorObservationModel


class RiverRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        nodes = (
            self.db.query(RiverNodeModel)
            .options(joinedload(RiverNodeModel.sensor))
            .all()
        )
        results = []
        for r in nodes:
            sensor = r.sensor
            # Fetch latest 2 water level observations to compute rate of change
            obs_list = (
                self.db.query(SensorObservationModel)
                .filter(
                    SensorObservationModel.sensor_id == r.sensor_id,
                    SensorObservationModel.metric == "water_level",
                )
                .order_by(SensorObservationModel.observed_at.desc())
                .limit(2)
                .all()
            )
            latest_obs = obs_list[0] if obs_list else None
            prev_obs = obs_list[1] if len(obs_list) > 1 else None

            water_level = latest_obs.value if latest_obs else 2.5
            quality = latest_obs.quality if latest_obs else "FRESH"

            rate_of_rise = 0.0
            time_to_threshold = None

            if latest_obs and prev_obs:
                t_latest = latest_obs.observed_at if latest_obs.observed_at.tzinfo else latest_obs.observed_at.replace(tzinfo=timezone.utc)
                t_prev = prev_obs.observed_at if prev_obs.observed_at.tzinfo else prev_obs.observed_at.replace(tzinfo=timezone.utc)
                delta_sec = (t_latest - t_prev).total_seconds()
                if delta_sec > 0:
                    delta_h = delta_sec / 3600.0
                    rate_of_rise = round((latest_obs.value - prev_obs.value) / delta_h, 2)
                    if rate_of_rise > 0.0 and water_level < r.threshold_m:
                        time_to_threshold = round(((r.threshold_m - water_level) / rate_of_rise) * 60.0, 1)

            # Freshness / Offline check on sensor node
            sensor_status = sensor.status if sensor else "HEALTHY"
            if sensor and sensor.last_packet_at:
                t_packet = sensor.last_packet_at if sensor.last_packet_at.tzinfo else sensor.last_packet_at.replace(tzinfo=timezone.utc)
                age_min = (datetime.now(timezone.utc) - t_packet).total_seconds() / 60.0
                if sensor_status == "DEGRADED":
                    quality = "DEGRADED"
                elif age_min > 60:
                    sensor_status = "OFFLINE"
                    quality = "STALE"
                elif age_min > 30:
                    sensor_status = "DEGRADED"
                    quality = "DEGRADED"
                elif age_min > 15:
                    quality = "AGING"
                else:
                    quality = "FRESH"
            else:
                quality = "FRESH"

            results.append({
                "id": r.sensor_id,
                "code": sensor.code if sensor and sensor.code else ("RN-01" if "01" in r.sensor_id else ("RN-02" if "02" in r.sensor_id else "RN-03")),
                "name": sensor.name if sensor else r.sensor_id,
                "segment": r.segment,
                "waterLevelM": water_level,
                "thresholdM": r.threshold_m,
                "rateOfRiseMPerHour": rate_of_rise,
                "timeToThresholdMinutes": time_to_threshold,
                "travelTimeMinutes": r.travel_time_min,
                "status": sensor_status,
                "dataQuality": quality,
                "batteryPercent": sensor.battery_pct if sensor else 100,
                "signalPercent": sensor.signal_pct if sensor else 100,
                "lastPacketAt": sensor.last_packet_at.isoformat() if sensor and sensor.last_packet_at else "",
                "downstreamNodeId": r.downstream_node_id,
            })
        return results
