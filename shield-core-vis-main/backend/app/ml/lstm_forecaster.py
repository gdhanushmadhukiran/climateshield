"""LSTM River Forecaster inference service.

Executes forward-pass predictions for 3-hour river stage using PyTorch CorrelatedLSTM
and bundled StandardScalers. Strictly enforces the 3x4 tensor contract and provides
safe deterministic fallbacks when observations are missing or invalid.
"""

import time
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from app.core.logging import logger
from app.ml.model_loader import model_loader, TORCH_AVAILABLE
from app.ml.schemas import MLForecastResponse

if TORCH_AVAILABLE:
    import torch
else:
    torch = None


class LSTMForecaster:
    """Inference runner for the 3-hour river stage LSTM model."""

    MODEL_VERSION = "CorrelatedLSTM-v1.0-synthetic"
    REQUIRED_SEQ_LEN = 3
    REQUIRED_NUM_FEATURES = 4
    FEATURE_NAMES = ["rainfall_mm", "soil_moisture_pct", "river_level_m", "temperature_c"]

    # Physical validity bounds
    BOUNDS = {
        "rainfall_mm": (0.0, 300.0),
        "soil_moisture_pct": (0.0, 100.0),
        "river_level_m": (0.0, 25.0),
        "temperature_c": (-20.0, 65.0),
    }

    @classmethod
    def validate_sequence(cls, raw_seq: Any) -> Tuple[bool, Optional[str], Optional[np.ndarray]]:
        """Validates that the input sequence strictly adheres to the (3, 4) shape and physical bounds."""
        try:
            arr = np.array(raw_seq, dtype=np.float64)
        except (ValueError, TypeError) as e:
            return False, f"Sequence cannot be cast to numeric array: {str(e)}", None

        if arr.shape != (cls.REQUIRED_SEQ_LEN, cls.REQUIRED_NUM_FEATURES):
            return (
                False,
                f"Invalid sequence shape {arr.shape}. Expected exactly ({cls.REQUIRED_SEQ_LEN}, {cls.REQUIRED_NUM_FEATURES})",
                None,
            )

        if np.isnan(arr).any() or np.isinf(arr).any():
            return False, "Sequence contains NaN or Infinite values", None

        # Check bounds for each feature across all timesteps
        for col_idx, feat_name in enumerate(cls.FEATURE_NAMES):
            col_vals = arr[:, col_idx]
            min_bound, max_bound = cls.BOUNDS[feat_name]
            if (col_vals < min_bound).any() or (col_vals > max_bound).any():
                return (
                    False,
                    f"Feature '{feat_name}' contains values outside physical bounds [{min_bound}, {max_bound}]: {col_vals.tolist()}",
                    None,
                )

        return True, None, arr

    @classmethod
    def predict(
        cls,
        sequence: List[List[float]],
        current_river_level: Optional[float] = None,
        data_quality: str = "FRESH",
    ) -> MLForecastResponse:
        """Executes inference on a validated 3x4 sequence of hourly observations.

        Returns an MLForecastResponse with fallback_used=True if model or data is invalid.
        """
        start_time = time.perf_counter()
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1. Validate sequence
        is_valid, validation_err, arr = cls.validate_sequence(sequence)
        if not is_valid or arr is None:
            latency = (time.perf_counter() - start_time) * 1000.0
            return MLForecastResponse(
                forecast_available=False,
                predicted_river_level_m=None,
                current_river_level_m=current_river_level,
                delta_m=None,
                forecast_horizon_hours=3,
                prediction_timestamp=now_iso,
                model_version=cls.MODEL_VERSION,
                inference_latency_ms=round(latency, 2),
                data_quality="DEGRADED",
                fallback_used=True,
                reason=validation_err or "Invalid input sequence",
            )

        # 2. Check model readiness
        bundle = model_loader.get_lstm_bundle()
        if not bundle or torch is None:
            latency = (time.perf_counter() - start_time) * 1000.0
            reason = model_loader.lstm_error or "PyTorch LSTM model not loaded in memory"
            logger.warning(f"[LSTM_FORECASTER] Fallback engaged: {reason}")
            return MLForecastResponse(
                forecast_available=False,
                predicted_river_level_m=None,
                current_river_level_m=current_river_level,
                delta_m=None,
                forecast_horizon_hours=3,
                prediction_timestamp=now_iso,
                model_version=cls.MODEL_VERSION,
                inference_latency_ms=round(latency, 2),
                data_quality=data_quality,
                fallback_used=True,
                reason=reason,
            )

        model, scaler_X, scaler_y = bundle

        # 3. Scale inputs & construct tensor
        try:
            scaled_seq = scaler_X.transform(arr)
            tensor_seq = torch.tensor(np.array([scaled_seq]), dtype=torch.float32)

            # 4. Inference pass
            with torch.no_grad():
                pred_scaled = model(tensor_seq).cpu().numpy()

            # 5. Inverse transform target
            pred_unscaled = scaler_y.inverse_transform(pred_scaled)[0][0]
            predicted_level = round(max(0.0, float(pred_unscaled)), 2)

            curr_level = current_river_level if current_river_level is not None else float(arr[-1, 2])
            delta = round(predicted_level - curr_level, 2)

            latency = (time.perf_counter() - start_time) * 1000.0
            model_loader.record_inference(latency)

            return MLForecastResponse(
                forecast_available=True,
                predicted_river_level_m=predicted_level,
                current_river_level_m=curr_level,
                delta_m=delta,
                forecast_horizon_hours=3,
                prediction_timestamp=now_iso,
                model_version=cls.MODEL_VERSION,
                inference_latency_ms=round(latency, 2),
                data_quality=data_quality,
                fallback_used=False,
                reason=None,
            )
        except Exception as e:
            latency = (time.perf_counter() - start_time) * 1000.0
            logger.error(f"[LSTM_FORECASTER] Inference exception: {str(e)}", exc_info=True)
            return MLForecastResponse(
                forecast_available=False,
                predicted_river_level_m=None,
                current_river_level_m=current_river_level,
                delta_m=None,
                forecast_horizon_hours=3,
                prediction_timestamp=now_iso,
                model_version=cls.MODEL_VERSION,
                inference_latency_ms=round(latency, 2),
                data_quality="DEGRADED",
                fallback_used=True,
                reason=f"Inference computation error: {str(e)}",
            )
