"""Automated tests for Phase 5 Response Optimization & Action Intelligence Engine."""

import pytest
from app.engine.route_logistics import RouteLogisticsEngine
from app.engine.resource_optimizer import ResourceOptimizer
from app.engine.simulation_engine import SimulationEngine


def test_route_logistics_haversine():
    """Verify great-circle distance calculation between two Visakhapatnam coordinates."""
    # Gajuwaka Depot (17.695, 83.215) to MVP Colony (17.742, 83.335)
    dist = RouteLogisticsEngine.haversine_distance_km(17.695, 83.215, 17.742, 83.335)
    assert 13.0 < dist < 17.0


def test_route_logistics_waterlogging_speed_penalty():
    """Verify severe waterlogging on arterial corridors increases transit time due to detour impedance."""
    clear_route = RouteLogisticsEngine.calculate_deployment_eta(
        depot_lat=17.695,
        depot_lng=83.215,
        target_lat=17.742,
        target_lng=83.335,
        mobilization_minutes=15,
        waterlogging_severity="NONE",
    )
    flooded_route = RouteLogisticsEngine.calculate_deployment_eta(
        depot_lat=17.695,
        depot_lng=83.215,
        target_lat=17.742,
        target_lng=83.335,
        mobilization_minutes=15,
        waterlogging_severity="SEVERE",
    )

    assert flooded_route["total_eta_minutes"] > clear_route["total_eta_minutes"]
    assert flooded_route["effective_speed_kmh"] < clear_route["effective_speed_kmh"]
    assert flooded_route["route_status"] == "IMPEDED_DETOUR_REQUIRED"


def test_resource_optimizer_allocation():
    """Verify multi-criteria optimization matches resources to priority actions."""
    zones = [
        {"id": "zone-a", "code": "ZONE-A", "dominant_hazard": "FLOOD", "risk_score": 84, "population": 185000},
        {"id": "zone-b", "code": "ZONE-B", "dominant_hazard": "DRAINAGE_STRESS", "risk_score": 68, "population": 290000},
    ]
    resources = [
        {"id": "r-pump-1", "name": "Pump Alpha", "category": "PUMP", "status": "AVAILABLE", "latitude": 17.7, "longitude": 83.2},
        {"id": "r-barr-1", "name": "Barrier Alpha", "category": "BARRIER", "status": "AVAILABLE", "latitude": 17.7, "longitude": 83.2},
    ]

    res = ResourceOptimizer.generate_and_optimize_plan(zones, resources)
    assert res["total_actions"] >= 2
    assert res["allocated_resources_count"] == 2
    assert res["total_projected_risk_reduction"] > 0
    assert res["total_population_protected"] > 0

    actions = res["actions"]
    assert actions[0]["priority"] in ("P1", "P2")
    assert actions[0]["expectedRiskReduction"] >= 10
    assert actions[0]["protectedPopulation"] > 0


def test_simulation_engine_what_if():
    """Verify closed-loop what-if counterfactual simulation math."""
    res = SimulationEngine.simulate_scenario(
        scenario_id="flood_mitigation_package",
        parameters={
            "additional_pumps": 3,
            "barrier_length_km": 2.5,
            "early_warning_hours": 4.0,
            "evac_compliance_pct": 80.0,
        },
        baseline_risk=82,
        total_population=620000,
    )

    assert res["baselineRisk"] == 82
    assert res["simulatedRisk"] < 82
    assert res["populationProtected"] > 50000
    assert res["assetsProtected"] >= 3
    assert res["confidence"] >= 85


def test_api_get_recommendations(client):
    """Verify GET /api/v1/optimization/recommendations returns prescriptive actions."""
    response = client.get("/api/v1/optimization/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

    first = data[0]
    # Check both backend Phase 2 and frontend TypeScript contracts
    assert "id" in first
    assert "action" in first
    assert "rationale" in first
    assert "priority" in first
    assert "expectedRiskReduction" in first
    assert "etaMinutes" in first
    assert "confidence" in first
    assert "cost" in first


def test_api_get_response_plan(client):
    """Verify GET /api/v1/optimization/plan returns comprehensive operational plan."""
    response = client.get("/api/v1/optimization/plan")
    assert response.status_code == 200
    data = response.json()

    assert data["total_actions"] > 0
    assert data["total_projected_risk_reduction"] > 0
    assert data["total_population_protected"] > 0
    assert len(data["actions"]) > 0


def test_api_get_resources(client):
    """Verify GET /api/v1/optimization/resources lists equipment inventory."""
    response = client.get("/api/v1/optimization/resources")
    assert response.status_code == 200
    resources = response.json()
    assert len(resources) >= 5

    categories = {r["category"] for r in resources}
    assert "PUMP" in categories
    assert "RESCUE" in categories
    assert "BARRIER" in categories


def test_api_approve_action_workflow(client):
    """Verify POST /api/v1/optimization/actions/{id}/approve dispatches resource and creates incident."""
    response = client.post(
        "/api/v1/optimization/actions/rec-1/approve",
        json={"operator_id": "lead-commander-01", "notes": "Approved for immediate deployment"},
    )
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "DISPATCHED"
    assert data["approved_by"] == "lead-commander-01"
    assert data["dispatched_incident_ref"].startswith("INC-DISP-")
    assert data["target_zone_id"] != ""

    # Verify incident is now reflected in incidents endpoint with IN_RESPONSE status
    incidents = client.get("/api/v1/incidents").json()
    dispatched_inc = next((i for i in incidents if i["ref"] == data["dispatched_incident_ref"]), None)
    assert dispatched_inc is not None
    assert dispatched_inc["status"] == "IN_RESPONSE"


def test_api_simulate_response(client):
    """Verify POST /api/v1/optimization/simulate computes residual risk."""
    payload = {
        "scenario_id": "inundation_defense_sprint",
        "parameters": {
            "additional_pumps": 2,
            "barrier_length_km": 1.5,
            "early_warning_hours": 3.0,
        },
    }
    response = client.post("/api/v1/optimization/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["scenarioId"] == "inundation_defense_sprint"
    assert data["baselineRisk"] > data["simulatedRisk"]
    assert data["populationProtected"] > 0
    assert data["assetsProtected"] > 0
