import type {
  ConfidenceLevel,
  DataQuality,
  RiskLevel,
  Severity,
  ServiceStatus,
} from "@/types/climate";

/** Unified risk vocabulary: 0-29 LOW, 30-59 MODERATE, 60-79 HIGH, 80-100 CRITICAL */
export function riskLevelFromScore(score: number): RiskLevel {
  if (score >= 80) return "CRITICAL";
  if (score >= 60) return "HIGH";
  if (score >= 30) return "MODERATE";
  return "LOW";
}

export const RISK_BANDS: { level: RiskLevel; range: string }[] = [
  { level: "LOW", range: "0–29" },
  { level: "MODERATE", range: "30–59" },
  { level: "HIGH", range: "60–79" },
  { level: "CRITICAL", range: "80–100" },
];

/** Severity is never communicated by color alone: every level has a glyph. */
export const RISK_GLYPH: Record<RiskLevel, string> = {
  LOW: "▁",
  MODERATE: "▃",
  HIGH: "▅",
  CRITICAL: "▇",
};

export const riskTextClass: Record<RiskLevel, string> = {
  LOW: "text-risk-low",
  MODERATE: "text-risk-moderate",
  HIGH: "text-risk-high",
  CRITICAL: "text-risk-critical",
};

export const riskBgClass: Record<RiskLevel, string> = {
  LOW: "bg-risk-low",
  MODERATE: "bg-risk-moderate",
  HIGH: "bg-risk-high",
  CRITICAL: "bg-risk-critical",
};

export const riskBorderClass: Record<RiskLevel, string> = {
  LOW: "border-risk-low/40",
  MODERATE: "border-risk-moderate/40",
  HIGH: "border-risk-high/40",
  CRITICAL: "border-risk-critical/50",
};

export const severityRank: Record<Severity, RiskLevel> = {
  INFO: "LOW",
  ADVISORY: "MODERATE",
  WARNING: "HIGH",
  EMERGENCY: "CRITICAL",
};

export function confidenceLevel(percent: number): ConfidenceLevel {
  if (percent >= 80) return "HIGH";
  if (percent >= 60) return "MEDIUM";
  return "LOW";
}

export const statusToneClass: Record<ServiceStatus, string> = {
  HEALTHY: "text-risk-low",
  ACTIVE: "text-intel",
  DEGRADED: "text-risk-moderate",
  OFFLINE: "text-risk-critical",
};

export const statusDotClass: Record<ServiceStatus, string> = {
  HEALTHY: "bg-risk-low",
  ACTIVE: "bg-intel",
  DEGRADED: "bg-risk-moderate",
  OFFLINE: "bg-risk-critical",
};

export const qualityLabel: Record<DataQuality, string> = {
  FRESH: "FRESH",
  AGING: "AGING",
  STALE: "STALE",
  DEGRADED: "DEGRADED",
  UNAVAILABLE: "NO DATA",
};

/** Compact relative age, e.g. "2 MIN AGO" */
export function relativeAge(iso: string, now: Date = new Date()): string {
  const diffMs = now.getTime() - new Date(iso).getTime();
  const min = Math.max(0, Math.round(diffMs / 60000));
  if (min < 1) return "JUST NOW";
  if (min < 60) return `${min} MIN AGO`;
  const hrs = Math.round(min / 60);
  if (hrs < 24) return `${hrs} HR AGO`;
  return `${Math.round(hrs / 24)} D AGO`;
}

export function clockTime(iso: string): string {
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    hour12: true,
  });
}

export function formatVelocity(v: number): string {
  const sign = v > 0 ? "+" : v < 0 ? "−" : "±";
  return `${sign}${Math.abs(v)} / HR`;
}

export function formatCompact(n: number): string {
  return new Intl.NumberFormat("en-US", { notation: "compact", maximumFractionDigits: 1 }).format(
    n,
  );
}
