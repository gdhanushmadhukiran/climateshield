"""ClimateShield Phase 7: Digital Twin Simulation API Endpoints.

Exposes REST routes for:
- POST /api/v1/simulation/run
- POST /api/v1/simulation/scenarios/{scenario_name}
- GET  /api/v1/simulation/scenarios
- GET  /api/v1/simulation/{simulation_id}
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.digital_twin_service import DigitalTwinService
from app.schemas.simulation import (
    SimulationRunRequest,
    SimulationRunResponse,
    ScenarioListResponse,
)

router = APIRouter(prefix="/simulation", tags=["Digital Twin & What-If Simulation"])


@router.get(
    "/scenarios",
    response_model=ScenarioListResponse,
    summary="List all available one-click pre-configured digital twin scenarios",
)
def get_scenarios(db: Session = Depends(get_db)) -> ScenarioListResponse:
    service = DigitalTwinService(db)
    return service.get_predefined_scenarios()


@router.post(
    "/run",
    response_model=SimulationRunResponse,
    summary="Execute in-memory what-if digital twin simulation with custom parameter overrides",
)
def run_simulation(
    request: SimulationRunRequest,
    db: Session = Depends(get_db),
) -> SimulationRunResponse:
    service = DigitalTwinService(db)
    return service.run_simulation(request)


@router.post(
    "/scenarios/{scenario_name}",
    response_model=SimulationRunResponse,
    summary="Execute one-click predefined simulation scenario by name",
)
def run_named_scenario(
    scenario_name: str = Path(..., description="Scenario identifier e.g. river_rise_0_5m, hospital_road_blocked, deploy_2_pumps"),
    db: Session = Depends(get_db),
) -> SimulationRunResponse:
    service = DigitalTwinService(db)
    try:
        return service.run_predefined_scenario(scenario_name)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/{simulation_id}",
    response_model=SimulationRunResponse,
    summary="Retrieve previously executed simulation results from memory cache by ID",
)
def get_simulation_result(
    simulation_id: str = Path(..., description="Unique simulation identifier e.g. SIM-XXXXXX"),
    db: Session = Depends(get_db),
) -> SimulationRunResponse:
    service = DigitalTwinService(db)
    sim = service.get_simulation_by_id(simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail=f"Simulation '{simulation_id}' not found in active session cache.")
    return sim
