/**
 * Demo dataset for Demo City. This is the ONLY module that contains prototype
 * values — UI components never import it directly, they receive data through
 * src/services/climate-api.ts so a real backend can replace it unchanged.
 */
import type {
  Alert,
  Asset,
  CascadeEdge,
  CascadeNode,
  DataSource,
  Forecast,
  Incident,
  Recommendation,
  RiskZone,
  RiverNode,
  SensorNode,
  SystemHealth,
} from "@/types/climate";
import { riskLevelFromScore } from "@/lib/risk";

const EPOCH = new Date();

export function minutesAgo(min: number): string {
  return new Date(EPOCH.getTime() - min * 60_000).toISOString();
}
function minutesAhead(min: number): string {
  return new Date(EPOCH.getTime() + min * 60_000).toISOString();
}

export const CITY = {
  id: "demo-city",
  name: "Demo City",
  centroid: { lat: 17.385, lng: 78.4867 },
  population: 1_240_000,
  zones: 4,
};

export const zones: RiskZone[] = [
  {
    id: "zone-a",
    name: "Zone A · Riverfront North",
    code: "ZN-A",
    population: 184_000,
    areaKm2: 22.4,
    dominantHazard: "FLOOD",
    risk: {
      value: 87,
      level: riskLevelFromScore(87),
      confidence: 93,
      velocityPerHour: 14,
      observedAt: minutesAgo(2),
      quality: "FRESH",
    },
    drivers: [
      {
        id: "d1",
        label: "River level (upstream)",
        contribution: 38,
        value: "4.12 m",
        trend: "RISING",
      },
      {
        id: "d2",
        label: "Rainfall intensity 3h",
        contribution: 27,
        value: "62 mm",
        trend: "RISING",
      },
      {
        id: "d3",
        label: "Drainage capacity",
        contribution: 21,
        value: "38% free",
        trend: "FALLING",
      },
      { id: "d4", label: "Soil saturation", contribution: 14, value: "91%", trend: "STABLE" },
    ],
    centroid: { lat: 17.42, lng: 78.47 },
    polygon: [
      [78.44, 17.44],
      [78.5, 17.44],
      [78.51, 17.4],
      [78.45, 17.39],
      [78.44, 17.44],
    ],
  },
  {
    id: "zone-b",
    name: "Zone B · Central District",
    code: "ZN-B",
    population: 342_000,
    areaKm2: 18.1,
    dominantHazard: "WATERLOGGING",
    risk: {
      value: 71,
      level: riskLevelFromScore(71),
      confidence: 88,
      velocityPerHour: 6,
      observedAt: minutesAgo(4),
      quality: "FRESH",
    },
    drivers: [
      {
        id: "d1",
        label: "Road surface water",
        contribution: 34,
        value: "17 segments",
        trend: "RISING",
      },
      { id: "d2", label: "Pump station load", contribution: 29, value: "82%", trend: "RISING" },
      {
        id: "d3",
        label: "Rainfall intensity 3h",
        contribution: 22,
        value: "48 mm",
        trend: "STABLE",
      },
      {
        id: "d4",
        label: "Population density",
        contribution: 15,
        value: "18.9k/km²",
        trend: "STABLE",
      },
    ],
    centroid: { lat: 17.385, lng: 78.4867 },
    polygon: [
      [78.45, 17.39],
      [78.51, 17.4],
      [78.52, 17.36],
      [78.46, 17.35],
      [78.45, 17.39],
    ],
  },
  {
    id: "zone-c",
    name: "Zone C · Industrial South",
    code: "ZN-C",
    population: 121_000,
    areaKm2: 31.7,
    dominantHazard: "HEAT",
    risk: {
      value: 46,
      level: riskLevelFromScore(46),
      confidence: 74,
      velocityPerHour: -3,
      observedAt: minutesAgo(21),
      quality: "AGING",
    },
    drivers: [
      {
        id: "d1",
        label: "Surface temperature",
        contribution: 41,
        value: "43.1 °C",
        trend: "FALLING",
      },
      { id: "d2", label: "Canopy cover", contribution: 26, value: "6%", trend: "STABLE" },
      { id: "d3", label: "Outdoor workforce", contribution: 19, value: "11.2k", trend: "STABLE" },
      { id: "d4", label: "Humidity", contribution: 14, value: "58%", trend: "STABLE" },
    ],
    centroid: { lat: 17.34, lng: 78.5 },
    polygon: [
      [78.46, 17.35],
      [78.52, 17.36],
      [78.53, 17.31],
      [78.47, 17.31],
      [78.46, 17.35],
    ],
  },
  {
    id: "zone-d",
    name: "Zone D · Western Ridge",
    code: "ZN-D",
    population: 96_500,
    areaKm2: 26.9,
    dominantHazard: "DRAINAGE_STRESS",
    risk: {
      value: 24,
      level: riskLevelFromScore(24),
      confidence: 51,
      velocityPerHour: 0,
      observedAt: minutesAgo(74),
      quality: "STALE",
    },
    drivers: [
      {
        id: "d1",
        label: "Culvert blockage reports",
        contribution: 44,
        value: "3 open",
        trend: "STABLE",
      },
      {
        id: "d2",
        label: "Rainfall intensity 3h",
        contribution: 31,
        value: "9 mm",
        trend: "FALLING",
      },
      { id: "d3", label: "Slope runoff", contribution: 25, value: "moderate", trend: "STABLE" },
    ],
    centroid: { lat: 17.4, lng: 78.42 },
    polygon: [
      [78.39, 17.43],
      [78.44, 17.44],
      [78.45, 17.37],
      [78.4, 17.36],
      [78.39, 17.43],
    ],
  },
];

