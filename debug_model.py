import joblib
import numpy as np
import json

# Load model and threshold
model = joblib.load("fraud_detection_model.pkl")
with open("fraud_threshold.json") as f:
    threshold = json.load(f)['threshold']

print(f"Threshold = {threshold}")

# Manually test a high-risk input
features = np.array([[
    10,                          # amount
    np.log1p(10),                # log amount
    5,                           # transaction_time
    0,                           # hour of day
    40,                          # num_transactions_past_week
    10 / (5 + 1),                # transaction rate
    3,                           # sender_encoded
    1,                           # receiver_encoded
    31,                          # sender_receiver_encoded
    1.0,                         # sender_receiver_freq
    100.0,                       # sender_avg_amount
    0.4                          # trust_score_real
]])
prob = model.predict_proba(features)[0][1]
print(f"Predicted fraud score: {prob:.4f}")