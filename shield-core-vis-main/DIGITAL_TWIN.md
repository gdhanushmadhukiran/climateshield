# ClimateShield Phase 7: Constrained Climate Resilience Digital Twin

> **Architecture, Mathematical Foundations, Operational Safety & Multi-Criteria Intervention Ranking**  
> _HackSprint 2026 — Sustainable Smart Cities & Climate Tech_

---

## 1. Executive Summary & Core Objective

The **ClimateShield Constrained Climate Resilience Digital Twin** is an in-memory, deterministic counterfactual simulation engine and decision-support workspace. It enables emergency managers, municipal civil protection authorities, and infrastructure operators to answer operational "what-if" questions ahead of hazardous climate crests:

1. **What happens if the river stage surges by +0.50m?**
2. **What happens if a convective cloudburst delivers a +30% rainfall spike?**
3. **What happens if the primary access route to King George District Hospital is submerged?**
4. **What happens if we deploy 2 mobile high-capacity dewatering pumps at critical culverts?**
5. **What happens if we deploy 500 meters of rapidly erectable flood barriers along the riverbank?**
6. **Which tactical intervention produces the best modeled resilience improvement across competing criteria?**
7. **What happens if civil authorities do nothing?**

---

## 2. Strict Architectural Invariants & Safety Guardrails

### 2.1 100% In-Memory Counterfactual Cloning (Zero Database Mutation)

A fundamental tenet of operational emergency operations centers (EOC) is that simulation and hypothetical testing **must never corrupt or pollute the active live telemetry or official historical audit logs**.

- **State Isolation**: When a simulation is requested via `POST /api/v1/simulation/run` or `POST /api/v1/simulation/scenarios/{scenario_name}`, the `DigitalTwinService` queries active production entities (`RiskZoneModel`, `AssetModel`, `RiverNodeModel`, `SensorNodeModel`) in read-only mode (`db.query()`).
- **Zero Database Commits**: `db.commit()`, `db.add()`, `db.delete()`, and `db.flush()` are **strictly prohibited** on simulation states. Database record counts before and after simulation runs are identical (verified by automated tests in `test_zero_database_mutation`).
- **Ephemeral Simulation Cache**: Simulation results are assigned a unique ephemeral ID (`SIM-<UUID8>`) and retained in an in-memory circular cache (max 100 entries) for retrieval via `GET /api/v1/simulation/{simulation_id}` without touching disk or database tables.

### 2.2 Strict Operational Terminology Enforcement

To prevent false operator confidence or unfounded guarantees of absolute safety, ClimateShield enforces calibrated operational terminology:

| Approved Terminology                 | Strictly Prohibited Terminology                    | Rationale                                                                |
| ------------------------------------ | -------------------------------------------------- | ------------------------------------------------------------------------ |
| **"MODELED IMPACT"**                 | "Definite outcome", "Guaranteed effect"            | Simulation models are approximations of physics and hydrology.           |
| **"ESTIMATED POPULATION PROTECTED"** | "100% saved residents", "Absolute protection"      | Human behavior and localized structural variations cannot be guaranteed. |
| **"SIMULATED RISK REDUCTION"**       | "Absolute risk elimination", "Complete mitigation" | Residual risk always remains during extreme climate events.              |
| **"PROJECTED"**                      | "Certain", "Proven"                                | Future forecasts carry inherent meteorological uncertainty.              |

---

## 3. Reuse of Existing Deterministic & ML Engines

Rather than building a disconnected toy simulation, Phase 7 directly harnesses and coordinates the proven ClimateShield intelligence stack:

```
                      HYPOTHETICAL WHAT-IF PARAMETERS
                                    │
                                    ▼
                 ┌──────────────────────────────────────┐
                 │         DigitalTwinService           │
                 │       (100% In-Memory Clone)         │
                 └──────────────────┬───────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Phase 4 Hazard  │       │  ML Forecaster   │       │ Phase 5 Response │
│     Engines      │       │     Signal       │       │    Optimizer     │
├──────────────────┤       ├──────────────────┤       ├──────────────────┤
│• FloodHazard     │       │• CorrelatedLSTM  │       │• RouteLogistics  │
│• HeatHazard      │       │  (+3h river      │       │• Multi-Criteria  │
│• SecondaryHazard │       │  stage advisory) │       │  Utility Ranking │
│• ExposureEngine  │       │• Deterministic   │       │• Resource Cost & │
│• Vulnerability   │       │  primacy guard   │       │  ETA Evaluation  │
│• CompositeRisk   │       └──────────────────┘       └──────────────────┘
└──────────────────┘
```