export const assets: Asset[] = [
  {
    id: "asset-1",
    name: "District Hospital",
    category: "HOSPITAL",
    zoneId: "zone-a",
    criticality: "TIER_1",
    location: { lat: 17.418, lng: 78.463 },
    exposure: "CRITICAL",
    servesPopulation: 410_000,
    status: "AT_RISK",
  },
  {
    id: "asset-2",
    name: "Emergency Response Center",
    category: "EMERGENCY",
    zoneId: "zone-b",
    criticality: "TIER_1",
    location: { lat: 17.388, lng: 78.489 },
    exposure: "HIGH",
    servesPopulation: 1_240_000,
    status: "OPERATIONAL",
  },
  {
    id: "asset-3",
    name: "Main Bridge",
    category: "BRIDGE",
    zoneId: "zone-a",
    criticality: "TIER_1",
    location: { lat: 17.409, lng: 78.475 },
    exposure: "CRITICAL",
    servesPopulation: 620_000,
    status: "IMPAIRED",
  },
  {
    id: "asset-4",
    name: "Water Treatment Facility",
    category: "WATER",
    zoneId: "zone-a",
    criticality: "TIER_1",
    location: { lat: 17.43, lng: 78.452 },
    exposure: "HIGH",
    servesPopulation: 780_000,
    status: "AT_RISK",
  },
  {
    id: "asset-5",
    name: "Power Substation",
    category: "POWER",
    zoneId: "zone-b",
    criticality: "TIER_2",
    location: { lat: 17.376, lng: 78.497 },
    exposure: "MODERATE",
    servesPopulation: 340_000,
    status: "OPERATIONAL",
  },
  {
    id: "asset-6",
    name: "Primary School",
    category: "SCHOOL",
    zoneId: "zone-c",
    criticality: "TIER_3",
    location: { lat: 17.343, lng: 78.505 },
    exposure: "MODERATE",
    servesPopulation: 1_850,
    status: "OPERATIONAL",
  },
];

export const incidents: Incident[] = [
  {
    id: "inc-1",
    ref: "INC-2418",
    title: "Flooding along Riverfront Road",
    hazard: "FLOOD",
    zoneId: "zone-a",
    severity: "EMERGENCY",
    reportedAt: minutesAgo(12),
    status: "IN_RESPONSE",
    location: { lat: 17.421, lng: 78.468 },
    affectedPopulation: 21_400,
    source: "SENSOR",
  },
  {
    id: "inc-2",
    ref: "INC-2417",
    title: "Road waterlogging at Central Junction",
    hazard: "WATERLOGGING",
    zoneId: "zone-b",
    severity: "WARNING",
    reportedAt: minutesAgo(34),
    status: "ACKNOWLEDGED",
    location: { lat: 17.387, lng: 78.492 },
    affectedPopulation: 8_900,
    source: "PUBLIC_REPORT",
  },
  {
    id: "inc-3",
    ref: "INC-2415",
    title: "Drainage stress, North pump station",
    hazard: "DRAINAGE_STRESS",
    zoneId: "zone-b",
    severity: "ADVISORY",
    reportedAt: minutesAgo(58),
    status: "OPEN",
    location: { lat: 17.394, lng: 78.481 },
    affectedPopulation: 3_100,
    source: "MODEL",
  },
  {
    id: "inc-4",
    ref: "INC-2411",
    title: "Extreme heat exposure, industrial belt",
    hazard: "HEAT",
    zoneId: "zone-c",
    severity: "ADVISORY",
    reportedAt: minutesAgo(146),
    status: "OPEN",
    location: { lat: 17.339, lng: 78.503 },
    affectedPopulation: 11_200,
    source: "OPERATOR",
  },
];

