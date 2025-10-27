import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Step 1: Top 10 Items by Loss Rate

# Load your master dataset
master = pd.read_csv("master_dataset.csv", parse_dates=["date"])

# Item-level summary
loss_items = master.groupby(["item_code","item_name"]).agg(
    avg_loss_rate=("loss_rate_pct","mean"),
    total_quantity=("quantity_kg","sum"),
    total_revenue=("revenue_rmb","sum"),
    total_adjusted_profit=("adjusted_profit_rmb","sum")
).reset_index()

# Top 10 items with highest average loss rate
top_loss_items = loss_items.sort_values("avg_loss_rate", ascending=False).head(10)

# Plot
plt.figure(figsize=(10,5))
sns.barplot(data=top_loss_items, x="item_name", y="avg_loss_rate", palette="Reds_r")
plt.title("Top 10 Items with Highest Loss Rate (%)")
plt.xticks(rotation=75)
plt.ylabel("Average Loss Rate (%)")
# plt.show()

print(top_loss_items)

# Step 2: Category-Level Spoilage Impact
category_loss = master.groupby("category_name").agg(
    avg_loss_rate=("loss_rate_pct","mean"),
    total_revenue=("revenue_rmb","sum"),
    gross_profit=("gross_profit_rmb","sum"),
    adjusted_profit=("adjusted_profit_rmb","sum")
).reset_index()

# Calculate % profit reduction due to spoilage
category_loss["profit_reduction_pct"] = (
    (category_loss["gross_profit"] - category_loss["adjusted_profit"]) / category_loss["gross_profit"]
) * 100

# Plot
plt.figure(figsize=(8,5))
sns.barplot(data=category_loss, x="category_name", y="profit_reduction_pct", palette="Oranges_r")
plt.title("Profit Reduction (%) due to Spoilage by Category")
plt.xticks(rotation=45)
plt.ylabel("Profit Reduction (%)")
# plt.show()

print(category_loss)

# Step 3: Spoilage vs Profitability (Scatter Plot)
plt.figure(figsize=(8,5))
sns.scatterplot(data=loss_items, x="avg_loss_rate", y="total_adjusted_profit", hue="total_revenue", size="total_quantity")
plt.title("Spoilage vs Adjusted Profit (per Item)")
plt.xlabel("Average Loss Rate (%)")
plt.ylabel("Adjusted Profit (RMB)")
plt.show()
