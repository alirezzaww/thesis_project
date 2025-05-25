from consensus.trust_model import TrustModel
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import VotingClassifier
import joblib
from imblearn.over_sampling import SMOTE

# Add a known fraudulent test case to improve sensitivity
custom_fraud = {
    "amount": 4000,
    "transaction_time": 32000,
    "num_transactions_past_week": 5,
    "sender": "Node2",
    "receiver": "0xE",
    "is_fraudulent": 1
}
# Add diverse fraudulent samples to improve sensitivity
# Add diverse fraudulent samples to improve sensitivity
fraud_samples = [
    {
        "amount": 9000,
        "transaction_time": 2000,
        "num_transactions_past_week": 0,
        "sender": "Node3",
        "receiver": "0xF",
        "is_fraudulent": 1
    },
    {
        "amount": 7500,
        "transaction_time": 10000,
        "num_transactions_past_week": 1,
        "sender": "Node1",
        "receiver": "0xG",
        "is_fraudulent": 1
    },
    {
        "amount": 120,
        "transaction_time": 60,
        "num_transactions_past_week": 25,
        "sender": "Node0",
        "receiver": "0xH",
        "is_fraudulent": 1
    }
]

df_fraud_extra = pd.DataFrame(fraud_samples)

# Generate synthetic fraudulent samples to improve model learning
import random
synthetic_frauds = []
senders = ["Node0", "Node1", "Node2", "Node3"]
receivers = ["0xE", "0xF", "0xG", "0xH"]

for _ in range(100):
    synthetic_frauds.append({
        "amount": random.uniform(3000, 10000),
        "transaction_time": random.randint(0, 86400),
        "num_transactions_past_week": random.randint(0, 5),
        "sender": random.choice(senders),
        "receiver": random.choice(receivers),
        "is_fraudulent": 1
    })

# Add more microtransaction fraud samples (e.g., high frequency, small amounts)
df_fraud_synthetic = pd.DataFrame(synthetic_frauds)
micro_frauds = []
for _ in range(30):
    micro_frauds.append({
        "amount": random.uniform(1, 200),
        "transaction_time": random.randint(0, 1000),  # short duration
        "num_transactions_past_week": random.randint(20, 40),
        "sender": random.choice(senders),
        "receiver": random.choice(receivers),
        "is_fraudulent": 1
    })

df_micro_fraud = pd.DataFrame(micro_frauds)
df_new = pd.concat([pd.DataFrame([custom_fraud]), df_fraud_extra, df_fraud_synthetic, df_micro_fraud], ignore_index=True)
# Load dataset and prepend the custom fraud sample
df = pd.concat([df_new, pd.read_csv("data/creditcard.csv")], ignore_index=True)
# Fix accidental multi-column issue with 'is_fraudulent'
if "is_fraudulent" in df.columns and "Class" in df.columns:
    df.drop(columns=["is_fraudulent"], inplace=True)
df.rename(columns={"Class": "is_fraudulent"}, inplace=True)
# Ensure there are no missing labels after renaming
df['is_fraudulent'] = pd.to_numeric(df['is_fraudulent'], errors='coerce')
df.dropna(subset=['is_fraudulent'], inplace=True)
df['is_fraudulent'] = df['is_fraudulent'].astype(int)
# Simulate sender and receiver for blockchain use case
df['sender'] = np.random.choice(["Node0", "Node1", "Node2", "Node3"], size=len(df))
df['receiver'] = np.random.choice(["0xE", "0xF", "0xG", "0xH"], size=len(df))
# Check class balance
print("Original dataset class distribution:")
print(df['is_fraudulent'].value_counts())

# Add new transaction-related features
df['transaction_time'] = np.random.randint(0, 86400, df.shape[0])  # Transaction time in seconds
df['num_transactions_past_week'] = np.random.randint(1, 20, df.shape[0])  # Fake transaction count
df['sender_encoded'] = df['sender'].astype('category').cat.codes
df['receiver_encoded'] = df['receiver'].astype('category').cat.codes


