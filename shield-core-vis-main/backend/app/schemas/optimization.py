"""Optimization and Response Intelligence schemas."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class RecommendationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    action: str
    rationale: Optional[str] = "Mitigates critical spatial hazard drivers."
    zoneId: Optional[str] = Field(None, alias="targetZoneId")
    targetZoneId: Optional[str] = None
    assetId: Optional[str] = None
    priority: str = "P1"
    expectedRiskReduction: int = 15
    etaMinutes: int = 25
    resources: List[str] = []
    confidence: int = 85
    cost: Optional[str] = "~$5,000"
    urgency: Optional[str] = "HIGH"
    status: str = "PENDING"
    cascadeMitigated: Optional[str] = None
    routeCorridor: Optional[str] = None
    protectedPopulation: Optional[int] = None


class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    category: str
    status: str
    depot_name: str
    latitude: float
    longitude: float
    hourly_cost: float
    mobilization_minutes: int
    assigned_zone_id: Optional[str] = None
    assigned_incident_id: Optional[str] = None


class ActionApprovalRequest(BaseModel):
    operator_id: str = "operator-vizag-01"
    notes: Optional[str] = "Approved by shift commander"


class ActionApprovalResponse(BaseModel):
    action_id: str
    status: str
    approved_by: str
    approved_at: str
    dispatched_incident_ref: str
    assigned_resource: Optional[str] = None
    target_zone_id: str
    eta_minutes: int


class ResponsePlanResponse(BaseModel):
    generated_at: str
    total_actions: int
    allocated_resources_count: int
    total_projected_risk_reduction: int
    total_population_protected: int
    actions: List[RecommendationResponse]


class SimulationScenarioRequest(BaseModel):
    scenario_id: Optional[str] = "custom-scenario"
    parameters: Dict[str, Any] = {}


class SimulationResultResponse(BaseModel):
    scenarioId: str
    baselineRisk: int
    simulatedRisk: int
    populationProtected: int
    assetsProtected: int
    confidence: int
