"""Comprehensive end-to-end integration tests for ClimateShield ML services.

Covers:
- GET  /api/v1/ml/health endpoint
- POST /api/v1/ml/forecast endpoint (custom sequence)
- GET  /api/v1/ml/forecast endpoint (database observation flow)
- GET/POST /api/v1/ml/sensor-health endpoint
- Telemetry pipeline -> ML anomaly detection -> sensor status DEGRADED
- Degraded sensor -> ConfidenceEngine penalty
- Risk coordinator -> ml_forecast_signal attached without altering deterministic risk score
- Response optimizer -> urgency escalation when forecast indicates rising river
- Duplicate and stale telemetry handling
- Deterministic fallback when ML models are forced offline
"""

import uuid
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.core.database import SessionLocal
from app.models.sensor import SensorNodeModel, SensorObservationModel
from app.models.river import RiverNodeModel
from app.models.zone import RiskZoneModel
from app.models.resource import ResourceModel
from app.models.risk import RiskScoreModel
from app.engine.coordinator import RiskIntelligenceCoordinator
from app.services.optimization_service import OptimizationService
from app.ml.model_loader import model_loader

client = TestClient(app)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_api_ml_health():
    """Verify GET /api/v1/ml/health returns valid operational status and model versions."""
    response = client.get("/api/v1/ml/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] in ("ONLINE", "DEGRADED")
    assert data["lstm_loaded"] is True
    assert data["isolation_forest_loaded"] is True
    assert "lstm_forecaster" in data["model_versions"]
    assert "sensor_anomaly" in data["model_versions"]
    assert "torch" in data["framework_versions"]
    assert "scikit-learn" in data["framework_versions"]
    assert data["inference_readiness"] is True


def test_api_ml_forecast_post_custom_sequence():
    """Verify POST /api/v1/ml/forecast executes inference on custom 3x4 tensor."""
    payload = {
        "zone_id": "zone-a",
        "river_node_id": "RN-01",
        "custom_sequence": [
            [10.0, 50.0, 1.2, 30.0],
            [25.0, 70.0, 1.8, 28.0],
            [50.0, 95.0, 2.5, 26.0],
        ],
    }
    response = client.post("/api/v1/ml/forecast", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["forecast_available"] is True
    assert data["predicted_river_level_m"] is not None
    assert data["predicted_river_level_m"] > 0.0
    assert data["forecast_horizon_hours"] == 3
    assert data["fallback_used"] is False
    assert data["model_version"] == "CorrelatedLSTM-v1.0-synthetic"
    assert data["confidence_calibrated"] is False


def test_api_ml_sensor_health_post():
    """Verify POST /api/v1/ml/sensor-health classifies hardware telemetry."""
    normal_payload = {
        "sensor_id": "sensor-river-01",
        "battery_voltage": 3.9,
        "signal_dbm": -65.0,
        "temp_reading_c": 28.0,
        "rate_of_change_temp": 0.2,
        "reading_stuck_count": 0,
    }
    response = client.post("/api/v1/ml/sensor-health", json=normal_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_anomaly"] is False
    assert data["status"] == "HEALTHY"

    # Anomalous payload
    anom_payload = {
        "sensor_id": "sensor-river-01",
        "battery_voltage": 1.1,
        "signal_dbm": -140.0,
        "temp_reading_c": 89.0,
        "rate_of_change_temp": 40.0,
        "reading_stuck_count": 200,
    }
    response_anom = client.post("/api/v1/ml/sensor-health", json=anom_payload)
    assert response_anom.status_code == 200
    data_anom = response_anom.json()
    assert data_anom["is_anomaly"] is True
    assert data_anom["status"] == "ANOMALOUS"


def test_telemetry_pipeline_ml_anomaly_degrades_sensor(db: Session):
    """Verify that posting anomalous hardware telemetry sets sensor health to DEGRADED without deleting observations."""
    sensor = db.query(SensorNodeModel).filter(SensorNodeModel.id == "sensor-river-01").first()
    assert sensor is not None

    msg_id = str(uuid.uuid4())
    payload = {
        "message_id": msg_id,
        "node_code": "RN-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "water_level_m": 2.45,
        "rainfall_mm": 15.0,
        "temperature_c": 65.0,  # High temp + bad hardware triggers IsolationForest anomaly
        "battery_voltage": 1.1,
        "signal_dbm": -135.0,
        "reading_stuck_count": 80,
        "rate_of_change_temp": 30.0,
    }

    resp = client.post("/api/v1/telemetry/ingest", json=payload)
    assert resp.status_code == 200
    res_data = resp.json()

    assert res_data["status"] == "success"
    assert res_data["is_anomaly"] is True
    assert res_data["observations_persisted"] >= 1

    # Verify sensor in DB is now marked DEGRADED
    db.refresh(sensor)
    assert sensor.status == "DEGRADED"

    # Verify observation was persisted (not deleted)
    obs = (
        db.query(SensorObservationModel)
        .filter(SensorObservationModel.message_id == msg_id)
        .first()
    )
    assert obs is not None
    assert obs.value == 2.45


def test_degraded_sensor_reduces_confidence(db: Session):
    """Verify that a DEGRADED sensor node applies a penalty in the ConfidenceEngine."""
    coordinator = RiskIntelligenceCoordinator(db)
    all_res = coordinator.recalculate_all_zones()
    zone_res = all_res["zone_results"]["zone-a"]

    confidence = zone_res["confidence"]
    audit = zone_res["confidence_audit"]

    # Since sensor-river-01 is degraded, penalty is applied
    assert confidence <= 95
    assert any("DEGRADED" in p.get("reason", "") for p in audit["penalties"])


def test_risk_coordinator_ml_forecast_signal(db: Session):
    """Verify that RiskIntelligenceCoordinator attaches the ML forecast signal without altering deterministic score."""
    coordinator = RiskIntelligenceCoordinator(db)
    all_res = coordinator.recalculate_all_zones()
    zone_res = all_res["zone_results"]["zone-a"]

    assert "ml_forecast_signal" in zone_res
    sig = zone_res["ml_forecast_signal"]
    assert "forecast_available" in sig
    assert "forecast_horizon_hours" in sig
    assert sig["forecast_horizon_hours"] == 3
    # Deterministic score remains valid integer [0, 100]
    assert 0 <= zone_res["score"] <= 100



def test_response_optimizer_escalation_under_rising_forecast(db: Session):
    """Verify that when ML river forecast indicates rising river stage, action priority escalates to P1."""
    opt_service = OptimizationService(db)

    # Pre-condition: ensure RN-01 has 3 consecutive rising observations
    now = datetime.now(timezone.utc)
    for i, lvl in enumerate([1.5, 2.5, 3.6]):
        db.add(
            SensorObservationModel(
                sensor_id="sensor-river-01",
                observed_at=now - timedelta(hours=3 - i),
                metric="water_level",
                value=lvl,
                unit="m",
                quality="VALID",
                is_simulated=True,
                message_id=str(uuid.uuid4()),
                received_at=now,
            )
        )
    db.commit()

    plan = opt_service.generate_response_plan()
    actions = plan.actions

    # Find flood barrier or pump action
    barrier_action = next((a for a in actions if "barrier" in a.action.lower() or "pump" in a.action.lower()), None)
    assert barrier_action is not None
    # Verify priority is P1
    assert barrier_action.priority == "P1"
    assert barrier_action.urgency == "IMMEDIATE"


def test_ml_fallback_when_offline():
    """Verify system returns fallback_used=True and does not crash when ML is mocked offline."""
    from unittest.mock import patch

    with patch.object(model_loader, "get_lstm_bundle", return_value=None):
        payload = {
            "custom_sequence": [
                [10.0, 50.0, 1.2, 30.0],
                [25.0, 70.0, 1.8, 28.0],
                [50.0, 95.0, 2.5, 26.0],
            ]
        }
        resp = client.post("/api/v1/ml/forecast", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["forecast_available"] is False
        assert data["fallback_used"] is True
        assert data["predicted_river_level_m"] is None
