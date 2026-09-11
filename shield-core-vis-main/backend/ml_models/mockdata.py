import numpy as np
import os

mongo_uri = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017/")
client = pymongo.MongoClient(mongo_uri)
db = client["climateshield_db"]

np.random.seed(42)
n_samples = 1000

# 1. Update Time-Series Data with Strong Trend Correlation
time_series_records = []
for i in range(n_samples):
    rain = round(float(np.random.uniform(0.0, 80.0)), 1)
    soil = round(float(np.random.uniform(40.0, 99.0)), 1)
    curr_level = round(float(np.random.uniform(0.5, 3.5)), 2)
    temp = round(float(np.random.uniform(24.0, 42.0)), 1)
    
    # Target directly correlates with rainfall + current level rise
    future_level = round(float(curr_level + (rain * 0.025) + (soil * 0.005)), 2)
    
    time_series_records.append({
        "timestamp": f"2026-09-10T{i % 24:02d}:00:00Z",
        "sensor_id": f"S-HYD-{(i % 10) + 1:02d}",
        "rainfall_mm": rain,
        "soil_moisture_pct": soil,
        "river_level_m": curr_level,
        "temperature_c": temp,
        "target_river_level_plus_3h": future_level
    })

db["time_series_data"].drop()
db["time_series_data"].insert_many(time_series_records)
print(f"✅ Re-seeded {len(time_series_records)} realistic records in 'time_series_data'")

# 2. Update Vision Metadata with Strong Linear/Quadratic Depth Scaling
cv_records = []
for i in range(n_samples):
    waterlogged = int(np.random.choice([0, 1], p=[0.7, 0.3]))
    conf = round(float(np.random.uniform(0.50, 0.99)), 2)
    
    # Depth directly scales with detection confidence score
    depth = round(float((conf ** 2) * 55.0 + np.random.uniform(-2, 2)), 1) if waterlogged else 0.0
    
    cv_records.append({
        "image_id": f"IMG_{1000+i}.jpg",
        "timestamp": f"2026-09-10T{i % 24:02d}:00:00Z",
        "location_id": f"CAM-LOC-{(i % 15) + 1:02d}",
        "waterlogging_detected": waterlogged,
        "flood_depth_estimated_cm": max(0.0, depth),
        "confidence_score": conf,
        "label": "waterlogged" if waterlogged else "normal"
    })

db["vision_metadata"].drop()
db["vision_metadata"].insert_many(cv_records)
print(f"✅ Re-seeded {len(cv_records)} realistic records in 'vision_metadata'")