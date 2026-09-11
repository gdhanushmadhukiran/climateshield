/**
 * API Data Adapters
 * Safely maps raw API payloads into typed frontend contracts.
 * Normalizes GeoJSON coordinate rings, drivers, and nullability.
 */

import type {
  RiskZone,
  RiskDriver,
  RiskScore,
  Incident,
  Alert,
  Recommendation,
  RiverNode,
  Forecast,
  CascadeNode,
  CascadeEdge,
} from "@/types/climate";
import { riskLevelFromScore } from "@/lib/risk";

export function adaptRiskZone(raw: Record<string, unknown>): RiskZone {
  const risk = raw.risk as Record<string, unknown> | undefined;
  const scoreVal = typeof risk?.value === "number" ? risk.value : 50;

  const rawDrivers = Array.isArray(raw.drivers) ? (raw.drivers as Record<string, unknown>[]) : [];
  const drivers: RiskDriver[] = rawDrivers.map((d, i) => ({
    id: String(d.id ?? `driver-${i}`),
    label: String(d.label ?? "Driver"),
    contribution: Number(d.contribution ?? 0),
    value: String(d.value ?? `${d.metricValue ?? 0} ${d.unit ?? ""}`.trim()),
    trend: (["RISING", "FALLING", "STABLE"].includes(String(d.trend))
      ? d.trend
      : "STABLE") as RiskDriver["trend"],
  }));

  // Handle GeoJSON geometry: extract 2D outer ring whether nested as Polygon [[[lng, lat]]] or flat [[lng, lat]]
  let polygon: [number, number][] = [];
  if (Array.isArray(raw.polygon)) {
    const p = raw.polygon;
    if (p.length > 0 && Array.isArray(p[0]) && Array.isArray(p[0][0])) {
      polygon = p[0] as [number, number][];
    } else {
      polygon = p as [number, number][];
    }
  }

  const centroidObj = (raw.centroid ?? {}) as { lat?: number; lng?: number };

  const riskScore: RiskScore = {
    value: scoreVal,
    level: (risk?.level as RiskScore["level"]) ?? riskLevelFromScore(scoreVal),
    confidence: Number(risk?.confidence ?? 80),
    velocityPerHour: Number(risk?.velocityPerHour ?? 0),
    observedAt: String(risk?.observedAt ?? new Date().toISOString()),
    quality: (risk?.quality as RiskScore["quality"]) ?? "FRESH",
  };

  return {
    id: String(raw.id ?? "zone-unknown"),
    name: String(raw.name ?? "Unknown Zone"),
    code: String(raw.code ?? "ZN"),
    population: Number(raw.population ?? 0),
    areaKm2: Number(raw.areaKm2 ?? 0),
    dominantHazard: (raw.dominantHazard as RiskZone["dominantHazard"]) ?? "FLOOD",
    risk: riskScore,
    drivers,
    centroid: {
      lat: Number(centroidObj.lat ?? 17.385),
      lng: Number(centroidObj.lng ?? 78.4867),
    },
    polygon,
  };
}

export function adaptIncident(raw: Record<string, unknown>): Incident {
  const loc = (raw.location ?? raw.coordinates ?? {}) as { lat?: number; lng?: number };
  return {
    id: String(raw.id ?? `inc-${Date.now()}`),
    ref: String(raw.ref ?? "INC"),
    title: String(raw.title ?? "Incident"),
    hazard: (raw.hazard as Incident["hazard"]) ?? "FLOOD",
    zoneId: String(raw.zoneId ?? "zone-a"),
    severity: (raw.severity as Incident["severity"]) ?? "WARNING",
    reportedAt: String(raw.reportedAt ?? new Date().toISOString()),
    status: (raw.status as Incident["status"]) ?? "OPEN",
    location: {
      lat: Number(loc.lat ?? 17.7041),
      lng: Number(loc.lng ?? 83.2977),
    },
    affectedPopulation: Number(raw.affectedPopulation ?? raw.affected_population ?? 0),
    source: (raw.source as Incident["source"]) ?? "OPERATOR",
  };
}

export function adaptAlert(raw: Record<string, unknown>): Alert {
  const alert: Alert = {
    id: String(raw.id ?? `alr-${Date.now()}`),
    ref: String(raw.ref ?? "ALR"),
    title: String(raw.title ?? "Alert"),
    message: String(raw.message ?? ""),
    severity: (raw.severity as Alert["severity"]) ?? "WARNING",
    issuedAt: String(raw.issuedAt ?? new Date().toISOString()),
    channels: Array.isArray(raw.channels) ? (raw.channels as Alert["channels"]) : ["SMS"],
    deliveryStatus: (raw.deliveryStatus as Alert["deliveryStatus"]) ?? "SENT",
    acknowledged: Boolean(raw.acknowledged),
  };
  if (raw.zoneId !== undefined && raw.zoneId !== null) {
    alert.zoneId = String(raw.zoneId);
  }
  return alert;
}

export function adaptRiverNode(raw: Record<string, unknown>): RiverNode {
  const loc = (raw.location ?? raw.coordinates ?? {}) as { lat?: number; lng?: number };
  const readings = Array.isArray(raw.readings) ? (raw.readings as RiverNode["readings"]) : [];

  const node: RiverNode = {
    id: String(raw.id ?? "river-node"),
    code: String(raw.code ?? raw.id ?? "RN"),
    name: String(raw.name ?? "River Node"),
    zoneId: String(raw.zoneId ?? "zone-a"),
    segment: (raw.segment as RiverNode["segment"]) ?? "MIDSTREAM",
    location: {
      lat: Number(loc.lat ?? 17.7041),
      lng: Number(loc.lng ?? 83.2977),
    },
    status: (raw.status as RiverNode["status"]) ?? "HEALTHY",
    batteryPercent: Number(raw.batteryPercent ?? 100),
    signalPercent: Number(raw.signalPercent ?? 100),
    lastPacketAt: String(raw.lastPacketAt ?? new Date().toISOString()),
    waterLevelM: Number(raw.waterLevelM ?? 0),
    thresholdM: Number(raw.thresholdM ?? 4),
    travelTimeMinutes: Number(raw.travelTimeMinutes ?? 0),
    rateOfRiseMPerHour:
      raw.rateOfRiseMPerHour !== undefined ? Number(raw.rateOfRiseMPerHour) : undefined,
    timeToThresholdMinutes:
      raw.timeToThresholdMinutes !== undefined ? Number(raw.timeToThresholdMinutes) : undefined,
    dataQuality: raw.dataQuality !== undefined ? String(raw.dataQuality) : undefined,
    readings,
  };

  if (raw.downstreamNodeId !== undefined && raw.downstreamNodeId !== null) {
    node.downstreamNodeId = String(raw.downstreamNodeId);
  }

  return node;
}

export function adaptCascade(raw: Record<string, unknown>): {
  nodes: CascadeNode[];
  edges: CascadeEdge[];
} {
  const nodes = Array.isArray(raw.nodes) ? (raw.nodes as CascadeNode[]) : [];
  const edges = Array.isArray(raw.edges) ? (raw.edges as CascadeEdge[]) : [];
  return { nodes, edges };
}
