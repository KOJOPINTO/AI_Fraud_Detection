
import pandas as pd

from src.database import get_connection
from src.transaction_log import LOG_PATH


def migrate_history():
    if not LOG_PATH.exists():
        print(f"CSV file not found: {LOG_PATH}")
        return

    history = pd.read_csv(LOG_PATH)
    print(f"CSV records found: {len(history)}")

    if history.empty:
        print("The CSV is empty. Nothing to migrate.")
        return

    required_columns = [
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

    missing = [column for column in required_columns if column not in history.columns]

    if missing:
        print(f"Migration stopped. Missing CSV columns: {missing}")
        return

    # Keep missing optional values as SQL NULL rather than pandas NaN.
    history = history.where(pd.notna(history), None)

    inserted_count = 0
    skipped_count = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for _, row in history.iterrows():
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
                    ON CONFLICT (transaction_id) DO NOTHING
                    RETURNING transaction_id
                    """,
                    (
                        row["transaction_id"],
                        row["timestamp"],
                        row["amount_received"],
                        row["amount_received"],
                        row["amount_paid"],
                        row["receiving_currency"],
                        row["payment_currency"],
                        row["payment_format"],
                        row["fraud_probability"],
                        row["prediction"],
                        row["risk_level"],
                        row["investigation_status"],
                        row["investigation_notes"],
                    ),
                )

                if cur.fetchone():
                    inserted_count += 1
                else:
                    skipped_count += 1

    print(f"Migration complete. Inserted: {inserted_count}")
    print(f"Already existed and skipped: {skipped_count}")


if __name__ == "__main__":
    migrate_history()
