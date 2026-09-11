"""Health and liveness endpoint tests."""


def test_root_liveness(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {"status": "ok"}
    assert "X-Request-ID" in response.headers


def test_system_health_deep_check(client):
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    data = response.json()
    assert "overallPercent" in data
    assert data["overallPercent"] >= 80
    assert "services" in data
    assert data["services"]["db"] == "HEALTHY"
    assert "weather" in data["services"]
    assert "checkedAt" in data
