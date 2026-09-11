# CLIMATESHIELD — ML MODEL FORENSIC AUDIT & INVENTORY REPORT

**Audit Date:** September 11, 2026  
**Auditor:** Senior Climate-Intelligence, Systems, & ML Forensics Lead  
**Audit Target:** `backend/ml_models/` directory (Supplied ML Model Artifacts)  
**Status:** FORENSIC AUDIT COMPLETE — ZERO APPLICATION CODE MODIFIED

---

## EXECUTIVE SUMMARY

A comprehensive forensic decompilation and source-code audit was conducted on the supplied ML bundle located in `backend/ml_models/`.

The bundle does **NOT** contain a single monolithic "climate risk model". Instead, it consists of **four distinct, decoupled models** spanning different frameworks (PyTorch, XGBoost, Scikit-learn):

1. **Model 1 (`asset_risk_model.pkl`)**: An **XGBoost 4-class classification model** that maps 5 environmental and asset attributes to discrete categorical risk levels (`0=Low, 1=Medium, 2=High, 3=Critical`). It was trained as a surrogate model imitating a hardcoded 4-line rule-based heuristic.
2. **Model 2 (`lstm_forecaster.pkl`)**: A **PyTorch LSTM time-series regression model** (`CorrelatedLSTM`) that takes a 3-timestep sequence of 4 hydrometeorological features and forecasts river water level 3 hours ahead (`target_river_level_plus_3h` in meters).
3. **Model 3 (`sensor_anomaly_model.pkl`)**: A **Scikit-learn Isolation Forest** unsupervised anomaly detector that inspects 5 hardware telemetry signals to identify faulty or failing physical sensors (`1=normal, -1=anomaly`).
4. **Model 4 (`cv_depth_model.pkl`)**: A **Scikit-learn Ridge Linear Regression** model that estimates flood inundation depth in centimeters ($cm$) as a function of a camera detection confidence score.

### Critical Forensic Findings:

- **Data Provenance**: All models were trained on **100% synthetic/mock data** generated via `np.random.uniform` in `mockdata.py` and `realtimedata.py`. None of the models were trained on real empirical historical sensor logs.
- **External Dependency & Hardcoded Credentials**: `realtimepredict.py`, `realtimedata.py`, `model1.py`, and `mockdata.py` contain **hardcoded MongoDB Atlas credentials** in plaintext (`mongodb+srv://viswesg15:31606021@cluster0.zcptndf.mongodb.net/`).
- **Database Mismatch**: The inference scripts expect a remote MongoDB NoSQL database with 4 collections (`time_series_data`, `tabular_risk_data`, `vision_metadata`, `sensor_telemetry_faults`), whereas ClimateShield's core operational system runs on PostgreSQL + PostGIS (with SQLAlchemy 2.0 and Pydantic v2).
- **Environment Incompatibility**: The current backend environment (`backend/requirements.txt`) does not have `torch`, `xgboost`, `scikit-learn`, `pandas`, `numpy`, `pymongo`, or `schedule` installed.

---

## 1. COMPLETE MODEL INVENTORY

The directory `backend/ml_models/` contains 9 files totaling ~2.1 MB:

