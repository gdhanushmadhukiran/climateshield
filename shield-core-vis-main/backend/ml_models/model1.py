import pickle
import numpy as np
import pandas as pd
import pymongo
import torch
import torch.nn as nn
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from torch.utils.data import DataLoader, TensorDataset

import os

mongo_uri = os.environ.get("MONGODB_URI", "mongodb://127.0.0.1:27017/")
client = pymongo.MongoClient(mongo_uri)
db = client["climateshield_db"]

np.random.seed(42)
torch.manual_seed(42)

# --- Retrain Model 2 ---
df_ts = pd.DataFrame(list(db["time_series_data"].find({}, {"_id": 0})))
X_raw = df_ts[["rainfall_mm", "soil_moisture_pct", "river_level_m", "temperature_c"]].values
y_raw = df_ts["target_river_level_plus_3h"].values.reshape(-1, 1)

scaler_X = StandardScaler()
scaler_y = StandardScaler()
X_scaled = scaler_X.fit_transform(X_raw)
y_scaled = scaler_y.fit_transform(y_raw)

seq_len = 3
X_seq, y_seq = [], []
for i in range(len(X_scaled) - seq_len):
    X_seq.append(X_scaled[i:i + seq_len])
    y_seq.append(y_scaled[i + seq_len])

X_tensor = torch.tensor(np.array(X_seq), dtype=torch.float32)
y_tensor = torch.tensor(np.array(y_seq), dtype=torch.float32)

dataset = TensorDataset(X_tensor, y_tensor)
dataloader = DataLoader(dataset, batch_size=16, shuffle=True)

class CorrelatedLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(4, 32, batch_first=True)
        self.fc = nn.Linear(32, 1)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

lstm_model = CorrelatedLSTM()
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(lstm_model.parameters(), lr=0.01)

lstm_model.train()
for epoch in range(60):
    for X_batch, y_batch in dataloader:
        optimizer.zero_grad()
        loss = criterion(lstm_model(X_batch), y_batch)
        loss.backward()
        optimizer.step()

with open("lstm_forecaster.pkl", "wb") as f:
    pickle.dump({"model": lstm_model, "scaler_X": scaler_X, "scaler_y": scaler_y}, f)

# --- Retrain Model 4 ---
df_cv = pd.DataFrame(list(db["vision_metadata"].find({}, {"_id": 0})))
df_water = df_cv[df_cv["waterlogging_detected"] == 1]

X_cv = df_water[["confidence_score"]].values
y_cv = df_water["flood_depth_estimated_cm"].values

scaler_cv = StandardScaler()
X_cv_scaled = scaler_cv.fit_transform(X_cv)

depth_model = Ridge(alpha=0.1)
depth_model.fit(X_cv_scaled, y_cv)

with open("cv_depth_model.pkl", "wb") as f:
    pickle.dump({"model": depth_model, "scaler": scaler_cv}, f)

print("🎉 Models retrained with high-sensitivity mock data!")