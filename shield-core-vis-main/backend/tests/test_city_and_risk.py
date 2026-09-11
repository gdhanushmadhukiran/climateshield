"""City and Risk endpoint tests."""


def test_get_city(client):
    response = client.get("/api/v1/city")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Visakhapatnam"
    assert data["country"] == "India"
    assert "coordinates" in data
    assert round(data["coordinates"]["lat"], 2) == 17.69
    assert round(data["coordinates"]["lng"], 2) == 83.22


def test_get_current_city_risk(client):
    response = client.get("/api/v1/risk/current")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Visakhapatnam"
    assert 0 <= data["value"] <= 100
    assert data["level"] in ("LOW", "MODERATE", "HIGH", "CRITICAL")
    assert data["confidence"] > 50
    assert data["quality"] in ("FRESH", "AGING", "STALE", "DEGRADED")
    assert "observedAt" in data


def test_get_risk_zones(client):
    response = client.get("/api/v1/risk/zones")
    assert response.status_code == 200
    zones = response.json()
    assert len(zones) >= 3
    zone_a = next(z for z in zones if z["id"] == "zone-a")
    assert zone_a["code"] == "ZONE-A"
    assert zone_a["dominantHazard"] == "FLOOD"
    assert "polygon" in zone_a
    assert len(zone_a["polygon"]) >= 4

    # Verify driver fields
    assert len(zone_a["drivers"]) > 0
    driver = zone_a["drivers"][0]
    assert "metricValue" in driver
    assert "unit" in driver
    assert "value" in driver


def test_get_single_zone(client):
    response = client.get("/api/v1/risk/zones/zone-a")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "zone-a"
    assert data["name"] == "MVP Colony - Sector 4"


def test_get_single_zone_not_found(client):
    response = client.get("/api/v1/risk/zones/zone-unknown")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "RISKZONE_NOT_FOUND"


def test_get_assets(client):
    response = client.get("/api/v1/assets")
    assert response.status_code == 200
    assets = response.json()
    assert len(assets) >= 6
    kgh = next(a for a in assets if "King George" in a["name"])
    assert kgh["category"] == "HOSPITAL"
    assert kgh["criticality"] == "TIER_1"
    assert kgh["status"] == "OPERATIONAL"
