"""ClimateShield Phase 7: Constrained Climate Resilience Digital Twin Service.

Executes in-memory counterfactual what-if simulations of multi-hazard scenarios,
infrastructure disruptions, and emergency response packages.

CRITICAL ARCHITECTURAL CONSTRAINTS:
1. Reuses existing Phase 4 risk engines and Phase 5 optimization engines.
2. 100% In-Memory: MUST NOT mutate production database state (zero db.commit() calls).
3. Integrates ML PyTorch LSTM river forecast as advisory forward baseline where available.
4. Strictly employs approved operational terminology: 'MODELED IMPACT', 'ESTIMATED POPULATION PROTECTED', 'SIMULATED RISK REDUCTION', 'PROJECTED'.
"""

import uuid
import time
import math
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.models.zone import RiskZoneModel
from app.models.asset import AssetModel
from app.models.sensor import SensorNodeModel, SensorObservationModel
from app.models.river import RiverNodeModel
from app.models.risk import RiskScoreModel
from app.engine.flood_engine import FloodHazardEngine
from app.engine.heat_engine import HeatHazardEngine
from app.engine.secondary_hazard_engine import SecondaryHazardEngine
from app.engine.exposure_engine import ExposureEngine
from app.engine.vulnerability_engine import VulnerabilityEngine
from app.engine.confidence_engine import ConfidenceEngine
from app.engine.composite_risk_engine import CompositeRiskEngine
from app.engine.route_logistics import RouteLogisticsEngine
from app.ml.ml_service import MLService
from app.schemas.simulation import (
    SimulationRunRequest,
    SimulationRunResponse,
    MetricComparisonItem,
    InterventionRankingItem,
    AffectedZoneSummary,
    AffectedAssetSummary,
    CascadeSummaryItem,
    ScenarioDefinition,
    ScenarioListResponse,
    EnvironmentalModifiers,
    InfrastructureModifiers,
    ResponseModifiers,
    SensorConfidenceModifiers,
)


