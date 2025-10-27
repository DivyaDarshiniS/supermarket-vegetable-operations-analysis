import pandas as pd

# Step 1: Group by Item and Calculate Avg Loss Rate
# Load your master dataset
master = pd.read_csv("master_dataset.csv", parse_dates=["date"])
# Summarize at item level
loss_items = master.groupby(["item_code","item_name","category_name"]).agg(
    avg_loss_rate=("loss_rate_pct","mean"),
    total_revenue=("revenue_rmb","sum"),
    total_adjusted_profit=("adjusted_profit_rmb","sum"),
    total_quantity=("quantity_kg","sum")
).reset_index()

# Step 2: Filter Items with >20% Spoilage
high_spoilage_items = loss_items[loss_items["avg_loss_rate"] > 20]

print("Items with >20% spoilage:\n", high_spoilage_items[[
    "item_code","item_name","category_name","avg_loss_rate","total_revenue","total_adjusted_profit"
]])

# Step 3: Save to CSV 
# high_spoilage_items.to_csv("high_spoilage_items.csv", index=False)
# print("✅ Saved list of high spoilage items to high_spoilage_items.csv")

# Filter items with high spoilage (>20%)
high_spoilage = loss_items[loss_items["avg_loss_rate"] > 20].copy()

# Step 2: Split into Profitable vs Unprofitable

# Profitable = adjusted profit > 0
profitable_spoilage = high_spoilage[high_spoilage["total_adjusted_profit"] > 0]

# Unprofitable = adjusted profit <= 0
unprofitable_spoilage = high_spoilage[high_spoilage["total_adjusted_profit"] <= 0]

print("High Spoilage but Still Profitable Items:\n",
      profitable_spoilage[["item_name","category_name","avg_loss_rate","total_revenue","total_adjusted_profit"]])

print("\nHigh Spoilage and Unprofitable Items:\n",
      unprofitable_spoilage[["item_name","category_name","avg_loss_rate","total_revenue","total_adjusted_profit"]])

# profitable_spoilage.to_csv("profitable_high_spoilage_items.csv", index=False)
# unprofitable_spoilage.to_csv("unprofitable_high_spoilage_items.csv", index=False)

# print("✅ Saved: profitable_high_spoilage_items.csv and unprofitable_high_spoilage_items.csv")
