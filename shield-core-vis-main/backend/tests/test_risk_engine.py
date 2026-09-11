"""Comprehensive tests for ClimateShield Multi-Hazard Spatial Risk Intelligence Engine."""

import pytest
from app.engine.flood_engine import FloodHazardEngine
from app.engine.heat_engine import HeatHazardEngine
from app.engine.secondary_hazard_engine import SecondaryHazardEngine
from app.engine.exposure_engine import ExposureEngine
from app.engine.vulnerability_engine import VulnerabilityEngine
from app.engine.confidence_engine import ConfidenceEngine
from app.engine.composite_risk_engine import CompositeRiskEngine
from app.engine.base import get_risk_level, clamp, linear_scale


def test_engine_determinism():
    """Verify that identical inputs produce perfectly identical outputs with zero randomness."""
    for _ in range(5):
        f1 = FloodHazardEngine.calculate(water_level_m=3.8, threshold_m=3.5, rate_of_rise_m_h=0.25)
        f2 = FloodHazardEngine.calculate(water_level_m=3.8, threshold_m=3.5, rate_of_rise_m_h=0.25)
        assert f1 == f2
        assert f1["score"] == f2["score"]

        h1 = HeatHazardEngine.calculate(temperature_c=34.0, relative_humidity_pct=72.0)
        h2 = HeatHazardEngine.calculate(temperature_c=34.0, relative_humidity_pct=72.0)
        assert h1 == h2
        assert h1["score"] == h2["score"]


def test_flood_hazard_surge_sensitivity():
    """Verify flood hazard score increases with higher water level and positive rate of rise."""
    low_flood = FloodHazardEngine.calculate(water_level_m=2.0, threshold_m=3.8, rate_of_rise_m_h=0.0)
    high_flood = FloodHazardEngine.calculate(water_level_m=4.1, threshold_m=3.8, rate_of_rise_m_h=0.35)

    assert high_flood["score"] > low_flood["score"]
    assert high_flood["level_ratio"] > 1.0
    assert high_flood["surge_penalty"] > 0


def test_heat_index_rothfusz_equation():
    """Verify NOAA Rothfusz heat index calculation against benchmark physics."""
    # At 35C and 70% RH, apparent temperature is significantly higher (>48C)
    hi_c = HeatHazardEngine.calculate_heat_index(temperature_c=35.0, relative_humidity_pct=70.0)
    assert hi_c > 48.0

    # At low temperature (22C), heat index is near ambient
    hi_c_low = HeatHazardEngine.calculate_heat_index(temperature_c=22.0, relative_humidity_pct=50.0)
    assert abs(hi_c_low - 22.0) < 2.0


def test_compounding_hazard_multiplier():
    """Verify that concurrent flood and drainage stress triggers compounding multiplier."""
    flood_res = {"score": 75.0, "water_level_m": 4.12, "rate_of_rise_m_h": 0.28}
    heat_res = {"score": 35.0, "heat_index_c": 32.0}
    drainage_high_stress = {"score": 78.0, "pump_capacity_pct": 55.0}
    drainage_normal = {"score": 25.0, "pump_capacity_pct": 95.0}
    surge_res = {"score": 20.0, "surge_height_m": 0.5}
    air_res = {"score": 30.0, "aqi_value": 65.0}
    exposure = {"exposure_index": 0.65}
    vulnerability = {"vulnerability_index": 0.60}

    # Concurrent flood + drainage stress
    res_compound = CompositeRiskEngine.calculate(
        dominant_hazard="FLOOD",
        flood_hazard=flood_res,
        heat_hazard=heat_res,
        drainage_hazard=drainage_high_stress,
        surge_hazard=surge_res,
        air_hazard=air_res,
        exposure=exposure,
        vulnerability=vulnerability,
    )

    # Isolated flood (normal drainage)
    res_normal = CompositeRiskEngine.calculate(
        dominant_hazard="FLOOD",
        flood_hazard=flood_res,
        heat_hazard=heat_res,
        drainage_hazard=drainage_normal,
        surge_hazard=surge_res,
        air_hazard=air_res,
        exposure=exposure,
        vulnerability=vulnerability,
    )

    assert res_compound["compound_multiplier"] >= 1.15
    assert len(res_compound["active_interactions"]) > 0
    assert any(i["type"] == "FLOOD_DRAINAGE_COMPOUND" for i in res_compound["active_interactions"])
    assert res_compound["score"] > res_normal["score"]


def test_confidence_penalties_and_audit():
    """Verify confidence drops on stale data or degraded/offline sensors with an explicit audit."""
    conf_healthy = ConfidenceEngine.calculate(
        data_quality="FRESH",
        sensors=[{"code": "RN-01", "status": "HEALTHY"}],
        missing_metrics=[],
        observation_age_minutes=2.0,
    )
    assert conf_healthy["confidence"] >= 95
    assert len(conf_healthy["missing_or_degraded_inputs"]) == 0

    conf_degraded = ConfidenceEngine.calculate(
        data_quality="STALE",
        sensors=[
            {"code": "RN-01", "status": "DEGRADED"},
            {"code": "RN-02", "status": "OFFLINE"},
        ],
        missing_metrics=["rainfall"],
        observation_age_minutes=45.0,
    )
    assert conf_degraded["confidence"] < conf_healthy["confidence"]
    assert conf_degraded["total_penalty"] > 30.0
    assert len(conf_degraded["missing_or_degraded_inputs"]) >= 3


