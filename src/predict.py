
from pathlib import Path
import joblib
import pandas as pd

# Locate the project root and saved model
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "random_forest_fraud_model.pkl"

# Load the trained pipeline
model = joblib.load(MODEL_PATH)


def predict_transaction(transaction):
    """
    Predict potential laundering for one transaction.

    transaction must contain the nine features used during training.
    """
    transaction_df = pd.DataFrame([transaction])

    probability = model.predict_proba(transaction_df)[0][1]

    # Use the threshold selected for our experiment
    prediction = int(probability >= 0.4)

    
    if probability >= 0.4:
        risk_level = "High"
    elif probability >= 0.2:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "prediction": prediction,
        "fraud_probability": float(probability),
        "risk_level": risk_level
    }
