import datetime
import pickle
import time
import numpy as np
import pandas as pd
import pymongo
import schedule
import torch
import torch.nn as nn

# Define exact PyTorch LSTM architecture matching your saved PKL file
class CorrelatedLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(4, 32, batch_first=True)
        self.fc = nn.Linear(32, 1)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


def process_hourly_batch_predictions():
    now = datetime.datetime.utcnow()
    one_hour_ago = now - datetime.timedelta(hours=1)
    
    timestamp_now_str = now.isoformat() + "Z"
    iso_one_hour_ago = one_hour_ago.isoformat() + "Z"

    print(f"\n=================================================================")
    print(f"⏰ [HOURLY BATCH RUNNER] Executing Pipeline for Window:")
    print(f"   • Start Time (ISO): {iso_one_hour_ago}")
    print(f"   • End Time   (ISO): {timestamp_now_str}")
    print(f"=================================================================")

    # 1. Connect to MongoDB Instance
    import os
    mongo_uri = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017/")
    client = pymongo.MongoClient(mongo_uri)
    
    # READ DATABASE: Source for real-time telemetry feeds
    read_db = client["climate_realtime_db"]
    
    # SEPARATE WRITE DATABASE: Dedicated exclusively for model predictions
    write_db = client["climateshield_predictions_db"]

    # 2. Load trained PKL models & scalers into memory
    print("📦 Loading PKL models from disk...")
    
    with open("asset_risk_model.pkl", "rb") as f:
        model_risk = pickle.load(f)

    with open("lstm_forecaster.pkl", "rb") as f:
        data_lstm = pickle.load(f)
        model_lstm = data_lstm["model"]
        scaler_X_lstm = data_lstm["scaler_X"]
        scaler_y_lstm = data_lstm["scaler_y"]
        model_lstm.eval()

    with open("sensor_anomaly_model.pkl", "rb") as f:
        model_sensor = pickle.load(f)

    with open("cv_depth_model.pkl", "rb") as f:
        data_cv = pickle.load(f)
        model_cv = data_cv["model"]
        scaler_cv = data_cv["scaler"]

    # Filter for past 1 hour of streaming telemetry
    time_filter = {"timestamp": {"$gte": iso_one_hour_ago, "$lte": timestamp_now_str}}

    # -------------------------------------------------------------
    # 1. Model 3: Sensor Fault Detection (Past 1 Hour Batch)
    # -------------------------------------------------------------
    sensor_docs = list(read_db["sensor_telemetry_faults"].find(time_filter, {"_id": 0}))
    if sensor_docs:
        df_sensors = pd.DataFrame(sensor_docs)
        X_sensor = df_sensors[["battery_voltage", "signal_dbm", "temp_reading_c", "rate_of_change_temp", "reading_stuck_count"]]
        sensor_preds = model_sensor.predict(X_sensor)
        faulty_count = int(sum(1 for flag in sensor_preds if flag == -1))
        total_sensors_audited = len(sensor_preds)
    else:
        faulty_count, total_sensors_audited = 0, 0

    # -------------------------------------------------------------
    # 2. Model 1: Asset Risk Classification (Past 1 Hour Batch)
    # -------------------------------------------------------------
    asset_docs = list(read_db["tabular_risk_data"].find(time_filter, {"_id": 0}))
    if asset_docs:
        df_assets = pd.DataFrame(asset_docs)
        X_risk = df_assets[["elevation_m", "drainage_capacity", "rainfall_mm_h", "temperature_c", "humidity_pct"]]
        risk_preds = model_risk.predict(X_risk).tolist()
        critical_count = int(sum(1 for r in risk_preds if r == 3))
        high_count = int(sum(1 for r in risk_preds if r == 2))
        total_assets_evaluated = len(risk_preds)
    else:
        critical_count, high_count, total_assets_evaluated = 0, 0, 0

    # -------------------------------------------------------------
    # 3. Model 2: PyTorch LSTM River Forecast (+3 Hours)
    # -------------------------------------------------------------
    ts_docs = list(read_db["time_series_data"].find(time_filter, {"_id": 0}))
    if len(ts_docs) >= 3:
        df_ts = pd.DataFrame(ts_docs)
        X_raw_ts = df_ts[["rainfall_mm", "soil_moisture_pct", "river_level_m", "temperature_c"]].values
        
        # Select latest 3-step sequence within the 1-hour window
        latest_seq = X_raw_ts[-3:]
        scaled_seq = scaler_X_lstm.transform(latest_seq)
        tensor_seq = torch.tensor(np.array([scaled_seq]), dtype=torch.float32)

        with torch.no_grad():
            pred_scaled = model_lstm(tensor_seq).numpy()
        
        predicted_river_m = round(float(scaler_y_lstm.inverse_transform(pred_scaled)[0][0]), 2)
    else:
        predicted_river_m = 0.0

    # -------------------------------------------------------------
    # 4. Model 4: CV Inundation Depth (Past 1 Hour Batch)
    # -------------------------------------------------------------
    cv_docs = list(read_db["vision_metadata"].find(
        {"$and": [time_filter, {"waterlogging_detected": 1}]}, {"_id": 0}
    ))
    if cv_docs:
        df_cv = pd.DataFrame(cv_docs)
        X_cv = df_cv[["confidence_score"]].values
        scaled_cv = scaler_cv.transform(X_cv)
        depth_preds = model_cv.predict(scaled_cv)
        avg_depth_cm = round(float(np.mean(depth_preds)), 2)
        max_depth_cm = round(float(np.max(depth_preds)), 2)
    else:
        avg_depth_cm, max_depth_cm = 0.0, 0.0

    # -------------------------------------------------------------
    # 5. Store Predictions Directly into SEPARATE Database
    # -------------------------------------------------------------
    prediction_record = {
        "execution_time": timestamp_now_str,
        "window_start": iso_one_hour_ago,
        "window_end": timestamp_now_str,
        "total_records_processed": {
            "sensors": total_sensors_audited,
            "assets": total_assets_evaluated,
            "time_series_ticks": len(ts_docs),
            "vision_events": len(cv_docs)
        },
        "model_outputs": {
            "faulty_sensors_detected": faulty_count,
            "critical_risk_assets": critical_count,
            "high_risk_assets": high_count,
            "forecasted_river_level_plus_3h_m": predicted_river_m,
            "avg_flood_depth_cm": avg_depth_cm,
            "max_flood_depth_cm": max_depth_cm
        },
        "status": "COMPLETED"
    }

    # Insert into SEPARATE database: climateshield_predictions_db -> model_predictions
    write_db["model_predictions"].insert_one(prediction_record)

    print("💾 PREDICTIONS STORED IN SEPARATE DATABASE ('climateshield_predictions_db'):")
    print(f"   • Database Name:                       climateshield_predictions_db")
    print(f"   • Collection Name:                     model_predictions")
    print(f"   • Total Input Records Evaluated (1hr): {total_sensors_audited + total_assets_evaluated + len(ts_docs) + len(cv_docs)}")
    print(f"   • Faulty Hardware Sensors Detected:    {faulty_count}")
    print(f"   • Critical Risk Assets Flagged:        {critical_count}")
    print(f"   • Forecasted River Height (+3 Hours):   {predicted_river_m} meters")
    print(f"   • Avg Estimated Inundation Depth:      {avg_depth_cm} cm")
    print("=================================================================\n")


# Schedule process to trigger every 1 hour automatically
schedule.every(1).hours.do(process_hourly_batch_predictions)

if __name__ == "__main__":
    print("🚀 ClimateShield Hourly Predictor Engine Started!")
    print("Executing immediate prediction run...")
    
    # Immediate initial execution
    process_hourly_batch_predictions()
    
    # Main scheduler loop
    while True:
        schedule.run_pending()
        time.sleep(30)