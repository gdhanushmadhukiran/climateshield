# CLIMATESHIELD — ML FAILURE MODES & RESILIENCE MATRIX

**Document Version:** 1.0  
**Status:** ACTIVE AUDIT & RECOVERY MANUAL

This document outlines the systematic failure modes, diagnostic symptoms, automated mitigations, and operator recovery procedures for ClimateShield's machine learning components.

---

## 1. FAILURE MODES SUMMARY MATRIX

| Failure Mode                                                 | Root Cause                                                               | Automated Detection Mechanism                                                                     | Immediate System Mitigation                                                                            | Operator Recovery Action                                                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------- |
| **FM-01: Model File Missing or Corrupted**                   | Pickle binary missing, permission error, or bad byte sequence            | `ModelLoader.load_all()` catches `FileNotFoundError` or `UnpicklingError`                         | Marks `model_loaded = False`, logs error, sets `fallback_used = True`. System remains 100% operational | Verify disk path in `backend/ml_models/` and restore validated `.pkl` weights from backup.                    |
| **FM-02: Missing Framework Runtime**                         | `torch` or `scikit-learn` not installed in environment                   | `ImportError` caught during `app/ml/model_loader.py` initialization                               | Sets framework flag to `False`; engages heuristic fallback rules; returns status `DEGRADED`            | Install missing dependencies: `py -m pip install torch scikit-learn`.                                         |
| **FM-03: Insufficient Historical Observations**              | New gauge installed or telemetry stream interrupted ($<3$ hours)         | `MLService.get_river_forecast()` counts valid observations                                        | Returns `forecast_available = False` with explanatory reason; never fabricates dummy points            | Allow gauge to accumulate 3 consecutive hourly readings; physical risk calculations proceed normally.         |
| **FM-04: Out-of-Bounds Sensor Inputs**                       | Sensor voltage spikes or gauge malfunction producing unphysical inputs   | `LSTMForecaster.validate_sequence()` and `SensorAnomalyDetector.validate_features()` bounds check | Rejects input tensor; flags `data_quality = DEGRADED`; logs validation warning                         | Dispatch field technician to inspect physical sensor node hardware.                                           |
| **FM-05: High-Frequency Inference Timeout / CPU Saturation** | Sudden burst of concurrent telemetry packets overloading CPU             | Synchronous thread execution with latency measurement                                             | Request latency logged in `ModelLoader.last_inference_latency_ms`; non-blocking async endpoints        | If sustained load exceeds thresholds, offload ML inference to an asynchronous background Celery/Redis worker. |
| **FM-06: Sensor False Anomaly Cascade**                      | Sensor marked `ANOMALOUS` due to unusual weather (e.g. ambient heatwave) | IsolationForest flags $-1$ on telemetry vector                                                    | Telemetry is **not deleted**; sensor health is marked `DEGRADED`; confidence is penalized 10%          | Review sensor status in dashboard; operators can acknowledge or override status via API.                      |
| **FM-07: External Database Credential Leak**                 | Legacy scripts attempting MongoDB Atlas connection                       | Discarded entirely from ML service architecture                                                   | All inference binds strictly to internal PostgreSQL/PostGIS; zero remote database calls                | Ensure no MongoDB libraries or credentials are added back to backend configurations.                          |

---

## 2. DETAILED FAILURE SCENARIOS & CODE FLOW

### Scenario A: PyTorch Fails During Inference

```text
Client Request: GET /api/v1/ml/forecast
       ↓
LSTMForecaster.predict()
       ↓
torch forward pass throws RuntimeError / CUDA out of memory
       ↓
Caught by 'except Exception as e:' in lstm_forecaster.py (Line 135)
       ↓
Logs error: [LSTM_FORECASTER] Inference exception: ...
       ↓
Returns:
{
  "forecast_available": false,
  "fallback_used": true,
  "reason": "Inference computation error: ...",
  "data_quality": "DEGRADED"
}
       ↓
HTTP 200 returned safely (FastAPI never crashes)
```

### Scenario B: Sensor Anomaly Detection Under Heuristic Fallback

```text
IsolationForest pickle unavailable / scikit-learn missing
       ↓
SensorAnomalyDetector.evaluate() detects model == None
       ↓
Engages deterministic heuristic rules:
- battery_voltage < 2.5V?
- signal_dbm < -115 dBm?
- reading_stuck_count > 8?
- |rate_of_change_temp| > 20°C?
       ↓
Returns:
{
  "status": "DEGRADED",
  "is_anomaly": true,
  "fallback_used": true,
  "reason": "IsolationForest model not loaded in memory; heuristic fallback active"
}
```

---

## 3. VERIFICATION & HEALTH AUDITING

To verify that fallback mechanisms are healthy:

1. Run `GET /api/v1/ml/health`
2. Check `inference_readiness` and `fallback_used`
3. Inspect `backend/tests/test_ml_integration.py::test_ml_fallback_when_offline` which mocks model failure and asserts zero crashes.
