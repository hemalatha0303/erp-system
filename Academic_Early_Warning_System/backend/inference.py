import joblib
import pandas as pd
import shap
import numpy as np

# ======================================================
# LOAD ARTIFACTS (ONCE)
# ======================================================
MODEL = joblib.load("academic_risk_model.pkl")
SCALER = joblib.load("scaler.pkl")
FEATURES = joblib.load("model_features.pkl")

# SHAP background (safe minimal background)
BACKGROUND = np.zeros((1, len(FEATURES)))
EXPLAINER = shap.Explainer(MODEL.predict_proba, BACKGROUND)

# ======================================================
# INFERENCE + NATURAL LANGUAGE EXPLANATION
# ======================================================
def predict_student_risk(student_dict):
    """
    Input:
        student_dict: dict with keys matching FEATURES

    Output:
        dict with probability + explanation text
    """

    # -----------------------------
    # 1. Prepare input
    # -----------------------------
    df = pd.DataFrame([student_dict])[FEATURES]
    scaled = SCALER.transform(df)

    # -----------------------------
    # 2. Predict probability
    # -----------------------------
    prob = MODEL.predict_proba(scaled)[0][1] * 100

    # -----------------------------
    # 3. SHAP explanation
    # -----------------------------
    shap_values = EXPLAINER(scaled)

    increases_risk = []
    decreases_risk = []

    for i, feature in enumerate(FEATURES):
        contribution = shap_values.values[0][i][1]
        if contribution > 0:
            increases_risk.append(feature)
        elif contribution < 0:
            decreases_risk.append(feature)

    # -----------------------------
    # 4. Construct explanation text
    # -----------------------------
    if increases_risk:
        explanation = (
            f"{', '.join(increases_risk)} "
            f"{'increase' if len(increases_risk) > 1 else 'increases'} "
            "the risk of failing."
        )
    else:
        explanation = "No risk factors detected."

    # -----------------------------
    # 5. Final output (same style as before)
    # -----------------------------
    return {
        "probability": f"Predicted probability of failing: {prob:.2f}%",
        "explanation_text": explanation
    }
