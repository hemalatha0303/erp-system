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

        # 4. SHAP Explanation (with error handling)
        increases_risk = []
        try:
            shap_values = EXPLAINER(scaled)
            
            # Handle different SHAP output formats
            if hasattr(shap_values, 'values'):
                shap_vals = shap_values.values
            else:
                shap_vals = shap_values
            
            # Extract values for positive class (class 1 = failure)
            if len(shap_vals.shape) == 3:  # (samples, features, classes)
                shap_contrib = shap_vals[0, :, 1]
            elif len(shap_vals.shape) == 2:  # (samples, features)
                shap_contrib = shap_vals[0, :]
            else:
                shap_contrib = []
            
            for i, feature in enumerate(FEATURES):
                if i < len(shap_contrib) and shap_contrib[i] > 0:
                    # Map technical feature names to readable text
                    feat_name = feature.replace("_30", "").replace("_100", "").replace("_10", "").replace("_", " ").title()
                    increases_risk.append(feat_name)
        except Exception as shap_err:
            print(f"SHAP Explanation Error: {shap_err}")
            # Continue with basic explanation if SHAP fails

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
        import traceback
        traceback.print_exc()
        return "Could not generate academic insight."


def predict_student_risk_structured(student_dict):
    """
    Same inputs as predict_student_risk; returns a dict for JSON APIs.
    Keys: risk_level (LOW|MEDIUM|HIGH), risk_probability (0-100 float), explanation (str)
    """
    if not MODEL:
        return {
            "risk_level": "LOW",
            "risk_probability": 0.0,
            "explanation": "AI risk model is unavailable. Factors shown are from live records only.",
        }
    try:
        data = {feat: student_dict.get(feat, 0) for feat in FEATURES}
        df = pd.DataFrame([data])[FEATURES]
        scaled = SCALER.transform(df)
        prob = float(MODEL.predict_proba(scaled)[0][1] * 100)

        increases_risk = []
        try:
            shap_values = EXPLAINER(scaled)
            if hasattr(shap_values, "values"):
                shap_vals = shap_values.values
            else:
                shap_vals = shap_values
            if len(shap_vals.shape) == 3:
                shap_contrib = shap_vals[0, :, 1]
            elif len(shap_vals.shape) == 2:
                shap_contrib = shap_vals[0, :]
            else:
                shap_contrib = []
            for i, feature in enumerate(FEATURES):
                if i < len(shap_contrib) and shap_contrib[i] > 0:
                    feat_name = (
                        feature.replace("_30", "")
                        .replace("_100", "")
                        .replace("_10", "")
                        .replace("_", " ")
                        .title()
                    )
                    increases_risk.append(feat_name)
        except Exception as shap_err:
            print(f"SHAP Explanation Error: {shap_err}")

        if prob < 30:
            risk_level = "LOW"
        elif prob < 70:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        if increases_risk:
            explanation = f"Main risk factors: {', '.join(increases_risk)}."
        else:
            explanation = "Academic indicators are within a typical range."

        return {
            "risk_level": risk_level,
            "risk_probability": round(prob, 1),
            "explanation": explanation,
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {
            "risk_level": "LOW",
            "risk_probability": 0.0,
            "explanation": "Could not run the risk model for this student.",
        }