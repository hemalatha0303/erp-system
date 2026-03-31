"""
Train and Save AEWS ML Model
This script trains an XGBoost model on student data and saves it for inference
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import os

print("=" * 70)
print("AEWS ML MODEL TRAINING")
print("=" * 70)

# ====================================
# STEP 1: Prepare Training Data
# ====================================
print("\n[STEP 1] Preparing training data...")

# Create sample student data (replace with real data from database)
np.random.seed(42)
n_samples = 500

data = {
    "mid1_exam_30": np.random.uniform(0, 30, n_samples),
    "mid2_exam_30": np.random.uniform(0, 30, n_samples),
    "attendance_pct_100": np.random.uniform(20, 100, n_samples),
    "prev_year_sgpa_10": np.random.uniform(3, 10, n_samples),
    "backlogs": np.random.randint(0, 5, n_samples),
}

df = pd.DataFrame(data)

# Create target: HIGH RISK
df["high_risk"] = (
    (df["attendance_pct_100"] < 65).astype(int) * 0.35 +
    (df["backlogs"] >= 2).astype(int) * 0.30 +
    (df["prev_year_sgpa_10"] < 6.5).astype(int) * 0.20 +
    (((df["mid1_exam_30"] + df["mid2_exam_30"]) / 2) < 15).astype(int) * 0.15
) >= 0.5

print(f"✅ Created {n_samples} sample records")
print(f"   Risk distribution: {df['high_risk'].value_counts().to_dict()}")

# ====================================
# STEP 2: Prepare Features & Target
# ====================================
print("\n[STEP 2] Preparing features...")

FEATURES = [
    "mid1_exam_30",
    "mid2_exam_30",
    "attendance_pct_100",
    "prev_year_sgpa_10",
    "backlogs"
]

X = df[FEATURES]
y = df["high_risk"].astype(int)

print(f"✅ Features: {FEATURES}")
print(f"✅ Target classes: {y.unique()}")

# ====================================
# STEP 3: Split Data
# ====================================
print("\n[STEP 3] Splitting train/test data...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    stratify=y,
    random_state=42
)

print(f"✅ Train set: {len(X_train)} samples")
print(f"✅ Test set: {len(X_test)} samples")

# ====================================
# STEP 4: Scale Features
# ====================================
print("\n[STEP 4] Scaling features...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("✅ Features scaled using StandardScaler")

# ====================================
# STEP 5: Train XGBoost Model
# ====================================
print("\n[STEP 5] Training XGBoost classifier...")

model = XGBClassifier(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbosity=0
)

model.fit(X_train_scaled, y_train)
print("✅ Model trained successfully!")

# ====================================
# STEP 6: Evaluate Model
# ====================================
print("\n[STEP 6] Evaluating model performance...")

train_pred = model.predict(X_train_scaled)
test_pred = model.predict(X_test_scaled)
test_pred_proba = model.predict_proba(X_test_scaled)

train_acc = (train_pred == y_train).mean()
test_acc = (test_pred == y_test).mean()
roc_score = roc_auc_score(y_test, test_pred_proba[:, 1])

print(f"✅ Training Accuracy: {train_acc:.2%}")
print(f"✅ Test Accuracy: {test_acc:.2%}")
print(f"✅ ROC-AUC Score: {roc_score:.2%}")

print("\nClassification Report:")
print(classification_report(y_test, test_pred, 
                          target_names=["Low Risk", "High Risk"]))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, test_pred))

# ====================================
# STEP 7: Save Model Artifacts
# ====================================
print("\n[STEP 7] Saving model artifacts...")

# Create ml_models directory if it doesn't exist
ml_dir = "app/ml_models"
os.makedirs(ml_dir, exist_ok=True)

# Save model
model_path = f"{ml_dir}/academic_risk_model.pkl"
joblib.dump(model, model_path)
print(f"✅ Model saved: {model_path}")

# Save scaler
scaler_path = f"{ml_dir}/scaler.pkl"
joblib.dump(scaler, scaler_path)
print(f"✅ Scaler saved: {scaler_path}")

# Save features list
features_path = f"{ml_dir}/model_features.pkl"
joblib.dump(FEATURES, features_path)
print(f"✅ Features saved: {features_path}")

print("\n" + "=" * 70)
print("✅ MODEL TRAINING COMPLETE!")
print("=" * 70)
print("\nNext steps:")
print("1. Update aews_service.py to use these ML models")
print("2. Restart the backend server")
print("3. Test the API endpoints")
print("\nModel files location:")
print(f"  - {model_path}")
print(f"  - {scaler_path}")
print(f"  - {features_path}")