class DigitalTwinService:
    """Constrained Climate Resilience Digital Twin in-memory simulator."""

    # Ephemeral in-memory store for recent simulation runs
    _simulations_cache: Dict[str, SimulationRunResponse] = {}

    PREDEFINED_SCENARIOS: Dict[str, Dict[str, Any]] = {
        "river_rise_0_5m": {
            "name": "River Rise +0.5m",
            "category": "ENVIRONMENTAL_SURGE",
            "description": "Simulates an upstream hydrological crest resulting in a +0.50m river stage surge along the urban corridor.",
            "projected_headline": "Modeled river stage rise of +0.50m increases Zone A flood risk into high-critical threshold.",
            "parameters": {
                "environmental": {"river_level_delta_m": 0.50, "rainfall_intensity_pct": 10.0},
                "infrastructure": {"hospital_road_available": True},
                "response": {"pumps_deployed": 0, "barriers_deployed_units": 0},
            },
        },
        "rainfall_surge_30pct": {
            "name": "Heavy Rainfall +30%",
            "category": "METEOROLOGICAL_EXTREME",
            "description": "Simulates a cloudburst or convective storm intensifying precipitation rates by +30% across all catchment zones.",
            "projected_headline": "Convective rainfall intensification (+30%) elevates stormwater drainage stress citywide.",
            "parameters": {
                "environmental": {"rainfall_intensity_pct": 30.0, "soil_moisture_pct": 88.0},
                "infrastructure": {"hospital_road_available": True},
                "response": {"pumps_deployed": 0, "barriers_deployed_units": 0},
            },
        },
        "hospital_road_blocked": {
            "name": "Hospital Access Road Unavailable",
            "category": "INFRASTRUCTURE_DISRUPTION",
            "description": "Simulates severe waterlogging or structural failure cutting off the primary arterial route to the District Hospital.",
            "projected_headline": "Emergency response transit impedance increases +35 minutes with critical medical facility isolated.",
            "parameters": {
                "environmental": {"river_level_delta_m": 0.25},
                "infrastructure": {"hospital_road_available": False},
                "response": {"response_delay_minutes": 35},
            },
        },
        "deploy_2_pumps": {
            "name": "Deploy 2 Additional Pumps",
            "category": "TACTICAL_INTERVENTION",
            "description": "Simulates rapid tactical deployment of two 5000 GPM mobile dewatering pumps to the North Pump Station low-lying culvert.",
            "projected_headline": "Modeled deployment of 2 mobile pumps increases drainage evacuation capacity by +24%.",
            "parameters": {
                "environmental": {"river_level_delta_m": 0.20},
                "infrastructure": {"hospital_road_available": True, "pump_station_operational": True},
                "response": {"pumps_deployed": 2, "response_delay_minutes": 15},
            },
        },
        "deploy_barriers": {
            "name": "Deploy Flood Barriers",
            "category": "TACTICAL_INTERVENTION",
            "description": "Simulates rapid deployment of 500m modular inflatable flood barriers along the riverfront embankment.",
            "projected_headline": "Simulated flood barrier perimeter dampens overland flow, shielding adjacent residential and commercial assets.",
            "parameters": {
                "environmental": {"river_level_delta_m": 0.35},
                "infrastructure": {"barrier_deployed_km": 0.5},
                "response": {"barriers_deployed_units": 4, "response_delay_minutes": 20},
            },
        },
        "sensor_outage": {
            "name": "Sensor Outage (Midstream RN-01)",
            "category": "TELEMETRY_FAILURE",
            "description": "Simulates complete loss of telemetry packets from Midstream Gauge RN-01 due to hardware battery exhaustion or signal fade.",
            "projected_headline": "Telemetry outage at Midstream RN-01 triggers confidence penalty (-25%) and engages heuristic fallback.",
            "parameters": {
                "sensor_confidence": {"sensor_status_overrides": {"sensor-river-01": "OFFLINE", "RN-01": "OFFLINE"}},
            },
        },
        "do_nothing": {
            "name": "Do Nothing (Status Quo)",
            "category": "BASELINE_PROJECTION",
            "description": "Projects unmitigated climate hazard evolution over the 3-hour horizon without tactical resource deployment.",
            "projected_headline": "Unmitigated baseline state demonstrates cascading vulnerability under persistent environmental load.",
            "parameters": {
                "environmental": {"river_level_delta_m": 0.0},
                "response": {"pumps_deployed": 0, "barriers_deployed_units": 0},
            },
        },
    }

    def __init__(self, db: Session):
        self.db = db

    def get_predefined_scenarios(self) -> ScenarioListResponse:
        """Returns catalogue of one-click pre-configured simulation scenarios."""
        scenario_defs = []
        for sid, sdata in self.PREDEFINED_SCENARIOS.items():
            scenario_defs.append(
                ScenarioDefinition(
                    scenario_id=sid,
                    name=sdata["name"],
                    category=sdata["category"],
                    description=sdata["description"],
                    parameters=sdata["parameters"],
                    projected_headline=sdata["projected_headline"],
                )
            )
        return ScenarioListResponse(
            scenarios=scenario_defs,
            count=len(scenario_defs),
            governance_note="Predefined digital twin scenarios for operational preparedness and stress-testing.",
        )

    def get_simulation_by_id(self, simulation_id: str) -> Optional[SimulationRunResponse]:
        """Retrieves a previously run simulation from ephemeral memory cache."""
        return self._simulations_cache.get(simulation_id)

    def run_simulation(self, request: SimulationRunRequest) -> SimulationRunResponse:
        """Executes full digital twin simulation in memory with ZERO database mutations."""
        start_time = time.perf_counter()
        now = datetime.now(timezone.utc)
        sim_id = f"SIM-{uuid.uuid4().hex[:8].upper()}"

        # 1. BASELINE EXTRACTION (Read-only query, no transaction commit)
        zones = self.db.query(RiskZoneModel).all()
        assets = self.db.query(AssetModel).all()
        sensors = self.db.query(SensorNodeModel).all()
        river_nodes = self.db.query(RiverNodeModel).all()
        recent_scores = (
            self.db.query(RiskScoreModel)
            .order_by(RiskScoreModel.observed_at.desc())
            .limit(len(zones) or 3)
            .all()
        )

        # Baseline city risk
        baseline_city_risk = (
            int(round(sum(s.value for s in recent_scores) / len(recent_scores)))
            if recent_scores
            else 68
        )

        # 2. CHECK ML LSTM FORECAST SIGNAL
        ml_integrated = False
        ml_advisory_note = "ML unavailable — deterministic fallback active."
        ml_predicted_delta = 0.0
        try:
            ml_forecast = MLService.get_river_forecast(db=self.db, river_node_id="RN-01")
            if ml_forecast.forecast_available and ml_forecast.predicted_river_level_m is not None:
                ml_integrated = True
                curr_l = ml_forecast.current_river_level_m or 2.84
                pred_l = ml_forecast.predicted_river_level_m
                ml_predicted_delta = round(pred_l - curr_l, 2)
                ml_advisory_note = (
                    f"ML advisory forecast integrated: projected river stage at +3h is {pred_l:.2f}m "
                    f"({'+' if ml_predicted_delta >= 0 else ''}{ml_predicted_delta:.2f}m change). "
                    "Deterministic risk engine remains authoritative."
                )
        except Exception as e:
            logger.warning(f"[DIGITAL_TWIN] ML forecast lookup error: {e}")

        # 3. EXTRACT HYPOTHETICAL MODIFIERS
        env = request.environmental or EnvironmentalModifiers()
        infra = request.infrastructure or InfrastructureModifiers()
        resp = request.response or ResponseModifiers()
        sens = request.sensor_confidence or SensorConfidenceModifiers()

        # Environmental adjustments
        river_delta = float(env.river_level_delta_m or 0.0)
        # If ML is available and scenario is baseline/do_nothing, incorporate ML projected delta
        if ml_integrated and request.scenario_id == "do_nothing":
            river_delta += ml_predicted_delta

        rain_pct = float(env.rainfall_intensity_pct or 0.0)
        explicit_rain = env.rainfall_intensity_mm_h

        # Infrastructure adjustments
        hospital_open = infra.hospital_road_available if infra.hospital_road_available is not None else True
        pump_operational = infra.pump_station_operational if infra.pump_station_operational is not None else True
        substation_operational = infra.substation_operational if infra.substation_operational is not None else True
        barrier_km = float(infra.barrier_deployed_km or 0.0)

        # Response adjustments
        pumps_added = int(resp.pumps_deployed or 0)
        barriers_added = int(resp.barriers_deployed_units or 0)
        resp_delay = int(resp.response_delay_minutes or 0)

        # 4. IN-MEMORY ZONE HAZARD & RISK EVALUATION
        zone_summaries: List[AffectedZoneSummary] = []
        total_pop_exposed = 0
        total_baseline_pop_exposed = 0
        simulated_zone_risks = []
        baseline_zone_risks = []

        for zone in zones:
            # Baseline parameters per zone
            is_zone_a = "ZONE-A" in zone.code.upper() or "MVP" in zone.name.upper()
            is_zone_b = "ZONE-B" in zone.code.upper() or "GAJUWAKA" in zone.name.upper()
            is_zone_c = "ZONE-C" in zone.code.upper() or "ONE TOWN" in zone.name.upper()

            # Baseline water level
            base_water = 4.12 if is_zone_a else (2.10 if is_zone_b else 1.80)
            threshold_m = 3.5 if is_zone_a else (4.0 if is_zone_b else 2.5)
            base_rain = 15.0 if is_zone_a else (10.0 if is_zone_b else 5.0)
            base_temp = 32.5
            base_humidity = 76.0
            base_elevation = 8.0 if is_zone_a else (14.0 if is_zone_b else 4.5)
            base_impervious = 55.0 if is_zone_a else (70.0 if is_zone_b else 85.0)
            base_pump_cap = 88.0 if is_zone_a else (62.0 if is_zone_b else 74.0)

            # Simulated water level & rain
            sim_water = max(0.1, base_water + river_delta)
            sim_rain = explicit_rain if explicit_rain is not None else base_rain * (1.0 + (rain_pct / 100.0))
            sim_temp = env.temperature_c if env.temperature_c is not None else base_temp
            sim_humidity = env.humidity_pct if env.humidity_pct is not None else base_humidity

            # Drainage capacity modification
            sim_pump_cap = base_pump_cap
            if not pump_operational:
                sim_pump_cap *= 0.35  # Major drainage failure
            if not substation_operational:
                sim_pump_cap *= 0.50  # Power outage drops capacity
            sim_pump_cap += pumps_added * 12.0  # Tactical pumps increase capacity
            sim_pump_cap = min(100.0, max(10.0, sim_pump_cap))

            # Barrier intervention damping effect on flood hazard
            barrier_effective_units = barriers_added + int(round(barrier_km * 4.0))
            barrier_flood_reduction = min(35.0, barrier_effective_units * 7.5)

            # Baseline Hazard Calculations
            b_flood = FloodHazardEngine.calculate(
                water_level_m=base_water,
                threshold_m=threshold_m,
                rate_of_rise_m_h=0.20 if is_zone_a else 0.05,
                rainfall_intensity_mm_h=base_rain,
                upstream_water_ratio=1.10 if is_zone_a else None,
                elevation_m=base_elevation,
            )
            b_heat = HeatHazardEngine.calculate(base_temp, base_humidity, base_impervious)
            b_drain = SecondaryHazardEngine.calculate_drainage_stress(base_pump_cap, 72.0)
            b_surge = SecondaryHazardEngine.calculate_coastal_surge(1.3 if is_zone_c else 0.6)
            b_air = SecondaryHazardEngine.calculate_air_quality(68.0)

            exp_dict = {"exposure_index": 0.72 if is_zone_a else (0.65 if is_zone_b else 0.58)}
            vuln_dict = {"vulnerability_index": 0.68 if is_zone_a else (0.75 if is_zone_b else 0.82)}

            b_composite = CompositeRiskEngine.calculate(
                dominant_hazard=zone.dominant_hazard,
                flood_hazard=b_flood,
                heat_hazard=b_heat,
                drainage_hazard=b_drain,
                surge_hazard=b_surge,
                air_hazard=b_air,
                exposure=exp_dict,
                vulnerability=vuln_dict,
            )
            b_risk = b_composite["score"]
            baseline_zone_risks.append(b_risk)

            # Simulated Hazard Calculations
            s_flood = FloodHazardEngine.calculate(
                water_level_m=sim_water,
                threshold_m=threshold_m,
                rate_of_rise_m_h=max(0.0, (0.20 + (river_delta * 0.35)) * (1.0 if hospital_open else 1.15)),
                rainfall_intensity_mm_h=sim_rain,
                upstream_water_ratio=(1.10 + (river_delta * 0.2)) if is_zone_a else None,
                elevation_m=base_elevation,
            )

            # Apply barrier direct reduction to flood score
            sim_flood_score = max(10, int(round(s_flood["score"] - barrier_flood_reduction)))
            sim_flood_hazard = dict(s_flood)
            sim_flood_hazard["score"] = sim_flood_score

            s_heat = HeatHazardEngine.calculate(sim_temp, sim_humidity, base_impervious)
            s_drain = SecondaryHazardEngine.calculate_drainage_stress(sim_pump_cap, 72.0 + (rain_pct * 0.2))
            s_surge = SecondaryHazardEngine.calculate_coastal_surge(1.3 if is_zone_c else 0.6)
            s_air = SecondaryHazardEngine.calculate_air_quality(68.0)

            # Check sensor confidence overrides
            confidence_penalty = 0
            for s_id, s_stat in sens.sensor_status_overrides.items():
                if s_stat.upper() == "OFFLINE":
                    confidence_penalty += 25
                elif s_stat.upper() == "DEGRADED":
                    confidence_penalty += 10
            confidence_penalty = min(40, confidence_penalty)

            # Response delay penalty
            delay_penalty = min(15, int(round(resp_delay * 0.35)))

            s_composite = CompositeRiskEngine.calculate(
                dominant_hazard=zone.dominant_hazard,
                flood_hazard=sim_flood_hazard,
                heat_hazard=s_heat,
                drainage_hazard=s_drain,
                surge_hazard=s_surge,
                air_hazard=s_air,
                exposure=exp_dict,
                vulnerability=vuln_dict,
            )
            s_risk = max(15, min(99, s_composite["score"] + delay_penalty - int(round(confidence_penalty * 0.2))))
            simulated_zone_risks.append(s_risk)

            r_delta = s_risk - b_risk
            zone_pop = getattr(zone, "population", 50000) or 50000
            sim_factor = max(0.10, (s_risk / 100.0) * 0.45)
            base_factor = max(0.10, (b_risk / 100.0) * 0.45)
            total_pop_exposed += int(zone_pop * sim_factor)
            total_baseline_pop_exposed += int(zone_pop * base_factor)

            zone_summaries.append(
                AffectedZoneSummary(
                    zone_id=zone.id,
                    name=zone.name,
                    baseline_risk=b_risk,
                    simulated_risk=s_risk,
                    risk_delta=r_delta,
                    dominant_hazard=zone.dominant_hazard,
                    status="CRITICAL" if s_risk >= 80 else ("HIGH" if s_risk >= 65 else ("ELEVATED" if s_risk >= 50 else "MODERATE")),
                    population=zone.population,
                    elevation_m=base_elevation,
                )
            )

        sim_city_risk = int(round(sum(simulated_zone_risks) / len(simulated_zone_risks))) if simulated_zone_risks else baseline_city_risk
        city_delta = sim_city_risk - baseline_city_risk
        city_delta_pct = round(((sim_city_risk - baseline_city_risk) / max(1.0, float(baseline_city_risk))) * 100.0, 1)

        # 5. ASSET IMPACT AUDIT (In-memory)
        asset_summaries: List[AffectedAssetSummary] = []
        critical_assets_exposed = 0
        infra_impacts = []

        for asset in assets:
            a_zone_match = next((zs for zs in zone_summaries if zs.zone_id == asset.zone_id), None)
            zone_r = a_zone_match.simulated_risk if a_zone_match else sim_city_risk

            sim_status = asset.status
            impact_desc = "Nominal operation under monitored baseline"

            # Check road closure scenario
            if not hospital_open and ("HOSPITAL" in asset.name.upper() or "HEALTH" in asset.asset_type.upper()):
                sim_status = "ISOLATED_AT_RISK"
                impact_desc = "MODELED IMPACT: Primary access arterial impassable; emergency ambulance transit impeded."
                critical_assets_exposed += 1
                infra_impacts.append("District Hospital primary arterial access severed (+35m transit detour)")
            elif not substation_operational and ("SUBSTATION" in asset.name.upper() or "POWER" in asset.asset_type.upper()):
                sim_status = "OUTAGE_TRIPPED"
                impact_desc = "MODELED IMPACT: Electrical substation de-energized; emergency feeder transfer required."
                critical_assets_exposed += 1
                infra_impacts.append("220kV Substation tripped; municipal pumps operating on emergency battery standby")
            elif not pump_operational and ("PUMP" in asset.name.upper() or "WATER" in asset.asset_type.upper()):
                sim_status = "OVERFLOW_WARNING"
                impact_desc = "MODELED IMPACT: Mechanical pump station impaired; overland backflow accumulating."
                critical_assets_exposed += 1
                infra_impacts.append("Municipal pump station capacity constrained; drainage backpressure rising")
            elif zone_r >= 75 and asset.criticality == "TIER_1":
                sim_status = "THREATENED"
                impact_desc = "MODELED IMPACT: High water stage encroaching perimeter defense."
                critical_assets_exposed += 1
            elif zone_r >= 65:
                sim_status = "ELEVATED_WATCH"
                impact_desc = "MODELED IMPACT: Pre-deployment watch in effect."

            asset_summaries.append(
                AffectedAssetSummary(
                    asset_id=asset.id,
                    name=asset.name,
                    asset_type=asset.asset_type,
                    criticality=asset.criticality,
                    status=sim_status,
                    zone_id=asset.zone_id,
                    simulated_impact=impact_desc,
                )
            )

        # 6. CASCADE NETWORK PROPAGATION (In-memory)
        cascade_items: List[CascadeSummaryItem] = []
        cascade_nodes = [
            ("node-inflow", "River Inflow Choke", "CRITICAL" if sim_city_risk >= 75 else ("HIGH" if sim_city_risk >= 60 else "MODERATE")),
            ("node-pump", "North Drainage Pump Station", "CRITICAL" if not pump_operational or sim_city_risk >= 75 else ("HIGH" if sim_city_risk >= 65 else "MODERATE")),
            ("node-substation", "220kV Power Substation", "HIGH" if not substation_operational or sim_city_risk >= 75 else ("ELEVATED" if sim_city_risk >= 65 else "MODERATE")),
            ("node-road", "Beach Road Access Arterial", "CRITICAL" if not hospital_open else ("HIGH" if sim_city_risk >= 75 else "ELEVATED")),
            ("node-hospital", "District General Hospital", "CRITICAL" if not hospital_open else ("HIGH" if sim_city_risk >= 80 else "MODERATE")),
        ]

        for nid, nname, srisk in cascade_nodes:
            cascade_items.append(
                CascadeSummaryItem(
                    node_id=nid,
                    name=nname,
                    baseline_risk="HIGH" if baseline_city_risk >= 70 else "MODERATE",
                    simulated_risk=srisk,
                    propagation_state="ACTIVE_CASCADE_CHAIN" if srisk in ("CRITICAL", "HIGH") else "STABLE_CONTAINED",
                )
            )

        # 7. MULTI-CRITERIA INTERVENTION RANKING (5 standard packages)
        interventions_catalog = [
            {
                "id": "INT-01-PUMP",
                "name": "Pre-stage 2x 5000 GPM Dewatering Pumps",
                "category": "PUMP",
                "reduction_pts": min(28, 14 + (pumps_added * 7) + (8 if sim_city_risk >= 70 else 4)),
                "pop_protected": int(round(total_pop_exposed * 0.42)),
                "assets_safeguarded": 2,
                "cost": 8500,
                "eta": 20,
                "cascade_interruption": 0.82,
                "desc": "Pre-positions high-capacity diesel pumps at Sector 4 culvert, mitigating stormwater buildup prior to river peak.",
            },
            {
                "id": "INT-02-BARRIER",
                "name": "Rapid Deployment of 500m Modular Flood Barriers",
                "category": "BARRIER",
                "reduction_pts": min(32, 16 + (barriers_added * 5) + (10 if river_delta > 0.3 else 6)),
                "pop_protected": int(round(total_pop_exposed * 0.48)),
                "assets_safeguarded": 3,
                "cost": 12000,
                "eta": 35,
                "cascade_interruption": 0.88,
                "desc": "Deploys inflatable rubber flood defenses along riverbank promenade to prevent overland street flooding.",
            },
            {
                "id": "INT-03-RESCUE",
                "name": "Pre-position 3x NDRF Swift-Water Rescue Teams",
                "category": "RESCUE",
                "reduction_pts": 15,
                "pop_protected": int(round(total_pop_exposed * 0.35)),
                "assets_safeguarded": 1,
                "cost": 5000,
                "eta": 15,
                "cascade_interruption": 0.65,
                "desc": "Stages specialized emergency inflatable boats and medical first-responders at Dolphin's Nose staging depot.",
            },
            {
                "id": "INT-04-REROUTE",
                "name": "Emergency Arterial Rerouting & High-Ground Corridor",
                "category": "REROUTING",
                "reduction_pts": 18 if not hospital_open else 10,
                "pop_protected": int(round(total_pop_exposed * 0.28)),
                "assets_safeguarded": 2 if not hospital_open else 1,
                "cost": 3200,
                "eta": 10,
                "cascade_interruption": 0.75,
                "desc": "Establishes police-escorted bypass corridor via NH-16 high-ground overpass ensuring uninterrupted hospital transit.",
            },
            {
                "id": "INT-05-POWER",
                "name": "Auxiliary Mobile Diesel Generator to 220kV Substation",
                "category": "POWER",
                "reduction_pts": 20 if not substation_operational else 12,
                "pop_protected": int(round(total_pop_exposed * 0.30)),
                "assets_safeguarded": 2,
                "cost": 6500,
                "eta": 25,
                "cascade_interruption": 0.78,
                "desc": "Dispatches self-contained 1.2 MW mobile generator to safeguard industrial drainage grid if primary feeder trips.",
            },
        ]

        # Multi-attribute utility score computation
        # Weighting: Reduction (35%), Pop (25%), Assets (20%), Cascade (10%), ETA/Cost (-10%)
        ranking_items: List[InterventionRankingItem] = []
        for raw_int in interventions_catalog:
            norm_red = raw_int["reduction_pts"] / 35.0
            norm_pop = raw_int["pop_protected"] / max(1.0, float(total_pop_exposed or 10000))
            norm_assets = raw_int["assets_safeguarded"] / 3.0
            norm_cascade = raw_int["cascade_interruption"]
            norm_time = 1.0 - (raw_int["eta"] / 60.0)

            utility_score = round(
                (0.35 * norm_red)
                + (0.25 * norm_pop)
                + (0.20 * norm_assets)
                + (0.10 * norm_cascade)
                + (0.10 * norm_time),
                3,
            )

            ranking_items.append(
                InterventionRankingItem(
                    rank=1,  # re-assigned after sort
                    intervention_id=raw_int["id"],
                    name=raw_int["name"],
                    category=raw_int["category"],
                    modeled_risk_reduction_points=raw_int["reduction_pts"],
                    estimated_population_protected=raw_int["pop_protected"],
                    critical_assets_safeguarded=raw_int["assets_safeguarded"],
                    estimated_cost_usd=raw_int["cost"],
                    response_eta_minutes=raw_int["eta"],
                    cascade_interruption_factor=raw_int["cascade_interruption"],
                    multi_attribute_utility_score=utility_score,
                    is_best_modeled_option=False,
                    description=raw_int["desc"],
                )
            )

        ranking_items.sort(key=lambda x: x.multi_attribute_utility_score, reverse=True)
        for idx, item in enumerate(ranking_items):
            item.rank = idx + 1
        if ranking_items:
            ranking_items[0].is_best_modeled_option = True

        best_opt = ranking_items[0] if ranking_items else None
        best_modeled_title = best_opt.name if best_opt else "Pre-stage 2x 5000 GPM Dewatering Pumps"
        est_pop_protected = best_opt.estimated_population_protected if best_opt else 28000
        assets_safeguarded = best_opt.critical_assets_safeguarded if best_opt else 2
        effective_reduction = best_opt.modeled_risk_reduction_points if best_opt else 18
        simulated_residual_risk = max(18, sim_city_risk - effective_reduction)

        # 8. METRICS COMPARISON
        metrics_comp: List[MetricComparisonItem] = [
            MetricComparisonItem(
                metric_name="Overall City Composite Risk",
                unit="Score [0-100]",
                baseline=float(baseline_city_risk),
                simulated=float(sim_city_risk),
                absolute_delta=float(city_delta),
                percentage_delta=city_delta_pct,
                interpretation=f"MODELED IMPACT: Risk {'elevates' if city_delta >= 0 else 'mitigated'} by {abs(city_delta)} points ({abs(city_delta_pct):.1f}%).",
            ),
            MetricComparisonItem(
                metric_name="Peak River Stage",
                unit="meters (m)",
                baseline=4.12,
                simulated=round(4.12 + river_delta, 2),
                absolute_delta=round(river_delta, 2),
                percentage_delta=round((river_delta / 4.12) * 100.0, 1),
                interpretation=f"PROJECTED: Midstream water level {'rises' if river_delta >= 0 else 'recedes'} by {abs(river_delta):.2f}m.",
            ),
            MetricComparisonItem(
                metric_name="Precipitation Intensity",
                unit="mm/h",
                baseline=15.0,
                simulated=round(15.0 * (1.0 + (rain_pct / 100.0)), 1),
                absolute_delta=round(15.0 * (rain_pct / 100.0), 1),
                percentage_delta=rain_pct,
                interpretation=f"MODELED IMPACT: Storm runoff stress modifies by {rain_pct:+.1f}%.",
            ),
            MetricComparisonItem(
                metric_name="Estimated Population Exposed",
                unit="Residents",
                baseline=float(total_baseline_pop_exposed or 18000),
                simulated=float(total_pop_exposed or 24000),
                absolute_delta=float(total_pop_exposed - total_baseline_pop_exposed),
                percentage_delta=round(((total_pop_exposed - total_baseline_pop_exposed) / max(1.0, float(total_baseline_pop_exposed))) * 100.0, 1),
                interpretation="ESTIMATED POPULATION PROTECTED potential across high-risk zones.",
            ),
            MetricComparisonItem(
                metric_name="Critical Assets Threatened",
                unit="Infrastructure Nodes",
                baseline=2.0,
                simulated=float(critical_assets_exposed),
                absolute_delta=float(critical_assets_exposed - 2),
                percentage_delta=None,
                interpretation=f"MODELED IMPACT: {critical_assets_exposed} assets in threatened hazard envelopes.",
            ),
            MetricComparisonItem(
                metric_name="Modeled Residual Risk (Post-Intervention)",
                unit="Score [0-100]",
                baseline=float(sim_city_risk),
                simulated=float(simulated_residual_risk),
                absolute_delta=float(simulated_residual_risk - sim_city_risk),
                percentage_delta=round(((simulated_residual_risk - sim_city_risk) / max(1.0, float(sim_city_risk))) * 100.0, 1),
                interpretation=f"SIMULATED RISK REDUCTION: Applying '{best_modeled_title}' reduces composite risk to {simulated_residual_risk}.",
            ),
        ]

        # 9. ASSUMPTIONS & OPERATIONAL WARNINGS
        assumptions = [
            "Simulation is evaluated entirely in-memory and does not mutate active production database records.",
            "Hydrological flood stage uses Saint-Venant 1D routing approximation with threshold overflow rules.",
            "Runoff rates assume uniform catchment infiltration until soil saturation threshold is crossed.",
            "Resource dispatch calculations assume unimpeded secondary corridors unless specifically designated closed.",
        ]

        warnings = []
        if not hospital_open:
            warnings.append("CRITICAL: Primary access corridor to District Hospital severed. Emergency detour required.")
        if not substation_operational:
            warnings.append("WARNING: 220kV Substation de-energized. Municipal pump redundancy compromised.")
        if river_delta >= 0.50:
            warnings.append("WARNING: Modeled river stage exceeds flood wall containment threshold (4.5m) in Sector 4.")
        if sens.sensor_status_overrides:
            warnings.append("ADVISORY: Telemetry degradation overrides active. Operational confidence penalized.")

        # Formulation of impact statement
        headline = (
            f"MODELED IMPACT: Under scenario '{request.name or request.scenario_id}', "
            f"simulated composite risk shifts to {sim_city_risk} ({city_delta_pct:+.1f}% vs baseline). "
            f"Implementing '{best_modeled_title}' yields an estimated SIMULATED RISK REDUCTION of {effective_reduction} points, "
            f"safeguarding an estimated {est_pop_protected:,} residents."
        )

        response = SimulationRunResponse(
            simulation_id=sim_id,
            scenario_id=request.scenario_id or "custom",
            scenario_name=request.name or "Custom What-If Run",
            timestamp=now.isoformat(),
            execution_latency_ms=round((time.perf_counter() - start_time) * 1000.0, 2),
            ml_forecast_integrated=ml_integrated,
            ml_advisory_note=ml_advisory_note,
            baseline_overall_risk=baseline_city_risk,
            simulated_overall_risk=sim_city_risk,
            modeled_risk_delta=city_delta,
            modeled_risk_delta_pct=city_delta_pct,
            simulated_residual_risk=simulated_residual_risk,
            response_priority="P1_IMMEDIATE" if sim_city_risk >= 70 else ("P2_ELEVATED" if sim_city_risk >= 55 else "P3_ROUTINE"),
            best_modeled_option=best_modeled_title,
            estimated_population_protected=est_pop_protected,
            critical_assets_safeguarded=assets_safeguarded,
            metrics_comparison=metrics_comp,
            affected_zones=zone_summaries,
            affected_assets=asset_summaries,
            cascade_changes=cascade_items,
            intervention_ranking=ranking_items,
            modeled_impact_statement=headline,
            assumptions=assumptions,
            warnings=warnings,
            data_quality="SIMULATION_HYPOTHETICAL",
            deterministic_safety_note="ML advisory — deterministic risk engine remains authoritative. In-memory simulation with zero database mutation.",
        )

        # Store in ephemeral memory cache for GET by ID
        self._simulations_cache[sim_id] = response
        if len(self._simulations_cache) > 100:
            # Pop oldest entry
            oldest_k = next(iter(self._simulations_cache))
            self._simulations_cache.pop(oldest_k, None)

        return response

    def run_predefined_scenario(self, scenario_name: str) -> SimulationRunResponse:
        """Runs a predefined one-click scenario by name."""
        scenario_key = scenario_name.lower().strip()
        if scenario_key not in self.PREDEFINED_SCENARIOS:
            raise KeyError(f"Unknown predefined scenario: '{scenario_name}'. Available: {list(self.PREDEFINED_SCENARIOS.keys())}")

        sdata = self.PREDEFINED_SCENARIOS[scenario_key]
        params = sdata.get("parameters", {})

        env_params = params.get("environmental", {})
        infra_params = params.get("infrastructure", {})
        resp_params = params.get("response", {})
        sens_params = params.get("sensor_confidence", {})

        req = SimulationRunRequest(
            scenario_id=scenario_key,
            name=sdata["name"],
            environmental=EnvironmentalModifiers(**env_params),
            infrastructure=InfrastructureModifiers(**infra_params),
            response=ResponseModifiers(**resp_params),
            sensor_confidence=SensorConfidenceModifiers(**sens_params),
        )

        return self.run_simulation(req)
