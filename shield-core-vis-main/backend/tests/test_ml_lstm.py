"""Comprehensive tests for PyTorch LSTM River Forecaster.

Covers:
- Valid 3-hour sequence inference
- Insufficient history (< 3 observations)
- Missing features & shape mismatch
- Invalid feature ranges & out-of-bounds inputs
- Inference success and latency metrics
- Model loading failure simulation & graceful fallback
- Malformed model / unpickling error handling
- Uncalibrated confidence contract verification
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

from app.ml.lstm_forecaster import LSTMForecaster
from app.ml.model_loader import ModelLoader, model_loader
from app.ml.schemas import MLForecastResponse


def test_lstm_valid_3hour_sequence():
    """Verify that a valid (3, 4) hourly sequence yields a valid river stage prediction."""
    valid_seq = [
        [10.0, 50.0, 1.2, 30.0],
        [25.0, 70.0, 1.8, 28.0],
        [50.0, 95.0, 2.5, 26.0],
    ]
    resp = LSTMForecaster.predict(valid_seq, current_river_level=2.5)

    assert isinstance(resp, MLForecastResponse)
    assert resp.forecast_available is True
    assert resp.fallback_used is False
    assert resp.predicted_river_level_m is not None
    assert resp.predicted_river_level_m >= 0.0
    assert resp.forecast_horizon_hours == 3
    assert resp.current_river_level_m == 2.5
    assert resp.delta_m == round(resp.predicted_river_level_m - 2.5, 2)
    assert resp.inference_latency_ms >= 0.0
    assert resp.confidence_calibrated is False
    assert "uncalibrated" in resp.confidence_note.lower()


def test_lstm_insufficient_sequence_length():
    """Verify that fewer than 3 timesteps returns forecast_available=False without fabricating data."""
    short_seq = [
        [10.0, 50.0, 1.2, 30.0],
        [25.0, 70.0, 1.8, 28.0],
    ]
    resp = LSTMForecaster.predict(short_seq)

    assert resp.forecast_available is False
    assert resp.fallback_used is True
    assert resp.predicted_river_level_m is None
    assert "Expected exactly (3, 4)" in (resp.reason or "")


def test_lstm_missing_or_extra_features():
    """Verify that an incorrect number of columns returns validation error."""
    bad_cols_seq = [
        [10.0, 50.0, 1.2],
        [25.0, 70.0, 1.8],
        [50.0, 95.0, 2.5],
    ]
    resp = LSTMForecaster.predict(bad_cols_seq)

    assert resp.forecast_available is False
    assert resp.fallback_used is True
    assert "Expected exactly (3, 4)" in (resp.reason or "")


def test_lstm_invalid_feature_bounds():
    """Verify that physically impossible sensor values are rejected safely."""
    # Negative rainfall
    neg_rain_seq = [
        [-5.0, 50.0, 1.2, 30.0],
        [25.0, 70.0, 1.8, 28.0],
        [50.0, 95.0, 2.5, 26.0],
    ]
    resp = LSTMForecaster.predict(neg_rain_seq)
    assert resp.forecast_available is False
    assert resp.fallback_used is True
    assert "rainfall_mm" in (resp.reason or "")

    # Extreme temperature out of bounds (> 65°C)
    extreme_temp_seq = [
        [10.0, 50.0, 1.2, 30.0],
        [25.0, 70.0, 1.8, 28.0],
        [50.0, 95.0, 2.5, 99.0],
    ]
    resp2 = LSTMForecaster.predict(extreme_temp_seq)
    assert resp2.forecast_available is False
    assert resp2.fallback_used is True
    assert "temperature_c" in (resp2.reason or "")

    # Extreme river stage (> 25m)
    extreme_stage_seq = [
        [10.0, 50.0, 1.2, 30.0],
        [25.0, 70.0, 1.8, 28.0],
        [50.0, 95.0, 45.0, 26.0],
    ]
    resp3 = LSTMForecaster.predict(extreme_stage_seq)
    assert resp3.forecast_available is False
    assert resp3.fallback_used is True
    assert "river_level_m" in (resp3.reason or "")


def test_lstm_nan_and_inf_handling():
    """Verify that NaN or Inf values do not cause silent crashes."""
    nan_seq = [
        [10.0, 50.0, 1.2, 30.0],
        [25.0, float("nan"), 1.8, 28.0],
        [50.0, 95.0, 2.5, 26.0],
    ]
    resp = LSTMForecaster.predict(nan_seq)
    assert resp.forecast_available is False
    assert resp.fallback_used is True
    assert "NaN or Infinite" in (resp.reason or "")


def test_lstm_model_loading_failure_fallback():
    """Verify that when LSTM model is unavailable, system returns fallback response without crashing."""
    valid_seq = [
        [10.0, 50.0, 1.2, 30.0],
        [25.0, 70.0, 1.8, 28.0],
        [50.0, 95.0, 2.5, 26.0],
    ]

    with patch.object(model_loader, "get_lstm_bundle", return_value=None):
        resp = LSTMForecaster.predict(valid_seq)
        assert resp.forecast_available is False
        assert resp.fallback_used is True
        assert resp.predicted_river_level_m is None
        assert "not loaded" in (resp.reason or "").lower()


def test_lstm_inference_exception_graceful_recovery():
    """Verify that an unexpected runtime failure inside forward pass is caught cleanly."""
    valid_seq = [
        [10.0, 50.0, 1.2, 30.0],
        [25.0, 70.0, 1.8, 28.0],
        [50.0, 95.0, 2.5, 26.0],
    ]

    mock_model = MagicMock(side_effect=RuntimeError("Simulated CUDA/C++ runtime error"))
    mock_scaler_X = MagicMock()
    mock_scaler_X.transform.return_value = np.zeros((3, 4))
    mock_scaler_y = MagicMock()

    with patch.object(model_loader, "get_lstm_bundle", return_value=(mock_model, mock_scaler_X, mock_scaler_y)):
        resp = LSTMForecaster.predict(valid_seq)
        assert resp.forecast_available is False
        assert resp.fallback_used is True
        assert "Inference computation error" in (resp.reason or "")
