import asyncio
import datetime
import random
import os
import pymongo

# 1. Connect to MongoDB instance
mongo_uri = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017/")
client = pymongo.MongoClient(mongo_uri)
db = client["climate_realtime_db"]

print("🚀 Starting ClimateShield Real-Time Data Ingestion Streamer (1 sec interval)...")
print("Press Ctrl+C in your terminal to stop streaming.\n")


def assign_risk(rain, elev, drain, temp, hum):
    """Rule engine for dynamic asset risk levels."""
    if rain > 60 and elev < 20 and drain < 0.4:
        return 3  # Critical
    elif temp > 42 and hum > 70:
        return 2  # High
    elif rain > 30 or temp > 38:
        return 1  # Medium
    return 0      # Low


async def stream_data_loop():
    counter = 1
    
    # State tracking to simulate realistic continuous river level rise/fall
    current_river_level = 1.2
    
    while True:
        timestamp_now = datetime.datetime.utcnow().isoformat() + "Z"

        # -------------------------------------------------------------
        # Collection 1: Real-Time Time-Series Stream (Model 2: LSTM)
        # -------------------------------------------------------------
        rain_val = round(random.uniform(0.0, 75.0), 1)
        soil_val = round(random.uniform(50.0, 98.0), 1)
        temp_val = round(random.uniform(25.0, 42.0), 1)
        
        # Simulate realistic continuous water accumulation physics
        current_river_level = round(max(0.5, current_river_level + (rain_val * 0.005) - 0.05), 2)
        future_river_level = round(current_river_level + (rain_val * 0.02) + (soil_val * 0.003), 2)

        ts_doc = {
            "timestamp": timestamp_now,
            "sensor_id": f"S-HYD-{(counter % 10) + 1:02d}",
            "rainfall_mm": rain_val,
            "soil_moisture_pct": soil_val,
            "river_level_m": current_river_level,
            "temperature_c": temp_val,
            "target_river_level_plus_3h": future_river_level
        }
        db["time_series_data"].insert_one(ts_doc)

        # -------------------------------------------------------------
        # Collection 2: Real-Time Asset Risk Stream (Model 1: XGBoost)
        # -------------------------------------------------------------
        elev_val = round(random.uniform(5.0, 100.0), 1)
        drain_val = round(random.uniform(0.1, 1.0), 2)
        hum_val = round(random.uniform(30.0, 95.0), 1)
        
        asset_doc = {
            "timestamp": timestamp_now,
            "asset_id": f"AST-{(counter % 100) + 1:04d}",
            "elevation_m": elev_val,
            "drainage_capacity": drain_val,
            "rainfall_mm_h": rain_val,
            "temperature_c": temp_val,
            "humidity_pct": hum_val,
            "risk_level": assign_risk(rain_val, elev_val, drain_val, temp_val, hum_val)
        }
        db["tabular_risk_data"].insert_one(asset_doc)

        # -------------------------------------------------------------
        # Collection 3: Real-Time Vision Streams (Model 4: CV Estimator)
        # -------------------------------------------------------------
        waterlogged_flag = random.choices([0, 1], weights=[0.7, 0.3])[0]
        conf_val = round(random.uniform(0.50, 0.99), 2)
        depth_val = round((conf_val ** 2) * 55.0 + random.uniform(-1, 1), 1) if waterlogged_flag else 0.0

        cv_doc = {
            "timestamp": timestamp_now,
            "image_id": f"IMG_{1000 + counter}.jpg",
            "location_id": f"CAM-LOC-{(counter % 15) + 1:02d}",
            "waterlogging_detected": waterlogged_flag,
            "flood_depth_estimated_cm": max(0.0, depth_val),
            "confidence_score": conf_val,
            "label": "waterlogged" if waterlogged_flag else "normal"
        }
        db["vision_metadata"].insert_one(cv_doc)

        # -------------------------------------------------------------
        # Collection 4: Real-Time Hardware Telemetry (Model 3: Faults)
        # -------------------------------------------------------------
        is_faulty_flag = random.choices([1, -1], weights=[0.88, 0.12])[0]
        
        sensor_doc = {
            "timestamp": timestamp_now,
            "sensor_id": f"S-HYD-{(counter % 20) + 1:02d}",
            "battery_voltage": round(1.2 if is_faulty_flag == -1 else random.uniform(3.3, 4.2), 1),
            "signal_dbm": int(-115 if is_faulty_flag == -1 else random.randint(-85, -50)),
            "temp_reading_c": round(85.0 if is_faulty_flag == -1 else random.uniform(20.0, 42.0), 1),
            "rate_of_change_temp": round(50.0 if is_faulty_flag == -1 else random.uniform(0.1, 2.0), 1),
            "reading_stuck_count": int(random.randint(20, 100) if is_faulty_flag == -1 else 0),
            "is_anomaly": is_faulty_flag
        }
        db["sensor_telemetry_faults"].insert_one(sensor_doc)

        # Console Log Update
        print(f"⏱️ [{timestamp_now}] Ingested 1 sample into all 4 MongoDB collections (Cycle #{counter})")

        counter += 1
        # Wait 1 second before generating next telemetry pulse
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(stream_data_loop())
    except KeyboardInterrupt:
        print("\n🛑 Stopped real-time ingestion generator.")