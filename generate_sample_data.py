import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate date range for the last 90 days
end_date = datetime.now()
start_date = end_date - timedelta(days=90)
date_range = [start_date + timedelta(days=i) for i in range(91)]

# Define potential transactions
transactions_templates = [
    # (Description keyword/template, category_hint, amount_range)
    ("Walmart Supercenter", "Groceries", (30.0, 150.0)),
    ("Target Store", "Groceries", (15.0, 80.0)),
    ("Local Grocery Market", "Groceries", (10.0, 60.0)),
    ("Netflix.com Subscription", "Subscriptions", (15.49, 15.49)),
    ("Spotify Premium", "Subscriptions", (9.99, 9.99)),
    ("Hulu Streaming", "Subscriptions", (7.99, 14.99)),
    ("Shell Gas Station", "Transportation", (25.0, 65.0)),
    ("Uber Trip", "Transportation", (12.0, 45.0)),
    ("Gas & Go", "Transportation", (20.0, 50.0)),
    ("Starbucks Coffee", "Other", (4.50, 12.00)),
    ("Amazon.com Order", "Other", (10.0, 120.0)),
    ("Steam Games Store", "Other", (5.0, 60.0)),
    ("Home Depot", "Other", (15.0, 200.0)),
    ("McDonalds Fast Food", "Other", (8.0, 25.0)),
    ("Electric Utility Bill", "Other", (70.0, 150.0)),
]

data = []

# Generate about 80 transactions over 90 days
for _ in range(80):
    date = random.choice(date_range).strftime("%Y-%m-%d")
    template = random.choice(transactions_templates)
    desc, _, amt_range = template
    amount = round(random.uniform(amt_range[0], amt_range[1]), 2)
    
    # Randomly add transaction IDs or locations to descriptions to make it realistic
    if "Supercenter" in desc or "Store" in desc or "Gas" in desc or "Trip" in desc or "Order" in desc:
        desc = f"{desc} #{random.randint(1000, 9999)}"
        
    data.append({
        "Transaction Date": date,
        "Transaction Description": desc,
        "Amount": amount
    })

# Convert to DataFrame and sort by Date
df = pd.DataFrame(data)
df = df.sort_values(by="Transaction Date").reset_index(drop=True)

# Save to CSV
output_path = "sample_transactions.csv"
df.to_csv(output_path, index=False)
print(f"Generated {len(df)} sample transactions and saved to '{output_path}'.")
