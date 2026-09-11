"""Incidents and Alerts endpoint tests."""


def test_get_incidents(client):
    response = client.get("/api/v1/incidents")
    assert response.status_code == 200
    incidents = response.json()
    assert len(incidents) >= 4
    inc1 = incidents[0]
    assert "ref" in inc1
    assert "hazard" in inc1
    assert "severity" in inc1
    assert "coordinates" in inc1


def test_update_incident_status_valid(client):
    response = client.post("/api/v1/incidents/inc-1/status", json={"status": "IN_RESPONSE"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "inc-1"
    assert data["status"] == "IN_RESPONSE"


def test_update_incident_status_illegal_transition(client):
    # First mark inc-4 as RESOLVED if not already
    client.post("/api/v1/incidents/inc-4/status", json={"status": "RESOLVED"})

    # Attempt illegal transition RESOLVED -> OPEN
    response = client.post("/api/v1/incidents/inc-4/status", json={"status": "OPEN"})
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "INVALID_STATE_TRANSITION"


def test_get_alerts(client):
    response = client.get("/api/v1/alerts")
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) >= 3
    alt1 = alerts[0]
    assert "channels" in alt1
    assert isinstance(alt1["channels"], list)
    assert "deliveryStatus" in alt1


def test_acknowledge_alert(client):
    response = client.post(
        "/api/v1/alerts/alt-1/acknowledge",
        json={"operatorId": "lead-operator-99"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "alt-1"
    assert data["acknowledged"] is True
    assert data["acknowledgedBy"] == "lead-operator-99"
    assert data["acknowledgedAt"] is not None
