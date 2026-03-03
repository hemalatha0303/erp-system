import joblib
import pandas as pd
import shap
import numpy as np
import os

# Define paths relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../ml_models")

# Load Artifacts

try:
    MODEL = joblib.load(os.path.join(MODEL_DIR, "academic_risk_model.pkl"))
    SCALER = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
    FEATURES = joblib.load(os.path.join(MODEL_DIR, "model_features.pkl"))
    # SHAP background
    BACKGROUND = np.zeros((1, len(FEATURES)))
    EXPLAINER = shap.Explainer(MODEL.predict_proba, BACKGROUND)
except Exception as e:
    print(f"Error loading ML models: {e}")
    MODEL = None

def predict_student_risk(student_dict):
    """
    Input: student_dict (keys: mid1_exam_30, mid2_exam_30, attendance_pct_100, prev_year_sgpa_10, backlogs)
    Output: formatted string insight
    """
    if not MODEL:
        return "AI Risk Model is currently unavailable."

    try:
        # 1. Prepare input
        # Ensure all features exist, default to 0 if missing
        data = {feat: student_dict.get(feat, 0) for feat in FEATURES}
        df = pd.DataFrame([data])[FEATURES]
        
        # 2. Scale
        scaled = SCALER.transform(df)

        # 3. Predict
        prob = MODEL.predict_proba(scaled)[0][1] * 100

        # 4. SHAP Explanation
        shap_values = EXPLAINER(scaled)
        increases_risk = []
        
        for i, feature in enumerate(FEATURES):
            contribution = shap_values.values[0][i][1]
            if contribution > 0:
                # Map technical feature names to readable text
                feat_name = feature.replace("_30", "").replace("_100", "").replace("_10", "").replace("_", " ").title()
                increases_risk.append(feat_name)

        # 5. Construct Insight
        if prob < 30:
            status = "Low Risk 🟢"
        elif prob < 70:
            status = "Moderate Risk 🟡"
        else:
            status = "High Risk 🔴"

        if increases_risk:
            factors = ", ".join(increases_risk)
            explanation = f"Main risk factors: {factors}."
        else:
            explanation = "Your academic performance looks stable."

        return f"{status} (Failure Probability: {prob:.1f}%)\n{explanation}"

    except Exception as e:
        print(f"Prediction Error: {e}")
        return "Could not generate academic insight."