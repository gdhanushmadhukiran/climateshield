"""ClimateShield Confidence & Data Quality Engine.

Evaluates operational confidence [35, 99]% based on observation freshness,
sensor node health states, and missing telemetry telemetry streams.
"""

from typing import List, Dict, Any
from app.engine.base import clamp


class ConfidenceEngine:
    """Calculates operational confidence and audits missing data."""

    BASE_CONFIDENCE = 98.0

    @classmethod
    def calculate(
        cls,
        data_quality: str = "FRESH",
        sensors: List[Dict[str, Any]] = None,
        missing_metrics: List[str] = None,
        observation_age_minutes: float = 2.0,
    ) -> Dict[str, Any]:
        sensors = sensors or []
        missing_metrics = missing_metrics or []
        penalties: List[Dict[str, Any]] = []
        missing_audit: List[str] = []

        total_penalty = 0.0

        # 1. Freshness Penalty
        if data_quality == "STALE" or observation_age_minutes > 30.0:
            pen = 15.0
            total_penalty += pen
            penalties.append({"reason": "Telemetry is STALE (>30m)", "penalty": pen})
            missing_audit.append("Real-time telemetry stream is stale (>30 minutes old)")
        elif data_quality == "AGING" or observation_age_minutes > 15.0:
            pen = 6.0
            total_penalty += pen
            penalties.append({"reason": "Telemetry is AGING (>15m)", "penalty": pen})
            missing_audit.append("Real-time telemetry stream is aging (>15 minutes old)")

        # 2. Sensor Node Health Penalties
        for s in sensors:
            status = s.get("status", "HEALTHY")
            code = s.get("code", s.get("id", "UNKNOWN"))
            if status == "OFFLINE":
                pen = 20.0
                total_penalty += pen
                penalties.append({"reason": f"Sensor {code} is OFFLINE", "penalty": pen})
                missing_audit.append(f"Primary IoT node {code} is OFFLINE")
            elif status == "DEGRADED":
                pen = 10.0
                total_penalty += pen
                penalties.append({"reason": f"Sensor {code} is DEGRADED (low battery/signal)", "penalty": pen})
                missing_audit.append(f"IoT node {code} battery or signal degraded")

        # 3. Missing Metric Penalties
        for m in missing_metrics:
            pen = 8.0
            total_penalty += pen
            penalties.append({"reason": f"Missing metric stream: {m}", "penalty": pen})
            missing_audit.append(f"Observation feed missing parameter: {m}")

        # Final Confidence [35, 99]
        confidence_val = int(clamp(cls.BASE_CONFIDENCE - total_penalty, 35.0, 99.0))

        # Overall data quality label
        if any(s.get("status") == "OFFLINE" for s in sensors) or observation_age_minutes > 60:
            overall_quality = "STALE"
        elif any(s.get("status") == "DEGRADED" for s in sensors) or observation_age_minutes > 30:
            overall_quality = "DEGRADED"
        elif observation_age_minutes > 15:
            overall_quality = "AGING"
        else:
            overall_quality = "FRESH"

        return {
            "confidence": confidence_val,
            "data_quality": overall_quality,
            "total_penalty": round(total_penalty, 1),
            "penalties": penalties,
            "missing_or_degraded_inputs": missing_audit,
        }
