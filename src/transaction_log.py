
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = PROJECT_ROOT / "data" / "transaction_history.csv"


def log_transaction(transaction, result, amount_received, amount_paid):
    """Save a transaction prediction to CSV."""

    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "transaction_id": f"TXN-{uuid4().hex[:12].upper()}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "amount_received": amount_received,
        "amount_paid": amount_paid,
        "receiving_currency": transaction["Receiving Currency"],
        "payment_currency": transaction["Payment Currency"],
        "payment_format": transaction["Payment Format"],
        "fraud_probability": result["fraud_probability"],
        "prediction": result["prediction"],
        "risk_level": result["risk_level"],
        "investigation_status": "New",
        "investigation_notes": "",
    }

    new_record = pd.DataFrame([record])
    if LOG_PATH.exists():
        existing_history = pd.read_csv(LOG_PATH)

        combined_history = pd.concat(
            [existing_history, new_record],
            ignore_index=True
        )

        combined_history.to_csv(LOG_PATH, index=False)
    else:
        new_record.to_csv(LOG_PATH, index=False)
    


def load_transaction_history():
    """Load previous predictions."""

    if LOG_PATH.exists():
        history = pd.read_csv(LOG_PATH)

        if "investigation_status" not in history.columns:
            history["investigation_status"] = "New"
        else:
            history["investigation_status"] = (
                history["investigation_status"].fillna("New")
            )

        if "investigation_notes" not in history.columns:
            history["investigation_notes"] = ""
        else:
            history["investigation_notes"] = (
                history["investigation_notes"].fillna("")
            )

        return history

    return pd.DataFrame()


def save_transaction_history(history):
    """Save the updated transaction history to CSV."""
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    history.to_csv(LOG_PATH, index=False)

