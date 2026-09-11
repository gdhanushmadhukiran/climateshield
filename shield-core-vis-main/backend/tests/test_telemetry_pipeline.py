"""Automated tests for the real-time IoT telemetry ingestion pipeline."""

import uuid
from datetime import datetime, timezone, timedelta
from app.models.sensor import SensorObservationModel, SensorNodeModel


def test_valid_telemetry_ingest(client):
    msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "message_id": msg_id,
        "node_code": "RN-01",
        "timestamp": now.isoformat(),
        "water_level_m": 4.15,
        "rainfall_mm": 5.2,
        "temperature_c": 28.0,
        "latitude": 17.750,
        "longitude": 83.340,
        "battery_percent": 95,
        "signal_percent": 90,
        "is_simulated": True,
    }
    response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["message_id"] == msg_id
    assert data["deduplicated"] is False
    assert data["observations_persisted"] == 3
    assert data["quality"] == "VALID"


def test_message_deduplication(client):
    msg_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    payload = {
        "message_id": msg_id,
        "node_code": "RN-01",
        "timestamp": now.isoformat(),
        "water_level_m": 4.16,
    }
    # First delivery
    resp1 = client.post("/api/v1/telemetry/ingest", json=payload)
    assert resp1.status_code == 200
    assert resp1.json()["deduplicated"] is False
    assert resp1.json()["observations_persisted"] == 1

    # Duplicate redelivery with same message_id
    resp2 = client.post("/api/v1/telemetry/ingest", json=payload)
    assert resp2.status_code == 200
    assert resp2.json()["deduplicated"] is True
    assert resp2.json()["observations_persisted"] == 0


def test_invalid_negative_water_level(client):
    payload = {
        "message_id": str(uuid.uuid4()),
        "node_code": "RN-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "water_level_m": -2.5,  # Illegal negative water level
    }
    response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_invalid_negative_rainfall(client):
    payload = {
        "message_id": str(uuid.uuid4()),
        "node_code": "RN-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "rainfall_mm": -10.0,  # Illegal negative rainfall
    }
    response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert response.status_code == 422


def test_invalid_temperature_bounds(client):
    payload = {
        "message_id": str(uuid.uuid4()),
        "node_code": "RN-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "temperature_c": 120.0,  # Physically implausible temperature
    }
    response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert response.status_code == 422


def test_invalid_coordinates(client):
    payload = {
        "message_id": str(uuid.uuid4()),
        "node_code": "RN-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latitude": 195.0,  # Out of range [-90, 90]
        "longitude": 83.0,
    }
    response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert response.status_code == 422


def test_unknown_sensor_node_rejection(client):
    payload = {
        "message_id": str(uuid.uuid4()),
        "node_code": "UNKNOWN-ROGUE-SENSOR-999",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "water_level_m": 3.0,
    }
    response = client.post("/api/v1/telemetry/ingest", json=payload)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "SENSORNODE_NOT_FOUND"


def test_rate_of_rise_and_time_to_threshold(client):
    node = "RN-02"  # Threshold is 3.2m in seed data
    t0 = datetime.now(timezone.utc) + timedelta(hours=1)
    t1 = t0 + timedelta(minutes=30)

    # Initial packet at T0: 2.80m
    client.post(
        "/api/v1/telemetry/ingest",
        json={
            "message_id": str(uuid.uuid4()),
            "node_code": node,
            "timestamp": t0.isoformat(),
            "water_level_m": 2.80,
        },
    )

    # Subsequent packet at T1 (30 mins later): 3.00m (+0.20m in 0.5h => 0.40 m/h)
    resp = client.post(
        "/api/v1/telemetry/ingest",
        json={
            "message_id": str(uuid.uuid4()),
            "node_code": node,
            "timestamp": t1.isoformat(),
            "water_level_m": 3.00,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["rate_of_rise_m_per_hour"] == 0.40
    # Threshold is 3.2m, current is 3.0m => diff is 0.2m => time is (0.2/0.4)*60 = 30.0 mins
    assert data["time_to_threshold_minutes"] == 30.0


def test_sensor_degraded_status(client):
    payload = {
        "message_id": str(uuid.uuid4()),
        "node_code": "RN-01",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "water_level_m": 4.12,
        "battery_percent": 12,  # Low battery (< 20%)
        "signal_percent": 15,   # Weak signal (< 20%)
    }
    resp = client.post("/api/v1/telemetry/ingest", json=payload)
    assert resp.status_code == 200

    # Query river nodes to verify status changed to DEGRADED
    river_nodes = client.get("/api/v1/river/nodes").json()
    up_node = next(n for n in river_nodes if n["id"] == "sensor-river-01")
    assert up_node["status"] == "DEGRADED"


def test_get_sensor_observations_history(client):
    response = client.get("/api/v1/sensors/sensor-river-01/observations?limit=10")
    assert response.status_code == 200
    obs = response.json()
    assert isinstance(obs, list)
    assert len(obs) > 0
    first = obs[0]
    assert "metric" in first
    assert "value" in first
    assert "is_simulated" in first


def test_river_nodes_enriched_telemetry(client):
    response = client.get("/api/v1/river/nodes")
    assert response.status_code == 200
    nodes = response.json()
    assert len(nodes) == 3
    for n in nodes:
        assert "rateOfRiseMPerHour" in n
        assert "dataQuality" in n
        assert n["dataQuality"] in ("FRESH", "AGING", "STALE", "DEGRADED")