| File Name                  | File Size                 | Type / Format      | Purpose in Supplied Bundle                                                                         |
| -------------------------- | ------------------------- | ------------------ | -------------------------------------------------------------------------------------------------- |
| `asset_risk_model.pkl`     | 401,180 bytes (~392 KB)   | Python Pickle (v4) | Pretrained XGBoost Classifier weights for 4-class asset risk categorization                        |
| `cv_depth_model.pkl`       | 729 bytes                 | Python Pickle (v4) | Pretrained Ridge Regression weights + StandardScaler for flood depth estimation                    |
| `lstm_forecaster.pkl`      | 23,288 bytes (~23 KB)     | Python Pickle (v4) | Pretrained PyTorch CorrelatedLSTM model + Scaler_X + Scaler_y for 3-hour river stage forecasting   |
| `sensor_anomaly_model.pkl` | 1,666,617 bytes (~1.6 MB) | Python Pickle (v4) | Pretrained Scikit-learn Isolation Forest for IoT hardware fault detection                          |
| `mockdata.py`              | 2,202 bytes               | Python Script      | Synthetic data generator populating MongoDB `time_series_data` and `vision_metadata`               |
| `model1.py`                | 2,590 bytes               | Python Script      | Training pipeline script retraining Model 2 (LSTM) and Model 4 (Ridge) from MongoDB                |
| `realtimedata.py`          | 5,368 bytes               | Python Script      | Continuous real-time async streamer (1s loop) inserting synthetic ticks into 4 MongoDB collections |
| `realtimepredict.py`       | 7,936 bytes               | Python Script      | Scheduled hourly batch inference runner loading the 4 PKLs and writing predictions to MongoDB      |
| `test.py`                  | 2,037 bytes               | Python Script      | Standalone verification test running Model 2 (LSTM) and Model 4 (Ridge) with synthetic tensors     |

### Missing Artifacts in Supplied Bundle:

- **No requirements.txt or environment.yml**: Dependencies (`torch`, `xgboost`, `scikit-learn`, `pymongo`, `schedule`, `pandas`) are undeclared.
- **No training code for Model 1 (XGBoost) or Model 3 (IsolationForest)**: Only retrain scripts for Model 2 and 4 exist (`model1.py`). The original training scripts for `asset_risk_model.pkl` and `sensor_anomaly_model.pkl` are absent.
- **No evaluation metrics / test datasets**: No test splits, validation sets, confusion matrices, RMSE/MAE evaluation reports, or ground truth benchmarks exist.
- **No tokenizer / encoders**: None required (all features are numeric floats/ints).

---

## 2. DETAILED MODEL SPECIFICATIONS

### Model 1: Asset Risk Classifier (`asset_risk_model.pkl`)

- **Algorithm / Architecture**: Gradient Boosted Decision Trees — `xgboost.sklearn.XGBClassifier` (underlying C++ `xgboost.core.Booster`).
- **Framework & Library**: XGBoost (`xgboost>=1.6`).
- **Hyperparameters**:
  - `n_estimators`: 100
  - `max_depth`: 4
  - `learning_rate` / `eta`: 0.3 (default)
  - `objective`: `multi:softprob`
  - `tree_method`: `auto`
- **Input Dimensions**: 5 scalar features: `[elevation_m, drainage_capacity, rainfall_mm_h, temperature_c, humidity_pct]`. Shape: `(batch_size, 5)`.
- **Output Dimensions**: Probability distribution over 4 classes or discrete integer class $\in \{0, 1, 2, 3\}$. Shape: `(batch_size,)`.
- **Prediction Target**: `risk_level` (0 = Low, 1 = Medium, 2 = High, 3 = Critical).
- **Training Objective / Loss**: Multi-class cross-entropy (`multi:softprob` with softmax activation).
- **Temporal / Spatial Resolution**: Static point tabular record per asset. No temporal sequence window.
- **Underlying Heuristic Imbalance**: Decompilation of `realtimedata.py` reveals the ground truth was generated by this exact rule:
  ```python
  if rain > 60 and elev < 20 and drain < 0.4:
      return 3  # Critical
  elif temp > 42 and hum > 70:
      return 2  # High
  elif rain > 30 or temp > 38:
      return 1  # Medium
  return 0      # Low
  ```

---

### Model 2: Hydrological Time-Series Forecaster (`lstm_forecaster.pkl`)

- **Algorithm / Architecture**: Recurrent Neural Network with Long Short-Term Memory — PyTorch `CorrelatedLSTM`:
  ```text
  Input Tensor: (batch_size, seq_len=3, input_size=4)
         ↓
  nn.LSTM(input_size=4, hidden_size=32, batch_first=True)
         ↓
  Extract last sequence output: out[:, -1, :]  (batch_size, 32)
         ↓
  nn.Linear(in_features=32, out_features=1)
         ↓
  Scalar Prediction: (batch_size, 1)
  ```
