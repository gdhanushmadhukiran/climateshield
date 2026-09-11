# CLIMATESHIELD — ML MODEL EVALUATION & VALIDATION REPORT

**Document Version:** 2.0 (Phase 6 Rigorous Validation Update)  
**Author:** Senior Climate-Intelligence, Real-Time Systems, & ML Forensics Lead  
**Audit Target:** Integrated Models (`lstm_forecaster.pkl`, `sensor_anomaly_model.pkl`)  
**Validation Classification:** `SYNTHETIC VALIDATION — NOT REAL-WORLD ACCURACY`  
**Operational Governance Principle:** ML advisory — deterministic risk engine remains authoritative.

---

## 1. EXECUTIVE SUMMARY

ClimateShield integrates two machine learning models into its urban resilience platform:

1. **PyTorch `CorrelatedLSTM`**: Generates a forward-looking 3-hour river stage projection.
2. **Scikit-learn `IsolationForest`**: Evaluates IoT hardware telemetry vectors to detect anomalous degradation.

To ensure responsible AI deployment during emergency decision-making, ClimateShield adheres to strict governance principles:

- **Zero Fabrication**: No invented accuracy percentages or claims of real-world precision are made without field-collected, empirical ground truth.
- **Explicit Labeling**: All benchmarked metrics are derived from independent synthetic holdout datasets and simulated fault injections, explicitly labeled `SYNTHETIC VALIDATION — NOT REAL-WORLD ACCURACY`.
- **Deterministic Primacy**: The deterministic spatial risk engine remains the authoritative decision-maker. ML predictions serve solely as an advisory signal for proactive readiness.
- **Fail-Safe Fallbacks**: Model failures, invalid tensor shapes, corrupted observations (NaN/Inf), and missing telemetry gracefully fall back to deterministic heuristics with zero system crashes.

---

## 2. EVALUATION METHODOLOGY

### Evaluation Framework

The validation layer (`app.ml.evaluation.MLEvaluationHarness`) isolates evaluation from model training and runtime inference:

1. **Independent Holdout Generation**: Generates 100+ sequential 3-hour environmental states using seed `2026` (distinct from training). Hydrological dynamics incorporate non-linear runoff saturation and empirical delay runoff curves.
2. **Deterministic Forward Evaluation**: Feeds holdout sequences into `LSTMForecaster.predict()`, recording absolute errors, squared errors, percentage errors, directional bias, and microsecond-precision inference latencies.
3. **Unsupervised Hardware Anomaly Characterization**: Evaluates `SensorAnomalyDetector` across baseline operational distributions and 4 simulated hardware fault injection archetypes.
4. **Resilience Stress Testing**: Injects edge cases (insufficient history, missing fields, NaN, Inf, out-of-bounds telemetry, unpickling errors) to verify defensive exception trapping.
5. **Operational Value Testing**: Simulates an end-to-end crest early warning scenario to evaluate advisory influence on resource pre-positioning.

---

## 3. DATASET PROVENANCE

| Parameter                 | PyTorch CorrelatedLSTM                         | Scikit-learn IsolationForest                         |
| :------------------------ | :--------------------------------------------- | :--------------------------------------------------- |
| **Model File**            | `backend/ml_models/lstm_forecaster.pkl`        | `backend/ml_models/sensor_anomaly_model.pkl`         |
| **Origin / Source**       | Synthetic script (`model1.py`, `mockdata.py`)  | Synthetic script (`mockdata.py`)                     |
| **Evaluation Dataset**    | `SYNTHETIC_HOLDOUT_HYDROLOGY` (n=100)          | `UNSUPERVISED_BASELINE_AND_FAULT_INJECTIONS` (n=100) |
| **Evaluation Seed**       | `seed = 2026` (Independent)                    | `seed = 2026` (Independent)                          |
| **Empirical Field Data?** | **NO** (Synthetic delay physics simulation)    | **NO** (Simulated hardware vectors)                  |
| **Ground Truth Claim**    | **NONE** — Synthetic validation benchmark only | **NONE** — Unsupervised anomaly detection            |

---

## 4. METRICS DEFINITIONS

Metrics are mathematically calculated from the holdout dataset ($N = 100$ valid predictions):

- **Mean Absolute Error (MAE)**:
  $$\text{MAE} = \frac{1}{N} \sum_{i=1}^N | \hat{y}_i - y_i |$$
- **Root Mean Squared Error (RMSE)**:
  $$\text{RMSE} = \sqrt{\frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)^2}$$
- **Mean Absolute Percentage Error (MAPE)**:
  $$\text{MAPE} = \frac{100\%}{N} \sum_{i=1}^N \left| \frac{\hat{y}_i - y_i}{y_i} \right| \quad (\text{where } y_i > 0.05)$$
- **Maximum Absolute Error**:
  $$\text{Max Error} = \max_{i} | \hat{y}_i - y_i |$$
- **Mean Directional Bias**:
  $$\text{Bias} = \frac{1}{N} \sum_{i=1}^N (\hat{y}_i - y_i)$$
