"""Pydantic schemas for ClimateShield ML services."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class MLHealthResponse(BaseModel):
    status: str = Field(..., description="Overall ML system status: ONLINE, DEGRADED, OFFLINE")
    lstm_loaded: bool = Field(..., description="Whether PyTorch CorrelatedLSTM model is loaded")
    isolation_forest_loaded: bool = Field(..., description="Whether Scikit-learn IsolationForest is loaded")
    model_versions: Dict[str, str] = Field(default_factory=dict, description="Loaded model version mappings")
    framework_versions: Dict[str, str] = Field(default_factory=dict, description="Underlying runtime framework versions")
    inference_readiness: bool = Field(..., description="True if at least one model is ready for real-time inference")
    last_inference_at: Optional[str] = Field(None, description="ISO timestamp of last inference execution")
    last_inference_latency_ms: Optional[float] = Field(None, description="Latency of last inference execution in milliseconds")
    fallback_used: bool = Field(False, description="True if system is currently relying on deterministic fallback")
    notes: Optional[str] = Field(None, description="Diagnostic notes or degradation rationale")


class MLForecastRequest(BaseModel):
    zone_id: Optional[str] = Field("zone-a", description="Target zone identifier")
    river_node_id: Optional[str] = Field("RN-01", description="Specific river telemetry gauge code or ID")
    custom_sequence: Optional[List[List[float]]] = Field(
        None,
        description="Optional explicit 3x4 sequence [[rainfall, moisture, level, temp], ...] for manual evaluation",
    )


class MLForecastResponse(BaseModel):
    forecast_available: bool = Field(..., description="True if sufficient valid observations allowed forecast generation")
    predicted_river_level_m: Optional[float] = Field(None, description="Predicted river level approximately 3 hours ahead in meters")
    current_river_level_m: Optional[float] = Field(None, description="Current river stage at latest observation in meters")
    delta_m: Optional[float] = Field(None, description="Predicted river stage rise (+) or fall (-) in meters")
    forecast_horizon_hours: int = Field(3, description="Forecast horizon in hours")
    prediction_timestamp: str = Field(..., description="ISO timestamp when the prediction was evaluated")
    model_version: str = Field("CorrelatedLSTM-v1.0-synthetic", description="Model version string")
    inference_latency_ms: float = Field(0.0, description="Execution latency in milliseconds")
    data_quality: str = Field("FRESH", description="Observation quality rating (FRESH, AGING, DEGRADED, STALE)")
    fallback_used: bool = Field(False, description="True if deterministic fallback was engaged")
    reason: Optional[str] = Field(None, description="Explanation when forecast is unavailable or fallback is active")
    confidence_calibrated: bool = Field(False, description="False: model produces uncalibrated point estimates")
    confidence_note: str = Field(
        "PyTorch LSTM produces deterministic uncalibrated point estimates; operational bounds derive from sensor error margins.",
        description="Operational guidance on model certainty",
    )


class SensorHealthRequest(BaseModel):
    sensor_id: str = Field(..., description="Sensor node identifier or code")
    battery_voltage: float = Field(..., description="Hardware battery voltage (expected 1.0 - 4.5 V)")
    signal_dbm: float = Field(..., description="Wireless signal strength in dBm (expected -130 to -40 dBm)")
    temp_reading_c: float = Field(..., description="Internal or ambient temperature reading in °C")
    rate_of_change_temp: float = Field(0.0, description="Temperature derivative (°C / interval)")
    reading_stuck_count: int = Field(0, description="Consecutive identical reading repetition count")


class SensorHealthResponse(BaseModel):
    sensor_id: str = Field(..., description="Sensor node identifier or code")
    status: str = Field(..., description="Evaluated health status: HEALTHY, DEGRADED, ANOMALOUS, OFFLINE")
    is_anomaly: bool = Field(..., description="True if IsolationForest flagged the telemetry as an anomaly (-1)")
    raw_prediction: int = Field(1, description="Scikit-learn IsolationForest output: +1 (normal), -1 (anomaly)")
    anomaly_score: Optional[float] = Field(None, description="Continuous decision function score (negative indicates anomaly)")
    model_version: str = Field("IsolationForest-v1.0-synthetic", description="Model version string")
    inference_latency_ms: float = Field(0.0, description="Execution latency in milliseconds")
    data_quality: str = Field("VALID", description="Data quality classification")
    timestamp: str = Field(..., description="ISO timestamp of evaluation")
    fallback_used: bool = Field(False, description="True if deterministic heuristic fallback was used")
    reason: Optional[str] = Field(None, description="Diagnostic explanation")


class MLEvaluationResponse(BaseModel):
    timestamp: str = Field(..., description="ISO evaluation timestamp")
    disclaimer: str = Field(..., description="Synthetic evaluation disclaimer notice")
    lstm_evaluation: Dict[str, Any] = Field(..., description="PyTorch LSTM evaluation metrics and latency")
    isolation_forest_evaluation: Dict[str, Any] = Field(..., description="Isolation Forest anomaly and fault injection metrics")
    failure_mode_testing: Dict[str, Any] = Field(..., description="Graceful degradation verification suite results")
    deterministic_primacy_principle: str = Field(
        "ML advisory — deterministic risk engine remains authoritative.",
        description="Core operational governance principle",
    )


class OperationalScenarioResponse(BaseModel):
    scenario_name: str
    zone_id: str
    target_node: str
    current_state: Dict[str, Any]
    ml_forecast: Dict[str, Any]
    response_adaptation: Dict[str, Any]
    governance_note: str