- **Framework & Library**: PyTorch (`torch>=2.0.0`).
- **Hyperparameters**:
  - `input_size`: 4
  - `hidden_size`: 32
  - `num_layers`: 1
  - `dropout`: 0.0
  - `batch_size`: 16
  - `epochs`: 60
  - `learning_rate`: 0.01 (Adam optimizer)
- **Loss Function**: Mean Squared Error (`nn.MSELoss()`).
- **Activation Functions**: Tanh and Sigmoid (internal to LSTM gates), Linear (output layer).
- **Sequence / Window Requirements**: Exactly **3 consecutive hourly timesteps** (`seq_len = 3`).
- **Input Dimensions**: 3 steps $\times$ 4 features: `[rainfall_mm, soil_moisture_pct, river_level_m, temperature_c]`. Shape: `(batch_size, 3, 4)`.
- **Preprocessors**:
  - `scaler_X`: `sklearn.preprocessing.StandardScaler` (4 features).
  - `scaler_y`: `sklearn.preprocessing.StandardScaler` (1 target feature).
- **Output Dimensions**: Single continuous scalar float. Shape: `(batch_size, 1)`.
- **Prediction Target**: `target_river_level_plus_3h` (projected river water level in meters at $t + 3\text{ hours}$).

---

### Model 3: Sensor Hardware Anomaly Detector (`sensor_anomaly_model.pkl`)

- **Algorithm / Architecture**: Isolation Forest — `sklearn.ensemble._iforest.IsolationForest`.
- **Framework & Library**: Scikit-learn (`scikit-learn>=1.2.0`).
- **Hyperparameters**:
  - `n_estimators`: 100 isolation trees
  - `max_samples`: "auto" (256 samples per tree)
  - `contamination`: 0.12 (assumes 12% baseline anomaly rate)
  - `bootstrap`: False
  - `n_jobs`: None
- **Input Dimensions**: 5 scalar features: `[battery_voltage, signal_dbm, temp_reading_c, rate_of_change_temp, reading_stuck_count]`. Shape: `(batch_size, 5)`.
- **Output Dimensions**: Binary classification flag $\in \{1, -1\}$. Shape: `(batch_size,)`.
- **Prediction Target**: `is_anomaly`:
  - `+1`: Normal operational telemetry.
  - `-1`: Hardware fault / telemetry anomaly.
- **Temporal / Spatial Resolution**: Point inspection per sensor telemetry packet. No temporal window required.

---

### Model 4: Vision-Based Flood Depth Estimator (`cv_depth_model.pkl`)

- **Algorithm / Architecture**: Ridge Linear Regression with $L_2$ regularization — `sklearn.linear_model._ridge.Ridge`.
- **Framework & Library**: Scikit-learn (`scikit-learn>=1.2.0`).
- **Hyperparameters**:
  - `alpha`: 0.1 ($L_2$ regularization strength)
  - `fit_intercept`: True
  - `solver`: "auto"
- **Input Dimensions**: 1 scalar feature: `confidence_score` (from a CCTV / YOLO waterlogging detector). Shape: `(batch_size, 1)`.
- **Preprocessor**: `sklearn.preprocessing.StandardScaler` fitted on `confidence_score`.
- **Output Dimensions**: Single continuous float. Shape: `(batch_size, 1)`.
- **Prediction Target**: `flood_depth_estimated_cm` (estimated inundation water depth in centimeters).
- **Underlying Training Assumption**: Decompilation of `mockdata.py` line 42 shows this was trained on:
  $$\text{depth} = (\text{confidence\_score}^2) \times 55.0 + \mathcal{N}(0, 2)$$
  _Note:_ The model does **NOT** process raw camera image pixels; it only performs linear regression on an upstream object detector's scalar confidence score.

---

## 3. WHAT EACH MODEL ACTUALLY PREDICTS