1. **Phase 4 Risk Engines**:
   - `FloodHazardEngine.calculate(...)`: Evaluates water level, overtopping threshold, rate of rise, rainfall intensity, upstream ratio, and elevation.
   - `HeatHazardEngine.calculate(...)`: Computes Rothfusz heat index under ambient temperatures and urban impervious surface fraction.
   - `SecondaryHazardEngine`: Computes drainage stress, storm surge swelling, and air quality index.
   - `ExposureEngine` & `VulnerabilityEngine`: Evaluates population exposure and socio-economic infrastructure vulnerability indices.
   - `CompositeRiskEngine.calculate(...)`: Synthesizes multi-hazard scores with compounding interaction multipliers (e.g. Flood + Drainage compounding multiplier $\times 1.15$).
2. **Phase 6 ML Advisory Signal**:
   - The PyTorch `CorrelatedLSTM` model provides a forward advisory forecast for midstream river stage at $T+3\text{h}$.
   - **Deterministic Primacy Principle**: ML predictions are clearly flagged as advisory. If telemetry is degraded or the model is unavailable, the deterministic risk engine remains authoritative.
3. **Telemetry & Sensor Health Degradation**:
   - If telemetry from `SN-UP-01` is overridden to `DEGRADED` or `OFFLINE`, the `ConfidenceEngine` penalizes composite operational confidence, and response mobilization delays are dynamically added.

---

## 4. Pre-Configured One-Click Scenarios

ClimateShield includes 7 pre-configured operational scenarios accessible via one-click triggers or the REST API:

| Scenario ID             | Name                   | Category                 | Scenario Description                                       | Expected Modeled Effect                                                                       |
| ----------------------- | ---------------------- | ------------------------ | ---------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| `river_rise_0_5m`       | River Rise +0.5m       | ENVIRONMENTAL_SURGE      | +0.50m river stage rise along urban corridor               | Zone A flood hazard escalates into High/Critical range; residual risk mitigable by barriers.  |
| `rainfall_surge_30pct`  | Rainfall Surge +30%    | ENVIRONMENTAL_SURGE      | +30% precipitation intensity across all zones              | Drainage stress increases by ~18%; stormwater pumps mitigate surface waterlogging dwell time. |
| `hospital_road_blocked` | Hospital Road Blocked  | INFRASTRUCTURE_SEVERANCE | Primary arterial road severed to District Hospital         | +15 min emergency detour; prompts NH-16 high-ground emergency bypass routing.                 |
| `deploy_2_pumps`        | Deploy 2x Pumps        | TACTICAL_INTERVENTION    | Mobilizes 2x 5000 GPM high-capacity dewatering pumps       | Lowers simulated composite risk by ~18-24 points at low culverts.                             |
| `deploy_barriers`       | Deploy 500m Barriers   | TACTICAL_INTERVENTION    | Rapid deployment of 500m modular inflatable flood barriers | Contains overbank crest up to 0.45m depth, protecting hospital corridor access.               |
| `sensor_outage`         | Upstream Sensor Outage | SENSOR_DEGRADATION       | Telemetry failure at upstream gauge SN-UP-01               | Composite operational confidence penalized; triggers safety margins.                          |
| `do_nothing`            | Do Nothing             | COUNTERFACTUAL_BASELINE  | Unmitigated hazard progression with zero interventions     | Demonstrates cumulative escalation across 3 zones and 4 infrastructure nodes.                 |

---

## 5. Multi-Criteria Intervention Ranking Methodology

To provide decision-makers with actionable recommendations, ClimateShield evaluates **5 standardized tactical intervention packages**:

