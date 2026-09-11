"""River, Forecast, Cascade, and Data Source endpoint tests."""


def test_get_river_nodes(client):
    response = client.get("/api/v1/river/nodes")
    assert response.status_code == 200
    nodes = response.json()
    assert len(nodes) == 3

    segments = {n["segment"]: n for n in nodes}
    assert "UPSTREAM" in segments
    assert "MIDSTREAM" in segments
    assert "DOWNSTREAM" in segments

    # Verify topology chaining
    assert segments["UPSTREAM"]["downstreamNodeId"] == segments["MIDSTREAM"]["id"]
    assert segments["MIDSTREAM"]["downstreamNodeId"] == segments["DOWNSTREAM"]["id"]
    assert segments["DOWNSTREAM"]["downstreamNodeId"] is None

    # Telemetry properties
    up = segments["UPSTREAM"]
    assert up["waterLevelM"] > 0
    assert up["thresholdM"] > 0
    assert up["batteryPercent"] >= 80
    assert up["signalPercent"] >= 80


def test_get_data_sources(client):
    response = client.get("/api/v1/data-sources")
    assert response.status_code == 200
    sources = response.json()
    assert len(sources) >= 5
    types = {s["sourceType"] for s in sources}
    assert "WEATHER" in types
    assert "SATELLITE" in types


def test_get_forecast_trajectory(client):
    response = client.get("/api/v1/forecast/trajectory?zoneId=zone-a")
    assert response.status_code == 200
    fc = response.json()
    assert fc["zoneId"] == "zone-a"
    assert len(fc["points"]) >= 5
    for p in fc["points"]:
        assert "timestamp" in p
        assert "value" in p
        assert p["lower"] <= p["value"] <= p["upper"]


def test_get_cascade_graph(client):
    response = client.get("/api/v1/cascade/graph")
    assert response.status_code == 200
    graph = response.json()
    assert len(graph["nodes"]) >= 4
    assert len(graph["edges"]) >= 3
    for edge in graph["edges"]:
        assert "from" in edge
        assert "to" in edge
        assert edge["likelihood"] > 0


def test_get_optimization_recommendations(client):
    response = client.get("/api/v1/optimization/recommendations")
    assert response.status_code == 200
    recs = response.json()
    assert len(recs) >= 3
    assert "expectedRiskReduction" in recs[0]