export const riverNodes: RiverNode[] = [
  {
    id: "river-up",
    code: "RN-01",
    name: "Upstream Node",
    zoneId: "zone-d",
    segment: "UPSTREAM",
    location: { lat: 17.46, lng: 78.43 },
    status: "HEALTHY",
    batteryPercent: 94,
    signalPercent: 88,
    lastPacketAt: minutesAgo(1),
    waterLevelM: 4.12,
    thresholdM: 4.5,
    travelTimeMinutes: 45,
    downstreamNodeId: "river-mid",
    readings: [
      { metric: "Water level", value: 4.12, unit: "m", timestamp: minutesAgo(1) },
      { metric: "Rainfall 1h", value: 24, unit: "mm", timestamp: minutesAgo(1) },
    ],
  },
  {
    id: "river-mid",
    code: "RN-02",
    name: "Midstream Node",
    zoneId: "zone-a",
    segment: "MIDSTREAM",
    location: { lat: 17.418, lng: 78.458 },
    status: "ACTIVE",
    batteryPercent: 71,
    signalPercent: 64,
    lastPacketAt: minutesAgo(3),
    waterLevelM: 3.68,
    thresholdM: 3.8,
    travelTimeMinutes: 35,
    downstreamNodeId: "river-down",
    readings: [
      { metric: "Water level", value: 3.68, unit: "m", timestamp: minutesAgo(3) },
      { metric: "Rainfall 1h", value: 19, unit: "mm", timestamp: minutesAgo(3) },
    ],
  },
  {
    id: "river-down",
    code: "RN-03",
    name: "Downstream Node",
    zoneId: "zone-b",
    segment: "DOWNSTREAM",
    location: { lat: 17.372, lng: 78.494 },
    status: "DEGRADED",
    batteryPercent: 38,
    signalPercent: 22,
    lastPacketAt: minutesAgo(27),
    waterLevelM: 2.41,
    thresholdM: 3.2,
    travelTimeMinutes: 0,
    readings: [{ metric: "Water level", value: 2.41, unit: "m", timestamp: minutesAgo(27) }],
  },
];

export const sensorNodes: SensorNode[] = riverNodes;

export const dataSources: DataSource[] = [
  {
    id: "ds-1",
    name: "National Weather Service",
    kind: "WEATHER",
    status: "HEALTHY",
    latencyMs: 320,
    lastSyncAt: minutesAgo(2),
    reliability: 98,
  },
  {
    id: "ds-2",
    name: "Municipal GIS Registry",
    kind: "GIS",
    status: "HEALTHY",
    latencyMs: 140,
    lastSyncAt: minutesAgo(9),
    reliability: 99,
  },
  {
    id: "ds-3",
    name: "River IoT Network (LoRa)",
    kind: "IOT",
    status: "DEGRADED",
    latencyMs: 2_400,
    lastSyncAt: minutesAgo(27),
    reliability: 71,
  },
  {
    id: "ds-4",
    name: "Hydrology Gauge Feed",
    kind: "HYDROLOGY",
    status: "HEALTHY",
    latencyMs: 510,
    lastSyncAt: minutesAgo(5),
    reliability: 94,
  },
  {
    id: "ds-5",
    name: "Satellite Rainfall Estimate",
    kind: "SATELLITE",
    status: "ACTIVE",
    latencyMs: 1_100,
    lastSyncAt: minutesAgo(14),
    reliability: 86,
  },
];

export const alerts: Alert[] = [
  {
    id: "al-1",
    ref: "ALR-0912",
    title: "Evacuation advisory · Zone A riverfront",
    message:
      "River level projected to exceed 4.5 m within 90 minutes. Move residents from low-lying blocks A3–A7.",
    severity: "EMERGENCY",
    zoneId: "zone-a",
    issuedAt: minutesAgo(8),
    channels: ["SMS", "PUSH", "SIREN"],
    deliveryStatus: "PARTIAL",
    acknowledged: false,
  },
  {
    id: "al-2",
    ref: "ALR-0911",
    title: "Traffic diversion · Central Junction",
    message: "Waterlogging above 30 cm. Divert traffic via Ring Road until drainage recovers.",
    severity: "WARNING",
    zoneId: "zone-b",
    issuedAt: minutesAgo(31),
    channels: ["PUSH", "API"],
    deliveryStatus: "SENT",
    acknowledged: true,
  },
  {
    id: "al-3",
    ref: "ALR-0910",
    title: "Heat advisory · Industrial South",
    message: "Outdoor work pause recommended between 12:00 and 16:00.",
    severity: "ADVISORY",
    zoneId: "zone-c",
    issuedAt: minutesAgo(122),
    channels: ["SMS", "EMAIL"],
    deliveryStatus: "SENT",
    acknowledged: true,
  },
];

export const recommendations: Recommendation[] = [
  {
    id: "rec-1",
    action: "Pre-position rescue teams at Main Bridge",
    rationale:
      "Bridge approach floods 40 min before the riverfront blocks; staging here protects the evacuation corridor.",
    zoneId: "zone-a",
    assetId: "asset-3",
    priority: "P1",
    expectedRiskReduction: 18,
    etaMinutes: 25,
    resources: ["2 rescue units", "1 boat team"],
    confidence: 91,
  },
  {
    id: "rec-2",
    action: "Raise pump station output to 100%",
    rationale:
      "Central district drainage is at 82% load with rainfall continuing for 2 more hours.",
    zoneId: "zone-b",
    priority: "P2",
    expectedRiskReduction: 11,
    etaMinutes: 10,
    resources: ["Utilities control room"],
    confidence: 84,
  },
  {
    id: "rec-3",
    action: "Open cooling shelters in Zone C",
    rationale: "Surface temperature above 43 °C with 11.2k outdoor workers exposed.",
    zoneId: "zone-c",
    priority: "P3",
    expectedRiskReduction: 7,
    etaMinutes: 60,
    resources: ["3 community halls"],
    confidence: 63,
  },
];

