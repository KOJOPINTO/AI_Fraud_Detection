
from src.database import get_connection


def test_transaction_insert_and_read():
    transaction_id = "TXN-DB-TEST-001"

    with get_connection() as conn:
        with conn.cursor() as cur:
            # Save a test transaction
            cur.execute(
                """
                INSERT INTO transactions (
                    transaction_id,
                    amount,
                    payment_method,
                    fraud_probability,
                    prediction,
                    risk_level
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (transaction_id) DO NOTHING
                RETURNING transaction_id
                """,
                (
                    transaction_id,
                    2500.00,
                    "ACH",
                    0.85,
                    1,
                    "High",
                ),
            )

            inserted = cur.fetchone()

            # Read the transaction back
            cur.execute(
                """
                SELECT transaction_id, amount, payment_method,
                       fraud_probability, prediction, risk_level
                FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,),
            )

            result = cur.fetchone()

    print("Inserted a new row:", inserted is not None)
    print("Transaction retrieved:", result)


if __name__ == "__main__":
    test_transaction_insert_and_read()
