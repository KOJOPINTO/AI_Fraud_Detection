import pandas as pd

transactions = pd.DataFrame({
    "transaction_id": [1, 2, 3, 4],
    "amount": [100, 250, 5000, 75],
    "payment_type": ["Card", "Bank Transfer", "Bank Transfer", "Card"]
})

print("AI Fraud Detection Project")
print("-" * 35)
print(transactions)

print("\nTotal transactions:", len(transactions))
print("Total transaction value:", transactions["amount"].sum())