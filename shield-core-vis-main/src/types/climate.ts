/**
 * ClimateShield typed frontend contracts.
 * These describe the shape of data the platform will consume from the
 * risk engine / API layer. UI components depend on these types only.
 */

export type RiskLevel = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
export type Severity = "INFO" | "ADVISORY" | "WARNING" | "EMERGENCY";
export type ConfidenceLevel = "HIGH" | "MEDIUM" | "LOW";
export type DataQuality = "FRESH" | "AGING" | "STALE" | "DEGRADED" | "UNAVAILABLE";
export type OperationalMode = "LIVE" | "DEMO" | "DEGRADED";
export type HazardType = "FLOOD" | "EXTREME_RAINFALL" | "HEAT" | "DRAINAGE_STRESS" | "WATERLOGGING";
export type ServiceStatus = "HEALTHY" | "ACTIVE" | "DEGRADED" | "OFFLINE";

export interface Coordinates {
  lat: number;
  lng: number;
}

/** Normalised 0-100 score with the metadata every risk object must carry. */
export interface RiskScore {
  /** 0-100 */
  value: number;
  level: RiskLevel;
  /** 0-100 model confidence */
  confidence: number;
  /** points per hour, signed */
  velocityPerHour: number;
  /** ISO timestamp of the observation the score is based on */
  observedAt: string;
  quality: DataQuality;
}

export interface RiskDriver {
  id: string;
  label: string;
  /** relative contribution 0-100 */
  contribution: number;
  value: string;
  metricValue?: number;
  unit?: string;
  trend: "RISING" | "FALLING" | "STABLE";
}

export interface RiskZone {
  id: string;
  name: string;
  code: string;
  population: number;
  areaKm2: number;
  dominantHazard: HazardType;
  risk: RiskScore;
  drivers: RiskDriver[];
  centroid: Coordinates;
  /** GeoJSON polygon ring in [lng, lat] pairs */
  polygon: [number, number][];
}

export interface ForecastPoint {
  timestamp: string;
  /** predicted risk score */
  value: number;
  /** prediction interval */
  lower: number;
  upper: number;
  confidence: number;
}

export interface Forecast {
  id: string;
  zoneId: string;
  hazard: HazardType;
  horizonHours: number;
  issuedAt: string;
  model: string;
  points: ForecastPoint[];
}

export interface CascadeNode {
  id: string;
  label: string;
  kind: "HAZARD" | "SYSTEM" | "ASSET" | "SERVICE" | "POPULATION";
  risk: RiskLevel;
}

export interface CascadeEdge {
  id?: string;
  from: string;
  to: string;
  /** 0-100 propagation likelihood */
  likelihood: number;
  lagMinutes: number;
}

export type AssetCategory =
  "HOSPITAL" | "EMERGENCY" | "BRIDGE" | "WATER" | "POWER" | "SCHOOL" | "ROAD";

export interface Asset {
  id: string;
  name: string;
  category: AssetCategory;
  zoneId: string;
  criticality: "TIER_1" | "TIER_2" | "TIER_3";
  location: Coordinates;
  exposure: RiskLevel;
  servesPopulation: number;
  status: "OPERATIONAL" | "AT_RISK" | "IMPAIRED";
}

export interface Incident {
  id: string;
  ref: string;
  title: string;
  hazard: HazardType;
  zoneId: string;
  severity: Severity;
  reportedAt: string;
  status: "OPEN" | "ACKNOWLEDGED" | "IN_RESPONSE" | "RESOLVED";
  location: Coordinates;
  affectedPopulation: number;
  source: "SENSOR" | "OPERATOR" | "MODEL" | "PUBLIC_REPORT";
}

export interface Recommendation {
  id: string;
  action: string;
  rationale: string;
  zoneId?: string;
  assetId?: string;
  priority: "P1" | "P2" | "P3";
  expectedRiskReduction: number;
  etaMinutes: number;
  resources: string[];
  confidence: number;
}

export interface SimulationScenario {
  id: string;
  name: string;
  hazard: HazardType;
  parameters: Record<string, number | string>;
}

export interface SimulationResult {
  scenarioId: string;
  baselineRisk: number;
  simulatedRisk: number;
  populationProtected: number;
  assetsProtected: number;
  confidence: number;
}

export interface Alert {
  id: string;
  ref: string;
  title: string;
  message: string;
  severity: Severity;
  zoneId?: string;
  issuedAt: string;
  channels: ("SMS" | "PUSH" | "EMAIL" | "SIREN" | "API")[];
  deliveryStatus: "QUEUED" | "SENT" | "PARTIAL" | "FAILED";
  acknowledged: boolean;
}

export interface DataSource {
  id: string;
  name: string;
  kind: "WEATHER" | "GIS" | "IOT" | "HYDROLOGY" | "SATELLITE" | "REGISTRY";
  status: ServiceStatus;
  latencyMs: number;
  lastSyncAt: string;
  /** 0-100 */
  reliability: number;
}

export interface SensorReading {
  metric: string;
  value: number;
  unit: string;
  timestamp: string;
}

