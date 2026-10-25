
from datetime import datetime, timezone
from uuid import uuid4

import pandas as pd

from src.database import get_connection


HISTORY_COLUMNS = [
    "transaction_id",
    "timestamp",
    "amount_received",
    "amount_paid",
    "receiving_currency",
    "payment_currency",
    "payment_format",
    "fraud_probability",
    "prediction",
    "risk_level",
    "investigation_status",
    "investigation_notes",
]


def log_transaction(transaction, result, amount_received, amount_paid):
    """Save a transaction prediction to PostgreSQL."""

    record = {
        "transaction_id": f"TXN-{uuid4().hex[:12].upper()}",
        "timestamp": datetime.now(timezone.utc),
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

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO transactions (
                    transaction_id,
                    transaction_time,
                    amount,
                    amount_received,
                    amount_paid,
                    receiving_currency,
                    payment_currency,
                    payment_format,
                    fraud_probability,
                    prediction,
                    risk_level,
                    investigation_status,
                    investigation_notes
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    record["transaction_id"],
                    record["timestamp"],
                    amount_received,
                    amount_received,
                    amount_paid,
                    record["receiving_currency"],
                    record["payment_currency"],
                    record["payment_format"],
                    record["fraud_probability"],
                    record["prediction"],
                    record["risk_level"],
                    record["investigation_status"],
                    record["investigation_notes"],
                ),
            )


def load_transaction_history():
    """Load transaction history from PostgreSQL as a DataFrame."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    transaction_id,
                    transaction_time AS timestamp,
                    amount_received,
                    amount_paid,
                    receiving_currency,
                    payment_currency,
                    payment_format,
                    fraud_probability,
                    prediction,
                    risk_level,
                    investigation_status,
                    investigation_notes
                FROM transactions
                ORDER BY transaction_time DESC
                """
            )

            rows = cur.fetchall()

    if not rows:
        return pd.DataFrame(columns=HISTORY_COLUMNS)

    return pd.DataFrame(rows, columns=HISTORY_COLUMNS)


def save_transaction_history(history):
    """Save investigation changes to existing PostgreSQL records."""

    if history.empty:
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in history.iterrows():
                timestamp = row.get("timestamp")

                if pd.isna(timestamp):
                    timestamp = None
                else:
                    timestamp = pd.to_datetime(
                        timestamp, utc=True
                    ).to_pydatetime()

                def clean(value):
                    return None if pd.isna(value) else value

                amount_received = clean(row.get("amount_received"))

                cur.execute(
                    """
                    UPDATE transactions
                    SET
                        transaction_time = COALESCE(
                            %s, transaction_time
                        ),
                        amount = COALESCE(%s, amount),
                        amount_received = %s,
                        amount_paid = %s,
                        receiving_currency = %s,
                        payment_currency = %s,
                        payment_format = %s,
                        fraud_probability = %s,
                        prediction = %s,
                        risk_level = %s,
                        investigation_status = %s,
                        investigation_notes = %s
                    WHERE transaction_id = %s
                    """,
                    (
                        timestamp,
                        amount_received,
                        amount_received,
                        clean(row.get("amount_paid")),
                        clean(row.get("receiving_currency")),
                        clean(row.get("payment_currency")),
                        clean(row.get("payment_format")),
                        clean(row.get("fraud_probability")),
                        clean(row.get("prediction")),
                        clean(row.get("risk_level")),
                        clean(row.get("investigation_status")) or "New",
                        clean(row.get("investigation_notes")) or "",
                        row["transaction_id"],
                    ),
                )
