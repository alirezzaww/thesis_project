import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Load dataset
df = pd.read_csv("data/transactions.csv")

# Check class balance
print("Original dataset class distribution:")
print(df['is_fraudulent'].value_counts())

# Balance dataset by undersampling majority class
fraud = df[df['is_fraudulent'] == 1]
non_fraud = df[df['is_fraudulent'] == 0].sample(len(fraud), random_state=42)
df_balanced = pd.concat([fraud, non_fraud])

print("\nBalanced dataset class distribution:")
print(df_balanced['is_fraudulent'].value_counts())

# Add new transaction-related features
df_balanced['transaction_time'] = np.random.randint(0, 86400, df_balanced.shape[0])  # Transaction time in seconds
df_balanced['num_transactions_past_week'] = np.random.randint(1, 20, df_balanced.shape[0])  # Fake transaction count
df_balanced['sender_encoded'] = df_balanced['sender'].astype('category').cat.codes
df_balanced['receiver_encoded'] = df_balanced['receiver'].astype('category').cat.codes

# Prepare features and labels
X = df_balanced[['amount', 'transaction_time', 'num_transactions_past_week', 'sender_encoded', 'receiver_encoded']].values
y = df_balanced['is_fraudulent'].values

# Split data into train-test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Use Logistic Regression to avoid overfitting
model = LogisticRegression(max_iter=500)

# Train model
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\nModel Accuracy: {accuracy:.2f}")
print("\nClassification Report:\n", classification_report(y_test, y_pred))

# Use cross-validation for better evaluation
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cross_val_scores = cross_val_score(model, X, y, cv=cv)

print(f"\nCross-Validation Accuracy: {cross_val_scores.mean():.2f} ± {cross_val_scores.std():.2f}")

# Save model
joblib.dump(model, "fraud_detection_model.pkl")
