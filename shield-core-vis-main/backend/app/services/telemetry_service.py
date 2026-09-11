"""Telemetry ingestion service with validation, deduplication, and hydrological rate calculations."""

import asyncio
from datetime import datetime, timezone
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.core.config import settings
from app.core.events import broadcaster
from app.core.exceptions import EntityNotFoundException
from app.models.sensor import SensorNodeModel, SensorObservationModel, ProcessedMessageModel
from app.models.river import RiverNodeModel
from app.schemas.telemetry import (
    TelemetryPayload,
    TelemetryIngestResponse,
    RiverUpdateEvent,
    SensorStatusEvent,
    RiskTriggerEvent,
)


class TelemetryService:
    def __init__(self, db: Session):
        self.db = db

    def process_telemetry(self, payload: TelemetryPayload) -> TelemetryIngestResponse:
        now_utc = datetime.now(timezone.utc)

        # 1. Deduplication check
        existing_msg = (
            self.db.query(ProcessedMessageModel)
            .filter(ProcessedMessageModel.message_id == payload.message_id)
            .first()
        )
        if existing_msg:
            logger.info(
                f"[DEDUPLICATION] Message {payload.message_id} from {payload.node_code} already processed",
                extra={"message_id": payload.message_id, "node_code": payload.node_code},
            )
            return TelemetryIngestResponse(
                status="duplicate",
                message_id=payload.message_id,
                node_code=payload.node_code,
                deduplicated=True,
                observations_persisted=0,
                quality="VALID",
                received_at=now_utc.isoformat(),
            )

        # 2. Sensor Node lookup (prevent rogue node creation)
        # Support matching by code, id, or alias (e.g. RN-01 -> sensor-river-01 or RIV-UP-01)
        sensor = (
            self.db.query(SensorNodeModel)
            .filter(
                (SensorNodeModel.code == payload.node_code)
                | (SensorNodeModel.id == payload.node_code)
                | (SensorNodeModel.code.ilike(f"%{payload.node_code}%"))
            )
            .first()
        )
        # Handle demo alias RN-01, RN-02, RN-03
        if not sensor and payload.node_code in ("RN-01", "RN-02", "RN-03"):
            alias_map = {
                "RN-01": "sensor-river-01",
                "RN-02": "sensor-river-02",
                "RN-03": "sensor-river-03",
            }
            sensor = self.db.query(SensorNodeModel).filter(SensorNodeModel.id == alias_map[payload.node_code]).first()

        if not sensor:
            logger.warning(
                f"[UNKNOWN_SENSOR] Telemetry rejected for unknown sensor node: {payload.node_code}",
                extra={"node_code": payload.node_code, "message_id": payload.message_id},
            )
            raise EntityNotFoundException("SensorNode", payload.node_code)

        # 3. Quality Assessment
        quality = "VALID"
        age_seconds = (now_utc - payload.timestamp).total_seconds()
        if age_seconds > settings.SENSOR_STALE_MINUTES * 60:
            quality = "STALE"

        # 4. Rate-of-Change & Time-to-Threshold Calculations
        rate_of_rise: Optional[float] = None
        time_to_threshold: Optional[float] = None
        river_node = self.db.query(RiverNodeModel).filter(RiverNodeModel.sensor_id == sensor.id).first()

        if payload.water_level_m is not None:
            rate_of_rise, time_to_threshold, anomaly = self._calculate_hydrological_metrics(
                sensor.id,
                payload.water_level_m,
                payload.timestamp,
                river_node.threshold_m if river_node else 3.8,
            )
            if anomaly and quality == "VALID":
                quality = "SUSPECT"

        # 5. Record Processed Message (Deduplication record)
        processed_record = ProcessedMessageModel(
            message_id=payload.message_id,
            node_code=sensor.code,
            received_at=now_utc,
            status="PROCESSED",
        )
        self.db.add(processed_record)

        # 6. Persist Observations
        observations_to_add = []
        if payload.water_level_m is not None:
            observations_to_add.append(
                SensorObservationModel(
                    sensor_id=sensor.id,
                    observed_at=payload.timestamp,
                    metric="water_level",
                    value=payload.water_level_m,
                    unit="m",
                    quality=quality,
                    is_simulated=payload.is_simulated,
                    message_id=payload.message_id,
                    received_at=now_utc,
                )
            )
        if payload.rainfall_mm is not None:
            observations_to_add.append(
                SensorObservationModel(
                    sensor_id=sensor.id,
                    observed_at=payload.timestamp,
                    metric="rainfall",
                    value=payload.rainfall_mm,
                    unit="mm",
                    quality=quality,
                    is_simulated=payload.is_simulated,
                    message_id=payload.message_id,
                    received_at=now_utc,
                )
            )
        if payload.temperature_c is not None:
            observations_to_add.append(
                SensorObservationModel(
                    sensor_id=sensor.id,
                    observed_at=payload.timestamp,
                    metric="temperature",
                    value=payload.temperature_c,
                    unit="C",
                    quality=quality,
                    is_simulated=payload.is_simulated,
                    message_id=payload.message_id,
                    received_at=now_utc,
                )
            )
        self.db.add_all(observations_to_add)

        # 7. Evaluate Hardware Telemetry with Isolation Forest ML & Update Sensor Status
        sensor.last_packet_at = payload.timestamp
        if payload.battery_percent is not None:
            sensor.battery_pct = payload.battery_percent
        if payload.signal_percent is not None:
            sensor.signal_pct = payload.signal_percent
        if payload.latitude is not None:
            sensor.latitude = payload.latitude
        if payload.longitude is not None:
            sensor.longitude = payload.longitude

        # Construct 5 hardware features for IsolationForest
        batt_v = (
            payload.battery_voltage
            if payload.battery_voltage is not None
            else round(3.0 + ((payload.battery_percent or sensor.battery_pct or 85) / 100.0) * 1.2, 2)
        )
        sig_dbm = (
            payload.signal_dbm
            if payload.signal_dbm is not None
            else round(-120.0 + ((payload.signal_percent or sensor.signal_pct or 80) / 100.0) * 70.0, 1)
        )
        temp_reading = payload.temperature_c if payload.temperature_c is not None else 28.0
        rate_temp = payload.rate_of_change_temp if payload.rate_of_change_temp is not None else 0.0
        stuck_cnt = payload.reading_stuck_count if payload.reading_stuck_count is not None else 0

        from app.ml.sensor_anomaly import SensorAnomalyDetector
        ml_anomaly = SensorAnomalyDetector.evaluate(
            sensor_id=sensor.id,
            battery_voltage=batt_v,
            signal_dbm=sig_dbm,
            temp_reading_c=temp_reading,
            rate_of_change_temp=rate_temp,
            reading_stuck_count=stuck_cnt,
        )

        # Dynamic health status determination:
        # If ML flags anomaly or hardware fails, mark DEGRADED (never delete observation)
        if ml_anomaly.is_anomaly or sensor.battery_pct < 20 or sensor.signal_pct < 20 or quality == "SUSPECT":
            sensor.status = "DEGRADED"
        else:
            sensor.status = "HEALTHY"

        self.db.commit()

        # 8. Broadcast Real-Time Events (async task schedule)
        self._dispatch_events(
            sensor=sensor,
            river_node=river_node,
            water_level=payload.water_level_m,
            rate_of_rise=rate_of_rise,
            time_to_threshold=time_to_threshold,
            quality=quality,
            is_simulated=payload.is_simulated,
            timestamp=payload.timestamp.isoformat(),
            anomaly_data=ml_anomaly.model_dump() if ml_anomaly.is_anomaly else None,
        )

        return TelemetryIngestResponse(
            status="success",
            message_id=payload.message_id,
            node_code=sensor.code,
            deduplicated=False,
            observations_persisted=len(observations_to_add),
            rate_of_rise_m_per_hour=rate_of_rise,
            time_to_threshold_minutes=time_to_threshold,
            quality=quality,
            received_at=now_utc.isoformat(),
            is_anomaly=ml_anomaly.is_anomaly,
            anomaly_score=ml_anomaly.anomaly_score,
            ml_model_version=ml_anomaly.model_version,
            ml_inference_latency_ms=ml_anomaly.inference_latency_ms,
        )


    def _calculate_hydrological_metrics(
        self,
        sensor_id: str,
        current_level: float,
        timestamp: datetime,
        threshold_m: float,
    ) -> Tuple[float, Optional[float], bool]:
        """Calculates rate of rise (m/hr), time to threshold (min), and checks for physical jump anomalies."""
        prev_obs = (
            self.db.query(SensorObservationModel)
            .filter(
                SensorObservationModel.sensor_id == sensor_id,
                SensorObservationModel.metric == "water_level",
                SensorObservationModel.observed_at < timestamp,
            )
            .order_by(SensorObservationModel.observed_at.desc())
            .first()
        )

        rate_of_rise = 0.0
        time_to_threshold = None
        anomaly = False

        if prev_obs:
            t_prev = prev_obs.observed_at if prev_obs.observed_at.tzinfo else prev_obs.observed_at.replace(tzinfo=timezone.utc)
            t_curr = timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=timezone.utc)
            delta_seconds = (t_curr - t_prev).total_seconds()
            if delta_seconds > 0:
                delta_hours = delta_seconds / 3600.0
                delta_level = current_level - prev_obs.value
                rate_of_rise = round(delta_level / delta_hours, 2)

                # Check for sudden unrealistic jump (> 1.5m in < 10 mins)
                if abs(delta_level) > 1.5 and delta_seconds < 600:
                    anomaly = True

                # Time to threshold extrapolation (only when rising and below threshold)
                if rate_of_rise > 0.0 and current_level < threshold_m:
                    diff = threshold_m - current_level
                    time_to_threshold = round((diff / rate_of_rise) * 60.0, 1)

        return rate_of_rise, time_to_threshold, anomaly

    def _dispatch_events(
        self,
        sensor: SensorNodeModel,
        river_node: Optional[RiverNodeModel],
        water_level: Optional[float],
        rate_of_rise: Optional[float],
        time_to_threshold: Optional[float],
        quality: str,
        is_simulated: bool,
        timestamp: str,
        anomaly_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        def safe_schedule(coro):
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(coro)
            except RuntimeError:
                coro.close()

        # 1. River update event
        if river_node and water_level is not None:
            river_event = RiverUpdateEvent(
                nodeCode=sensor.code,
                segment=river_node.segment,
                waterLevelM=water_level,
                thresholdM=river_node.threshold_m,
                rateOfRiseMPerHour=rate_of_rise or 0.0,
                timeToThresholdMinutes=time_to_threshold,
                status=sensor.status,
                dataQuality=quality,
                isSimulated=is_simulated,
                timestamp=timestamp,
            )
            safe_schedule(broadcaster.publish("river_update", river_event.model_dump()))

            # Trigger risk recalculation if approaching critical threshold
            if (water_level >= river_node.threshold_m) or (rate_of_rise and rate_of_rise > 0.25):
                from app.engine.coordinator import RiskIntelligenceCoordinator
                try:
                    coordinator = RiskIntelligenceCoordinator(self.db)
                    coordinator.recalculate_all_zones()
                except Exception:
                    pass

                risk_event = RiskTriggerEvent(
                    zoneId=sensor.zone_id,
                    reason=f"Water level ({water_level}m) or rate of rise ({rate_of_rise}m/h) breached operational watch",
                    nodeCode=sensor.code,
                    timestamp=timestamp,
                )
                safe_schedule(broadcaster.publish("risk_trigger", risk_event.model_dump()))

        # 2. Sensor health event
        sensor_event = SensorStatusEvent(
            nodeCode=sensor.code,
            status=sensor.status,
            batteryPercent=sensor.battery_pct,
            signalPercent=sensor.signal_pct,
            lastPacketAt=timestamp,
        )
        safe_schedule(broadcaster.publish("sensor_status", sensor_event.model_dump()))

        # 3. Dedicated ML Sensor Anomaly event
        if anomaly_data is not None:
            safe_schedule(broadcaster.publish("sensor_anomaly", anomaly_data))

        # 4. Real-time ML River Forecast update event
        if river_node:
            try:
                from app.ml.ml_service import MLService
                ml_fc = MLService.get_river_forecast(self.db, river_node_id=sensor.code)
                if ml_fc.forecast_available:
                    safe_schedule(broadcaster.publish("ml_forecast_update", ml_fc.model_dump()))
            except Exception:
                pass


