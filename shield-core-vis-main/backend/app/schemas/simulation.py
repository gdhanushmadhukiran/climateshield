"""Pydantic schemas for ClimateShield Phase 7: Constrained Climate Resilience Digital Twin."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class EnvironmentalModifiers(BaseModel):
    river_level_delta_m: Optional[float] = Field(0.0, description="Hypothetical river level delta in meters (e.g. +0.5)")
    rainfall_intensity_pct: Optional[float] = Field(0.0, description="Hypothetical rainfall intensity change in percent (e.g. +30.0)")
    rainfall_intensity_mm_h: Optional[float] = Field(None, description="Explicit rainfall intensity in mm/h")
    temperature_c: Optional[float] = Field(None, description="Hypothetical ambient temperature in °C")
    humidity_pct: Optional[float] = Field(None, description="Hypothetical relative humidity in %")
    soil_moisture_pct: Optional[float] = Field(None, description="Hypothetical soil saturation in %")


class InfrastructureModifiers(BaseModel):
    hospital_road_available: Optional[bool] = Field(True, description="Whether primary arterial route to hospital is open")
    pump_station_operational: Optional[bool] = Field(True, description="Whether municipal drainage pump station is active")
    substation_operational: Optional[bool] = Field(True, description="Whether 220kV power substation is energized")
    barrier_deployed_km: Optional[float] = Field(0.0, description="Length of temporary flood barriers deployed in km")
    critical_asset_status_overrides: Optional[Dict[str, str]] = Field(default_factory=dict, description="Asset ID -> Status overrides")


class ResponseModifiers(BaseModel):
    pumps_deployed: Optional[int] = Field(0, description="Number of additional mobile high-capacity pumps deployed")
    rescue_teams_deployed: Optional[int] = Field(0, description="Number of water rescue teams pre-positioned")
    barriers_deployed_units: Optional[int] = Field(0, description="Number of modular barrier units deployed")
    response_delay_minutes: Optional[int] = Field(0, description="Simulated response mobilization delay in minutes")


class SensorConfidenceModifiers(BaseModel):
    sensor_status_overrides: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Sensor ID or code -> Status ('HEALTHY', 'DEGRADED', 'OFFLINE')",
    )


class SimulationRunRequest(BaseModel):
    scenario_id: Optional[str] = Field("custom", description="Identifier of scenario or 'custom'")
    name: Optional[str] = Field("Custom Digital Twin Simulation", description="Human-readable simulation title")
    environmental: Optional[EnvironmentalModifiers] = Field(default_factory=EnvironmentalModifiers)
    infrastructure: Optional[InfrastructureModifiers] = Field(default_factory=InfrastructureModifiers)
    response: Optional[ResponseModifiers] = Field(default_factory=ResponseModifiers)
    sensor_confidence: Optional[SensorConfidenceModifiers] = Field(default_factory=SensorConfidenceModifiers)


class MetricComparisonItem(BaseModel):
    metric_name: str
    unit: str
    baseline: float
    simulated: float
    absolute_delta: float
    percentage_delta: Optional[float] = None
    interpretation: str


class InterventionRankingItem(BaseModel):
    rank: int
    intervention_id: str
    name: str
    category: str = Field(..., description="PUMP, BARRIER, RESCUE, REROUTING, POWER")
    modeled_risk_reduction_points: int
    estimated_population_protected: int
    critical_assets_safeguarded: int
    estimated_cost_usd: int
    response_eta_minutes: int
    cascade_interruption_factor: float
    multi_attribute_utility_score: float
    is_best_modeled_option: bool = False
    description: str


class AffectedZoneSummary(BaseModel):
    zone_id: str
    name: str
    baseline_risk: int
    simulated_risk: int
    risk_delta: int
    dominant_hazard: str
    status: str
    population: int
    elevation_m: float


class AffectedAssetSummary(BaseModel):
    asset_id: str
    name: str
    asset_type: str
    criticality: str
    status: str
    zone_id: str
    simulated_impact: str


class CascadeSummaryItem(BaseModel):
    node_id: str
    name: str
    baseline_risk: str
    simulated_risk: str
    propagation_state: str


class SimulationRunResponse(BaseModel):
    simulation_id: str
    scenario_id: str
    scenario_name: str
    timestamp: str
    execution_latency_ms: float
    ml_forecast_integrated: bool
    ml_advisory_note: str

    baseline_overall_risk: int
    simulated_overall_risk: int
    modeled_risk_delta: int
    modeled_risk_delta_pct: float
    simulated_residual_risk: int

    response_priority: str
    best_modeled_option: str
    estimated_population_protected: int
    critical_assets_safeguarded: int

    metrics_comparison: List[MetricComparisonItem]
    affected_zones: List[AffectedZoneSummary]
    affected_assets: List[AffectedAssetSummary]
    cascade_changes: List[CascadeSummaryItem]
    intervention_ranking: List[InterventionRankingItem]

    modeled_impact_statement: str
    assumptions: List[str]
    warnings: List[str]
    data_quality: str
    deterministic_safety_note: str = Field(
        "ML advisory — deterministic risk engine remains authoritative. In-memory simulation with zero database mutation.",
        description="Core operational governance declaration",
    )


class ScenarioDefinition(BaseModel):
    scenario_id: str
    name: str
    category: str
    description: str
    parameters: Dict[str, Any]
    projected_headline: str


class ScenarioListResponse(BaseModel):
    scenarios: List[ScenarioDefinition]
    count: int
    governance_note: str
