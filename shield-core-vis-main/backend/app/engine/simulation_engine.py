"""ClimateShield What-If Simulation Engine.

Simulates counterfactual response interventions, calculating expected residual risk,
safeguarded populations, and critical asset protection metrics.
"""

from typing import Dict, Any, List


class SimulationEngine:
    """Evaluates counterfactual intervention packages against baseline risk."""

    @staticmethod
    def simulate_interventions(
        baseline_risk: int,
        interventions: List[Dict[str, Any]],
        total_population: int = 620000,
        total_assets: int = 6,
    ) -> Dict[str, Any]:
        """Calculates simulated residual risk and protection impact."""
        total_delta_risk = 0
        total_pop_protected = 0
        total_assets_protected = 0

        for item in interventions:
            delta_r = item.get("expected_reduction", 12)
            total_delta_risk += delta_r
            total_pop_protected += item.get("population_protected", int(total_population * 0.10))
            total_assets_protected += item.get("assets_protected", 1)

        # Dampen cumulative risk reduction using diminishing returns
        # delta_effective = total_delta_risk * 0.85
        effective_reduction = int(round(total_delta_risk * 0.82))
        simulated_risk = max(18, baseline_risk - effective_reduction)

        pop_protected = min(total_population, total_pop_protected)
        assets_protected = min(total_assets, total_assets_protected)

        return {
            "baseline_risk": baseline_risk,
            "simulated_risk": simulated_risk,
            "effective_risk_reduction": baseline_risk - simulated_risk,
            "population_protected": pop_protected,
            "assets_protected": assets_protected,
            "confidence": 89,
        }

    @classmethod
    def simulate_scenario(
        cls,
        scenario_id: str,
        parameters: Dict[str, Any],
        baseline_risk: int = 74,
        total_population: int = 620000,
        total_assets: int = 6,
    ) -> Dict[str, Any]:
        """Evaluates named scenarios like additional pumps, barrier extensions, or early warnings."""
        # Extract parameter inputs with defaults
        additional_pumps = int(parameters.get("additional_pumps", 0))
        barrier_km = float(parameters.get("barrier_length_km", 0.0))
        early_warning_h = float(parameters.get("early_warning_hours", 0.0))
        evac_compliance_pct = float(parameters.get("evac_compliance_pct", 75.0))

        # Calculate estimated reduction points
        pump_reduction = min(20, additional_pumps * 6)
        barrier_reduction = min(18, int(round(barrier_km * 7.5)))
        warning_reduction = min(14, int(round(early_warning_h * 3.5)))
        compliance_factor = evac_compliance_pct / 100.0

        total_reduction = int(round((pump_reduction + barrier_reduction + warning_reduction) * compliance_factor))
        simulated_risk = max(20, baseline_risk - total_reduction)

        pop_protected = int(round(total_population * (total_reduction / 100.0) * 1.2))
        pop_protected = min(total_population, max(15000, pop_protected))

        assets_protected = min(total_assets, int(round(additional_pumps * 1.5 + barrier_km * 1.2)))

        return {
            "scenarioId": scenario_id,
            "baselineRisk": baseline_risk,
            "simulatedRisk": simulated_risk,
            "populationProtected": pop_protected,
            "assetsProtected": assets_protected,
            "confidence": 88,
        }
