"""Comprehensive tests for Scikit-learn IsolationForest Sensor Anomaly Detector.

Covers:
- Normal telemetry classification (+1 normal, HEALTHY)
- Anomalous telemetry detection (-1 anomaly, ANOMALOUS)
- Invalid telemetry bounds & negative voltages
- Missing telemetry features
- Model loading failure simulation & heuristic fallback
- Inference exception handling & graceful degradation
"""

import pytest
from unittest.mock import patch, MagicMock

from app.ml.sensor_anomaly import SensorAnomalyDetector
from app.ml.model_loader import model_loader
from app.ml.schemas import SensorHealthResponse


def test_sensor_anomaly_normal_telemetry():
    """Verify that typical operational telemetry is classified as HEALTHY and normal (+1)."""
    resp = SensorAnomalyDetector.evaluate(
        sensor_id="sensor-river-01",
        battery_voltage=3.85,
        signal_dbm=-68.0,
        temp_reading_c=27.5,
        rate_of_change_temp=0.1,
        reading_stuck_count=0,
    )

    assert isinstance(resp, SensorHealthResponse)
    assert resp.sensor_id == "sensor-river-01"
    assert resp.is_anomaly is False
    assert resp.raw_prediction == 1
    assert resp.status == "HEALTHY"
    assert resp.anomaly_score is not None
    assert resp.anomaly_score > 0.0
    assert resp.fallback_used is False
    assert resp.inference_latency_ms >= 0.0


def test_sensor_anomaly_anomalous_telemetry():
    """Verify that degraded/faulty telemetry (rapid spike, stuck counter, low voltage) triggers an anomaly."""
    resp = SensorAnomalyDetector.evaluate(
        sensor_id="sensor-river-02",
        battery_voltage=1.2,
        signal_dbm=-135.0,
        temp_reading_c=85.0,
        rate_of_change_temp=45.0,
        reading_stuck_count=150,
    )

    assert isinstance(resp, SensorHealthResponse)
    assert resp.sensor_id == "sensor-river-02"
    assert resp.is_anomaly is True
    assert resp.raw_prediction == -1
    assert resp.status == "ANOMALOUS"
    assert resp.anomaly_score is not None
    assert resp.anomaly_score < 0.0
    assert resp.fallback_used is False


def test_sensor_anomaly_invalid_bounds():
    """Verify that physically impossible hardware telemetry (e.g. negative battery) is rejected with fallback."""
    resp = SensorAnomalyDetector.evaluate(
        sensor_id="sensor-river-01",
        battery_voltage=-2.0,  # Physically invalid
        signal_dbm=-70.0,
        temp_reading_c=25.0,
    )

    assert resp.is_anomaly is True
    assert resp.status == "DEGRADED"
    assert resp.fallback_used is True
    assert "battery_voltage" in (resp.reason or "")


def test_sensor_anomaly_missing_features():
    """Verify validation when required features are missing."""
    is_valid, err, arr = SensorAnomalyDetector.validate_features({
        "battery_voltage": 3.7,
        "signal_dbm": -75.0,
        # missing temp_reading_c, rate_of_change_temp, reading_stuck_count
    })
    assert is_valid is False
    assert "Missing required telemetry feature" in (err or "")


def test_sensor_anomaly_model_loading_failure_heuristic_fallback():
    """Verify that when IsolationForest is unavailable, deterministic heuristic fallback engages."""
    with patch.object(model_loader, "get_anomaly_model", return_value=None):
        # Normal inputs under fallback
        normal_resp = SensorAnomalyDetector.evaluate(
            sensor_id="sensor-fallback-01",
            battery_voltage=3.8,
            signal_dbm=-70.0,
            temp_reading_c=25.0,
            rate_of_change_temp=0.0,
            reading_stuck_count=0,
        )
        assert normal_resp.status == "HEALTHY"
        assert normal_resp.is_anomaly is False
        assert normal_resp.fallback_used is True
        assert "heuristic fallback" in (normal_resp.reason or "").lower()

        # Low battery under fallback -> triggers degraded
        bad_batt_resp = SensorAnomalyDetector.evaluate(
            sensor_id="sensor-fallback-02",
            battery_voltage=1.8,
            signal_dbm=-70.0,
            temp_reading_c=25.0,
        )
        assert bad_batt_resp.status == "DEGRADED"
        assert bad_batt_resp.is_anomaly is True
        assert bad_batt_resp.fallback_used is True


def test_sensor_anomaly_inference_exception_recovery():
    """Verify that an unexpected runtime failure inside sklearn predict is caught without crashing."""
    mock_model = MagicMock()
    mock_model.predict.side_effect = RuntimeError("Simulated sklearn runtime error")

    with patch.object(model_loader, "get_anomaly_model", return_value=mock_model):
        resp = SensorAnomalyDetector.evaluate(
            sensor_id="sensor-exc-01",
            battery_voltage=3.7,
            signal_dbm=-70.0,
            temp_reading_c=25.0,
        )
        assert resp.status == "DEGRADED"
        assert resp.is_anomaly is True
        assert resp.fallback_used is True
        assert "Anomaly detection exception" in (resp.reason or "")
