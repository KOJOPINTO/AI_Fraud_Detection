
from src.predict import predict_transaction

# Use the first transaction from your dataset.
# Replace these example values with the actual values from X_test.iloc[0].
transaction = {
    "transaction_hour": 10,
    "day_of_week": 2,
    "is_weekend": 0,
    "log_amount_received": 5.5,
    "log_amount_paid": 5.5,
    "currency_mismatch": 0,
    "Receiving Currency": "US Dollar",
    "Payment Currency": "US Dollar",
    "Payment Format": "ACH"
}

result = predict_transaction(transaction)

print(result)
