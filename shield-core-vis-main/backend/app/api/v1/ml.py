"""Machine Learning Intelligence API Endpoints.

Exposes REST routes for:
- GET  /api/v1/ml/health
- GET  /api/v1/ml/forecast
- POST /api/v1/ml/forecast
- GET  /api/v1/ml/sensor-health
- POST /api/v1/ml/sensor-health
"""

from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.ml.ml_service import MLService
from app.ml.evaluation import MLEvaluationHarness
from app.ml.schemas import (
    MLHealthResponse,
    MLForecastRequest,
    MLForecastResponse,
    SensorHealthRequest,
    SensorHealthResponse,
    MLEvaluationResponse,
    OperationalScenarioResponse,
)

router = APIRouter(prefix="/ml", tags=["Machine Learning Intelligence"])



@router.get(
    "/health",
    response_model=MLHealthResponse,
    summary="Get ML model loading, framework runtime, and operational readiness status",
)
def get_ml_health() -> MLHealthResponse:
    return MLService.get_health()


@router.get(
    "/forecast",
    response_model=MLForecastResponse,
    summary="Get 3-hour forward-looking river stage forecast using PyTorch LSTM",
)
def get_river_forecast(
    river_node_id: str = Query("RN-01", description="River gauge node identifier or code (e.g. RN-01)"),
    zone_id: str = Query("zone-a", description="Risk zone identifier"),
    db: Session = Depends(get_db),
) -> MLForecastResponse:
    return MLService.get_river_forecast(db=db, river_node_id=river_node_id, zone_id=zone_id)


@router.post(
    "/forecast",
    response_model=MLForecastResponse,
    summary="Evaluate custom 3x4 tensor sequence against PyTorch LSTM river forecaster",
)
def evaluate_custom_forecast(
    request: MLForecastRequest,
    db: Session = Depends(get_db),
) -> MLForecastResponse:
    return MLService.get_river_forecast(
        db=db,
        river_node_id=request.river_node_id or "RN-01",
        zone_id=request.zone_id or "zone-a",
        custom_sequence=request.custom_sequence,
    )


@router.get(
    "/sensor-health",
    response_model=SensorHealthResponse,
    summary="Evaluate single sensor telemetry for hardware faults using Scikit-learn IsolationForest",
)
def get_sensor_health_query(
    sensor_id: str = Query(..., description="Sensor node identifier (e.g. sensor-river-01)"),
    battery_voltage: float = Query(3.7, description="Battery voltage in Volts"),
    signal_dbm: float = Query(-75.0, description="Wireless RSSI signal in dBm"),
    temp_reading_c: float = Query(28.0, description="Sensor PCB temperature reading in °C"),
    rate_of_change_temp: float = Query(0.0, description="Rate of temperature variation"),
    reading_stuck_count: int = Query(0, description="Consecutive identical measurement count"),
) -> SensorHealthResponse:
    return MLService.evaluate_sensor_telemetry(
        sensor_id=sensor_id,
        battery_voltage=battery_voltage,
        signal_dbm=signal_dbm,
        temp_reading_c=temp_reading_c,
        rate_of_change_temp=rate_of_change_temp,
        reading_stuck_count=reading_stuck_count,
    )


@router.post(
    "/sensor-health",
    response_model=SensorHealthResponse,
    summary="Evaluate sensor telemetry vector for hardware degradation via POST payload",
)
def post_sensor_health(
    request: SensorHealthRequest,
    background_tasks: BackgroundTasks,
) -> SensorHealthResponse:
    response = MLService.evaluate_sensor_telemetry(
        sensor_id=request.sensor_id,
        battery_voltage=request.battery_voltage,
        signal_dbm=request.signal_dbm,
        temp_reading_c=request.temp_reading_c,
        rate_of_change_temp=request.rate_of_change_temp,
        reading_stuck_count=request.reading_stuck_count,
    )
    if response.is_anomaly:
        background_tasks.add_task(MLService.broadcast_sensor_anomaly, response)
    return response


@router.get(
    "/evaluation",
    response_model=MLEvaluationResponse,
    summary="Get rigorous evaluation metrics, fault injection results, and failure testing for ML models",
)
def get_ml_evaluation(
    samples: int = Query(100, ge=20, le=300, description="Synthetic holdout sample size for evaluation"),
) -> MLEvaluationResponse:
    lstm_eval = MLEvaluationHarness.evaluate_lstm(n_samples=samples)
    iso_eval = MLEvaluationHarness.evaluate_isolation_forest(n_samples=samples)
    failures = MLEvaluationHarness.test_failure_modes()

    return MLEvaluationResponse(
        timestamp=datetime.now(timezone.utc).isoformat(),
        disclaimer="SYNTHETIC VALIDATION — NOT REAL-WORLD ACCURACY. Independent synthetic holdout and fault simulation.",
        lstm_evaluation=lstm_eval,
        isolation_forest_evaluation=iso_eval,
        failure_mode_testing=failures,
        deterministic_primacy_principle="ML advisory — deterministic risk engine remains authoritative.",
    )


@router.get(
    "/operational-scenario",
    response_model=OperationalScenarioResponse,
    summary="Get end-to-end operational value demonstration scenario showing advisory forecast flow",
)
def get_operational_scenario() -> OperationalScenarioResponse:
    scenario = MLEvaluationHarness.get_operational_scenario()
    return OperationalScenarioResponse(**scenario)


@router.get(
    "/agentic-action-plan",
    summary="Unified 6-Agent Decision Matrix Endpoint under ML Intelligence",
)
def get_ml_agentic_plan():
    from app.api.v1.agentic import get_master_agentic_plan

    return get_master_agentic_plan()