export interface SensorNode {
  id: string;
  code: string;
  name: string;
  zoneId: string;
  location: Coordinates;
  status: ServiceStatus;
  batteryPercent: number;
  signalPercent: number;
  lastPacketAt: string;
  readings: SensorReading[];
}

export interface RiverNode extends SensorNode {
  segment: "UPSTREAM" | "MIDSTREAM" | "DOWNSTREAM";
  waterLevelM: number;
  thresholdM: number;
  rateOfRiseMPerHour?: number;
  timeToThresholdMinutes?: number;
  dataQuality?: string;
  /** minutes for water to reach the next node */
  travelTimeMinutes: number;
  downstreamNodeId?: string;
}

export interface SystemHealthService {
  id: string;
  label: string;
  status: ServiceStatus;
  detail?: string;
}

export interface SystemHealth {
  overallPercent: number;
  mode: OperationalMode;
  lastSyncAt: string;
  services: SystemHealthService[];
}

export interface MLHealthInfo {
  status: "ONLINE" | "DEGRADED" | "OFFLINE";
  lstmLoaded: boolean;
  isolationForestLoaded: boolean;
  modelVersions: Record<string, string>;
  frameworkVersions: Record<string, string>;
  inferenceReadiness: boolean;
  lastInferenceAt?: string;
  lastInferenceLatencyMs?: number;
  fallbackUsed: boolean;
  notes?: string;
}

export interface MLRiverForecast {
  forecastAvailable: boolean;
  predictedRiverLevelM?: number;
  currentRiverLevelM?: number;
  deltaM?: number;
  forecastHorizonHours: number;
  predictionTimestamp: string;
  modelVersion: string;
  inferenceLatencyMs: number;
  dataQuality: DataQuality;
  fallbackUsed: boolean;
  reason?: string;
  confidenceCalibrated: boolean;
  confidenceNote?: string;
}

export interface MLSensorAnomaly {
  sensorId: string;
  status: "HEALTHY" | "DEGRADED" | "ANOMALOUS" | "OFFLINE";
  isAnomaly: boolean;
  anomalyScore?: number;
  modelVersion: string;
  inferenceLatencyMs: number;
  dataQuality: string;
  timestamp: string;
  fallbackUsed: boolean;
  reason?: string;
}

export interface LSTMMetrics {
  maeMeters: number;
  rmseMeters: number;
  mapePercent?: number;
  maxAbsoluteErrorMeters: number;
  meanBiasMeters: number;
}

export interface LatencyStats {
  mean: number;
  p50: number;
  p95: number;
}

export interface LSTMEvaluation {
  modelName: string;
  modelVersion: string;
  architecture: string;
  evaluationDatasetType: string;
  disclaimer: string;
  sampleSize: number;
  validPredictions: number;
  rejectedPredictions: number;
  metrics: LSTMMetrics;
  latencyMs: LatencyStats;
  confidenceCalibrated: boolean;
  calibrationNote: string;
}

export interface InjectedFaultResult {
  faultName: string;
  description: string;
  injectedVector: Record<string, number>;
  detectedAsAnomaly: boolean;
  anomalyScore?: number;
  operationalStatus: string;
  fallbackUsed: boolean;
}

export interface IsolationForestEvaluation {
  modelName: string;
  modelVersion: string;
  architecture: string;
  evaluationType: string;
  disclaimer: string;
  sampleSize: number;
  baselineAnomalyRatePercent: number;
  scoreDistribution: {
    min: number;
    max: number;
    mean: number;
    std: number;
  };
  latencyMs: LatencyStats;
  injectedFaultSimulations: InjectedFaultResult[];
  groundTruthNote: string;
}

export interface FailureModeTestItem {
  test: string;
  handledGracefully: boolean;
  reason?: string;
}

export interface FailureModeTesting {
  allFailureModesHandled: boolean;
  lstmFailureTests: FailureModeTestItem[];
  isolationForestFailureTests: FailureModeTestItem[];
  climateShieldResilience: string;
}

export interface MLEvaluationReport {
  timestamp: string;
  disclaimer: string;
  lstmEvaluation: LSTMEvaluation;
  isolationForestEvaluation: IsolationForestEvaluation;
  failureModeTesting: FailureModeTesting;
  deterministicPrimacyPrinciple: string;
}

export interface OperationalScenarioData {
  scenarioName: string;
  zoneId: string;
  targetNode: string;
  currentState: {
    riverStageM: number;
    deterministicZoneRiskScore: number;
    deterministicStatus: string;
    baselinePriority: string;
  };
  mlForecast: {
    forecastHorizonHours: number;
    predictedStageM: number;
    predictedDeltaM: number;
    advisoryStatement: string;
    guaranteeStatement: string;
  };
  responseAdaptation: {
    priorityEscalation: string;
    rationale: string;
    recommendedResources: Array<{
      type: string;
      quantity: number;
      stagingLocation: string;
      action: string;
    }>;
  };
  governanceNote: string;
}