| Model Artifact | File Name                  | What Does It Actually Output?                        | Unit / Domain                             | Is It a "Risk Score"?                                                                        |
| -------------- | -------------------------- | ---------------------------------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Model 1**    | `asset_risk_model.pkl`     | **Categorical asset risk class** (`0, 1, 2, 3`)      | Enum: 0=Low, 1=Medium, 2=High, 3=Critical | **YES (Class)**: Categorizes asset risk level, but only learns a synthetic 4-rule heuristic. |
| **Model 2**    | `lstm_forecaster.pkl`      | **Future River Water Level at $t + 3\text{ hours}$** | Meters ($m$)                              | **NO**: It is a hydrological physical time-series forecast, NOT a risk score.                |
| **Model 3**    | `sensor_anomaly_model.pkl` | **Binary Sensor Hardware Fault Flag**                | `+1` (Normal) or `-1` (Fault)             | **NO**: It is an IoT hardware health status classifier.                                      |
| **Model 4**    | `cv_depth_model.pkl`       | **Estimated Flood Inundation Depth**                 | Centimeters ($cm$)                        | **NO**: It is a physical water depth estimator.                                              |

---

## 4. FORMAL INPUT CONTRACTS

### Contract: Model 1 (`asset_risk_model.pkl`)

| Feature Name        | Python Type | Physical Unit              | Required? | Expected Domain / Range | Normalization             | Data Source                           | Window Requirement     |
| ------------------- | ----------- | -------------------------- | --------- | ----------------------- | ------------------------- | ------------------------------------- | ---------------------- |
| `elevation_m`       | `float`     | meters ($m$)               | Yes       | $[5.0, 100.0]$          | None (handled by XGBoost) | GIS Digital Elevation Model (DEM)     | Instantaneous snapshot |
| `drainage_capacity` | `float`     | ratio ($0.0 - 1.0$)        | Yes       | $[0.10, 1.00]$          | None                      | Municipal stormwater network registry | Instantaneous snapshot |
| `rainfall_mm_h`     | `float`     | $mm/hour$                  | Yes       | $[0.0, 150.0]$          | None                      | Weather Radar / Rain Gauge            | 1-hour accumulation    |
| `temperature_c`     | `float`     | Celsius ($^\circ\text{C}$) | Yes       | $[20.0, 50.0]$          | None                      | Weather Station / Ambient Sensor      | Instantaneous snapshot |
| `humidity_pct`      | `float`     | percentage ($\%$)          | Yes       | $[20.0, 100.0]$         | None                      | Ambient Humidity Sensor               | Instantaneous snapshot |

---

### Contract: Model 2 (`lstm_forecaster.pkl`)

| Feature Name        | Python Type | Physical Unit              | Required? | Expected Domain / Range | Normalization                 | Data Source                  | Window Requirement                          |
| ------------------- | ----------- | -------------------------- | --------- | ----------------------- | ----------------------------- | ---------------------------- | ------------------------------------------- |
| `rainfall_mm`       | `float`     | $mm$                       | Yes       | $[0.0, 120.0]$          | `StandardScaler` (`scaler_X`) | Rain Gauge / Telemetry       | 3 consecutive hours ($t_{-2}, t_{-1}, t_0$) |
| `soil_moisture_pct` | `float`     | percentage ($\%$)          | Yes       | $[30.0, 100.0]$         | `StandardScaler` (`scaler_X`) | Ground Saturation Sensor     | 3 consecutive hours ($t_{-2}, t_{-1}, t_0$) |
| `river_level_m`     | `float`     | meters ($m$)               | Yes       | $[0.5, 6.0]$            | `StandardScaler` (`scaler_X`) | Ultrasonic River Stage Gauge | 3 consecutive hours ($t_{-2}, t_{-1}, t_0$) |
| `temperature_c`     | `float`     | Celsius ($^\circ\text{C}$) | Yes       | $[15.0, 50.0]$          | `StandardScaler` (`scaler_X`) | Environmental Sensor         | 3 consecutive hours ($t_{-2}, t_{-1}, t_0$) |

---

### Contract: Model 3 (`sensor_anomaly_model.pkl`)