def test_exposure_and_vulnerability_indices():
    """Verify exposure and vulnerability scales appropriately with assets and population."""
    assets = [
        {"id": "a1", "name": "King George Hospital", "asset_type": "HOSPITAL", "criticality": "TIER_1", "status": "OPERATIONAL"},
        {"id": "a2", "name": "Power Substation", "asset_type": "POWER", "criticality": "TIER_2", "status": "DEGRADED"},
    ]
    exp = ExposureEngine.calculate(population=240000, area_km2=15.0, assets=assets)
    assert 0.0 < exp["exposure_index"] <= 1.0
    assert exp["tier_counts"]["TIER_1"] == 1
    assert exp["tier_counts"]["TIER_2"] == 1

    vuln = VulnerabilityEngine.calculate(assets=assets, drainage_pump_capacity_pct=60.0, soil_saturation_pct=85.0)
    assert 0.0 < vuln["vulnerability_index"] <= 1.0
    assert vuln["degraded_assets_count"] == 1


def test_driver_decomposition_sum_to_100():
    """Verify composite risk engine decomposes drivers that strictly sum to 100.0%."""
    flood_res = {"score": 68.0, "water_level_m": 3.9, "rate_of_rise_m_h": 0.22, "rainfall_intensity_mm_h": 35.0}
    heat_res = {"score": 40.0, "heat_index_c": 33.0}
    drainage_res = {"score": 65.0, "pump_capacity_pct": 68.0}
    surge_res = {"score": 25.0, "surge_height_m": 0.8}
    air_res = {"score": 30.0, "aqi_value": 70.0}
    exposure = {"exposure_index": 0.6}
    vulnerability = {"vulnerability_index": 0.55}

    res = CompositeRiskEngine.calculate(
        dominant_hazard="EXTREME_RAINFALL",
        flood_hazard=flood_res,
        heat_hazard=heat_res,
        drainage_hazard=drainage_res,
        surge_hazard=surge_res,
        air_hazard=air_res,
        exposure=exposure,
        vulnerability=vulnerability,
    )

    drivers = res["drivers"]
    assert len(drivers) == 3
    total_pct = sum(d["contribution"] for d in drivers)
    assert abs(total_pct - 100.0) < 0.001


def test_api_explain_risk_zone(client):
    """Verify GET /api/v1/risk/explain/{zone_id} answers all 10 core operational questions."""
    response = client.get("/api/v1/risk/explain/zone-a")
    assert response.status_code == 200
    data = response.json()

    assert "answers" in data
    ans = data["answers"]

    # 1. WHERE
    assert "where_is_risk" in ans
    assert ans["where_is_risk"]["zone_id"] == "zone-a"
    assert "centroid" in ans["where_is_risk"]

    # 2. HOW SEVERE
    assert "how_severe" in ans
    assert 0 <= ans["how_severe"]["score"] <= 100
    assert ans["how_severe"]["level"] in ("CRITICAL", "HIGH", "MODERATE", "LOW")

    # 3. WHY SEVERE
    assert "why_severe" in ans
    assert len(ans["why_severe"]["drivers"]) > 0
    assert abs(ans["why_severe"]["contribution_sum_pct"] - 100.0) < 0.1

    # 4. WHO EXPOSED
    assert "who_is_exposed" in ans
    assert ans["who_is_exposed"]["population"] > 0
    assert ans["who_is_exposed"]["population_density_per_km2"] > 0

    # 5. WHICH ASSETS
    assert "which_assets_affected" in ans
    assert ans["which_assets_affected"]["total_assets"] > 0

    # 6. HOW QUICKLY INCREASING
    assert "how_quickly_increasing" in ans
    assert "velocity_points_per_hour" in ans["how_quickly_increasing"]
    assert ans["how_quickly_increasing"]["trend_direction"] in ("RISING", "FALLING", "STABLE")

    # 7. WHAT IS LIKELY NEXT
    assert "what_is_likely_next" in ans
    assert ans["what_is_likely_next"]["forecast_horizon_hours"] == 12

    # 8. WHICH HAZARDS INTERACTING
    assert "which_hazards_interacting" in ans
    assert "compounding_detected" in ans["which_hazards_interacting"]

    # 9. HOW CONFIDENT
    assert "how_confident" in ans
    assert 30 <= ans["how_confident"]["confidence_pct"] <= 99

    # 10. WHAT IS MISSING
    assert "what_is_missing" in ans
    assert "degraded_sensor_nodes" in ans["what_is_missing"]


def test_api_recalculate_risk(client):
    """Verify POST /api/v1/risk/recalculate triggers full pipeline and returns summary."""
    response = client.post("/api/v1/risk/recalculate")
    assert response.status_code == 200
    data = response.json()

    assert data["zones_evaluated"] >= 3
    assert "zone_results" in data
    assert "cascade_summary" in data
    assert data["cascade_summary"]["nodes_updated"] > 0
    assert data["cascade_summary"]["edges_updated"] > 0


def test_api_hazard_matrix(client):
    """Verify GET /api/v1/risk/matrix returns multi-hazard comparison."""
    response = client.get("/api/v1/risk/matrix")
    assert response.status_code == 200
    data = response.json()

    assert "matrix" in data
    assert len(data["matrix"]) >= 3
    first = data["matrix"][0]
    assert "hazards" in first
    assert "flood" in first["hazards"]
    assert "heat" in first["hazards"]
    assert "drainage_stress" in first["hazards"]