export const cascadeNodes: CascadeNode[] = [
  { id: "c1", label: "Extreme rainfall", kind: "HAZARD", risk: "CRITICAL" },
  { id: "c2", label: "River level rise", kind: "HAZARD", risk: "CRITICAL" },
  { id: "c3", label: "Drainage saturation", kind: "SYSTEM", risk: "HIGH" },
  { id: "c4", label: "Main Bridge closure", kind: "ASSET", risk: "CRITICAL" },
  { id: "c5", label: "Power substation trip", kind: "ASSET", risk: "MODERATE" },
  { id: "c6", label: "Hospital access loss", kind: "SERVICE", risk: "HIGH" },
  { id: "c7", label: "Population isolated", kind: "POPULATION", risk: "HIGH" },
];

export const cascadeEdges: CascadeEdge[] = [
  { from: "c1", to: "c2", likelihood: 92, lagMinutes: 45 },
  { from: "c1", to: "c3", likelihood: 88, lagMinutes: 20 },
  { from: "c2", to: "c4", likelihood: 74, lagMinutes: 90 },
  { from: "c3", to: "c5", likelihood: 41, lagMinutes: 120 },
  { from: "c4", to: "c6", likelihood: 69, lagMinutes: 30 },
  { from: "c6", to: "c7", likelihood: 63, lagMinutes: 60 },
];

export const forecast: Forecast = {
  id: "fc-1",
  zoneId: "zone-a",
  hazard: "FLOOD",
  horizonHours: 12,
  issuedAt: minutesAgo(6),
  model: "CS-HYDRO v0.4",
  points: Array.from({ length: 13 }, (_, i) => {
    const base = ([62, 68, 74, 79, 83, 87, 89, 88, 84, 78, 71, 64, 58][i] ?? 58) as number;
    const spread = 3 + i * 1.4;
    return {
      timestamp: minutesAhead(i * 60),
      value: base,
      lower: Math.max(0, Math.round(base - spread)),
      upper: Math.min(100, Math.round(base + spread)),
      confidence: Math.max(48, 95 - i * 3),
    };
  }),
};

export const systemHealth: SystemHealth = {
  overallPercent: 98,
  mode: "DEMO",
  lastSyncAt: minutesAgo(2),
  services: [
    { id: "weather", label: "Weather", status: "HEALTHY", detail: "320 ms" },
    { id: "gis", label: "GIS", status: "HEALTHY", detail: "140 ms" },
    { id: "iot", label: "IoT", status: "DEGRADED", detail: "1 node offline" },
    { id: "risk", label: "Risk Engine", status: "ACTIVE", detail: "cycle 00:14" },
    { id: "alerts", label: "Alert Service", status: "HEALTHY", detail: "queue 0" },
    { id: "db", label: "Database", status: "HEALTHY", detail: "PostGIS" },
  ],
};

export const mlHealthDemo = {
  status: "ONLINE" as const,
  lstmLoaded: true,
  isolationForestLoaded: true,
  modelVersions: {
    lstm_forecaster: "CorrelatedLSTM-v1.0-synthetic",
    sensor_anomaly: "IsolationForest-v1.0-synthetic",
  },
  frameworkVersions: {
    torch: "2.14.0+cpu",
    "scikit-learn": "1.9.1",
  },
  inferenceReadiness: true,
  lastInferenceAt: minutesAgo(1),
  lastInferenceLatencyMs: 14.8,
  fallbackUsed: false,
  notes: "PyTorch LSTM and Scikit-learn IsolationForest active",
};

export const mlForecastDemo = {
  forecastAvailable: true,
  predictedRiverLevelM: 3.41,
  currentRiverLevelM: 2.84,
  deltaM: 0.57,
  forecastHorizonHours: 3,
  predictionTimestamp: minutesAgo(1),
  modelVersion: "CorrelatedLSTM-v1.0-synthetic",
  inferenceLatencyMs: 17.5,
  dataQuality: "FRESH" as const,
  fallbackUsed: false,
  confidenceCalibrated: false,
  confidenceNote: "PyTorch LSTM produces uncalibrated point estimates.",
};