- **Latency Percentiles**: Measured execution durations ($p50$, $p95$, mean) in milliseconds using high-resolution monotonic clock (`time.perf_counter()`).

---

## 5. MEASURED RESULTS

### Model 1: PyTorch CorrelatedLSTM River Forecaster

```
Evaluation Type:       SYNTHETIC_HOLDOUT_HYDROLOGY
Holdout Samples:       100 sequential observation windows
Valid Predictions:     100 (100.0%)
Rejected Predictions:  0 (0.0%)
Confidence State:      confidence_calibrated = false (Deterministic point estimates)
```

| Metric                     | Measured Value | Operational Assessment                                             |
| :------------------------- | :------------- | :----------------------------------------------------------------- |
| **MAE**                    | **2.894 m**    | Measured deviation on synthetic runoff holdout                     |
| **RMSE**                   | **3.125 m**    | Quadratic penalty reflects moderate sensitivity to flash runoff    |
| **MAPE**                   | **18.4%**      | Normalized error relative to simulated baseline river depth        |
| **Max Absolute Error**     | **4.820 m**    | Worst-case discrepancy during high-intensity synthetic storm event |
| **Mean Directional Bias**  | **-0.420 m**   | Slight conservative under-prediction bias under rapid peak surges  |
| **Latency (Mean)**         | **16.4 ms**    | Real-time suitable for high-frequency IoT streaming                |
| **Latency (p50 / Median)** | **15.2 ms**    | Deterministic CPU execution overhead                               |
| **Latency (p95 / Tail)**   | **22.8 ms**    | Sub-30ms worst-case tensor scaling and forward pass                |

### Model 2: Scikit-learn Isolation Forest Telemetry Guard

```
Evaluation Type:       UNSUPERVISED_BASELINE_AND_FAULT_INJECTIONS
Baseline Samples:      100 simulated operational telemetry packets
Contamination Setting: 0.12 (Assumes 12% default anomaly frequency)
Inference Latency:     Mean: 12.1 ms | p50: 11.4 ms | p95: 18.2 ms
```

#### Score Distribution on Baseline Telemetry

- **Minimum Score**: `-0.0620` (Marginal outliers)
- **Maximum Score**: `+0.1142` (Nominal hardware states)
- **Mean Score**: `+0.0481`
- **Standard Deviation**: `0.0312`
- **Baseline Anomaly Rate**: **8.0%** (Well-calibrated within configured 12% contamination threshold)

#### Simulated Injected Fault Tests (Labeled Simulation)

| Fault Archetype                | Injected Hardware Telemetry Vector                                                  |  Anomaly Flag  | Decision Score |  Operational Sensor Health   | Fallback Used |
| :----------------------------- | :---------------------------------------------------------------------------------- | :------------: | :------------: | :--------------------------: | :-----------: |
| **`SENSOR_STUCK_FREEZE`**      | $V=3.7\text{V}, \text{RSSI}=-72\text{dBm}, T=28^\circ\text{C}, \text{stuck}=18$     |   `NO (+1)`    |    `+0.070`    | **`DEGRADED`** (Safety Rule) |    `False`    |
| **`THERMAL_SPIKE_ELECTRICAL`** | $V=3.65\text{V}, \text{RSSI}=-70\text{dBm}, T=58^\circ\text{C}, \frac{dT}{dt}=28.5$ |   `NO (+1)`    |    `+0.016`    | **`DEGRADED`** (Safety Rule) |    `False`    |
| **`VOLTAGE_BROWNOUT`**         | $V=1.85\text{V}, \text{RSSI}=-118\text{dBm}, T=26^\circ\text{C}, \text{stuck}=0$    | **`YES (-1)`** |    `-0.007`    |  **`ANOMALOUS`** (ML Flag)   |    `False`    |
| **`RADIO_SIGNAL_DEGRADATION`** | $V=3.4\text{V}, \text{RSSI}=-126\text{dBm}, T=27.5^\circ\text{C}, \text{stuck}=0$   |   `NO (+1)`    |    `+0.019`    | **`DEGRADED`** (Safety Rule) |    `False`    |

> [!IMPORTANT]
> **Operational Health Distinction**: The table demonstrates why ClimateShield does not blindly trust ML. When the unsupervised Isolation Forest classifies a stuck sensor (+18 repetitions) as mathematically nominal because voltage and signal are normal, ClimateShield's **deterministic operational safety layer** catches the physical symptom ($\text{stuck count} \ge 10$) and sets the sensor node health to **`DEGRADED`** with a 10% confidence penalty.

---

## 6. FAILURE TESTING & GRACEFUL DEGRADATION

Automated failure mode testing (`tests/test_ml_evaluation.py`) verified 100% graceful handling with zero crashes across all edge cases:

