"""ClimateShield Multi-Hazard Composite Risk Engine.

Synthesizes multi-hazard scores, exposure, vulnerability, and compounding hazard multipliers
into an explainable, deterministic spatial risk score [0, 100] with driver decomposition.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.engine.base import clamp, get_risk_level


class CompositeRiskEngine:
    """Deterministic Multi-Hazard Composite Risk Synthesizer."""

    @classmethod
    def calculate(
        cls,
        dominant_hazard: str,
        flood_hazard: Dict[str, Any],
        heat_hazard: Dict[str, Any],
        drainage_hazard: Dict[str, Any],
        surge_hazard: Dict[str, Any],
        air_hazard: Dict[str, Any],
        exposure: Dict[str, Any],
        vulnerability: Dict[str, Any],
        previous_score: Optional[int] = None,
        previous_observed_at: Optional[datetime] = None,
        now: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        now = now or datetime.now(timezone.utc)
        f_score = flood_hazard.get("score", 0.0)
        h_score = heat_hazard.get("score", 0.0)
        d_score = drainage_hazard.get("score", 0.0)
        s_score = surge_hazard.get("score", 0.0)
        a_score = air_hazard.get("score", 0.0)

        # 1. Multi-Hazard Base Synthesis based on dominant hazard profile
        upper_dominant = dominant_hazard.upper()
        if "DRAINAGE" in upper_dominant:
            h_synth = (0.50 * d_score) + (0.30 * f_score) + (0.10 * s_score) + (0.10 * h_score)
        elif "HEAT" in upper_dominant:
            h_synth = (0.65 * h_score) + (0.15 * a_score) + (0.10 * d_score) + (0.10 * f_score)
        elif "SURGE" in upper_dominant or "COASTAL" in upper_dominant:
            h_synth = (0.50 * s_score) + (0.30 * f_score) + (0.10 * d_score) + (0.10 * h_score)
        else:
            # Default: Flood / Rainfall dominant
            h_synth = (0.55 * f_score) + (0.25 * d_score) + (0.10 * s_score) + (0.10 * h_score)

        # 2. Compounding Hazard Interactions
        active_interactions: List[Dict[str, Any]] = []
        compound_multiplier = 1.0

        if f_score >= 50.0 and d_score >= 50.0:
            mult = 1.15
            compound_multiplier = max(compound_multiplier, mult)
            active_interactions.append({
                "type": "FLOOD_DRAINAGE_COMPOUND",
                "description": "High river stage concurrent with urban drainage bottleneck",
                "multiplier": mult,
            })

        if f_score >= 55.0 and s_score >= 50.0:
            mult = 1.18
            compound_multiplier = max(compound_multiplier, mult)
            active_interactions.append({
                "type": "ESTUARY_BACKWATER_SURGE",
                "description": "Coastal storm surge swell impeding gravity river discharge",
                "multiplier": mult,
            })

        if h_score >= 55.0 and d_score >= 50.0:
            mult = 1.10
            compound_multiplier = max(compound_multiplier, mult)
            active_interactions.append({
                "type": "HEAT_INFRASTRUCTURE_STRAIN",
                "description": "Extreme thermal stress compounding power substation and pump station grid load",
                "multiplier": mult,
            })

        # 3. Exposure and Vulnerability Integration
        e_idx = exposure.get("exposure_index", 0.5)
        v_idx = vulnerability.get("vulnerability_index", 0.5)

        # Integrated Multi-Hazard Score [0, 100]
        raw_score = h_synth * (0.40 + (0.30 * e_idx) + (0.30 * v_idx)) * compound_multiplier
        final_score = int(round(clamp(raw_score, 0.0, 100.0)))
        level = get_risk_level(final_score)

        # 4. Velocity per hour
        velocity = 0.0
        trend = "STABLE"
        if previous_score is not None and previous_observed_at is not None:
            t_prev = previous_observed_at if previous_observed_at.tzinfo else previous_observed_at.replace(tzinfo=timezone.utc)
            t_curr = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
            delta_sec = (t_curr - t_prev).total_seconds()
            if delta_sec > 10.0:
                hours = delta_sec / 3600.0
                velocity = round((final_score - previous_score) / hours, 1)
                if velocity > 0.5:
                    trend = "RISING"
                elif velocity < -0.5:
                    trend = "FALLING"

        # 5. Explainable Risk Driver Decomposition (summing to 100.0%)
        drivers = cls._decompose_drivers(
            dominant_hazard=upper_dominant,
            flood_hazard=flood_hazard,
            heat_hazard=heat_hazard,
            drainage_hazard=drainage_hazard,
            surge_hazard=surge_hazard,
            air_hazard=air_hazard,
            trend=trend,
        )

        return {
            "score": final_score,
            "level": level,
            "velocity_per_hour": velocity,
            "trend": trend,
            "compound_multiplier": round(compound_multiplier, 2),
            "active_interactions": active_interactions,
            "synthesized_hazard_index": round(h_synth, 1),
            "exposure_index": e_idx,
            "vulnerability_index": v_idx,
            "drivers": drivers,
        }

    @staticmethod
    def _decompose_drivers(
        dominant_hazard: str,
        flood_hazard: Dict[str, Any],
        heat_hazard: Dict[str, Any],
        drainage_hazard: Dict[str, Any],
        surge_hazard: Dict[str, Any],
        air_hazard: Dict[str, Any],
        trend: str,
    ) -> List[Dict[str, Any]]:
        """Extracts top 3 drivers and normalizes contributions to exactly 100.0%."""
        candidates = []

        # 1. Flood driver
        candidates.append({
            "metric_name": "River level (upstream)",
            "metric_value": flood_hazard.get("water_level_m", 3.2),
            "unit": "m",
            "weight": flood_hazard.get("score", 20.0) * 1.2,
            "trend": "RISING" if flood_hazard.get("rate_of_rise_m_h", 0) > 0.05 else "STABLE",
        })

        # 2. Rainfall driver
        candidates.append({
            "metric_name": "Rainfall rate",
            "metric_value": flood_hazard.get("rainfall_intensity_mm_h", 12.0),
            "unit": "mm/h",
            "weight": flood_hazard.get("rainfall_intensity_mm_h", 12.0) * 1.5,
            "trend": "RISING" if flood_hazard.get("rainfall_intensity_mm_h", 0) > 20 else "STABLE",
        })

        # 3. Drainage pump capacity
        pump_cap = drainage_hazard.get("pump_capacity_pct", 85.0)
        candidates.append({
            "metric_name": "Drainage pump capacity",
            "metric_value": pump_cap,
            "unit": "%",
            "weight": max(10.0, (100.0 - pump_cap) * 1.4),
            "trend": "FALLING" if pump_cap < 75 else "STABLE",
        })

        # 4. Storm surge
        surge_m = surge_hazard.get("surge_height_m", 0.5)
        candidates.append({
            "metric_name": "Storm surge swell",
            "metric_value": surge_m,
            "unit": "m",
            "weight": surge_m * 40.0,
            "trend": "RISING" if surge_m > 1.0 else "STABLE",
        })

        # 5. Thermal index
        hi_c = heat_hazard.get("heat_index_c", 32.0)
        candidates.append({
            "metric_name": "Thermal heat index",
            "metric_value": hi_c,
            "unit": "C",
            "weight": heat_hazard.get("score", 20.0),
            "trend": "RISING" if hi_c > 38.0 else "STABLE",
        })

        # Sort candidates descending by weight and pick top 3
        candidates.sort(key=lambda x: x["weight"], reverse=True)
        top_3 = candidates[:3]

        total_w = sum(c["weight"] for c in top_3) or 1.0
        results = []
        accum = 0.0

        for i, c in enumerate(top_3):
            if i == 2:
                # Guarantee exact 100.0% sum
                pct = round(100.0 - accum, 1)
            else:
                pct = round((c["weight"] / total_w) * 100.0, 1)
                accum += pct

            results.append({
                "metric_name": c["metric_name"],
                "metric_value": c["metric_value"],
                "unit": c["unit"],
                "contribution": pct,
                "trend": c["trend"],
            })

        return results