export interface EnvironmentalModifiers {
  river_level_delta_m?: number;
  rainfall_intensity_pct?: number;
  rainfall_intensity_mm_h?: number;
  temperature_c?: number;
  humidity_pct?: number;
  soil_moisture_pct?: number;
}

export interface InfrastructureModifiers {
  hospital_road_available?: boolean;
  pump_station_operational?: boolean;
  substation_operational?: boolean;
  barrier_deployed_km?: number;
  critical_asset_status_overrides?: Record<string, string>;
}

export interface ResponseModifiers {
  pumps_deployed?: number;
  rescue_teams_deployed?: number;
  barriers_deployed_units?: number;
  response_delay_minutes?: number;
}

export interface SensorConfidenceModifiers {
  sensor_status_overrides?: Record<string, string>;
}

export interface SimulationRunRequest {
  scenario_id?: string;
  name?: string;
  environmental?: EnvironmentalModifiers;
  infrastructure?: InfrastructureModifiers;
  response?: ResponseModifiers;
  sensor_confidence?: SensorConfidenceModifiers;
}

export interface MetricComparisonItem {
  metric_name: string;
  unit: string;
  baseline: number;
  simulated: number;
  absolute_delta: number;
  percentage_delta?: number;
  interpretation: string;
}

export interface InterventionRankingItem {
  rank: number;
  intervention_id: string;
  name: string;
  category: string;
  modeled_risk_reduction_points: number;
  estimated_population_protected: number;
  critical_assets_safeguarded: number;
  estimated_cost_usd: number;
  response_eta_minutes: number;
  cascade_interruption_factor: number;
  multi_attribute_utility_score: number;
  is_best_modeled_option: boolean;
  description: string;
}

export interface AffectedZoneSummary {
  zone_id: string;
  name: string;
  baseline_risk: number;
  simulated_risk: number;
  risk_delta: number;
  dominant_hazard: string;
  status: string;
  population: number;
  elevation_m: number;
}

export interface AffectedAssetSummary {
  asset_id: string;
  name: string;
  asset_type?: string;
  category?: string;
  criticality: string;
  status?: string;
  baseline_status?: string;
  simulated_status?: string;
  zone_id?: string;
  simulated_impact?: string;
  flood_depth_m?: number;
  is_access_compromised?: boolean;
}

export interface CascadeSummaryItem {
  node_id: string;
  name: string;
  baseline_risk: string;
  simulated_risk: string;
  propagation_state: string;
}

export interface SimulationRunResponse {
  simulation_id: string;
  scenario_id: string;
  scenario_name: string;
  timestamp: string;
  execution_latency_ms: number;
  ml_forecast_integrated: boolean;
  ml_advisory_note: string;
  baseline_overall_risk: number;
  simulated_overall_risk: number;
  modeled_risk_delta: number;
  modeled_risk_delta_pct: number;
  simulated_residual_risk: number;
  response_priority: string;
  best_modeled_option: string;
  estimated_population_protected: number;
  critical_assets_safeguarded: number;
  metrics_comparison: MetricComparisonItem[];
  affected_zones: AffectedZoneSummary[];
  affected_assets: AffectedAssetSummary[];
  cascade_changes: CascadeSummaryItem[];
  intervention_ranking: InterventionRankingItem[];
  modeled_impact_statement: string;
  assumptions: string[];
  warnings: string[];
  data_quality: string;
  deterministic_safety_note: string;
}

export interface ScenarioDefinition {
  scenario_id: string;
  name: string;
  category: string;
  description: string;
  parameters: {
    environmental?: EnvironmentalModifiers;
    infrastructure?: InfrastructureModifiers;
    response?: ResponseModifiers;
    sensor_confidence?: SensorConfidenceModifiers;
  };
  projected_headline: string;
}

export interface ScenarioListResponse {
  scenarios: ScenarioDefinition[];
  count: number;
  governance_note: string;
}

export interface AgenticActionPlanResponse {
  timestamp: string;
  system_telemetry_health: {
    status: string;
    data_freshness_pct: string;
    sensors_audited: number;
    faulty_hardware_detected: number;
    isolation_forest_audit: string;
  };
  voiceops_ingestion_context: {
    source: string;
    extracted_location: string;
    extracted_hazard: string;
    confidence_score: number;
    status: string;
  };
  agents: {
    "1_geospatial_agent": {
      agent_name: string;
      predicted_inundation_depth_cm: number;
      high_risk_boundary_zones: string[];
      spatial_status: string;
    };
    "2_infrastructure_agent": {
      agent_name: string;
      critical_assets_threatened: number;
      high_threat_assets: number;
      vulnerable_nodes: string[];
      cascade_risk_warning: string;
    };
    "3_mobility_agent": {
      agent_name: string;
      blocked_corridors: string[];
      active_detours: string[];
      transit_status: string;
    };
    "4_emergency_agent": {
      agent_name: string;
      recommended_dispatches: string[];
      inventory_status: string;
    };
    "5_communication_agent": {
      agent_name: string;
      public_broadcast_alert: string;
      field_briefing: string;
    };
    "6_decision_agent_master": {
      agent_name: string;
      prioritized_city_action_plan: string[];
    };
  };
}
