"""Tests for ClimateShield Phase 6 ML Evaluation & Validation Layer."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ml.evaluation import MLEvaluationHarness
from app.ml.lstm_forecaster import LSTMForecaster
from app.ml.sensor_anomaly import SensorAnomalyDetector


@pytest.fixture
def client():
    return TestClient(app)


class TestMLEvaluationHarness:
    """Unit tests for ML evaluation methods and synthetic holdout harness."""

    def test_synthetic_holdout_generation(self):
        holdout = MLEvaluationHarness.generate_synthetic_holdout(n_samples=25, seed=42)
        assert len(holdout) == 25
        for sample in holdout:
            assert "sample_id" in sample
            assert "sequence" in sample
            assert "current_level" in sample
            assert "ground_truth_target_3h" in sample
            seq = sample["sequence"]
            assert len(seq) == 3
            assert all(len(step) == 4 for step in seq)
            assert sample["ground_truth_target_3h"] > 0

    def test_lstm_evaluation_metrics(self):
        eval_result = MLEvaluationHarness.evaluate_lstm(n_samples=30, seed=123)
        assert eval_result["model_name"] == "CorrelatedLSTM River Forecaster"
        assert eval_result["evaluation_dataset_type"] == "SYNTHETIC_HOLDOUT_HYDROLOGY"
        assert "SYNTHETIC VALIDATION — NOT REAL-WORLD ACCURACY" in eval_result["disclaimer"]
        assert eval_result["confidence_calibrated"] is False
        assert eval_result["valid_predictions"] > 0

        metrics = eval_result["metrics"]
        assert "mae_meters" in metrics and metrics["mae_meters"] >= 0.0
        assert "rmse_meters" in metrics and metrics["rmse_meters"] >= 0.0
        assert "max_absolute_error_meters" in metrics and metrics["max_absolute_error_meters"] >= 0.0
        assert "mean_bias_meters" in metrics
        assert metrics["rmse_meters"] >= metrics["mae_meters"]  # Mathematical property: RMSE >= MAE

        latencies = eval_result["latency_ms"]
        assert latencies["mean"] > 0
        assert latencies["p50"] > 0
        assert latencies["p95"] >= latencies["p50"]

    def test_isolation_forest_evaluation(self):
        eval_result = MLEvaluationHarness.evaluate_isolation_forest(n_samples=30, seed=123)
        assert eval_result["model_name"] == "Sensor Telemetry Isolation Forest"
        assert eval_result["evaluation_type"] == "UNSUPERVISED_BASELINE_AND_FAULT_INJECTIONS"
        assert "SIMULATION" in eval_result["disclaimer"]
        assert 0.0 <= eval_result["baseline_anomaly_rate_percent"] <= 100.0

        scores = eval_result["score_distribution"]
        assert scores["min"] <= scores["max"]

        faults = eval_result["injected_fault_simulations"]
        assert len(faults) >= 4
        # Verify simulated fault archetypes
        fault_names = {f["fault_name"] for f in faults}
        assert "SENSOR_STUCK_FREEZE" in fault_names
        assert "THERMAL_SPIKE_ELECTRICAL" in fault_names
        assert "VOLTAGE_BROWNOUT" in fault_names
        assert "RADIO_SIGNAL_DEGRADATION" in fault_names

        for f in faults:
            assert f["detected_as_anomaly"] is True or f["operational_status"] in ("ANOMALOUS", "DEGRADED")

    def test_forecast_quality_categorization(self):
        # Good clean sequence
        good_seq = [[5.0, 45.0, 3.2, 28.0], [8.0, 48.0, 3.3, 27.5], [12.0, 52.0, 3.4, 27.0]]
        res_good = MLEvaluationHarness.categorize_forecast_quality(good_seq, data_freshness_seconds=60.0)
        assert res_good["category"] == "GOOD"
        assert res_good["confidence_calibrated"] is False

        # Insufficient data
        res_insufficient = MLEvaluationHarness.categorize_forecast_quality([[5.0, 45.0, 3.2, 28.0]])
        assert res_insufficient["category"] == "INSUFFICIENT_DATA"
        assert res_insufficient["confidence_calibrated"] is False

        # Degraded sequence (out of bounds or stale)
        bad_seq = [[5.0, 45.0, -10.0, 28.0], [8.0, 48.0, 3.3, 27.5], [12.0, 52.0, 3.4, 27.0]]
        res_degraded = MLEvaluationHarness.categorize_forecast_quality(bad_seq)
        assert res_degraded["category"] == "DEGRADED"

        # Stale observations (e.g. 3 hours old)
        res_stale = MLEvaluationHarness.categorize_forecast_quality(good_seq, data_freshness_seconds=10800.0)
        assert res_stale["category"] == "DEGRADED"

    def test_failure_modes_zero_crashes(self):
        failures = MLEvaluationHarness.test_failure_modes()
        assert failures["all_failure_modes_handled"] is True
        assert len(failures["lstm_failure_tests"]) >= 4
        assert len(failures["isolation_forest_failure_tests"]) >= 2
        assert all(t["handled_gracefully"] for t in failures["lstm_failure_tests"])
        assert all(t["handled_gracefully"] for t in failures["isolation_forest_failure_tests"])

    def test_operational_scenario_governance(self):
        scenario = MLEvaluationHarness.get_operational_scenario()
        assert scenario["scenario_name"] == "MIDSTREAM_CREST_EARLY_WARNING"
        assert scenario["current_state"]["river_stage_m"] == 4.85
        assert scenario["ml_forecast"]["predicted_stage_m"] == 6.45
        assert scenario["response_adaptation"]["priority_escalation"] == "P2_ELEVATED -> P1_IMMEDIATE"
        # Verify non-alarmist wording requirement
        assert "Forecast indicates elevated future river-stage risk" in scenario["ml_forecast"]["advisory_statement"]
        assert "Flood will definitely occur" not in scenario["ml_forecast"]["advisory_statement"]
        assert "deterministic risk engine remains authoritative" in scenario["governance_note"]


class TestMLEvaluationAPI:
    """Integration tests for FastAPI evaluation endpoints."""

    def test_get_evaluation_endpoint(self, client):
        response = client.get("/api/v1/ml/evaluation?samples=25")
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "SYNTHETIC VALIDATION" in data["disclaimer"]
        assert "lstm_evaluation" in data
        assert "isolation_forest_evaluation" in data
        assert "failure_mode_testing" in data
        assert data["deterministic_primacy_principle"] == "ML advisory — deterministic risk engine remains authoritative."

        lstm = data["lstm_evaluation"]
        assert lstm["model_version"] == "CorrelatedLSTM-v1.0-synthetic"
        assert lstm["confidence_calibrated"] is False
        assert "mae_meters" in lstm["metrics"]

        iso = data["isolation_forest_evaluation"]
        assert iso["model_version"] == "IsolationForest-v1.0-synthetic"
        assert "injected_fault_simulations" in iso

    def test_get_operational_scenario_endpoint(self, client):
        response = client.get("/api/v1/ml/operational-scenario")
        assert response.status_code == 200
        data = response.json()
        assert data["scenario_name"] == "MIDSTREAM_CREST_EARLY_WARNING"
        assert "response_adaptation" in data
        assert "resources" in str(data["response_adaptation"]).lower() or "recommended_resources" in data["response_adaptation"]
        assert "Forecast indicates elevated future river-stage risk" in data["ml_forecast"]["advisory_statement"]
