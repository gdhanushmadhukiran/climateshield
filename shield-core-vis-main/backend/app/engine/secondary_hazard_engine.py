"""ClimateShield Secondary Hazards Engine.

Computes deterministic hazard scores for urban drainage stress, coastal storm surge,
and industrial particulate air quality index.
"""

from typing import Dict, Any
from app.engine.base import clamp, linear_scale


class SecondaryHazardEngine:
    """Calculates deterministic secondary hazard scores [0, 100]."""

    @staticmethod
    def calculate_drainage_stress(
        drainage_pump_capacity_pct: float = 85.0,
        soil_saturation_pct: float = 65.0,
        surface_runoff_m_s: float = 1.2,
    ) -> Dict[str, Any]:
        """Calculates urban drainage bottleneck stress."""
        pump_deficit = max(0.0, 100.0 - drainage_pump_capacity_pct)
        saturation_factor = clamp(soil_saturation_pct, 0.0, 100.0)
        runoff_score = linear_scale(surface_runoff_m_s, 0.5, 4.5, 10.0, 95.0)

        # 45% pump deficit, 35% soil saturation, 20% runoff velocity
        drainage_score = (0.45 * pump_deficit) + (0.35 * saturation_factor) + (0.20 * runoff_score)
        drainage_score = round(clamp(drainage_score, 0.0, 100.0), 1)

        return {
            "hazard_name": "DRAINAGE_STRESS",
            "score": drainage_score,
            "pump_capacity_pct": round(drainage_pump_capacity_pct, 1),
            "soil_saturation_pct": round(soil_saturation_pct, 1),
            "surface_runoff_m_s": round(surface_runoff_m_s, 2),
        }

    @staticmethod
    def calculate_coastal_surge(storm_surge_m: float = 0.5) -> Dict[str, Any]:
        """Calculates coastal storm surge hazard score."""
        # < 0.5m: baseline (0-15)
        # 0.5m - 1.2m: moderate (15-50)
        # 1.2m - 2.0m: high (50-80)
        # > 2.0m: critical (80-100)
        if storm_surge_m < 0.5:
            surge_score = linear_scale(storm_surge_m, 0.0, 0.5, 0.0, 15.0)
        elif storm_surge_m < 1.2:
            surge_score = linear_scale(storm_surge_m, 0.5, 1.2, 15.0, 50.0)
        elif storm_surge_m < 2.0:
            surge_score = linear_scale(storm_surge_m, 1.2, 2.0, 50.0, 80.0)
        else:
            surge_score = linear_scale(storm_surge_m, 2.0, 3.5, 80.0, 100.0)

        surge_score = round(clamp(surge_score, 0.0, 100.0), 1)

        return {
            "hazard_name": "COASTAL_SURGE",
            "score": surge_score,
            "surge_height_m": round(storm_surge_m, 2),
        }

    @staticmethod
    def calculate_air_quality(aqi: float = 65.0) -> Dict[str, Any]:
        """Calculates Air Quality Index hazard score."""
        # Standard AQI scale: 0-50 Good, 51-100 Moderate, 101-150 Sensitive, 151-200 Unhealthy, 201-300 Very Unhealthy
        score = linear_scale(aqi, 20.0, 300.0, 5.0, 95.0)
        return {
            "hazard_name": "AIR_QUALITY",
            "score": round(clamp(score, 0.0, 100.0), 1),
            "aqi_value": round(aqi, 1),
        }