| Feature Name          | Python Type     | Physical Unit                      | Required? | Expected Domain / Range | Normalization     | Data Source                           | Window Requirement   |
| --------------------- | --------------- | ---------------------------------- | --------- | ----------------------- | ----------------- | ------------------------------------- | -------------------- |
| `battery_voltage`     | `float`         | Volts ($V$)                        | Yes       | $[1.0, 4.5]$            | None (Tree-based) | ESP32 Hardware Telemetry              | Instantaneous packet |
| `signal_dbm`          | `int` / `float` | $dBm$                              | Yes       | $[-130, -40]$           | None              | Cellular / LoRa Telemetry             | Instantaneous packet |
| `temp_reading_c`      | `float`         | Celsius ($^\circ\text{C}$)         | Yes       | $[-10.0, 90.0]$         | None              | Onboard Temperature Sensor            | Instantaneous packet |
| `rate_of_change_temp` | `float`         | $^\circ\text{C} / \text{interval}$ | Yes       | $[0.0, 60.0]$           | None              | Telemetry Derivative ($t_0 - t_{-1}$) | Instantaneous delta  |
| `reading_stuck_count` | `int`           | consecutive count                  | Yes       | $[0, 500]$              | None              | Telemetry Validator Health Check      | Cumulative counter   |

---

### Contract: Model 4 (`cv_depth_model.pkl`)

| Feature Name       | Python Type | Physical Unit             | Required? | Expected Domain / Range | Normalization                  | Data Source                          | Window Requirement      |
| ------------------ | ----------- | ------------------------- | --------- | ----------------------- | ------------------------------ | ------------------------------------ | ----------------------- |
| `confidence_score` | `float`     | probability ($0.0 - 1.0$) | Yes       | $[0.50, 0.99]$          | `StandardScaler` (`scaler_cv`) | CCTV Computer Vision Object Detector | Event detection trigger |

---

## 5. RECONCILIATION WITH CLIMATESHIELD ARCHITECTURE

| ML Model Artifact                        | Intended Role                   | Current ClimateShield Phase Equivalent                                                                             | Can It Be Safely Integrated?                                                                                                                                           |
| ---------------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Model 1 (`asset_risk_model.pkl`)**     | Asset Risk Classification       | **Phase 4 Risk Intelligence Engine** (`app/engine/composite_risk_engine.py`)                                       | **Advisory Only**: Phase 4's deterministic engine is far more comprehensive, transparent, and multi-hazard than this simple 5-feature tree trained on synthetic rules. |
| **Model 2 (`lstm_forecaster.pkl`)**      | 3-Hour River Level Forecast     | **Phase 2 Forecast Trajectory & Phase 3 River Telemetry** (`app/api/v1/forecast.py`, `app/engine/flood_engine.py`) | **High Value**: Can serve as an ML-based forward trajectory curve alongside the deterministic hydrological physics engine.                                             |
| **Model 3 (`sensor_anomaly_model.pkl`)** | Hardware Fault Detection        | **Phase 3 Telemetry Ingestion Pipeline** (`app/services/telemetry_service.py`)                                     | **High Value**: Fits cleanly into the sensor health classifier (`HEALTHY` vs `DEGRADED` vs `OFFLINE`).                                                                 |
| **Model 4 (`cv_depth_model.pkl`)**       | CCTV Inundation Depth Estimator | **Phase 2 Incidents & Spatial Sensors** (`app/models/incident.py`)                                                 | **Low / Conditional**: Only meaningful if municipal cameras provide detection confidence scores.                                                                       |

---

## 6. RECOMMENDATIONS BEFORE ANY FUTURE INTEGRATION

1. **Remove Hardcoded MongoDB Credentials**: Migrate data IO from MongoDB Atlas to ClimateShield's existing PostgreSQL/PostGIS database.
2. **Containerize Model Dependencies**: If PyTorch and XGBoost are to be executed in the backend, add lightweight CPU runtimes to a dedicated worker or microservice to avoid bloating the core FastAPI web service.
3. **Keep Deterministic Engines as Baseline Ground Truth**: Follow Section 2 of Phase 4 instructions: never replace the explainable deterministic risk engine with a black-box model. If ML predictions are exposed, label them explicitly as `PREDICTED_BY_ML` with confidence intervals.
