"""Optimization and Response Intelligence endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.optimization_service import OptimizationService
from app.schemas.optimization import (
    RecommendationResponse,
    ResourceResponse,
    ResponsePlanResponse,
    ActionApprovalRequest,
    ActionApprovalResponse,
    SimulationScenarioRequest,
    SimulationResultResponse,
)

router = APIRouter(prefix="/optimization", tags=["Optimization"])


@router.get(
    "/recommendations",
    response_model=List[RecommendationResponse],
    summary="Get prescriptive action recommendations for decision makers",
)
def get_recommendations(db: Session = Depends(get_db)):
    service = OptimizationService(db)
    return service.get_recommendations()


@router.get(
    "/plan",
    response_model=ResponsePlanResponse,
    summary="Get optimized emergency response plan across all zones",
)
def get_response_plan(db: Session = Depends(get_db)):
    service = OptimizationService(db)
    return service.generate_response_plan()


@router.get(
    "/resources",
    response_model=List[ResourceResponse],
    summary="List emergency response equipment and crews inventory",
)
def get_resources(
    category: Optional[str] = Query(None, description="Filter by category (PUMP, RESCUE, BARRIER, POWER, MEDICAL)"),
    db: Session = Depends(get_db),
):
    service = OptimizationService(db)
    return service.get_resources(category)


@router.post(
    "/actions/{action_id}/approve",
    response_model=ActionApprovalResponse,
    summary="Approve an action, dispatch assigned resource, and create operational incident task",
)
def approve_action(
    action_id: str = Path(..., description="Recommendation or action ID, e.g. rec-1"),
    payload: ActionApprovalRequest = ActionApprovalRequest(),
    db: Session = Depends(get_db),
):
    service = OptimizationService(db)
    return service.approve_action(action_id=action_id, operator_id=payload.operator_id)


@router.post(
    "/simulate",
    response_model=SimulationResultResponse,
    summary="Simulate what-if counterfactual response intervention packages",
)
def simulate_response(
    payload: SimulationScenarioRequest,
    db: Session = Depends(get_db),
):
    service = OptimizationService(db)
    return service.run_simulation(
        scenario_id=payload.scenario_id or "custom",
        parameters=payload.parameters,
    )
