"""ClimateShield Spatial Exposure Engine.

Calculates deterministic exposure index E in [0, 1.0] by spatially evaluating
population density and critical infrastructure asset density by tier.
"""

from typing import List, Dict, Any
from app.engine.base import clamp


class ExposureEngine:
    """Evaluates who and what is exposed within a risk zone."""

    # Reference maximum density for normalization: 25,000 people / km2
    MAX_POP_DENSITY = 25000.0

    @classmethod
    def calculate(
        cls,
        population: int,
        area_km2: float,
        assets: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        area = max(0.1, area_km2)
        pop_density = population / area

        # 1. Population Exposure Index [0, 1.0]
        pop_index = clamp(pop_density / cls.MAX_POP_DENSITY, 0.05, 1.0)

        # 2. Critical Infrastructure Asset Tally & Weighting
        tier_counts = {"TIER_1": 0, "TIER_2": 0, "TIER_3": 0}
        tier_weights = {"TIER_1": 1.0, "TIER_2": 0.6, "TIER_3": 0.3}

        weighted_asset_score = 0.0
        affected_assets = []

        for a in assets:
            crit = a.get("criticality", "TIER_3")
            tier_counts[crit] = tier_counts.get(crit, 0) + 1
            w = tier_weights.get(crit, 0.3)
            weighted_asset_score += w
            affected_assets.append({
                "id": a.get("id"),
                "name": a.get("name"),
                "type": a.get("asset_type"),
                "criticality": crit,
                "status": a.get("status", "OPERATIONAL"),
            })

        # Asset Exposure Index: normalized against reference threshold of 5 weighted assets
        asset_index = clamp(weighted_asset_score / 5.0, 0.0, 1.0)

        # Composite Exposure Index E [0, 1.0]: 60% population, 40% critical assets
        composite_exposure = (0.60 * pop_index) + (0.40 * asset_index)
        composite_exposure = round(clamp(composite_exposure, 0.05, 1.0), 3)

        return {
            "exposure_index": composite_exposure,
            "population": population,
            "population_density_per_km2": round(pop_density, 1),
            "pop_exposure_index": round(pop_index, 3),
            "asset_exposure_index": round(asset_index, 3),
            "total_assets_count": len(assets),
            "tier_counts": tier_counts,
            "affected_assets": affected_assets,
        }
