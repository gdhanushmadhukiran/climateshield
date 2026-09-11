"""Singleton Model Loader for ClimateShield ML Models.

Safely deserializes and caches pretrained PyTorch and Scikit-learn models once,
preventing repetitive disk I/O and unpickling per request.
Includes custom unpickler class redirection and graceful fallback on corruption.
"""

import os
import io
import pickle
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

from app.core.logging import logger

# Try importing runtime frameworks
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    torch = None
    nn = None
    TORCH_AVAILABLE = False

try:
    import sklearn
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    sklearn = None
    IsolationForest = None
    SKLEARN_AVAILABLE = False


# PyTorch architecture matching lstm_forecaster.pkl
if TORCH_AVAILABLE and nn is not None:
    class CorrelatedLSTM(nn.Module):
        def __init__(self):
            super().__init__()
            self.lstm = nn.LSTM(4, 32, batch_first=True)
            self.fc = nn.Linear(32, 1)

        def forward(self, x):
            out, _ = self.lstm(x)
            return self.fc(out[:, -1, :])
else:
    class CorrelatedLSTM:  # type: ignore
        pass


class _ModelUnpickler(pickle.Unpickler):
    """Custom unpickler to resolve CorrelatedLSTM regardless of originating module."""
    def find_class(self, module, name):
        if name == "CorrelatedLSTM":
            return CorrelatedLSTM
        return super().find_class(module, name)


class ModelLoader:
    """Thread-safe singleton model loader for ClimateShield ML artifacts."""

    _instance: Optional["ModelLoader"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "ModelLoader":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelLoader, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self._initialized = True
        self.models_dir = Path(__file__).resolve().parent.parent.parent / "ml_models"

        # Model references
        self.lstm_model: Optional[Any] = None
        self.lstm_scaler_X: Optional[Any] = None
        self.lstm_scaler_y: Optional[Any] = None

        self.anomaly_model: Optional[Any] = None

        # State tracking
        self.lstm_loaded: bool = False
        self.anomaly_loaded: bool = False
        self.lstm_error: Optional[str] = None
        self.anomaly_error: Optional[str] = None

        self.last_inference_at: Optional[str] = None
        self.last_inference_latency_ms: Optional[float] = None

        # Load models on creation
        self.load_all()

    def load_all(self) -> None:
        """Attempts to load both ML models from disk."""
        self._load_lstm()
        self._load_anomaly()

    def _load_lstm(self) -> None:
        if not TORCH_AVAILABLE:
            self.lstm_loaded = False
            self.lstm_error = "PyTorch is not installed in the current environment"
            logger.warning(f"[ML_LOADER] {self.lstm_error}")
            return

        lstm_path = self.models_dir / "lstm_forecaster.pkl"
        if not lstm_path.exists():
            self.lstm_loaded = False
            self.lstm_error = f"Model file not found: {lstm_path.name}"
            logger.warning(f"[ML_LOADER] {self.lstm_error}")
            return

        try:
            with open(lstm_path, "rb") as f:
                unpickler = _ModelUnpickler(f)
                bundle = unpickler.load()

            self.lstm_model = bundle["model"]
            self.lstm_scaler_X = bundle["scaler_X"]
            self.lstm_scaler_y = bundle["scaler_y"]

            if hasattr(self.lstm_model, "eval"):
                self.lstm_model.eval()

            self.lstm_loaded = True
            self.lstm_error = None
            logger.info("[ML_LOADER] Successfully loaded lstm_forecaster.pkl (PyTorch CorrelatedLSTM)")
        except Exception as e:
            self.lstm_loaded = False
            self.lstm_error = f"Failed to deserialize LSTM model: {str(e)}"
            logger.error(f"[ML_LOADER] {self.lstm_error}", exc_info=True)

    def _load_anomaly(self) -> None:
        if not SKLEARN_AVAILABLE:
            self.anomaly_loaded = False
            self.anomaly_error = "Scikit-learn is not installed in the current environment"
            logger.warning(f"[ML_LOADER] {self.anomaly_error}")
            return

        anomaly_path = self.models_dir / "sensor_anomaly_model.pkl"
        if not anomaly_path.exists():
            self.anomaly_loaded = False
            self.anomaly_error = f"Model file not found: {anomaly_path.name}"
            logger.warning(f"[ML_LOADER] {self.anomaly_error}")
            return

        try:
            with open(anomaly_path, "rb") as f:
                self.anomaly_model = pickle.load(f)

            self.anomaly_loaded = True
            self.anomaly_error = None
            logger.info("[ML_LOADER] Successfully loaded sensor_anomaly_model.pkl (Scikit-learn IsolationForest)")
        except Exception as e:
            self.anomaly_loaded = False
            self.anomaly_error = f"Failed to deserialize sensor anomaly model: {str(e)}"
            logger.error(f"[ML_LOADER] {self.anomaly_error}", exc_info=True)

    def get_lstm_bundle(self) -> Optional[Tuple[Any, Any, Any]]:
        """Returns (model, scaler_X, scaler_y) if loaded and ready, else None."""
        if self.lstm_loaded and self.lstm_model is not None:
            return self.lstm_model, self.lstm_scaler_X, self.lstm_scaler_y
        return None

    def get_anomaly_model(self) -> Optional[Any]:
        """Returns the loaded IsolationForest model or None."""
        if self.anomaly_loaded and self.anomaly_model is not None:
            return self.anomaly_model
        return None

    def record_inference(self, latency_ms: float) -> None:
        """Records telemetry on inference execution."""
        self.last_inference_at = datetime.now(timezone.utc).isoformat()
        self.last_inference_latency_ms = round(latency_ms, 2)

    def get_health_status(self) -> Dict[str, Any]:
        """Generates health assessment dictionary."""
        readiness = self.lstm_loaded or self.anomaly_loaded
        if self.lstm_loaded and self.anomaly_loaded:
            status = "ONLINE"
        elif readiness:
            status = "DEGRADED"
        else:
            status = "OFFLINE"

        framework_versions = {}
        if TORCH_AVAILABLE and torch is not None:
            framework_versions["torch"] = getattr(torch, "__version__", "unknown")
        if SKLEARN_AVAILABLE and sklearn is not None:
            framework_versions["scikit-learn"] = getattr(sklearn, "__version__", "unknown")

        notes_parts = []
        if self.lstm_error:
            notes_parts.append(f"LSTM: {self.lstm_error}")
        if self.anomaly_error:
            notes_parts.append(f"IsolationForest: {self.anomaly_error}")

        return {
            "status": status,
            "lstm_loaded": self.lstm_loaded,
            "isolation_forest_loaded": self.anomaly_loaded,
            "model_versions": {
                "lstm_forecaster": "CorrelatedLSTM-v1.0-synthetic" if self.lstm_loaded else "NOT_LOADED",
                "sensor_anomaly": "IsolationForest-v1.0-synthetic" if self.anomaly_loaded else "NOT_LOADED",
            },
            "framework_versions": framework_versions,
            "inference_readiness": readiness,
            "last_inference_at": self.last_inference_at,
            "last_inference_latency_ms": self.last_inference_latency_ms,
            "fallback_used": not (self.lstm_loaded and self.anomaly_loaded),
            "notes": " | ".join(notes_parts) if notes_parts else "All vetted models operational and ready for inference",
        }


# Global singleton access
model_loader = ModelLoader()
