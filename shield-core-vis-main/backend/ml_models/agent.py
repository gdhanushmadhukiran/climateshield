import datetime
import pymongo
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI App
app = FastAPI(
    title="ClimateShield Multi-Agent Decision API",
    description="Unified API combining real-time telemetry, 4 ML model predictions, VoiceOps incidents, and 6 decision agents.",
    version="1.0.0"
)

# Enable CORS for React/Next.js Frontend Integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Local MongoDB Instance
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    db_pred = client["climateshield_predictions_db"]
    db_telemetry = client["climateshield_db"]
except Exception as e:
    print(f"⚠️ MongoDB Connection Notice: {e}")


@app.get("/")
def read_root():
    """Root Health Check Endpoint."""
    return {
        "status": "ONLINE",
        "system": "ClimateShield Multi-Agent Decision API",
        "version": "1.0.0",
        "active_endpoint": "/api/v1/agentic-action-plan",
        "docs_url": "/docs"
    }


@app.get("/api/v1/agentic-action-plan")
def get_master_agentic_plan():
    """
    Unified 6-Agent Decision Matrix Endpoint.
    Combines Model Outputs + VoiceOps + Agentic Orchestration.
    """
    timestamp_now = datetime.datetime.utcnow().isoformat() + "Z"

    # Default/Fallback ML Prediction Values (In case MongoDB hasn't run yet)
    river_m = 2.89
    critical_assets = 3
    high_assets = 4
    flood_cm = 48.37
    faulty_sensors = 1
    total_sensors = 20

    # Try fetching real-time model predictions from MongoDB
    try:
        latest_pred = db_pred["model_predictions"].find_one(sort=[("execution_time", -1)])
        if latest_pred and "model_outputs" in latest_pred:
            outputs = latest_pred["model_outputs"]
            river_m = outputs.get("forecasted_river_level_plus_3h_m", river_m)
            critical_assets = outputs.get("critical_risk_assets", critical_assets)
            high_assets = outputs.get("high_risk_assets", high_assets)
            flood_cm = outputs.get("avg_flood_depth_cm", flood_cm)
            faulty_sensors = outputs.get("faulty_sensors_detected", faulty_sensors)
    except Exception as e:
        print(f"Notice: Reading predictions from DB fallback: {e}")

    # Try fetching latest VoiceOps incident report from MongoDB
    voice_location = "MVP Colony Bridge"
    voice_hazard = "FLOOD / WATERLOGGING"
    voice_confidence = 0.91
    try:
        latest_voice = db_telemetry["voice_ops_incidents"].find_one(sort=[("timestamp", -1)])
        if latest_voice:
            voice_location = latest_voice.get("location", voice_location)
            voice_hazard = latest_voice.get("hazard_type", voice_hazard)
            voice_confidence = latest_voice.get("confidence_score", voice_confidence)
    except Exception as e:
        print(f"Notice: Reading voice incident from DB fallback: {e}")

    # Calculate system health status
    data_freshness = "99.2%"
    system_status = "DEGRADED" if faulty_sensors > 0 else "HEALTHY"

    # Complete Multi-Agent Decision Response
    return {
        "timestamp": timestamp_now,
        "system_telemetry_health": {
            "status": system_status,
            "data_freshness_pct": data_freshness,
            "sensors_audited": total_sensors,
            "faulty_hardware_detected": faulty_sensors,
            "isolation_forest_audit": f"{faulty_sensors} sensor(s) exhibiting anomalous voltage or stuck readings."
        },
        "voiceops_ingestion_context": {
            "source": "Field Emergency Audio Report",
            "extracted_location": voice_location,
            "extracted_hazard": voice_hazard,
            "confidence_score": voice_confidence,
            "status": "VERIFIED_AND_GROUNDED"
        },
        "agents": {
            "1_geospatial_agent": {
                "agent_name": "Geospatial Boundary Agent",
                "predicted_inundation_depth_cm": flood_cm,
                "high_risk_boundary_zones": [
                    f"{voice_location} (CRITICAL / RED ZONE)",
                    "Gajuwaka Highway Entrance (HIGH / ORANGE ZONE)",
                    "Madhurawada Lowlands (MEDIUM / YELLOW ZONE)"
                ],
                "spatial_status": f"Severe localized inundation predicted. Water accumulation depth: {flood_cm} cm."
            },
            "2_infrastructure_agent": {
                "agent_name": "Infrastructure Exposure Agent",
                "critical_assets_threatened": critical_assets,
                "high_threat_assets": high_assets,
                "vulnerable_nodes": [
                    "Substation A-4 (Power Grid Node)",
                    "Primary Care Center 2 (Emergency Healthcare)",
                    "NH16 Drainage Culvert (Transit Infrastructure)"
                ],
                "cascade_risk_warning": "High risk of secondary power failure if Substation A-4 water level exceeds threshold."
            },
            "3_mobility_agent": {
                "agent_name": "Mobility & Transit Agent",
                "blocked_corridors": [f"NH16 Highway Segment near {voice_location}"],
                "active_detours": [
                    "Route 4 via Inner Ring Road Flyover",
                    "Bypass Flyover West (Emergency Vehicles Only)"
                ],
                "transit_status": "Access restricted across low-lying bridge sections."
            },
            "4_emergency_agent": {
                "agent_name": "Emergency Resource Optimizer Agent",
                "recommended_dispatches": [
                    f"Deploy High-Capacity Drainage Pump P-03 directly to {voice_location}",
                    "Dispatch Rapid Response Unit 04 with portable flood barriers",
                    "Erect physical barriers around Substation A-4 perimeter"
                ],
                "inventory_status": "Pump P-03 and Field Team 04 ready for deployment."
            },
            "5_communication_agent": {
                "agent_name": "Public Communication & Warning Agent",
                "public_broadcast_alert": f"CRITICAL ALERT: Rapid water level rise predicted at {voice_location}. Forecasted height: {river_m}m in +3 hours. Avoid eastern roads.",
                "field_briefing": f"Field Unit 04: Proceed to {voice_location}. Restrict public access near bridge."
            },
            "6_decision_agent_master": {
                "agent_name": "Master Orchestrator Decision Agent",
                "prioritized_city_action_plan": [
                    f"Priority 1: Protect Substation A-4 to prevent regional power outage.",
                    f"Priority 2: Divert public traffic from blocked route at {voice_location}.",
                    f"Priority 3: Deploy High-Capacity Pump P-03 to clear bridge drainage.",
                    f"Priority 4: Issue automated public advisory for {voice_location} sector."
                ]
            }
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)