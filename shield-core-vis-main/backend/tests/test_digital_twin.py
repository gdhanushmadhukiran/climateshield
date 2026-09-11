"""ClimateShield Phase 7: Digital Twin & What-If Simulation Automated Test Suite."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.models.risk import RiskScoreModel
from app.models.incident import IncidentModel
from app.models.sensor import SensorObservationModel
from app.services.digital_twin_service import DigitalTwinService
from app.schemas.simulation import (
    SimulationRunRequest,
    EnvironmentalModifiers,
    InfrastructureModifiers,
    ResponseModifiers,
    SensorConfidenceModifiers,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestDigitalTwinService:
    """Unit and integration tests for DigitalTwinService."""

    def test_get_scenarios(self, db_session):
        service = DigitalTwinService(db_session)
        res = service.get_predefined_scenarios()
        assert res.count == 7
        scenario_ids = {s.scenario_id for s in res.scenarios}
        assert "river_rise_0_5m" in scenario_ids
        assert "rainfall_surge_30pct" in scenario_ids
        assert "hospital_road_blocked" in scenario_ids
        assert "deploy_2_pumps" in scenario_ids
        assert "deploy_barriers" in scenario_ids
        assert "sensor_outage" in scenario_ids
        assert "do_nothing" in scenario_ids

    def test_do_nothing_baseline_simulation(self, db_session):
        service = DigitalTwinService(db_session)
        res = service.run_predefined_scenario("do_nothing")

        assert res.simulation_id.startswith("SIM-")
        assert res.scenario_id == "do_nothing"
        assert res.baseline_overall_risk > 0
        assert res.simulated_overall_risk > 0
        assert len(res.affected_zones) >= 3
        assert len(res.affected_assets) >= 4
        assert len(res.metrics_comparison) >= 5
        assert len(res.assumptions) >= 3
        assert "MODELED IMPACT" in res.modeled_impact_statement
        assert "deterministic risk engine remains authoritative" in res.deterministic_safety_note

    def test_river_rise_simulation(self, db_session):
        service = DigitalTwinService(db_session)
        res = service.run_predefined_scenario("river_rise_0_5m")

        # River rise should elevate flood risk and overall composite risk
        assert res.simulated_overall_risk >= res.baseline_overall_risk
        assert res.modeled_risk_delta >= 0

        # Verify Peak River Stage metric in comparison
        stage_metric = next(m for m in res.metrics_comparison if "River Stage" in m.metric_name)
        assert stage_metric.simulated > stage_metric.baseline
        assert stage_metric.absolute_delta == 0.50

    def test_rainfall_surge_simulation(self, db_session):
        service = DigitalTwinService(db_session)
        res = service.run_predefined_scenario("rainfall_surge_30pct")

        rain_metric = next(m for m in res.metrics_comparison if "Precipitation" in m.metric_name)
        assert rain_metric.simulated > rain_metric.baseline
        assert rain_metric.percentage_delta == 30.0

    def test_hospital_road_blocked_simulation(self, db_session):
        service = DigitalTwinService(db_session)
        res = service.run_predefined_scenario("hospital_road_blocked")

        # Check asset status for hospital
        hosp_asset = next((a for a in res.affected_assets if "HOSPITAL" in a.name.upper()), None)
        assert hosp_asset is not None
        assert hosp_asset.status == "ISOLATED_AT_RISK"
        assert "transit" in hosp_asset.simulated_impact.lower() or "arterial" in hosp_asset.simulated_impact.lower()

        # Check warning exists
        assert any("Hospital" in w for w in res.warnings)

    def test_deploy_pumps_and_barriers_reduces_risk(self, db_session):
        service = DigitalTwinService(db_session)
        req = SimulationRunRequest(
            scenario_id="tactical_package",
            name="Deploy 2 Pumps and 500m Barriers",
            environmental=EnvironmentalModifiers(river_level_delta_m=0.30),
            response=ResponseModifiers(pumps_deployed=2, barriers_deployed_units=4),
        )
        res = service.run_simulation(req)

        assert res.simulated_residual_risk <= res.simulated_overall_risk
        assert res.estimated_population_protected > 0
        assert res.critical_assets_safeguarded >= 1
        assert "SIMULATED RISK REDUCTION" in str(res.metrics_comparison)

    def test_sensor_outage_confidence_penalty(self, db_session):
        service = DigitalTwinService(db_session)
        res = service.run_predefined_scenario("sensor_outage")

        # Warning regarding sensor telemetry degradation should be present
        assert any("telemetry" in w.lower() or "sensor" in w.lower() for w in res.warnings)

    def test_intervention_ranking(self, db_session):
        service = DigitalTwinService(db_session)
        res = service.run_predefined_scenario("river_rise_0_5m")

        assert len(res.intervention_ranking) == 5
        # Check ranks 1 through 5
        ranks = [item.rank for item in res.intervention_ranking]
        assert ranks == [1, 2, 3, 4, 5]

        # Top ranked option must be marked as best modeled option
        best = res.intervention_ranking[0]
        assert best.is_best_modeled_option is True
        assert best.name == res.best_modeled_option
        assert best.multi_attribute_utility_score >= res.intervention_ranking[1].multi_attribute_utility_score

    def test_deterministic_repeatability(self, db_session):
        service = DigitalTwinService(db_session)
        req = SimulationRunRequest(
            scenario_id="repeatability_test",
            name="Deterministic Test",
            environmental=EnvironmentalModifiers(river_level_delta_m=0.42, rainfall_intensity_pct=15.0),
            response=ResponseModifiers(pumps_deployed=1),
        )
        res1 = service.run_simulation(req)
        res2 = service.run_simulation(req)

        assert res1.simulated_overall_risk == res2.simulated_overall_risk
        assert res1.modeled_risk_delta == res2.modeled_risk_delta
        assert res1.simulated_residual_risk == res2.simulated_residual_risk
        assert res1.best_modeled_option == res2.best_modeled_option
        assert res1.estimated_population_protected == res2.estimated_population_protected

    def test_zero_database_mutation(self, db_session):
        """Strictly verifies that simulations DO NOT mutate production database records."""
        # Record baseline row counts
        risk_count_before = db_session.query(RiskScoreModel).count()
        incident_count_before = db_session.query(IncidentModel).count()
        obs_count_before = db_session.query(SensorObservationModel).count()

        service = DigitalTwinService(db_session)
        # Run multiple diverse simulation scenarios
        for _ in range(5):
            service.run_predefined_scenario("river_rise_0_5m")
            service.run_predefined_scenario("hospital_road_blocked")
            service.run_predefined_scenario("deploy_2_pumps")

        # Verify row counts remain 100% identical
        assert db_session.query(RiskScoreModel).count() == risk_count_before
        assert db_session.query(IncidentModel).count() == incident_count_before
        assert db_session.query(SensorObservationModel).count() == obs_count_before


class TestDigitalTwinAPI:
    """FastAPI endpoint integration tests."""

    def test_get_scenarios_endpoint(self, client):
        response = client.get("/api/v1/simulation/scenarios")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 7
        assert len(data["scenarios"]) == 7

    def test_post_named_scenario_endpoint(self, client):
        response = client.post("/api/v1/simulation/scenarios/river_rise_0_5m")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "river_rise_0_5m"
        assert "simulation_id" in data
        assert "MODELED IMPACT" in data["modeled_impact_statement"]
        assert len(data["intervention_ranking"]) == 5

    def test_post_custom_simulation_endpoint(self, client):
        payload = {
            "scenario_id": "custom_convective",
            "name": "Custom Convective Storm",
            "environmental": {
                "river_level_delta_m": 0.35,
                "rainfall_intensity_pct": 25.0,
            },
            "response": {
                "pumps_deployed": 1,
                "barriers_deployed_units": 2,
            },
        }
        response = client.post("/api/v1/simulation/run", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_id"] == "custom_convective"
        assert data["simulated_overall_risk"] > 0
        sim_id = data["simulation_id"]

        # Now test GET /simulation/{simulation_id}
        get_res = client.get(f"/api/v1/simulation/{sim_id}")
        assert get_res.status_code == 200
        assert get_res.json()["simulation_id"] == sim_id

    def test_unknown_named_scenario_returns_404(self, client):
        response = client.post("/api/v1/simulation/scenarios/non_existent_catastrophe")
        assert response.status_code == 404

    def test_affected_assets_and_metrics_contract(self, client):
        """Regression test ensuring affected_assets, metrics_comparison and cascade items conform to frontend contract."""
        response = client.post("/api/v1/simulation/scenarios/river_rise_0_5m")
        assert response.status_code == 200
        data = response.json()
        assert "affected_assets" in data
        assert len(data["affected_assets"]) > 0
        for asset in data["affected_assets"]:
            assert "asset_id" in asset
            assert "name" in asset
            assert "status" in asset and asset["status"] is not None
            assert "asset_type" in asset and asset["asset_type"] is not None
            assert "criticality" in asset

        assert "metrics_comparison" in data
        for metric in data["metrics_comparison"]:
            assert "metric_name" in metric and metric["metric_name"] is not None
            assert "baseline" in metric
            assert "simulated" in metric
            assert "absolute_delta" in metric