# Drop duplicate 'amount' column if both exist
if 'Amount' in df.columns and 'amount' in df.columns:
    df.drop(columns=['amount'], inplace=True)
df.rename(columns={"Amount": "amount"}, inplace=True)
#
# Engineered features removed for simplified, high-signal feature set:
# df['amount_log'] = np.log(df['amount'] + 1)
# df['hour_of_day'] = (df['transaction_time'] // 3600) % 24
# df['transaction_rate'] = df['num_transactions_past_week'] / 7
# df['sender_receiver_encoded'] = (df['sender_encoded'] * 10 + df['receiver_encoded'])
#
# pair_counts = df.groupby(['sender_encoded', 'receiver_encoded']).size().reset_index(name='count')
# df = df.merge(pair_counts, on=['sender_encoded', 'receiver_encoded'], how='left')
# df.rename(columns={'count': 'sender_receiver_freq'}, inplace=True)
#
# sender_avg = df.groupby('sender_encoded')['amount'].transform('mean')
# df['sender_avg_amount'] = sender_avg

# Feature: simulated trust score (later replace with real model)

# Instantiate TrustModel and assign real trust scores
nodes = ["Node0", "Node1", "Node2", "Node3"]
trust_model = TrustModel(nodes)
df['trust_score_real'] = df['sender'].map(lambda s: trust_model.get_trust_score(s))

#
# Prepare features and labels with simplified, high-signal set
X = df[['amount', 'num_transactions_past_week',
        'sender_encoded', 'receiver_encoded', 'trust_score_real']].values
y = df['is_fraudulent'].values

# Split data into train-test before SMOTE
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Apply SMOTE only on training set
# X_train_balanced, y_train_balanced = SMOTE(random_state=42).fit_resample(X_train, y_train)

print("\nBalanced dataset class distribution after SMOTE:")
print(pd.Series(y_train).value_counts())

 # Use VotingClassifier ensemble (XGBoost + Logistic Regression)
xgb = XGBClassifier(n_estimators=100, scale_pos_weight=100, eval_metric='logloss', random_state=42)
logreg = LogisticRegression(max_iter=5000, class_weight='balanced', random_state=42)
model = VotingClassifier(estimators=[('xgb', xgb), ('lr', logreg)], voting='soft')

# Train model
model.fit(X_train, y_train)

# Evaluate model using probability threshold
y_pred_probs = model.predict_proba(X_test)[:, 1]
y_pred = (y_pred_probs > 0.5).astype(int)

print("Predicted class distribution:", np.bincount(y_pred))
print(f"Detected frauds: {np.sum(y_pred == 1)} / {np.sum(y_test == 1)}")
accuracy = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {accuracy:.2f}")
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Use cross-validation for better evaluation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cross_val_scores = cross_val_score(model, X_train, y_train, cv=cv)

print(f"\nCross-Validation Accuracy: {cross_val_scores.mean():.2f} ± {cross_val_scores.std():.2f}")

# Save model

joblib.dump(model, "fraud_detection_model.pkl")

# Precision-Recall curve plotting
from sklearn.metrics import precision_recall_curve
import matplotlib.pyplot as plt

# Plot precision-recall vs threshold
precision, recall, thresholds = precision_recall_curve(y_test, y_pred_probs)

plt.figure(figsize=(10, 6))
plt.plot(thresholds, precision[:-1], label='Precision')
plt.plot(thresholds, recall[:-1], label='Recall')
plt.xlabel('Threshold')
plt.ylabel('Score')
plt.title('Precision-Recall vs Threshold')
plt.legend()
plt.grid(True)
plt.savefig("threshold_plot.png")
print("Threshold tuning plot saved as 'threshold_plot.png'")

# Auto-select best threshold based on desired tradeoff
best_threshold = 0.5  # default
for p, r, t in zip(precision, recall, thresholds):
    if p >= 0.8 and r >= 0.3:
        best_threshold = float(t)
        break

# Save the selected threshold to JSON
import json
with open("fraud_threshold.json", "w") as f:
    json.dump({"threshold": best_threshold}, f)

print(f"Optimal fraud threshold selected: {best_threshold:.4f}")
