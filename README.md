# Data-Driven Insights for Sales Optimization in Supermarket Vegetable Operations

## 📌 Project Overview
This project analyzes supermarket vegetable sales data to understand profitability patterns and identify loss drivers such as spoilage, discounts, and product returns. The analysis combines Python-based data processing with Excel-based visualization to produce actionable business insights.

## 🎯 Objectives
1. **Sales & Profitability Analysis**  
   Evaluate product- and category-level revenue, gross profit, and adjusted profit.
2. **Loss & Discount Impact Assessment**  
   Quantify the effect of spoilage, discounts, and returns on overall profitability.

## 🗂️ Dataset Source (Proof of Originality)
The dataset used in this project is publicly available:  
**Kaggle Dataset:**  
https://www.kaggle.com/datasets/yapwh1208/supermarket-sales-data  

**Processed Master Dataset (Google Drive):**  
<Your Drive Link Here>

## 🔧 Tools & Technologies
- Python (Pandas, NumPy, Matplotlib, Seaborn)
- Jupyter / Google Colab
- Microsoft Excel (Pivot Tables, Pivot Charts, Dashboard)

## 🧹 Data Processing Steps
- Merged sales, wholesale, spoilage, and product master datasets
- Standardized date formats and cleaned inconsistent entries
- Created KPIs:
  - `Revenue = Quantity × Unit Selling Price`
  - `Cost = Quantity × Wholesale Price`
  - `Gross Profit = Revenue – Cost`
  - `Adjusted Profit = (Price – Wholesale Price) × Quantity × (1 - LossRate%)`

## 📈 Key Insights (Summary)
- High spoilage (22–28%) in Leaf/Flower Vegetables reduced profitability.
- Discounts reduced unit profit by **58%**, indicating margin erosion.
- Product returns resulted in **negative revenue and profit**.
- Top 10 items contributed **major share of profit**, requiring focused inventory control.

## ✅ Recommendations
- Improve cold storage and rotation to reduce spoilage.
- Use **targeted discounts** only for slow-moving items.
- Strengthen return-checking processes to reduce negative profit transactions.

## 👩‍💻 Author
**Divya Darshini S**  
IIT Madras BDM Capstone Project  
2025