export const mlEvaluationDemo = {
  timestamp: minutesAgo(2),
  disclaimer:
    "SYNTHETIC VALIDATION — NOT REAL-WORLD ACCURACY. Evaluated against synthetic holdout hydrology.",
  lstmEvaluation: {
    modelName: "CorrelatedLSTM River Forecaster",
    modelVersion: "CorrelatedLSTM-v1.0-synthetic",
    architecture: "PyTorch CorrelatedLSTM (seq_len=3, num_features=4 -> 1)",
    evaluationDatasetType: "SYNTHETIC_HOLDOUT_HYDROLOGY",
    disclaimer:
      "SYNTHETIC VALIDATION — NOT REAL-WORLD ACCURACY. Metrics derived from synthetic physical hydrology generator.",
    sampleSize: 100,
    validPredictions: 100,
    rejectedPredictions: 0,
    metrics: {
      maeMeters: 2.894,
      rmseMeters: 3.125,
      mapePercent: 18.4,
      maxAbsoluteErrorMeters: 4.82,
      meanBiasMeters: -0.42,
    },
    latencyMs: {
      mean: 16.4,
      p50: 15.2,
      p95: 22.8,
    },
    confidenceCalibrated: false,
    calibrationNote:
      "confidence_calibrated = false. Uncalibrated deterministic point estimates; safety margins maintained by deterministic risk engine.",
  },
  isolationForestEvaluation: {
    modelName: "Sensor Telemetry Isolation Forest",
    modelVersion: "IsolationForest-v1.0-synthetic",
    architecture: "Scikit-learn IsolationForest (5 features, n_estimators=100)",
    evaluationType: "UNSUPERVISED_BASELINE_AND_FAULT_INJECTIONS",
    disclaimer:
      "SIMULATION — Evaluated against synthetic baseline and injected hardware fault profiles.",
    sampleSize: 100,
    baselineAnomalyRatePercent: 8.0,
    scoreDistribution: {
      min: -0.062,
      max: 0.114,
      mean: 0.048,
      std: 0.031,
    },
    latencyMs: {
      mean: 12.1,
      p50: 11.4,
      p95: 18.2,
    },
    injectedFaultSimulations: [
      {
        faultName: "SENSOR_STUCK_FREEZE",
        description: "Hardware ADC frozen producing identical readings",
        injectedVector: {
          battery_voltage: 3.7,
          signal_dbm: -72.0,
          temp_reading_c: 28.0,
          rate_of_change_temp: 0.0,
          reading_stuck_count: 18,
        },
        detectedAsAnomaly: false,
        anomalyScore: 0.07,
        operationalStatus: "DEGRADED",
        fallbackUsed: false,
      },
      {
        faultName: "THERMAL_SPIKE_ELECTRICAL",
        description: "Abnormal sudden temperature derivative jump",
        injectedVector: {
          battery_voltage: 3.65,
          signal_dbm: -70.0,
          temp_reading_c: 58.0,
          rate_of_change_temp: 28.5,
          reading_stuck_count: 0,
        },
        detectedAsAnomaly: false,
        anomalyScore: 0.016,
        operationalStatus: "DEGRADED",
        fallbackUsed: false,
      },
      {
        faultName: "VOLTAGE_BROWNOUT",
        description: "Lithium cell depleted below operational threshold",
        injectedVector: {
          battery_voltage: 1.85,
          signal_dbm: -118.0,
          temp_reading_c: 26.0,
          rate_of_change_temp: 0.2,
          reading_stuck_count: 0,
        },
        detectedAsAnomaly: true,
        anomalyScore: -0.007,
        operationalStatus: "ANOMALOUS",
        fallbackUsed: false,
      },
      {
        faultName: "RADIO_SIGNAL_DEGRADATION",
        description: "Near complete wireless packet attenuation",
        injectedVector: {
          battery_voltage: 3.4,
          signal_dbm: -126.0,
          temp_reading_c: 27.5,
          rate_of_change_temp: 0.0,
          reading_stuck_count: 0,
        },
        detectedAsAnomaly: false,
        anomalyScore: 0.019,
        operationalStatus: "DEGRADED",
        fallbackUsed: false,
      },
    ],
    groundTruthNote:
      "Unsupervised model. Real-world accuracy cannot be claimed without field-labeled ground truth.",
  },
  failureModeTesting: {
    allFailureModesHandled: true,
    lstmFailureTests: [
      {
        test: "LSTM Insufficient History (1 step)",
        handledGracefully: true,
        reason: "Invalid sequence shape. Expected (3, 4)",
      },
      {
        test: "LSTM NaN Value Injection",
        handledGracefully: true,
        reason: "Sequence contains NaN or Infinite values",
      },
      {
        test: "LSTM Inf Value Injection",
        handledGracefully: true,
        reason: "Sequence contains NaN or Infinite values",
      },
      {
        test: "LSTM Out of Bounds Rainfall (500mm)",
        handledGracefully: true,
        reason: "Feature outside bounds [0.0, 300.0]",
      },
    ],
    isolationForestFailureTests: [
      {
        test: "Sensor Missing Telemetry Fields",
        handledGracefully: true,
        reason: "Missing required telemetry feature",
      },
      {
        test: "Sensor Voltage Out of Bounds (12.5V)",
        handledGracefully: true,
        reason: "Feature value outside bounds [0.5, 6.0]",
      },
    ],
    climateShieldResilience:
      "VERIFIED — Zero system crashes; fallback engaged on all anomalous/corrupted inputs.",
  },
  deterministicPrimacyPrinciple: "ML advisory — deterministic risk engine remains authoritative.",
};

