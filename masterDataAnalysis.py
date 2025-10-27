import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#Step 1: Load Master Dataset

# Load master dataset
master = pd.read_csv("master_dataset.csv", parse_dates=["date"])

# Quick check
print("Shape:", master.shape)
print("Columns:", master.columns.tolist())

#Step 2: Sales Trends Over Time
# Monthly Revenue
monthly = master.groupby(master['date'].dt.to_period('M')).agg(
    total_revenue=("revenue_rmb", "sum"),
    total_quantity=("quantity_kg", "sum"),
    total_gross_profit=("gross_profit_rmb", "sum"),
    total_adjusted_profit=("adjusted_profit_rmb", "sum")
).reset_index()

# Convert 'date' period back to datetime for plotting
monthly['date'] = monthly['date'].dt.to_timestamp()

# Plot revenue trend
plt.figure(figsize=(10,5))
sns.lineplot(data=monthly, x="date", y="total_revenue", marker="o")
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue (RMB)")
plt.xticks(rotation=45)
# plt.show()

#Step 3: Top-Selling Items
item_summary = master.groupby(["item_code","item_name"]).agg(
    total_quantity=("quantity_kg","sum"),
    total_revenue=("revenue_rmb","sum"),
    total_gross_profit=("gross_profit_rmb","sum"),
    total_adjusted_profit=("adjusted_profit_rmb","sum")
).reset_index()

# Top 10 items by revenue
top_items = item_summary.sort_values("total_revenue", ascending=False).head(10)

plt.figure(figsize=(10,5))
sns.barplot(data=top_items, x="item_name", y="total_revenue")
plt.title("Top 10 Items by Revenue")
plt.xticks(rotation=75)
plt.ylabel("Revenue (RMB)")
# plt.show()

#Step 4: Category-Level Summary
category_summary = master.groupby("category_name").agg(
    total_revenue=("revenue_rmb","sum"),
    total_gross_profit=("gross_profit_rmb","sum"),
    total_adjusted_profit=("adjusted_profit_rmb","sum"),
    avg_loss_rate=("loss_rate_pct","mean")
).reset_index()

plt.figure(figsize=(8,5))
sns.barplot(data=category_summary, x="category_name", y="total_adjusted_profit")
plt.title("Category-wise Adjusted Profit")
plt.xticks(rotation=45)
plt.ylabel("Adjusted Profit (RMB)")
# plt.show()

# Step 5: Discounts, Returns, and Loss Impact
# Discount impact
discount_summary = master.groupby("is_discounted").agg(
    avg_revenue=("revenue_rmb","mean"),
    avg_profit=("adjusted_profit_rmb","mean")
).reset_index()

print("Discount Impact:\n", discount_summary)

# Returns impact
return_summary = master.groupby("is_return").agg(
    total_revenue=("revenue_rmb","sum"),
    total_profit=("adjusted_profit_rmb","sum")
).reset_index()

print("Returns Impact:\n", return_summary)

# Loss vs Profit scatter
plt.figure(figsize=(8,5))
sns.scatterplot(data=item_summary, x="total_revenue", y="total_adjusted_profit")
plt.title("Revenue vs Adjusted Profit (per Item)")
plt.xlabel("Total Revenue (RMB)")
plt.ylabel("Adjusted Profit (RMB)")
plt.show()

# Step 6: Save Aggregated Summaries
# item_summary.to_csv("item_summary.csv", index=False)
# category_summary.to_csv("category_summary.csv", index=False)
# monthly.to_csv("monthly_summary.csv", index=False)

print("✅ Summaries saved: item_summary.csv, category_summary.csv, monthly_summary.csv")


# Discount summary
discount_summary = master.groupby("is_discounted").agg(
    avg_profit=("adjusted_profit_rmb","mean")
).reset_index()
discount_summary.to_csv("discount_summary.csv", index=False)

# Return summary
return_summary = master.groupby("is_return").agg(
    total_profit=("adjusted_profit_rmb","sum")
).reset_index()
return_summary.to_csv("return_summary.csv", index=False)
