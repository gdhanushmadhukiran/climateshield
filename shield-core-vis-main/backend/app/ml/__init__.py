"""ClimateShield Machine Learning Integration Package."""

from app.ml.schemas import (
    MLHealthResponse,
    MLForecastRequest,
    MLForecastResponse,
    SensorHealthRequest,
    SensorHealthResponse,
)
from app.ml.model_loader import model_loader, ModelLoader
from app.ml.lstm_forecaster import LSTMForecaster
from app.ml.sensor_anomaly import SensorAnomalyDetector
from app.ml.ml_service import MLService

__all__ = [
    "MLHealthResponse",
    "MLForecastRequest",
    "MLForecastResponse",
    "SensorHealthRequest",
    "SensorHealthResponse",
    "model_loader",
    "ModelLoader",
    "LSTMForecaster",
    "SensorAnomalyDetector",
    "MLService",
]
