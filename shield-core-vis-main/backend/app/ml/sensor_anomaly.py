"""IoT Sensor Hardware Anomaly Detection service.

Executes unsupervised anomaly detection using Scikit-learn IsolationForest
on 5-dimensional hardware telemetry vectors [battery_voltage, signal_dbm,
temp_reading_c, rate_of_change_temp, reading_stuck_count].
Flags faulty/degraded sensor nodes without deleting raw observations.
"""

import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple
import numpy as np

from app.core.logging import logger
from app.ml.model_loader import model_loader, SKLEARN_AVAILABLE
from app.ml.schemas import SensorHealthResponse


class SensorAnomalyDetector:
    """Evaluates telemetry packets for IoT hardware faults and sensor degradation."""

    MODEL_VERSION = "IsolationForest-v1.0-synthetic"
    REQUIRED_FEATURES = [
        "battery_voltage",
        "signal_dbm",
        "temp_reading_c",
        "rate_of_change_temp",
        "reading_stuck_count",
    ]

    # Operational validity bounds
    BOUNDS = {
        "battery_voltage": (0.5, 6.0),
        "signal_dbm": (-150.0, 0.0),
        "temp_reading_c": (-40.0, 100.0),
        "rate_of_change_temp": (-60.0, 60.0),
        "reading_stuck_count": (0, 10000),
    }

    @classmethod
    def validate_features(cls, features: Dict[str, Any]) -> Tuple[bool, Optional[str], Optional[np.ndarray]]:
        """Validates presence and bounds of all 5 telemetry features."""
        vector = []
        for feat in cls.REQUIRED_FEATURES:
            if feat not in features or features[feat] is None:
                return False, f"Missing required telemetry feature: '{feat}'", None
            try:
                val = float(features[feat])
            except (ValueError, TypeError):
                return False, f"Feature '{feat}' must be numeric, got: {features[feat]}", None

            min_b, max_b = cls.BOUNDS[feat]
            if val < min_b or val > max_b:
                return False, f"Feature '{feat}' value {val} outside bounds [{min_b}, {max_b}]", None

            vector.append(val)

        return True, None, np.array([vector], dtype=np.float64)

    @classmethod
    def evaluate(
        cls,
        sensor_id: str,
        battery_voltage: float,
        signal_dbm: float,
        temp_reading_c: float,
        rate_of_change_temp: float = 0.0,
        reading_stuck_count: int = 0,
    ) -> SensorHealthResponse:
        """Evaluates hardware telemetry and returns classification (+1 normal, -1 anomaly)."""
        start_time = time.perf_counter()
        now_iso = datetime.now(timezone.utc).isoformat()

        feat_dict = {
            "battery_voltage": battery_voltage,
            "signal_dbm": signal_dbm,
            "temp_reading_c": temp_reading_c,
            "rate_of_change_temp": rate_of_change_temp,
            "reading_stuck_count": reading_stuck_count,
        }

        # 1. Feature validation
        is_valid, err_msg, arr = cls.validate_features(feat_dict)
        if not is_valid or arr is None:
            latency = (time.perf_counter() - start_time) * 1000.0
            return SensorHealthResponse(
                sensor_id=sensor_id,
                status="DEGRADED",
                is_anomaly=True,
                raw_prediction=-1,
                anomaly_score=-0.5,
                model_version=cls.MODEL_VERSION,
                inference_latency_ms=round(latency, 2),
                data_quality="SUSPECT",
                timestamp=now_iso,
                fallback_used=True,
                reason=err_msg or "Invalid hardware telemetry vector",
            )

        # 2. Check model availability
        model = model_loader.get_anomaly_model()
        if not model or not SKLEARN_AVAILABLE:
            latency = (time.perf_counter() - start_time) * 1000.0
            # Deterministic heuristic fallback
            is_anom = (
                battery_voltage < 2.5
                or signal_dbm < -115.0
                or reading_stuck_count > 8
                or abs(rate_of_change_temp) > 20.0
            )
            status = "DEGRADED" if is_anom else "HEALTHY"
            reason = model_loader.anomaly_error or "IsolationForest model not loaded in memory; heuristic fallback active"

            return SensorHealthResponse(
                sensor_id=sensor_id,
                status=status,
                is_anomaly=is_anom,
                raw_prediction=-1 if is_anom else 1,
                anomaly_score=-0.2 if is_anom else 0.2,
                model_version=cls.MODEL_VERSION,
                inference_latency_ms=round(latency, 2),
                data_quality="VALID",
                timestamp=now_iso,
                fallback_used=True,
                reason=reason,
            )

        # 3. Model inference
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=UserWarning)
                raw_pred = int(model.predict(arr)[0])  # +1 = normal, -1 = anomaly
                anomaly_score = float(model.decision_function(arr)[0])
            is_anomaly = raw_pred == -1

            # Operational status classification:
            # - If ML flags anomaly -> ANOMALOUS (downstream sets node health to DEGRADED)
            # - If physical hardware exhibits degradation (battery, signal, stuck ADC, or thermal shock) -> DEGRADED
            # - Otherwise -> HEALTHY
            is_hardware_degraded = (
                battery_voltage < 2.8
                or signal_dbm < -110.0
                or reading_stuck_count >= 10
                or abs(rate_of_change_temp) >= 20.0
            )

            if is_anomaly:
                status = "ANOMALOUS"
            elif is_hardware_degraded:
                status = "DEGRADED"
            else:
                status = "HEALTHY"

            latency = (time.perf_counter() - start_time) * 1000.0
            model_loader.record_inference(latency)

            return SensorHealthResponse(
                sensor_id=sensor_id,
                status=status,
                is_anomaly=is_anomaly,
                raw_prediction=raw_pred,
                anomaly_score=round(anomaly_score, 4),
                model_version=cls.MODEL_VERSION,
                inference_latency_ms=round(latency, 2),
                data_quality="VALID",
                timestamp=now_iso,
                fallback_used=False,
                reason=None,
            )
        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"[SENSOR_ANOMALY] Inference exception: {str(e)}", exc_info=True)
            return SensorHealthResponse(
                sensor_id=sensor_id,
                status="DEGRADED",
                is_anomaly=True,
                raw_prediction=-1,
                anomaly_score=None,
                model_version=cls.MODEL_VERSION,
                inference_latency_ms=round(latency, 2),
                data_quality="SUSPECT",
                timestamp=now_iso,
                fallback_used=True,
                reason=f"Anomaly detection exception: {str(e)}",
            )
