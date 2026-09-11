"""Tests for the Multi-Agent Decision API."""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_master_agentic_plan_direct_route(client):
    """Test GET /api/v1/agentic-action-plan returns full 6-agent decision matrix."""
    response = client.get("/api/v1/agentic-action-plan")
    assert response.status_code == 200
    data = response.json()

    assert "timestamp" in data
    assert "system_telemetry_health" in data
    assert "voiceops_ingestion_context" in data
    assert "agents" in data

    # Verify telemetry health audit
    health = data["system_telemetry_health"]
    assert "status" in health
    assert "data_freshness_pct" in health
    assert "sensors_audited" in health
    assert "faulty_hardware_detected" in health
    assert "isolation_forest_audit" in health

    # Verify VoiceOps audio grounding
    voice = data["voiceops_ingestion_context"]
    assert voice["status"] == "VERIFIED_AND_GROUNDED"
    assert "extracted_location" in voice
    assert "confidence_score" in voice

    # Verify all 6 Decision Agents
    agents = data["agents"]
    assert "1_geospatial_agent" in agents
    assert "2_infrastructure_agent" in agents
    assert "3_mobility_agent" in agents
    assert "4_emergency_agent" in agents
    assert "5_communication_agent" in agents
    assert "6_decision_agent_master" in agents

    # Verify specific agent outputs
    assert agents["1_geospatial_agent"]["agent_name"] == "Geospatial Boundary Agent"
    assert "predicted_inundation_depth_cm" in agents["1_geospatial_agent"]
    assert len(agents["1_geospatial_agent"]["high_risk_boundary_zones"]) > 0

    assert agents["2_infrastructure_agent"]["agent_name"] == "Infrastructure Exposure Agent"
    assert "critical_assets_threatened" in agents["2_infrastructure_agent"]
    assert len(agents["2_infrastructure_agent"]["vulnerable_nodes"]) > 0

    assert agents["3_mobility_agent"]["agent_name"] == "Mobility & Transit Agent"
    assert len(agents["3_mobility_agent"]["active_detours"]) > 0

    assert agents["4_emergency_agent"]["agent_name"] == "Emergency Resource Optimizer Agent"
    assert len(agents["4_emergency_agent"]["recommended_dispatches"]) > 0

    assert agents["5_communication_agent"]["agent_name"] == "Public Communication & Warning Agent"
    assert "public_broadcast_alert" in agents["5_communication_agent"]

    assert agents["6_decision_agent_master"]["agent_name"] == "Master Orchestrator Decision Agent"
    assert len(agents["6_decision_agent_master"]["prioritized_city_action_plan"]) >= 4


def test_get_master_agentic_plan_under_ml_router(client):
    """Test GET /api/v1/ml/agentic-action-plan is also accessible via ML router."""
    response = client.get("/api/v1/ml/agentic-action-plan")
    assert response.status_code == 200
    data = response.json()
    assert "agents" in data
    assert "6_decision_agent_master" in data["agents"]
