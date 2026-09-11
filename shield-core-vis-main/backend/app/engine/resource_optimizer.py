"""ClimateShield Prescriptive Resource & Action Optimizer.

Solves multi-criteria emergency resource allocation, matching prioritized actions
to available equipment/crews while maximizing risk reduction and mitigating cascade failures.
"""

from typing import List, Dict, Any, Optional
from app.engine.route_logistics import RouteLogisticsEngine


class ResourceOptimizer:
    """Multi-criteria prescriptive response optimization engine."""

    ACTION_TEMPLATES = {
        "FLOOD": [
            {
                "action": "Deploy temporary inflatable flood barriers at Sector 4 drainage choke-point",
                "rationale": "Upstream river stage exceeding threshold; barrier containment prevents overland flow into high-density residential zone.",
                "category": "BARRIER",
                "base_reduction": 28,
                "cost_str": "~$12,000",
                "cascade_edge": "inflow_to_pump",
                "priority": "P1",
            },
            {
                "action": "Pre-stage mobile 5000 GPM high-capacity dewatering pumps at low-lying culvert",
                "rationale": "Accelerates runoff evacuation into secondary storm canal before river peak reaches culvert at T+45m.",
                "category": "PUMP",
                "base_reduction": 20,
                "cost_str": "~$8,500",
                "cascade_edge": "pump_to_substation",
                "priority": "P1",
            },
        ],
        "DRAINAGE_STRESS": [
            {
                "action": "Pre-stage mobile high-capacity pumps at North Pump Station",
                "rationale": "Municipal pump station operating at high load; supplementary pump provides backup redundancy for power substation corridor.",
                "category": "PUMP",
                "base_reduction": 22,
                "cost_str": "~$8,000",
                "cascade_edge": "pump_to_substation",
                "priority": "P1",
            },
            {
                "action": "Deploy mobile auxiliary diesel generator to 220kV Substation",
                "rationale": "Ensures uninterrupted power for industrial drainage grid in the event of primary feeder waterlogging trip.",
                "category": "POWER",
                "base_reduction": 18,
                "cost_str": "~$6,500",
                "cascade_edge": "substation_to_road",
                "priority": "P2",
            },
        ],
        "COASTAL_SURGE": [
            {
                "action": "Pre-position NDRF water rescue teams at Dolphin's Nose staging base",
                "rationale": "Coastal wave swell combined with extreme precipitation risks inundation of coastal heritage corridor arterial.",
                "category": "RESCUE",
                "base_reduction": 16,
                "cost_str": "~$4,200",
                "cascade_edge": "substation_to_road",
                "priority": "P2",
            },
            {
                "action": "Open municipal high school emergency cooling and evacuation shelter",
                "rationale": "Provides secure staging for vulnerable populations exposed to severe compound heat and localized waterlogging.",
                "category": "CREW",
                "base_reduction": 12,
                "cost_str": "~$3,000",
                "cascade_edge": "road_to_hospital",
                "priority": "P3",
            },
        ],
    }

    @classmethod
    def generate_and_optimize_plan(
        cls,
        zones_data: List[Dict[str, Any]],
        available_resources: List[Dict[str, Any]],
        waterlogging_states: Dict[str, str] = None,
        ml_forecast_signal: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generates prioritized action recommendations and optimizes resource allocations."""
        waterlogging_states = waterlogging_states or {}
        allocated_resource_ids = set()
        plan_actions: List[Dict[str, Any]] = []

        total_risk_reduction = 0
        total_population_protected = 0

        action_counter = 1

        # Check for rising river stage forecast
        forecast_rising = False
        forecast_delta = 0.0
        if ml_forecast_signal and ml_forecast_signal.get("forecast_available"):
            delta = ml_forecast_signal.get("delta_m") or 0.0
            pred_level = ml_forecast_signal.get("predicted_river_level_m") or 0.0
            if delta > 0.20 or pred_level >= 3.4:
                forecast_rising = True
                forecast_delta = delta

        for z in zones_data:
            zone_id = z.get("id")
            zone_code = z.get("code", "ZONE")
            dominant = z.get("dominant_hazard", "FLOOD").upper()
            risk_score = z.get("risk_score", 50)
            population = z.get("population", 100000)
            centroid_lat = z.get("centroid_lat", 17.72)
            centroid_lng = z.get("centroid_lng", 83.30)

            # Select hazard template
            if "DRAINAGE" in dominant:
                templates = cls.ACTION_TEMPLATES["DRAINAGE_STRESS"]
            elif "SURGE" in dominant or "HERITAGE" in z.get("name", "").upper():
                templates = cls.ACTION_TEMPLATES["COASTAL_SURGE"]
            else:
                templates = cls.ACTION_TEMPLATES["FLOOD"]

            waterlog_status = waterlogging_states.get(zone_id, "NONE")
            if risk_score >= 80:
                waterlog_status = "SEVERE"
            elif risk_score >= 65:
                waterlog_status = "MODERATE"

            for tmpl in templates:
                req_category = tmpl["category"]

                # Find closest available resource matching category
                best_res = None
                best_eta_dict = None
                min_eta = 999999

                for r in available_resources:
                    if r["id"] in allocated_resource_ids:
                        continue
                    if r.get("category") == req_category and r.get("status") == "AVAILABLE":
                        eta_dict = RouteLogisticsEngine.calculate_deployment_eta(
                            depot_lat=r.get("latitude", centroid_lat),
                            depot_lng=r.get("longitude", centroid_lng),
                            target_lat=centroid_lat,
                            target_lng=centroid_lng,
                            mobilization_minutes=r.get("mobilization_minutes", 15),
                            waterlogging_severity=waterlog_status,
                        )
                        if eta_dict["total_eta_minutes"] < min_eta:
                            min_eta = eta_dict["total_eta_minutes"]
                            best_res = r
                            best_eta_dict = eta_dict

                # Scale expected risk reduction by active zone risk
                reduction_pts = int(round(tmpl["base_reduction"] * (risk_score / 70.0)))
                reduction_pts = max(5, min(35, reduction_pts))

                # Assigned resource information
                assigned_id = None
                assigned_name = "Reserve Contingency Pool"
                eta_minutes = tmpl.get("eta_minutes", 30)
                primary_corridor = "Direct Municipal Access"

                if best_res and best_eta_dict:
                    allocated_resource_ids.add(best_res["id"])
                    assigned_id = best_res["id"]
                    assigned_name = best_res["name"]
                    eta_minutes = best_eta_dict["total_eta_minutes"]
                    primary_corridor = best_eta_dict["primary_corridor"]

                # Protected population estimate: fraction of zone population
                protected_pop = int(round(population * (reduction_pts / 100.0) * 0.75))

                # Determine Priority and Urgency, with ML Forecast escalation
                priority_val = tmpl["priority"]
                urgency_val = "IMMEDIATE" if priority_val == "P1" else ("HIGH" if priority_val == "P2" else "MEDIUM")
                rationale_text = tmpl["rationale"]

                if forecast_rising and req_category in ("BARRIER", "PUMP"):
                    priority_val = "P1"
                    urgency_val = "IMMEDIATE"
                    rationale_text += f" [Forecast indicates elevated future river-stage risk (+{forecast_delta:.2f}m at T+3h). Earlier intervention advised.]"

                action_item = {
                    "id": f"rec-{action_counter}",
                    "action": tmpl["action"],
                    "rationale": rationale_text,
                    "zoneId": zone_id,
                    "targetZoneId": zone_id,
                    "zoneCode": zone_code,
                    "priority": priority_val,
                    "expectedRiskReduction": reduction_pts,
                    "etaMinutes": eta_minutes,
                    "cost": tmpl["cost_str"],
                    "confidence": 88 if best_res else 74,
                    "urgency": urgency_val,
                    "status": "PENDING",
                    "cascadeMitigated": tmpl["cascade_edge"],
                    "assignedResourceId": assigned_id,
                    "assignedResourceName": assigned_name,
                    "resources": [assigned_name],
                    "routeCorridor": primary_corridor,
                    "protectedPopulation": protected_pop,
                }


                plan_actions.append(action_item)
                total_risk_reduction += reduction_pts
                total_population_protected += protected_pop
                action_counter += 1

        # Sort actions strictly by Priority (P1 -> P2 -> P3) and then Expected Reduction descending
        priority_rank = {"P1": 0, "P2": 1, "P3": 2}
        plan_actions.sort(key=lambda a: (priority_rank.get(a["priority"], 9), -a["expectedRiskReduction"]))

        return {
            "total_actions": len(plan_actions),
            "allocated_resources_count": len(allocated_resource_ids),
            "total_projected_risk_reduction": total_risk_reduction,
            "total_population_protected": total_population_protected,
            "actions": plan_actions,
        }
