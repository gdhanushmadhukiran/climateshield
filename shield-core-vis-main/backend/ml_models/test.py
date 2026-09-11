import pickle
import numpy as np
import torch
import torch.nn as nn

# 1. Define the exact PyTorch architecture used during training
class CorrelatedLSTM(nn.Module):
    def __init__(self):
        super().__init__()
        self.lstm = nn.LSTM(4, 32, batch_first=True)
        self.fc = nn.Linear(32, 1)
        
    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])


# =====================================================================
# 2. Test Model 2 (LSTM River Level Forecaster)
# =====================================================================
print("--- [2/4] Testing High-Precision LSTM Forecaster ---")
with open("lstm_forecaster.pkl", "rb") as f:
    data = pickle.load(f)
    lstm_model = data["model"]
    scaler_X = data["scaler_X"]
    scaler_y = data["scaler_y"]

lstm_model.eval()

# Sample sequence showing rising trends
raw_seq = np.array([
    [10.0, 50.0, 1.2, 30.0],
    [25.0, 70.0, 1.8, 28.0],
    [50.0, 95.0, 2.5, 26.0]
])

scaled_seq = scaler_X.transform(raw_seq)
tensor_seq = torch.tensor(np.array([scaled_seq]), dtype=torch.float32)

with torch.no_grad():
    predicted_scaled = lstm_model(tensor_seq).numpy()

predicted_river_level = scaler_y.inverse_transform(predicted_scaled)[0][0]
print(f"Predicted River Level (+3 Hours): {predicted_river_level:.2f} meters\n")


# =====================================================================
# 3. Test Model 4 (CV Flood Depth Estimator)
# =====================================================================
print("--- [4/4] Testing High-Precision CV Depth Estimator ---")
with open("cv_depth_model.pkl", "rb") as f:
    data_cv = pickle.load(f)
    depth_model = data_cv["model"]
    scaler_cv = data_cv["scaler"]

sample_conf = np.array([[0.95]])
scaled_conf = scaler_cv.transform(sample_conf)

predicted_depth = depth_model.predict(scaled_conf)[0]
print(f"Input Confidence Score: 0.95")
print(f"Estimated Flood Depth: {predicted_depth:.2f} cm")