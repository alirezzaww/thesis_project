

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from joblib import load

# Load data
df = pd.read_csv("data/creditcard.csv")
df.rename(columns={"Class": "is_fraudulent", "Amount": "amount"}, inplace=True)

# Simulate sender and receiver
df['sender'] = np.random.choice(["0xA", "0xB", "0xC", "0xD"], size=len(df))
df['receiver'] = np.random.choice(["0xE", "0xF", "0xG", "0xH"], size=len(df))
df['transaction_time'] = np.random.randint(0, 86400, df.shape[0])
df['num_transactions_past_week'] = np.random.randint(1, 20, df.shape[0])
df['sender_encoded'] = df['sender'].astype('category').cat.codes
df['receiver_encoded'] = df['receiver'].astype('category').cat.codes

X = df[['amount', 'transaction_time', 'num_transactions_past_week', 'sender_encoded', 'receiver_encoded']].values
y = df['is_fraudulent'].values

# Split into train-test
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# Load model
model = load("fraud_detection_model.pkl")
y_scores = model.predict_proba(X_test)[:, 1]

# Compute precision-recall curve
precision, recall, thresholds = precision_recall_curve(y_test, y_scores)

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(thresholds, precision[:-1], label="Precision")
plt.plot(thresholds, recall[:-1], label="Recall")
plt.xlabel("Threshold")
plt.ylabel("Score")
plt.title("Precision-Recall vs Threshold")
plt.legend()
plt.grid(True)
plt.savefig("threshold_plot.png")
print("Plot saved to threshold_plot.png")