export const mlOperationalScenarioDemo = {
  scenarioName: "MIDSTREAM_CREST_EARLY_WARNING",
  zoneId: "zone-a",
  targetNode: "RN-01 (Midstream Gauge)",
  currentState: {
    riverStageM: 4.85,
    deterministicZoneRiskScore: 62.4,
    deterministicStatus: "ELEVATED",
    baselinePriority: "P2_ELEVATED",
  },
  mlForecast: {
    forecastHorizonHours: 3,
    predictedStageM: 6.45,
    predictedDeltaM: 1.6,
    advisoryStatement:
      "Forecast indicates elevated future river-stage risk. River level projected to rise from 4.85m to 6.45m (+1.6m) in 3h, crossing warning threshold (6.0m).",
    guaranteeStatement:
      "Forecast indicates elevated future river-stage risk — not an absolute flood guarantee.",
  },
  responseAdaptation: {
    priorityEscalation: "P2_ELEVATED -> P1_IMMEDIATE",
    rationale:
      "Proactive preparedness ahead of crest allows deploying mobile barriers prior to road inundation.",
    recommendedResources: [
      {
        type: "MOBILE_FLOOD_BARRIER",
        quantity: 2,
        stagingLocation: "Midstream Sector 4 Low Culvert",
        action: "Pre-deploy modular defense barrier",
      },
      {
        type: "HIGH_CAPACITY_DEWATERING_PUMP",
        quantity: 1,
        stagingLocation: "Sub-station Drainage Pit RN-01",
        action: "Stage emergency pump for immediate activation",
      },
    ],
  },
  governanceNote: "ML advisory — deterministic risk engine remains authoritative.",
};

export const digitalTwinScenariosDemo = {
  count: 7,
  governance_note:
    "Constrained Climate Resilience Digital Twin operates 100% in-memory without database mutations. Terminology uses strictly modeled, projected, and estimated quantities.",
  scenarios: [
    {
      scenario_id: "river_rise_0_5m",
      name: "River Rise +0.5m",
      category: "ENVIRONMENTAL_SURGE",
      description:
        "Simulates an upstream hydrological crest resulting in a +0.50m river stage surge along the urban corridor.",
      projected_headline:
        "Modeled river stage rise of +0.50m increases Zone A flood risk into high-critical threshold.",
      parameters: {
        environmental: { river_level_delta_m: 0.5 },
      },
    },
    {
      scenario_id: "rainfall_surge_30pct",
      name: "Rainfall Surge +30%",
      category: "ENVIRONMENTAL_SURGE",
      description:
        "Simulates severe convective cloudburst storm cell adding +30% rainfall intensity across all urban zones.",
      projected_headline:
        "Modeled +30% rainfall increases municipal drainage stress by 18% across low-elevation sectors.",
      parameters: {
        environmental: { rainfall_intensity_pct: 30.0 },
      },
    },
    {
      scenario_id: "hospital_road_blocked",
      name: "Hospital Road Inundation / Blocked",
      category: "INFRASTRUCTURE_SEVERANCE",
      description:
        "Simulates critical arterial road submergence severing direct emergency access to King George District Hospital.",
      projected_headline:
        "Loss of primary hospital route increases detour transit by +14.5 minutes, elevating cascading mortality risk.",
      parameters: {
        infrastructure: { hospital_road_available: false },
        response: { response_delay_minutes: 15 },
      },
    },
    {
      scenario_id: "deploy_2_pumps",
      name: "Deploy 2x High-Capacity Pumps",
      category: "TACTICAL_INTERVENTION",
      description:
        "Counterfactual deployment of 2 mobile 5000 GPM dewatering pumps at low-lying drainage culverts.",
      projected_headline:
        "Estimated drainage drawdown mitigates flood dwell time by 3.2 hours and lowers local composite risk.",
      parameters: {
        response: { pumps_deployed: 2 },
      },
    },
    {
      scenario_id: "deploy_barriers",
      name: "Deploy 500m Modular Flood Barriers",
      category: "TACTICAL_INTERVENTION",
      description:
        "Deployment of 500 meters of rapidly erectable inflatable rubber flood barriers along the riverbank promenade.",
      projected_headline:
        "Temporary flood wall contains overbank crest up to 0.45m depth, protecting commercial and hospital access.",
      parameters: {
        infrastructure: { barrier_deployed_km: 0.5 },
        response: { barriers_deployed_units: 4 },
      },
    },
    {
      scenario_id: "sensor_outage",
      name: "Upstream Sensor Outage (Offline)",
      category: "SENSOR_DEGRADATION",
      description:
        "Simulates sudden communication failure at Upstream Hydrological Gauge SN-UP-01 during a rise event.",
      projected_headline:
        "Loss of primary upstream telemetry reduces composite operational confidence score from 85% to 58%.",
      parameters: {
        sensor_confidence: {
          sensor_status_overrides: { "SN-UP-01": "OFFLINE" },
        },
      },
    },
    {
      scenario_id: "do_nothing",
      name: "Do Nothing (No Intervention Counterfactual)",
      category: "COUNTERFACTUAL_BASELINE",
      description:
        "Evaluates the unmitigated hazard progression assuming zero additional pumps, barriers, or rerouting.",
      projected_headline:
        "Unmitigated hazard results in cumulative flood inundation across 3 critical infrastructure zones.",
      parameters: {
        environmental: { river_level_delta_m: 0.4, rainfall_intensity_pct: 20.0 },
      },
    },
  ],
};

