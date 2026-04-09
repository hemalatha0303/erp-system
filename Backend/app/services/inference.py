import os

import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "../ml_models")

MODEL = None
SCALER = None
FEATURES = None
MODEL_LOAD_ATTEMPTED = False
MODEL_LOAD_ERROR = None


def _load_model_artifacts():
    global MODEL, SCALER, FEATURES, MODEL_LOAD_ATTEMPTED, MODEL_LOAD_ERROR

    if MODEL_LOAD_ATTEMPTED:
        return

    MODEL_LOAD_ATTEMPTED = True

    try:
        MODEL = joblib.load(os.path.join(MODEL_DIR, "academic_risk_model.pkl"))
        SCALER = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
        FEATURES = joblib.load(os.path.join(MODEL_DIR, "model_features.pkl"))
    except Exception as exc:
        MODEL_LOAD_ERROR = str(exc)
        print(f"Error loading ML models: {exc}")


def _basic_risk_explanation(student_dict):
    reasons = []

    attendance = float(student_dict.get("attendance_pct_100", 0) or 0)
    prev_sgpa = float(student_dict.get("prev_year_sgpa_10", 0) or 0)
    backlogs = int(student_dict.get("backlogs", 0) or 0)
    mid1 = float(student_dict.get("mid1_exam_30", 0) or 0)
    mid2 = float(student_dict.get("mid2_exam_30", 0) or 0)
    avg_mid = (mid1 + mid2) / 2 if mid1 or mid2 else 0

    if attendance < 75:
        reasons.append("attendance is below 75%")
    if prev_sgpa and prev_sgpa < 6:
        reasons.append("previous SGPA is low")
    if backlogs > 0:
        reasons.append(f"{backlogs} backlog(s) are present")
    if avg_mid and avg_mid < 15:
        reasons.append("mid exam scores are low")

    if reasons:
        return f"Main risk factors: {', '.join(reasons)}."
    return "Academic indicators are within a typical range."


def _predict_probability(student_dict):
    _load_model_artifacts()

    if not MODEL or not SCALER or not FEATURES:
        return None

    data = {feat: student_dict.get(feat, 0) for feat in FEATURES}
    df = pd.DataFrame([data])[FEATURES]
    scaled = SCALER.transform(df)
    return float(MODEL.predict_proba(scaled)[0][1] * 100)


def predict_student_risk(student_dict):
    """
    Input: student_dict (keys: mid1_exam_30, mid2_exam_30, attendance_pct_100, prev_year_sgpa_10, backlogs)
    Output: formatted string insight
    """
    prob = _predict_probability(student_dict)
    explanation = _basic_risk_explanation(student_dict)

    if prob is None:
        if MODEL_LOAD_ERROR:
            return "AI Risk Model is currently unavailable."
        return f"Risk assessment unavailable.\n{explanation}"

    if prob < 30:
        status = "Low Risk"
    elif prob < 70:
        status = "Moderate Risk"
    else:
        status = "High Risk"

    return f"{status} (Failure Probability: {prob:.1f}%)\n{explanation}"


def predict_student_risk_structured(student_dict):
    """
    Same inputs as predict_student_risk; returns a dict for JSON APIs.
    Keys: risk_level (LOW|MEDIUM|HIGH), risk_probability (0-100 float), explanation (str)
    """
    prob = _predict_probability(student_dict)
    explanation = _basic_risk_explanation(student_dict)

    if prob is None:
        return {
            "risk_level": "LOW",
            "risk_probability": 0.0,
            "explanation": explanation if not MODEL_LOAD_ERROR else "AI risk model is unavailable. Live academic data is still available.",
        }

    if prob < 30:
        risk_level = "LOW"
    elif prob < 70:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "risk_level": risk_level,
        "risk_probability": round(prob, 1),
        "explanation": explanation,
    }
