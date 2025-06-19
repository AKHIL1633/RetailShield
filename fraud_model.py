import pandas as pd
from sklearn.ensemble import IsolationForest

# Load the generated dataset
df = pd.read_csv('data/generated_transactions.csv')

# Feature columns
feature_cols = [
    'amount', 'frequency', 'location_match',
    'payment_method', 'time_of_day', 'device_known', 'is_return'
]
X = df[feature_cols]

# Train Isolation Forest model
model = IsolationForest(contamination=0.15, random_state=42)
model.fit(X)

# --- Helper function for rules
def rule_based_reason(transaction):
    reasons = []
    if transaction['amount'] > 1000:
        reasons.append("Unusually high amount")
    if not transaction['device_known']:
        reasons.append("Unknown device")
    if not transaction['location_match']:
        reasons.append("Location mismatch")
    if transaction['frequency'] > 5:
        reasons.append("High transaction frequency")
    if transaction['is_return']:
        reasons.append("Return transaction")
    if transaction['time_of_day'] == 0:  # 0 = Night
        reasons.append("Transaction at night")
    return "; ".join(reasons) if reasons else "-"

# --- Fraud prediction function
def detect_fraud(transaction):
    features = [[
        transaction['amount'],
        transaction['frequency'],
        transaction['location_match'],
        transaction['payment_method'],
        transaction['time_of_day'],
        transaction['device_known'],
        transaction['is_return']
    ]]
    result = model.predict(features)[0]
    risk_level = "Fraud" if result == -1 else "Safe"
    reason = rule_based_reason(transaction) if risk_level == "Fraud" else "-"
    return {
        "risk_level": risk_level,
        "reason": reason
    }