1. `INT-01-PUMP`: Pre-stage 2x 5000 GPM Dewatering Pumps
2. `INT-02-BARRIER`: Rapid Deployment of 500m Modular Flood Barriers
3. `INT-03-RESCUE`: Pre-position 3x NDRF Swift-Water Rescue Teams
4. `INT-04-REROUTE`: Emergency Arterial Rerouting & High-Ground Corridor
5. `INT-05-POWER`: Auxiliary Mobile Diesel Generator to 220kV Substation

### 5.1 Multi-Attribute Utility Formulation

Each package $i$ is evaluated across 5 normalized dimensions:

$$U_i = w_{\text{red}} \cdot \tilde{R}_i + w_{\text{pop}} \cdot \tilde{P}_i + w_{\text{assets}} \cdot \tilde{A}_i + w_{\text{cascade}} \cdot C_i + w_{\text{time}} \cdot \left(1 - \frac{\text{ETA}_i}{60}\right)$$

Where:

- **Risk Reduction Weight** ($w_{\text{red}} = 0.35$): Normalized modeled risk score reduction $\tilde{R}_i = \min(1.0, R_i / 35.0)$
- **Population Protected Weight** ($w_{\text{pop}} = 0.25$): Normalized estimated population protected $\tilde{P}_i = P_i / P_{\text{exposed}}$
- **Critical Assets Safeguarded Weight** ($w_{\text{assets}} = 0.20$): Normalized assets protected $\tilde{A}_i = A_i / 3.0$
- **Cascade Interruption Factor** ($w_{\text{cascade}} = 0.10$): Efficacy in halting compounding infrastructural failure $C_i \in [0.65, 0.88]$
- **Response Dispatch Feasibility** ($w_{\text{time}} = 0.10$): Mobilization speed factor based on logistics ETA in minutes

The package with the highest $U_i$ is highlighted as the **"BEST MODELED OPTION"** in the operator interface, accompanied by transparent scoring, cost, and logistics ETAs.

---

## 6. REST API Endpoints

The Digital Twin Simulator is fully exposed via REST APIs mounted at `/api/v1/simulation`:

### 6.1 `GET /api/v1/simulation/scenarios`

Returns the catalog of all 7 pre-configured scenarios with descriptions and parameters.

### 6.2 `POST /api/v1/simulation/scenarios/{scenario_name}`

Executes a named scenario immediately in-memory and returns a full `SimulationRunResponse`.

### 6.3 `POST /api/v1/simulation/run`

Executes an arbitrary parameterized what-if simulation with custom environmental, infrastructure, response, and sensor modifiers.

### 6.4 `GET /api/v1/simulation/{simulation_id}`

Retrieves a previously computed simulation result from the in-memory circular cache.

---

## 7. Verification & Test Suite Summary

The Digital Twin Simulator is validated by **14 automated test cases** in `backend/tests/test_digital_twin.py`, ensuring complete coverage:

- `test_get_scenarios`: Verifies retrieval of all 7 predefined scenarios.
- `test_do_nothing_baseline_simulation`: Verifies counterfactual escalation under unmitigated hazard.
- `test_river_rise_simulation`: Confirms river level surge escalates Zone A risk.
- `test_rainfall_surge_simulation`: Confirms precipitation spike increases drainage stress.
- `test_hospital_road_blocked_simulation`: Verifies accessibility status and cascade chain activation.
- `test_deploy_pumps_and_barriers_reduces_risk`: Confirms residual risk reduction and population protection.
- `test_sensor_outage_confidence_penalty`: Verifies telemetry outage applies confidence penalty.
- `test_intervention_ranking`: Validates multi-attribute utility ranking and Best Modeled Option designation.
- `test_deterministic_repeatability`: Guarantees identical simulation runs produce bit-for-bit identical outputs.
- `test_zero_database_mutation`: **Strictly verifies that database row counts are 100% identical before and after simulation runs.**
- `test_get_scenarios_endpoint`: Verifies HTTP 200 on scenarios API.
- `test_post_named_scenario_endpoint`: Verifies HTTP 200 on named scenario runner.
- `test_post_custom_simulation_endpoint`: Verifies HTTP 200 on custom parameterized runner.
- `test_unknown_named_scenario_returns_404`: Verifies HTTP 404 on invalid scenario names.

**Test Suite Status**: **92 / 92 automated tests passing** across the backend test suite.
**Frontend Status**: `npm run lint` passing (0 errors); `npm run build` passing.
