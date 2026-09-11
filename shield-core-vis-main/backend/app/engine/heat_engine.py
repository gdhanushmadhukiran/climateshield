"""ClimateShield Thermal Heat Hazard Engine.

Deterministic calculation of thermal stress using the NOAA Steadman Heat Index equation,
Urban Heat Island (UHI) impervious surface amplification, and atmospheric stagnation.
"""

from typing import Dict, Any
from app.engine.base import clamp, linear_scale


class HeatHazardEngine:
    """Calculates deterministic heat hazard score [0, 100] for a spatial zone."""

    @staticmethod
    def calculate_heat_index(temperature_c: float, relative_humidity_pct: float) -> float:
        """Computes the NOAA Rothfusz regression Heat Index in Celsius."""
        tf = (temperature_c * 9.0 / 5.0) + 32.0
        rh = clamp(relative_humidity_pct, 0.0, 100.0)

        if tf < 80.0:
            # Simple average approximation below 80F
            hi_f = 0.5 * (tf + 61.0 + ((tf - 68.0) * 1.2) + (rh * 0.094))
        else:
            # Full Rothfusz regression equation
            hi_f = (
                -42.379
                + (2.04901523 * tf)
                + (10.14333127 * rh)
                - (0.22475541 * tf * rh)
                - (0.00683783 * tf * tf)
                - (0.05481717 * rh * rh)
                + (0.00122874 * tf * tf * rh)
                + (0.00085282 * tf * rh * rh)
                - (0.00000199 * tf * tf * rh * rh)
            )

        hi_c = (hi_f - 32.0) * 5.0 / 9.0
        return round(hi_c, 1)

    @classmethod
    def calculate(
        cls,
        temperature_c: float = 33.0,
        relative_humidity_pct: float = 75.0,
        impervious_surface_pct: float = 40.0,
        wind_speed_km_h: float = 12.0,
    ) -> Dict[str, Any]:
        heat_index_c = cls.calculate_heat_index(temperature_c, relative_humidity_pct)

        # Map Heat Index to Base Hazard Score:
        # < 27C: minimal (< 20)
        # 27C - 32C (Caution): 20 - 45
        # 32C - 41C (Extreme Caution): 45 - 75
        # 41C - 54C (Danger): 75 - 95
        # > 54C (Extreme Danger): 95 - 100
        if heat_index_c < 27.0:
            base_score = linear_scale(heat_index_c, 18.0, 27.0, 0.0, 20.0)
        elif heat_index_c < 32.0:
            base_score = linear_scale(heat_index_c, 27.0, 32.0, 20.0, 45.0)
        elif heat_index_c < 41.0:
            base_score = linear_scale(heat_index_c, 32.0, 41.0, 45.0, 75.0)
        elif heat_index_c < 54.0:
            base_score = linear_scale(heat_index_c, 41.0, 54.0, 75.0, 95.0)
        else:
            base_score = linear_scale(heat_index_c, 54.0, 65.0, 95.0, 100.0)

        # Urban Heat Island (UHI) concrete retention adjustment: up to +8 pts for 100% concrete
        uhi_adjustment = (clamp(impervious_surface_pct, 0.0, 100.0) / 100.0) * 8.0

        # Wind cooling relief: wind > 15 km/h reduces apparent heat stress
        wind_relief = 0.0
        if wind_speed_km_h > 15.0:
            wind_relief = min(6.0, (wind_speed_km_h - 15.0) * 0.3)

        final_score = round(clamp(base_score + uhi_adjustment - wind_relief, 0.0, 100.0), 1)

        return {
            "hazard_name": "HEAT",
            "score": final_score,
            "ambient_temp_c": round(temperature_c, 1),
            "relative_humidity_pct": round(relative_humidity_pct, 1),
            "heat_index_c": heat_index_c,
            "uhi_adjustment": round(uhi_adjustment, 1),
            "wind_relief": round(wind_relief, 1),
        }