export const digitalTwinRunDemo = {
  simulation_id: "SIM-DEMO-2026",
  scenario_id: "river_rise_0_5m",
  scenario_name: "River Rise +0.5m",
  timestamp: new Date().toISOString(),
  execution_latency_ms: 38.4,
  ml_forecast_integrated: true,
  ml_advisory_note:
    "ML advisory forecast integrated: projected river stage at +3h is 4.62m (+0.50m change). Deterministic risk engine remains authoritative.",
  baseline_overall_risk: 32,
  simulated_overall_risk: 54,
  modeled_risk_delta: 22,
  modeled_risk_delta_pct: 68.8,
  simulated_residual_risk: 28,
  response_priority: "P2_ELEVATED",
  best_modeled_option: "Rapid Deployment of 500m Modular Flood Barriers",
  estimated_population_protected: 36500,
  critical_assets_safeguarded: 3,
  metrics_comparison: [
    {
      metric_name: "Overall City Composite Risk",
      unit: "Score [0-100]",
      baseline: 32.0,
      simulated: 54.0,
      absolute_delta: 22.0,
      percentage_delta: 68.8,
      interpretation: "MODELED IMPACT: Risk elevates by 22 points (68.8%).",
    },
    {
      metric_name: "Peak River Stage",
      unit: "meters (m)",
      baseline: 4.12,
      simulated: 4.62,
      absolute_delta: 0.5,
      percentage_delta: 12.1,
      interpretation: "PROJECTED: Midstream water level rises by 0.50m.",
    },
    {
      metric_name: "Precipitation Intensity",
      unit: "mm/h",
      baseline: 15.0,
      simulated: 15.0,
      absolute_delta: 0.0,
      percentage_delta: 0.0,
      interpretation: "MODELED IMPACT: Storm runoff stress modifies by +0.0%.",
    },
    {
      metric_name: "Estimated Population in Elevated Risk",
      unit: "Residents",
      baseline: 18000.0,
      simulated: 54500.0,
      absolute_delta: 36500.0,
      percentage_delta: 202.8,
      interpretation: "ESTIMATED POPULATION PROTECTED potential across high-risk zones.",
    },
    {
      metric_name: "Critical Assets Threatened",
      unit: "Infrastructure Nodes",
      baseline: 2.0,
      simulated: 4.0,
      absolute_delta: 2.0,
      percentage_delta: 100.0,
      interpretation: "MODELED IMPACT: 4 assets in threatened hazard envelopes.",
    },
    {
      metric_name: "Modeled Residual Risk (Post-Intervention)",
      unit: "Score [0-100]",
      baseline: 54.0,
      simulated: 28.0,
      absolute_delta: -26.0,
      percentage_delta: -48.1,
      interpretation:
        "SIMULATED RISK REDUCTION: Applying 'Rapid Deployment of 500m Modular Flood Barriers' reduces composite risk to 28.",
    },
  ],
  affected_zones: [
    {
      zone_id: "ZONE-A",
      name: "Old Town Riverbank",
      baseline_risk: 42,
      simulated_risk: 76,
      risk_delta: 34,
      dominant_hazard: "FLOOD",
      status: "HIGH",
      population: 45000,
      elevation_m: 6.2,
    },
    {
      zone_id: "ZONE-B",
      name: "Midstream Industrial Park",
      baseline_risk: 31,
      simulated_risk: 51,
      risk_delta: 20,
      dominant_hazard: "DRAINAGE_STRESS",
      status: "ELEVATED",
      population: 28000,
      elevation_m: 14.5,
    },
    {
      zone_id: "ZONE-C",
      name: "Coastal Port Corridor",
      baseline_risk: 24,
      simulated_risk: 36,
      risk_delta: 12,
      dominant_hazard: "WATERLOGGING",
      status: "MODERATE",
      population: 62000,
      elevation_m: 4.8,
    },
  ],
  affected_assets: [
    {
      asset_id: "ASSET-HOSPITAL",
      name: "King George District Hospital",
      category: "HEALTHCARE",
      asset_type: "HEALTHCARE",
      criticality: "TIER_1",
      status: "ACCESSIBILITY_THREATENED",
      baseline_status: "OPERATIONAL",
      simulated_status: "ACCESSIBILITY_THREATENED",
      flood_depth_m: 0.15,
      is_access_compromised: true,
    },
    {
      asset_id: "ASSET-SUBSTATION",
      name: "220kV Port Power Substation",
      category: "POWER",
      asset_type: "POWER",
      criticality: "TIER_1",
      status: "SURCHARGE_RISK",
      baseline_status: "OPERATIONAL",
      simulated_status: "SURCHARGE_RISK",
      flood_depth_m: 0.08,
      is_access_compromised: false,
    },
    {
      asset_id: "ASSET-PUMP-01",
      name: "Old Town Stormwater Pump Station",
      category: "WATER_INFRASTRUCTURE",
      asset_type: "WATER_INFRASTRUCTURE",
      criticality: "TIER_2",
      status: "AT_CAPACITY",
      baseline_status: "OPERATIONAL",
      simulated_status: "AT_CAPACITY",
      flood_depth_m: 0.28,
      is_access_compromised: false,
    },
  ],
  cascade_changes: [
    {
      node_id: "RIVER_SURGE",
      name: "Upstream River Swell",
      baseline_risk: "MODERATE",
      simulated_risk: "CRITICAL",
      propagation_state: "ACTIVE_CASCADE_CHAIN",
    },
    {
      node_id: "CULVERT_SURCHARGE",
      name: "Sector 4 Culvert Backwater",
      baseline_risk: "MODERATE",
      simulated_risk: "HIGH",
      propagation_state: "ACTIVE_CASCADE_CHAIN",
    },
    {
      node_id: "HOSPITAL_ACCESS",
      name: "District Hospital Direct Access Road",
      baseline_risk: "MODERATE",
      simulated_risk: "HIGH",
      propagation_state: "ACTIVE_CASCADE_CHAIN",
    },
  ],
  intervention_ranking: [
    {
      rank: 1,
      intervention_id: "INT-02-BARRIER",
      name: "Rapid Deployment of 500m Modular Flood Barriers",
      category: "BARRIER",
      modeled_risk_reduction_points: 26,
      estimated_population_protected: 36500,
      critical_assets_safeguarded: 3,
      estimated_cost_usd: 12000,
      response_eta_minutes: 35,
      cascade_interruption_factor: 0.88,
      multi_attribute_utility_score: 0.842,
      is_best_modeled_option: true,
      description:
        "Deploys inflatable rubber flood defenses along riverbank promenade to prevent overland street flooding.",
    },
    {
      rank: 2,
      intervention_id: "INT-01-PUMP",
      name: "Pre-stage 2x 5000 GPM Dewatering Pumps",
      category: "PUMP",
      modeled_risk_reduction_points: 21,
      estimated_population_protected: 31000,
      critical_assets_safeguarded: 2,
      estimated_cost_usd: 8500,
      response_eta_minutes: 20,
      cascade_interruption_factor: 0.82,
      multi_attribute_utility_score: 0.795,
      is_best_modeled_option: false,
      description:
        "Pre-positions high-capacity diesel pumps at Sector 4 culvert, mitigating stormwater buildup prior to river peak.",
    },
    {
      rank: 3,
      intervention_id: "INT-04-REROUTE",
      name: "Emergency Arterial Rerouting & High-Ground Corridor",
      category: "REROUTING",
      modeled_risk_reduction_points: 16,
      estimated_population_protected: 22000,
      critical_assets_safeguarded: 2,
      estimated_cost_usd: 3200,
      response_eta_minutes: 10,
      cascade_interruption_factor: 0.75,
      multi_attribute_utility_score: 0.718,
      is_best_modeled_option: false,
      description:
        "Establishes police-escorted bypass corridor via NH-16 high-ground overpass ensuring uninterrupted hospital transit.",
    },
    {
      rank: 4,
      intervention_id: "INT-03-RESCUE",
      name: "Pre-position 3x NDRF Swift-Water Rescue Teams",
      category: "RESCUE",
      modeled_risk_reduction_points: 15,
      estimated_population_protected: 25000,
      critical_assets_safeguarded: 1,
      estimated_cost_usd: 5000,
      response_eta_minutes: 15,
      cascade_interruption_factor: 0.65,
      multi_attribute_utility_score: 0.684,
      is_best_modeled_option: false,
      description:
        "Stages specialized emergency inflatable boats and medical first-responders at Dolphin's Nose staging depot.",
    },
    {
      rank: 5,
      intervention_id: "INT-05-POWER",
      name: "Auxiliary Mobile Diesel Generator to 220kV Substation",
      category: "POWER",
      modeled_risk_reduction_points: 12,
      estimated_population_protected: 21000,
      critical_assets_safeguarded: 2,
      estimated_cost_usd: 6500,
      response_eta_minutes: 25,
      cascade_interruption_factor: 0.78,
      multi_attribute_utility_score: 0.635,
      is_best_modeled_option: false,
      description:
        "Dispatches self-contained 1.2 MW mobile generator to safeguard industrial drainage grid if primary feeder trips.",
    },
  ],
  modeled_impact_statement:
    "MODELED IMPACT: Under scenario 'River Rise +0.5m', simulated composite risk shifts to 54 (+68.8% vs baseline). Implementing 'Rapid Deployment of 500m Modular Flood Barriers' yields an estimated SIMULATED RISK REDUCTION of 26 points, safeguarding an estimated 36,500 residents.",
  assumptions: [
    "Simulation is evaluated entirely in-memory and does not mutate active production database records.",
    "Hydrological flood stage uses Saint-Venant 1D routing approximation with threshold overflow rules.",
    "Runoff rates assume uniform catchment infiltration until soil saturation threshold is crossed.",
    "Resource dispatch calculations assume unimpeded secondary corridors unless specifically designated closed.",
  ],
  warnings: [
    "WARNING: Modeled river stage exceeds flood wall containment threshold (4.5m) in Sector 4.",
  ],
  data_quality: "SIMULATION_HYPOTHETICAL",
  deterministic_safety_note:
    "ML advisory — deterministic risk engine remains authoritative. In-memory simulation with zero database mutation.",
};
