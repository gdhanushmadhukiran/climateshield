"""ClimateShield Optimization Service.

Coordinates prescriptive response planning, emergency resource allocation,
operator approval dispatch workflow, and closed-loop what-if simulation.
"""

import uuid
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.resource import ResourceModel
from app.models.action_plan import ActionRecommendationModel
from app.models.incident import IncidentModel
from app.models.zone import RiskZoneModel
from app.models.risk import RiskScoreModel
from app.engine.resource_optimizer import ResourceOptimizer
from app.engine.simulation_engine import SimulationEngine
from app.core.events import broadcaster
from app.core.exceptions import EntityNotFoundException, APIException
from app.schemas.optimization import (
    RecommendationResponse,
    ResourceResponse,
    ResponsePlanResponse,
    ActionApprovalResponse,
    SimulationResultResponse,
)


class OptimizationService:
    """Service layer for response optimization and closed-loop action intelligence."""

    def __init__(self, db: Session):
        self.db = db

    def get_recommendations(self) -> List[RecommendationResponse]:
        """Generates dynamic prescriptive recommendations from current Phase 4 risk."""
        plan = self.generate_response_plan()
        return plan.actions

    def generate_response_plan(self) -> ResponsePlanResponse:
        """Optimizes emergency resource allocation across all active risk zones."""
        zones = self.db.query(RiskZoneModel).all()
        zones_data = []

        for z in zones:
            latest = (
                self.db.query(RiskScoreModel)
                .filter(RiskScoreModel.zone_id == z.id)
                .order_by(RiskScoreModel.observed_at.desc())
                .first()
            )
            score = latest.value if latest else 65
            zones_data.append({
                "id": z.id,
                "code": z.code,
                "name": z.name,
                "dominant_hazard": z.dominant_hazard,
                "risk_score": score,
                "population": z.population,
                "centroid_lat": z.centroid_lat,
                "centroid_lng": z.centroid_lng,
            })

        resources = self.db.query(ResourceModel).all()
        res_dicts = [
            {
                "id": r.id,
                "name": r.name,
                "category": r.category,
                "status": r.status,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "mobilization_minutes": r.mobilization_minutes,
            }
            for r in resources
        ]

        from app.ml.ml_service import MLService
        ml_fc = MLService.get_river_forecast(self.db, river_node_id="RN-01")

        opt_result = ResourceOptimizer.generate_and_optimize_plan(
            zones_data=zones_data,
            available_resources=res_dicts,
            ml_forecast_signal=ml_fc.model_dump(),
        )


        action_responses = []
        for a in opt_result["actions"]:
            action_responses.append(
                RecommendationResponse(
                    id=a["id"],
                    action=a["action"],
                    rationale=a["rationale"],
                    zoneId=a["zoneId"],
                    targetZoneId=a["targetZoneId"],
                    priority=a["priority"],
                    expectedRiskReduction=a["expectedRiskReduction"],
                    etaMinutes=a["etaMinutes"],
                    resources=a["resources"],
                    confidence=a["confidence"],
                    cost=a["cost"],
                    urgency=a["urgency"],
                    status=a["status"],
                    cascadeMitigated=a.get("cascadeMitigated"),
                    routeCorridor=a.get("routeCorridor"),
                    protectedPopulation=a.get("protectedPopulation"),
                )
            )

        now = datetime.now(timezone.utc)
        return ResponsePlanResponse(
            generated_at=now.isoformat(),
            total_actions=opt_result["total_actions"],
            allocated_resources_count=opt_result["allocated_resources_count"],
            total_projected_risk_reduction=opt_result["total_projected_risk_reduction"],
            total_population_protected=opt_result["total_population_protected"],
            actions=action_responses,
        )

    def get_resources(self, category: Optional[str] = None) -> List[ResourceResponse]:
        """Returns inventory of response resources."""
        q = self.db.query(ResourceModel)
        if category:
            q = q.filter(ResourceModel.category == category.upper())
        resources = q.all()
        return [ResourceResponse.model_validate(r) for r in resources]

    def approve_action(
        self, action_id: str, operator_id: str = "operator-vizag-01"
    ) -> ActionApprovalResponse:
        """Operator approval workflow: dispatches action, assigns resource, and creates operational incident."""
        now = datetime.now(timezone.utc)

        # Generate active plan to match action_id
        plan = self.generate_response_plan()
        action = next((a for a in plan.actions if a.id == action_id), None)

        if not action:
            # Check if exists in DB
            db_action = self.db.query(ActionRecommendationModel).filter(ActionRecommendationModel.id == action_id).first()
            if not db_action:
                raise EntityNotFoundException("ActionRecommendation", action_id)
            target_zone_id = db_action.zone_id
            action_title = db_action.action
            eta_min = db_action.eta_minutes
        else:
            target_zone_id = action.targetZoneId or action.zoneId or "zone-a"
            action_title = action.action
            eta_min = action.etaMinutes

        zone = self.db.query(RiskZoneModel).filter(RiskZoneModel.id == target_zone_id).first()

        # Find and allocate available resource
        avail_resource = (
            self.db.query(ResourceModel)
            .filter(ResourceModel.status == "AVAILABLE")
            .first()
        )

        assigned_res_name = None
        if avail_resource:
            avail_resource.status = "DEPLOYED"
            avail_resource.assigned_zone_id = target_zone_id
            assigned_res_name = avail_resource.name

        # Create dispatched incident task
        inc_ref = f"INC-DISP-{uuid.uuid4().hex[:6].upper()}"
        new_incident = IncidentModel(
            id=str(uuid.uuid4()),
            ref=inc_ref,
            title=f"DEPLOYMENT: {action_title[:100]}",
            hazard_type=zone.dominant_hazard if zone else "FLOOD",
            zone_id=target_zone_id,
            severity="EMERGENCY" if action and action.priority == "P1" else "WARNING",
            status="IN_RESPONSE",
            latitude=zone.centroid_lat if zone else 17.72,
            longitude=zone.centroid_lng if zone else 83.30,
            reported_at=now,
        )
        self.db.add(new_incident)

        if avail_resource:
            avail_resource.assigned_incident_id = new_incident.id

        self.db.commit()

        # Broadcast SSE dispatch event
        def safe_schedule(coro):
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(coro)
            except RuntimeError:
                coro.close()

        safe_schedule(broadcaster.publish("action_dispatched", {
            "action_id": action_id,
            "incident_ref": inc_ref,
            "assigned_resource": assigned_res_name,
            "zone_id": target_zone_id,
            "approved_by": operator_id,
            "timestamp": now.isoformat(),
        }))

        return ActionApprovalResponse(
            action_id=action_id,
            status="DISPATCHED",
            approved_by=operator_id,
            approved_at=now.isoformat(),
            dispatched_incident_ref=inc_ref,
            assigned_resource=assigned_res_name,
            target_zone_id=target_zone_id,
            eta_minutes=eta_min,
        )

    def run_simulation(
        self, scenario_id: str, parameters: Dict[str, Any]
    ) -> SimulationResultResponse:
        """Simulates counterfactual response intervention packages."""
        # Get baseline risk
        scores = self.db.query(RiskScoreModel).order_by(RiskScoreModel.observed_at.desc()).limit(3).all()
        baseline = int(round(sum(s.value for s in scores) / len(scores))) if scores else 74

        res = SimulationEngine.simulate_scenario(
            scenario_id=scenario_id,
            parameters=parameters,
            baseline_risk=baseline,
        )

        return SimulationResultResponse(
            scenarioId=res["scenarioId"],
            baselineRisk=res["baselineRisk"],
            simulatedRisk=res["simulatedRisk"],
            populationProtected=res["populationProtected"],
            assetsProtected=res["assetsProtected"],
            confidence=res["confidence"],
        )
