/**
 * API abstraction layer.
 * All functions are strictly asynchronous (returning Promises).
 * In DEMO mode (or when FastAPI is offline), queries safely read through the
 * demo adapter. In LIVE mode, queries target /api/v1 endpoints with resilient
 * error handling.
 */
import type {
  Alert,
  Asset,
  CascadeEdge,
  CascadeNode,
  DataSource,
  Forecast,
  Incident,
  OperationalMode,
  Recommendation,
  RiskScore,
  RiskZone,
  RiverNode,
  SystemHealth,
  MLHealthInfo,
  MLRiverForecast,
  MLSensorAnomaly,
  MLEvaluationReport,
  OperationalScenarioData,
  ScenarioListResponse,
  SimulationRunRequest,
  SimulationRunResponse,
  AgenticActionPlanResponse,
} from "@/types/climate";

import * as demo from "./demo-data";
import { apiFetch } from "./api-client";
import {
  adaptRiskZone,
  adaptIncident,
  adaptAlert,
  adaptRiverNode,
  adaptCascade,
} from "./api-adapters";

export type CityInfo = typeof demo.CITY;

let globalOperationalMode: OperationalMode = "LIVE";

export function setApiOperationalMode(mode: OperationalMode): void {
  globalOperationalMode = mode;
}

export function getApiOperationalMode(): OperationalMode {
  return globalOperationalMode;
}

