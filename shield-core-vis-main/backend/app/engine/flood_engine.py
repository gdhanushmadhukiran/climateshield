"""ClimateShield Hydrological Flood Hazard Engine.

Deterministic calculation of spatial flood hazard from river stage, rate of rise,
upstream pulse propagation, rainfall intensity, and topographical elevation.
"""

from typing import Dict, Any, Optional
from app.engine.base import clamp, linear_scale


class FloodHazardEngine:
    """Calculates deterministic flood hazard score [0, 100] for a spatial zone."""

    @staticmethod
    def calculate(
        water_level_m: Optional[float],
        threshold_m: float = 3.5,
        rate_of_rise_m_h: float = 0.0,
        rainfall_intensity_mm_h: float = 0.0,
        rainfall_24h_mm: float = 0.0,
        upstream_water_ratio: Optional[float] = None,
        elevation_m: float = 12.0,
    ) -> Dict[str, Any]:
        # 1. Water level to threshold ratio
        level = water_level_m if water_level_m is not None else (threshold_m * 0.6)
        level_ratio = level / threshold_m if threshold_m > 0 else 0.5

        if level_ratio < 0.6:
            score_level = linear_scale(level_ratio, 0.0, 0.6, 5.0, 30.0)
        elif level_ratio <= 1.0:
            score_level = linear_scale(level_ratio, 0.6, 1.0, 30.0, 75.0)
        else:
            # Over threshold: 75 to 100
            score_level = linear_scale(level_ratio, 1.0, 1.3, 75.0, 100.0)

        # 2. Rate of rise surge penalty
        surge_penalty = 0.0
        if rate_of_rise_m_h > 0.05:
            # Scale from 0.05 to 0.5 m/h -> 0 to 20 penalty points
            surge_penalty = linear_scale(rate_of_rise_m_h, 0.05, 0.50, 2.0, 20.0)
        elif rate_of_rise_m_h < -0.05:
            # Falling river level provides relief
            surge_penalty = -5.0

        # 3. Rainfall factor
        rain_score = linear_scale(rainfall_intensity_mm_h, 0.0, 60.0, 0.0, 100.0)
        rain_accum_factor = min(1.2, 1.0 + (rainfall_24h_mm / 250.0))

        # 4. Upstream propagation pulse
        upstream_surge = 0.0
        if upstream_water_ratio is not None and upstream_water_ratio > 0.9:
            # If upstream is near or over threshold, downstream inherits surge pressure
            upstream_surge = linear_scale(upstream_water_ratio, 0.9, 1.2, 5.0, 25.0)

        # 5. Topographical elevation modifier
        # Lower elevation (e.g. <= 5m) accumulates water; higher elevation drains
        elevation_factor = clamp(1.15 - (elevation_m / 60.0), 0.70, 1.20)

        # Combine weighted sub-components
        # 50% river stage, 30% rainfall, 20% upstream pulse + surge penalty
        base_hazard = (0.50 * score_level) + (0.30 * rain_score) + (0.20 * max(score_level, upstream_surge))
        adjusted_hazard = (base_hazard + surge_penalty) * rain_accum_factor * elevation_factor

        final_score = round(clamp(adjusted_hazard, 0.0, 100.0), 1)

        return {
            "hazard_name": "FLOOD",
            "score": final_score,
            "water_level_m": level,
            "threshold_m": threshold_m,
            "level_ratio": round(level_ratio, 2),
            "rate_of_rise_m_h": round(rate_of_rise_m_h, 2),
            "rainfall_intensity_mm_h": round(rainfall_intensity_mm_h, 1),
            "surge_penalty": round(surge_penalty, 1),
            "upstream_surge": round(upstream_surge, 1),
        }