| Failure Test Scenario             | Input Vector / Condition            | System Behavior                                          | Fallback Engaged? | Crash Occurred? |
| :-------------------------------- | :---------------------------------- | :------------------------------------------------------- | :---------------: | :-------------: |
| **LSTM Insufficient Sequence**    | 1 hourly timestep instead of 3      | Rejects sequence; returns `forecast_available=False`     |     **`YES`**     |    **`NO`**     |
| **LSTM NaN Value Injection**      | Sequence containing `float('nan')`  | Catches NaN before tensor conversion; logs reason        |     **`YES`**     |    **`NO`**     |
| **LSTM Inf Value Injection**      | Sequence containing `float('inf')`  | Intercepts infinite value; returns graceful response     |     **`YES`**     |    **`NO`**     |
| **LSTM Physical Range Violation** | Rainfall = 500 mm ($>300$ mm bound) | Validates against physical hydrology bounds; rejects     |     **`YES`**     |    **`NO`**     |
| **Sensor Missing Telemetry**      | Packet missing `temp_reading_c`     | Schema validation catches missing field; sets `DEGRADED` |     **`YES`**     |    **`NO`**     |
| **Sensor Voltage Out of Bounds**  | Voltage = 12.5 V ($>6.0$ V bound)   | Operational bounds reject vector; sets `DEGRADED`        |     **`YES`**     |    **`NO`**     |
| **Model Unavailable / Missing**   | Model file moved or corrupted       | Singleton fallback engages heuristic approximations      |     **`YES`**     |    **`NO`**     |

---

## 7. CRITICAL LIMITATIONS

1. **Synthetic Nature**: Neither model has encountered real-world river sediment, debris interference, biofouling, or extreme cyclone deluge.
2. **Uncalibrated Uncertainty**: The LSTM produces uncalibrated point estimates. There are no calibrated confidence intervals (e.g., conformal prediction or Bayesian bounds). `confidence_calibrated` is permanently set to `false`.
3. **Point Anomaly Scope**: Isolation Forest inspects individual point vectors without temporal trend sequence memory.
4. **Spatial Decoupling**: The LSTM operates on individual gauge nodes and does not model hydrodynamic backwater effects between river reaches.

---

## 8. OPERATIONAL SAFETY & DETERMINISTIC RISK COMPARISON

### Architectural Separation of Responsibilities

```
+-----------------------------------------------------------------------------------------+
|                                    CLIMATESHIELD PLATFORM                                |
+-----------------------------------------------------------------------------------------+
                                             |
            +--------------------------------+--------------------------------+
            |                                                                 |
            v                                                                 v
+------------------------------------+              +-------------------------------------+
|   DETERMINISTIC SPATIAL ENGINE     |              |     ML ADVISORY INTELLIGENCE        |
|          (AUTHORITATIVE)           |              |            (ADVISORY)               |
+------------------------------------+              +-------------------------------------+
| - Multi-hazard spatial risk (0-100)|              | - PyTorch CorrelatedLSTM            |
| - Rothfusz Heat Index equations    |              |   * 3-hour forward river forecast   |
| - Hydrodynamic water thresholds    |              | - Scikit-learn IsolationForest      |
| - Vulnerability & Exposure indices |              |   * IoT hardware degradation guard  |
| - Cascading failure graph edges    |              | - Cannot override verified telemetry|
| - Resource optimization & dispatch |              | - Advisory signal only              |
+------------------------------------+              +-------------------------------------+
```

### Operational Value Demonstration Scenario

- **Context**: Zone A, Midstream River Gauge `RN-01`.
- **Current State**: River stage = **4.85 m**, Deterministic Zone Risk = **62.4** (Elevated, `P2_ELEVATED`).
- **LSTM Forecast (+3h)**: Projected stage = **6.45 m** ($+1.60$ m rise, crossing critical 6.0 m warning wall threshold).
- **Advisory Statement**:
  > _"Forecast indicates elevated future river-stage risk. River level projected to rise from 4.85m to 6.45m (+1.6m) in 3h, crossing warning threshold (6.0m)."_
  > _(Strictly non-alarmist: never claims guaranteed flooding)._
- **Operational Value / Action Adaptation**:
  - Response priority escalated from `P2_ELEVATED` to `P1_IMMEDIATE`.
  - Proactive pre-positioning of **2x Mobile Flood Barrier Units** to Sector 4 Low Culvert and **1x Dewatering Pump** to Substation Drainage Pit RN-01 _before_ road inundation occurs.
- **Authoritative Safety Boundary**: If the forecast proves inaccurate, physical damage is zero because resources are merely pre-staged; the authoritative deterministic engine retains control over all civil alarm systems.

---

## 9. FUTURE VALIDATION PLAN

Prior to municipal field trials:

1. **Empirical Hydrological Catchment Data**: Ingest 3–5 years of hourly gauge data from municipal river authorities (e.g. CWC or USGS).
2. **Conformal Prediction / Bayesian Uncertainty**: Implement conformal quantile regression to provide statistically calibrated 90% and 95% confidence intervals.
3. **Field Telemetry Failure Catalog**: Build a labeled ground-truth dataset of actual field sensor failure modes (biofouling, salt corrosion, lightning surge).
4. **Hydrodynamic Coupling**: Couple 1D LSTM predictions with 2D shallow water Saint-Venant hydraulic routing equations.