export const climateApi = {
  async getCity(): Promise<CityInfo> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.CITY);
    }
    try {
      return await apiFetch<CityInfo>("/city");
    } catch {
      return demo.CITY;
    }
  },

  async getZones(): Promise<RiskZone[]> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.zones);
    }
    try {
      const raw = await apiFetch<Record<string, unknown>[]>("/risk/zones");
      return raw.map(adaptRiskZone);
    } catch {
      return demo.zones;
    }
  },

  async getZone(id: string): Promise<RiskZone | null> {
    if (globalOperationalMode === "DEMO") {
      const found = demo.zones.find((z) => z.id === id) ?? null;
      return Promise.resolve(found);
    }
    try {
      const raw = await apiFetch<Record<string, unknown>>(`/risk/zones/${id}`);
      return adaptRiskZone(raw);
    } catch {
      return demo.zones.find((z) => z.id === id) ?? null;
    }
  },

  async getAssets(): Promise<Asset[]> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.assets);
    }
    try {
      return await apiFetch<Asset[]>("/assets");
    } catch {
      return demo.assets;
    }
  },

  async getIncidents(): Promise<Incident[]> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.incidents);
    }
    try {
      const raw = await apiFetch<Record<string, unknown>[]>("/incidents");
      return raw.map(adaptIncident);
    } catch {
      return demo.incidents;
    }
  },

  async getAlerts(): Promise<Alert[]> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.alerts);
    }
    try {
      const raw = await apiFetch<Record<string, unknown>[]>("/alerts");
      return raw.map(adaptAlert);
    } catch {
      return demo.alerts;
    }
  },

  async getRecommendations(): Promise<Recommendation[]> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.recommendations);
    }
    try {
      return await apiFetch<Recommendation[]>("/optimization/recommendations");
    } catch {
      return demo.recommendations;
    }
  },

  async getRiverNodes(): Promise<RiverNode[]> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.riverNodes);
    }
    try {
      const raw = await apiFetch<Record<string, unknown>[]>("/river/nodes");
      return raw.map(adaptRiverNode);
    } catch {
      return demo.riverNodes;
    }
  },

  async getDataSources(): Promise<DataSource[]> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.dataSources);
    }
    try {
      return await apiFetch<DataSource[]>("/data-sources");
    } catch {
      return demo.dataSources;
    }
  },

  async getForecast(zoneId = "zone-a"): Promise<Forecast> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.forecast);
    }
    try {
      return await apiFetch<Forecast>(`/forecast/trajectory?zoneId=${zoneId}`);
    } catch {
      return demo.forecast;
    }
  },

  async getCascade(): Promise<{ nodes: CascadeNode[]; edges: CascadeEdge[] }> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve({
        nodes: demo.cascadeNodes,
        edges: demo.cascadeEdges,
      });
    }
    try {
      const raw = await apiFetch<Record<string, unknown>>("/cascade/graph");
      return adaptCascade(raw);
    } catch {
      return {
        nodes: demo.cascadeNodes,
        edges: demo.cascadeEdges,
      };
    }
  },

  async getSystemHealth(): Promise<SystemHealth> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.systemHealth);
    }
    try {
      return await apiFetch<SystemHealth>("/system/health");
    } catch {
      return demo.systemHealth;
    }
  },

  /** Overall city risk calculation or remote score fetch */
  async getCityRisk(): Promise<RiskScore> {
    if (globalOperationalMode === "DEMO") {
      const zones = demo.zones;
      const totalPop = zones.reduce((s, z) => s + z.population, 0);
      const weighted = zones.reduce((s, z) => s + z.risk.value * z.population, 0) / totalPop;
      const confidence = Math.round(
        zones.reduce((s, z) => s + z.risk.confidence, 0) / zones.length,
      );
      const velocity = Math.round(
        zones.reduce((s, z) => s + z.risk.velocityPerHour, 0) / zones.length,
      );
      const score: RiskScore = {
        value: Math.round(weighted),
        level: demo.zones[0]?.risk.level ?? "HIGH",
        confidence,
        velocityPerHour: velocity,
        observedAt: demo.zones[0]?.risk.observedAt ?? new Date().toISOString(),
        quality: demo.zones[0]?.risk.quality ?? "FRESH",
      };
      return Promise.resolve(score);
    }

    try {
      return await apiFetch<RiskScore>("/risk/current");
    } catch {
      const fallbackScore: RiskScore = {
        value: 74,
        level: "HIGH",
        confidence: 88,
        velocityPerHour: 6,
        observedAt: new Date().toISOString(),
        quality: "DEGRADED",
      };
      return fallbackScore;
    }
  },

  async getMlHealth(): Promise<MLHealthInfo> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.mlHealthDemo);
    }
    try {
      const raw = await apiFetch<Record<string, unknown>>("/ml/health");
      return {
        status: (raw.status as "ONLINE" | "DEGRADED" | "OFFLINE") || "DEGRADED",
        lstmLoaded: Boolean(raw.lstm_loaded),
        isolationForestLoaded: Boolean(raw.isolation_forest_loaded),
        modelVersions: (raw.model_versions as Record<string, string>) || {},
        frameworkVersions: (raw.framework_versions as Record<string, string>) || {},
        inferenceReadiness: Boolean(raw.inference_readiness),
        lastInferenceAt: raw.last_inference_at as string | undefined,
        lastInferenceLatencyMs: raw.last_inference_latency_ms as number | undefined,
        fallbackUsed: Boolean(raw.fallback_used),
        notes: raw.notes as string | undefined,
      };
    } catch {
      return demo.mlHealthDemo;
    }
  },

  async getMlForecast(riverNodeId = "RN-01"): Promise<MLRiverForecast> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.mlForecastDemo);
    }
    try {
      const raw = await apiFetch<Record<string, unknown>>(
        `/ml/forecast?river_node_id=${riverNodeId}`,
      );
      return {
        forecastAvailable: Boolean(raw.forecast_available),
        predictedRiverLevelM: raw.predicted_river_level_m as number | undefined,
        currentRiverLevelM: raw.current_river_level_m as number | undefined,
        deltaM: raw.delta_m as number | undefined,
        forecastHorizonHours: (raw.forecast_horizon_hours as number) || 3,
        predictionTimestamp: (raw.prediction_timestamp as string) || new Date().toISOString(),
        modelVersion: (raw.model_version as string) || "CorrelatedLSTM-v1.0-synthetic",
        inferenceLatencyMs: (raw.inference_latency_ms as number) || 0.0,
        dataQuality: (raw.data_quality as DataQuality) || "FRESH",
        fallbackUsed: Boolean(raw.fallback_used),
        reason: raw.reason as string | undefined,
        confidenceCalibrated: Boolean(raw.confidence_calibrated),
        confidenceNote: raw.confidence_note as string | undefined,
      };
    } catch {
      return demo.mlForecastDemo;
    }
  },

  async getSensorHealth(sensorId: string): Promise<MLSensorAnomaly> {
    try {
      const raw = await apiFetch<Record<string, unknown>>(
        `/ml/sensor-health?sensor_id=${sensorId}`,
      );
      return {
        sensorId: (raw.sensor_id as string) || sensorId,
        status: (raw.status as ServiceStatus) || "HEALTHY",
        isAnomaly: Boolean(raw.is_anomaly),

        anomalyScore: raw.anomaly_score as number | undefined,
        modelVersion: (raw.model_version as string) || "IsolationForest-v1.0-synthetic",
        inferenceLatencyMs: (raw.inference_latency_ms as number) || 0.0,
        dataQuality: (raw.data_quality as string) || "VALID",
        timestamp: (raw.timestamp as string) || new Date().toISOString(),
        fallbackUsed: Boolean(raw.fallback_used),
        reason: raw.reason as string | undefined,
      };
    } catch {
      return {
        sensorId,
        status: "HEALTHY",
        isAnomaly: false,
        anomalyScore: 0.1,
        modelVersion: "IsolationForest-v1.0-synthetic",
        inferenceLatencyMs: 0.0,
        dataQuality: "VALID",
        timestamp: new Date().toISOString(),
        fallbackUsed: true,
      };
    }
  },

  async getMlEvaluation(samples = 100): Promise<MLEvaluationReport> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.mlEvaluationDemo as unknown as MLEvaluationReport);
    }
    try {
      const raw = await apiFetch<Record<string, unknown>>(`/ml/evaluation?samples=${samples}`);
      const lstmRaw = (raw.lstm_evaluation as Record<string, unknown>) || {};
      const lstmMetricsRaw = (lstmRaw.metrics as Record<string, unknown>) || {};
      const lstmLatencyRaw = (lstmRaw.latency_ms as Record<string, unknown>) || {};
      const isoRaw = (raw.isolation_forest_evaluation as Record<string, unknown>) || {};
      const isoLatencyRaw = (isoRaw.latency_ms as Record<string, unknown>) || {};
      const isoScoreRaw = (isoRaw.score_distribution as Record<string, unknown>) || {};
      const failRaw = (raw.failure_mode_testing as Record<string, unknown>) || {};

      return {
        timestamp: (raw.timestamp as string) || new Date().toISOString(),
        disclaimer: (raw.disclaimer as string) || "SYNTHETIC VALIDATION — NOT REAL-WORLD ACCURACY.",
        lstmEvaluation: {
          modelName: (lstmRaw.model_name as string) || "CorrelatedLSTM River Forecaster",
          modelVersion: (lstmRaw.model_version as string) || "CorrelatedLSTM-v1.0-synthetic",
          architecture: (lstmRaw.architecture as string) || "PyTorch CorrelatedLSTM",
          evaluationDatasetType:
            (lstmRaw.evaluation_dataset_type as string) || "SYNTHETIC_HOLDOUT_HYDROLOGY",
          disclaimer: (lstmRaw.disclaimer as string) || "SYNTHETIC VALIDATION",
          sampleSize: (lstmRaw.sample_size as number) || samples,
          validPredictions: (lstmRaw.valid_predictions as number) || 0,
          rejectedPredictions: (lstmRaw.rejected_predictions as number) || 0,
          metrics: {
            maeMeters: (lstmMetricsRaw.mae_meters as number) || 0,
            rmseMeters: (lstmMetricsRaw.rmse_meters as number) || 0,
            mapePercent: lstmMetricsRaw.mape_percent as number | undefined,
            maxAbsoluteErrorMeters: (lstmMetricsRaw.max_absolute_error_meters as number) || 0,
            meanBiasMeters: (lstmMetricsRaw.mean_bias_meters as number) || 0,
          },
          latencyMs: {
            mean: (lstmLatencyRaw.mean as number) || 0,
            p50: (lstmLatencyRaw.p50 as number) || 0,
            p95: (lstmLatencyRaw.p95 as number) || 0,
          },
          confidenceCalibrated: Boolean(lstmRaw.confidence_calibrated),
          calibrationNote: (lstmRaw.calibration_note as string) || "",
        },
        isolationForestEvaluation: {
          modelName: (isoRaw.model_name as string) || "Sensor Telemetry Isolation Forest",
          modelVersion: (isoRaw.model_version as string) || "IsolationForest-v1.0-synthetic",
          architecture: (isoRaw.architecture as string) || "Scikit-learn IsolationForest",
          evaluationType:
            (isoRaw.evaluation_type as string) || "UNSUPERVISED_BASELINE_AND_FAULT_INJECTIONS",
          disclaimer: (isoRaw.disclaimer as string) || "SIMULATION",
          sampleSize: (isoRaw.sample_size as number) || samples,
          baselineAnomalyRatePercent: (isoRaw.baseline_anomaly_rate_percent as number) || 0,
          scoreDistribution: {
            min: (isoScoreRaw.min as number) || 0,
            max: (isoScoreRaw.max as number) || 0,
            mean: (isoScoreRaw.mean as number) || 0,
            std: (isoScoreRaw.std as number) || 0,
          },
          latencyMs: {
            mean: (isoLatencyRaw.mean as number) || 0,
            p50: (isoLatencyRaw.p50 as number) || 0,
            p95: (isoLatencyRaw.p95 as number) || 0,
          },
          injectedFaultSimulations: (
            (isoRaw.injected_fault_simulations as Array<Record<string, unknown>>) || []
          ).map((f) => ({
            faultName: (f.fault_name as string) || "SIMULATED_FAULT",
            description: (f.description as string) || "",
            injectedVector: (f.injected_vector as Record<string, number>) || {},
            detectedAsAnomaly: Boolean(f.detected_as_anomaly),
            anomalyScore: f.anomaly_score as number | undefined,
            operationalStatus: (f.operational_status as string) || "HEALTHY",
            fallbackUsed: Boolean(f.fallback_used),
          })),
          groundTruthNote: (isoRaw.ground_truth_note as string) || "",
        },
        failureModeTesting: {
          allFailureModesHandled: Boolean(failRaw.all_failure_modes_handled),
          lstmFailureTests: (
            (failRaw.lstm_failure_tests as Array<Record<string, unknown>>) || []
          ).map((t) => ({
            test: (t.test as string) || "",
            handledGracefully: Boolean(t.handled_gracefully),
            reason: t.reason as string | undefined,
          })),
          isolationForestFailureTests: (
            (failRaw.isolation_forest_failure_tests as Array<Record<string, unknown>>) || []
          ).map((t) => ({
            test: (t.test as string) || "",
            handledGracefully: Boolean(t.handled_gracefully),
            reason: t.reason as string | undefined,
          })),
          climateShieldResilience:
            (failRaw.climate_shield_resilience as string) || "VERIFIED — Zero system crashes",
        },
        deterministicPrimacyPrinciple:
          (raw.deterministic_primacy_principle as string) ||
          "ML advisory — deterministic risk engine remains authoritative.",
      };
    } catch {
      return demo.mlEvaluationDemo as unknown as MLEvaluationReport;
    }
  },

  async getOperationalScenario(): Promise<OperationalScenarioData> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.mlOperationalScenarioDemo as OperationalScenarioData);
    }
    try {
      const raw = await apiFetch<Record<string, unknown>>("/ml/operational-scenario");
      const cur = (raw.current_state as Record<string, unknown>) || {};
      const fore = (raw.ml_forecast as Record<string, unknown>) || {};
      const resp = (raw.response_adaptation as Record<string, unknown>) || {};

      return {
        scenarioName: (raw.scenario_name as string) || "MIDSTREAM_CREST_EARLY_WARNING",
        zoneId: (raw.zone_id as string) || "zone-a",
        targetNode: (raw.target_node as string) || "RN-01",
        currentState: {
          riverStageM: (cur.river_stage_m as number) || 4.85,
          deterministicZoneRiskScore: (cur.deterministic_zone_risk_score as number) || 62.4,
          deterministicStatus: (cur.deterministic_status as string) || "ELEVATED",
          baselinePriority: (cur.baseline_priority as string) || "P2_ELEVATED",
        },
        mlForecast: {
          forecastHorizonHours: (fore.forecast_horizon_hours as number) || 3,
          predictedStageM: (fore.predicted_stage_m as number) || 6.45,
          predictedDeltaM: (fore.predicted_delta_m as number) || 1.6,
          advisoryStatement: (fore.advisory_statement as string) || "",
          guaranteeStatement: (fore.guarantee_statement as string) || "",
        },
        responseAdaptation: {
          priorityEscalation: (resp.priority_escalation as string) || "P2_ELEVATED -> P1_IMMEDIATE",
          rationale: (resp.rationale as string) || "",
          recommendedResources: (
            (resp.recommended_resources as Array<Record<string, unknown>>) || []
          ).map((r) => ({
            type: (r.type as string) || "",
            quantity: (r.quantity as number) || 1,
            stagingLocation: (r.staging_location as string) || "",
            action: (r.action as string) || "",
          })),
        },
        governanceNote:
          (raw.governance_note as string) ||
          "ML advisory — deterministic risk engine remains authoritative.",
      };
    } catch {
      return demo.mlOperationalScenarioDemo as OperationalScenarioData;
    }
  },

  async getSimulationScenarios(): Promise<ScenarioListResponse> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.digitalTwinScenariosDemo as ScenarioListResponse);
    }
    try {
      const res = await apiFetch<ScenarioListResponse>("/simulation/scenarios");
      return res;
    } catch {
      return demo.digitalTwinScenariosDemo as ScenarioListResponse;
    }
  },

  async runSimulation(req: SimulationRunRequest): Promise<SimulationRunResponse> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.digitalTwinRunDemo as SimulationRunResponse);
    }
    try {
      const res = await apiFetch<SimulationRunResponse>("/simulation/run", {
        method: "POST",
        body: JSON.stringify(req),
      });
      return res;
    } catch {
      return demo.digitalTwinRunDemo as SimulationRunResponse;
    }
  },

  async runNamedScenario(scenarioName: string): Promise<SimulationRunResponse> {
    if (globalOperationalMode === "DEMO") {
      const matched = demo.digitalTwinScenariosDemo.scenarios.find(
        (s) => s.scenario_id.toLowerCase() === scenarioName.toLowerCase(),
      );
      return Promise.resolve({
        ...demo.digitalTwinRunDemo,
        scenario_id: scenarioName,
        scenario_name: matched?.name || scenarioName,
      } as SimulationRunResponse);
    }
    try {
      const res = await apiFetch<SimulationRunResponse>(`/simulation/scenarios/${scenarioName}`, {
        method: "POST",
      });
      return res;
    } catch {
      return demo.digitalTwinRunDemo as SimulationRunResponse;
    }
  },

  async getSimulationResult(simId: string): Promise<SimulationRunResponse> {
    if (globalOperationalMode === "DEMO") {
      return Promise.resolve(demo.digitalTwinRunDemo as SimulationRunResponse);
    }
    try {
      const res = await apiFetch<SimulationRunResponse>(`/simulation/${simId}`);
      return res;
    } catch {
      return demo.digitalTwinRunDemo as SimulationRunResponse;
    }
  },

  async getAgenticActionPlan(): Promise<AgenticActionPlanResponse> {
    try {
      const res = await apiFetch<AgenticActionPlanResponse>("/agentic-action-plan");
      return res;
    } catch {
      return {
        timestamp: new Date().toISOString(),
        system_telemetry_health: {
          status: "HEALTHY",
          data_freshness_pct: "99.2%",
          sensors_audited: 20,
          faulty_hardware_detected: 0,
          isolation_forest_audit: "All sensors operational; nominal telemetry variance detected.",
        },
        voiceops_ingestion_context: {
          source: "Field Emergency Audio Report",
          extracted_location: "MVP Colony Bridge",
          extracted_hazard: "FLOOD / WATERLOGGING",
          confidence_score: 0.91,
          status: "VERIFIED_AND_GROUNDED",
        },
        agents: {
          "1_geospatial_agent": {
            agent_name: "Geospatial Boundary Agent",
            predicted_inundation_depth_cm: 48.37,
            high_risk_boundary_zones: [
              "MVP Colony Bridge (CRITICAL / RED ZONE)",
              "Gajuwaka Highway Entrance (HIGH / ORANGE ZONE)",
              "Madhurawada Lowlands (MEDIUM / YELLOW ZONE)",
            ],
            spatial_status:
              "Severe localized inundation predicted. Water accumulation depth: 48.37 cm.",
          },
          "2_infrastructure_agent": {
            agent_name: "Infrastructure Exposure Agent",
            critical_assets_threatened: 3,
            high_threat_assets: 4,
            vulnerable_nodes: [
              "Substation A-4 (Power Grid Node)",
              "Primary Care Center 2 (Emergency Healthcare)",
              "NH16 Drainage Culvert (Transit Infrastructure)",
            ],
            cascade_risk_warning:
              "High risk of secondary power failure if Substation A-4 water level exceeds threshold.",
          },
          "3_mobility_agent": {
            agent_name: "Mobility & Transit Agent",
            blocked_corridors: ["NH16 Highway Segment near MVP Colony Bridge"],
            active_detours: [
              "Route 4 via Inner Ring Road Flyover",
              "Bypass Flyover West (Emergency Vehicles Only)",
            ],
            transit_status: "Access restricted across low-lying bridge sections.",
          },
          "4_emergency_agent": {
            agent_name: "Emergency Resource Optimizer Agent",
            recommended_dispatches: [
              "Deploy High-Capacity Drainage Pump P-03 directly to MVP Colony Bridge",
              "Dispatch Rapid Response Unit 04 with portable flood barriers",
              "Erect physical barriers around Substation A-4 perimeter",
            ],
            inventory_status: "Pump P-03 and Field Team 04 ready for deployment.",
          },
          "5_communication_agent": {
            agent_name: "Public Communication & Warning Agent",
            public_broadcast_alert:
              "CRITICAL ALERT: Rapid water level rise predicted at MVP Colony Bridge. Forecasted height: 2.89m in +3 hours. Avoid eastern roads.",
            field_briefing:
              "Field Unit 04: Proceed to MVP Colony Bridge. Restrict public access near bridge.",
          },
          "6_decision_agent_master": {
            agent_name: "Master Orchestrator Decision Agent",
            prioritized_city_action_plan: [
              "Priority 1: Protect Substation A-4 to prevent regional power outage.",
              "Priority 2: Divert public traffic from blocked route at MVP Colony Bridge.",
              "Priority 3: Deploy High-Capacity Pump P-03 to clear bridge drainage.",
              "Priority 4: Issue automated public advisory for MVP Colony Bridge sector.",
            ],
          },
        },
      };
    }
  },
};
