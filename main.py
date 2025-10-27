import pandas as pd
# Annex 1
annex1 = pd.read_csv("archiveWorking/annex1.csv")

# Annex 2
annex2 = pd.read_csv("archiveWorking/annex2.csv")

# Annex 3
annex3 = pd.read_csv("archiveWorking/annex3.csv")

# Annex 4
annex4 = pd.read_csv("archiveWorking/annex4.csv")

# Check first few rows
# print(annex1.head())
# print(annex2.head())
# Step 1: Merge sales (annex2) with wholesale price (annex3) using Date + Item Code
merged = pd.merge(annex2, annex3, on=["Date", "Item Code"], how="left")

# Step 2: Merge with product details (annex1)
merged = pd.merge(merged, annex1, on="Item Code", how="left")

# Step 3: Merge with loss rates (annex4)
master = pd.merge(merged, annex4[["Item Code", "Loss Rate (%)"]], on="Item Code", how="left")

# Basic structure
print("Shape:", master.shape)   # rows and columns
print("\nColumns:", master.columns.tolist())  # list of columns

# Data types and missing values
print("\nInfo:")
print(master.info())

print("\nMissing values per column:")
print(master.isnull().sum()+master.isna().sum())

# First few rows
print("\nPreview of dataset:")
print(master.head())

# Quick stats for numeric columns
print("\nDescriptive statistics:")
print(master.describe())

# ---------- 2. Standardize column names ----------
def clean_cols(df):
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
                  .str.lower()
                  .str.replace(" ", "_")
                  .str.replace(r"[\(\)%]", "", regex=True)
                  .str.replace("-", "_")
    )
    return df

annex1 = clean_cols(annex1)
annex2 = clean_cols(annex2)
annex3 = clean_cols(annex3)
annex4 = clean_cols(annex4)

# ---------- 3. Parse dates and types ----------
# Ensure date columns are datetime
annex2['date'] = pd.to_datetime(annex2['date'], errors='coerce')
annex3['date'] = pd.to_datetime(annex3['date'], errors='coerce')

# Convert item_code to str to ensure merges don't fail due to dtype mismatch
for df in (annex1, annex2, annex3, annex4):
    if 'item_code' in df.columns:
        df['item_code'] = df['item_code'].astype(str)

# Convert numeric-ish columns safely
def to_numeric_cols(df, keywords):
    for col in df.columns:
        if any(k in col for k in keywords):
            df[col] = pd.to_numeric(df[col], errors='coerce')

to_numeric_cols(annex2, ['quantity', 'price', 'unit', 'selling'])
to_numeric_cols(annex3, ['wholesale', 'price'])
to_numeric_cols(annex4, ['loss', 'rate'])

# ---------- 4. Merge strategy ----------
# 4.A: Exact outer join on date + item_code for rows where exact dates match
# Start from sales as the base
sales = annex2.copy().sort_values(['item_code', 'date']).reset_index(drop=True)

# Exact left-merge on date + item_code
master = pd.merge(sales, annex3, on=['date', 'item_code'], how='left', suffixes=('', '_wh_exact'))

# After exact merge, some rows may still lack a wholesale price.
# We'll fill missing wholesale prices by using the most recent previous wholesale price available for that item.
# For that we will:
#  - prepare wholesale timeseries sorted by item_code + date
#  - use pd.merge_asof on only the rows that still have wholesale missing

# Prepare wholesale sorted
wholesale = annex3[['item_code', 'date'] + [c for c in annex3.columns if 'wholesale' in c or 'price' in c]].copy()
wholesale = wholesale.sort_values(['item_code', 'date']).reset_index(drop=True)

# Identify which rows in master have missing wholesale price
# Find the wholesale price column name produced by annex3 (try to detect it)
wholesale_cols = [c for c in master.columns if 'wholesale' in c or 'price' in c and c != 'unit_selling_price']
# Prefer explicit 'wholesale_price' if present
wh_col_candidates = [c for c in master.columns if 'wholesale' in c]
if len(wh_col_candidates) > 0:
    wh_col = wh_col_candidates[0]
else:
    # fallback: try common names
    wh_col = 'wholesale_price' if 'wholesale_price' in master.columns else wholesale.columns[-1]

# Rows missing wholesale
missing_wh = master[master[wh_col].isna()].copy()
not_missing_wh = master[master[wh_col].notna()].copy()

# If there are any rows missing wholesale, apply merge_asof to fill from most recent prior date
if not missing_wh.empty and not wholesale.empty:
    # Prepare subset to merge_asof: must be sorted by item_code + date and have same dtypes
    missing_wh = missing_wh.sort_values(['item_code', 'date']).reset_index(drop=True)
    wholesale_sorted = wholesale.sort_values(['item_code', 'date']).reset_index(drop=True)
    
    # merge_asof requires the 'on' key (date) to be sorted and the 'by' key present
    # Ensure date is not null in both
    missing_wh = missing_wh.dropna(subset=['date']).reset_index(drop=True)
    wholesale_sorted = wholesale_sorted.dropna(subset=['date']).reset_index(drop=True)
    
    # Use merge_asof to attach the last wholesale price at or before the sale date
    filled = pd.merge_asof(missing_wh,
                           wholesale_sorted,
                           on='date',
                           by='item_code',
                           direction='backward',
                           suffixes=('', '_wh_asof'))
    
    # Decide which column contains wholesale price in the filled frame
    # Attempt to find any column with 'wholesale' in its name
    wh_from_asof = next((c for c in filled.columns if 'wholesale' in c), None)
    if wh_from_asof is None:
        # fallback to any numeric column from wholesale_sorted
        wh_from_asof = [c for c in wholesale_sorted.columns if c not in ('item_code','date')][0]
    
    # transfer filled wholesale into missing_wh rows
    filled_wh_prices = filled[[ 'date', 'item_code', wh_from_asof ]].copy()
    # rename for clarity
    filled_wh_prices = filled_wh_prices.rename(columns={wh_from_asof: 'wh_from_asof'})
    
    # merge the filled prices back into master missing set
    filled = filled.merge(filled_wh_prices, on=['date','item_code'], how='left')
    # update original missing rows with wh_from_asof where available
    filled[wh_col] = filled_wh_prices['wh_from_asof'].values if 'wh_from_asof' in filled.columns else filled[wh_from_asof]
    
    # Now combine not_missing_wh + filled (with wholesale filled)
    # Keep columns aligned: drop duplicated columns from asof merge if necessary
    # For simplicity, replace missing_wh subset in master with filled
    master = pd.concat([not_missing_wh, filled], ignore_index=True, sort=False)
    # Optional: sort back to original order by date
    master = master.sort_values(['item_code', 'date']).reset_index(drop=True)
else:
    # nothing to fill, master already has wholesale values where available
    master = master.copy()

# ---------- 5. Merge item master & loss rates ----------
# Annex1 join by item_code
master = master.merge(annex1, on='item_code', how='left', suffixes=('', '_item'))

# Annex4 (loss rates) join by item_code (detect loss-rate col name)
loss_cols = [c for c in annex4.columns if 'loss' in c or 'rate' in c]
if loss_cols:
    master = master.merge(annex4[['item_code'] + loss_cols], on='item_code', how='left')

# ---------- 6. Create KPI columns & flags ----------
# Detect quantity and selling price columns
qty_col = next((c for c in master.columns if 'quantity' in c), None)
sell_price_col = next((c for c in master.columns if 'unit_selling' in c or 'unit price' in c or 'unit' in c and 'selling' in c), None)
# fallback generic price column
if sell_price_col is None:
    sell_price_col = next((c for c in master.columns if 'unit' in c and 'price' in c), None)

wholesale_price_col = next((c for c in master.columns if 'wholesale' in c), None)
loss_rate_col = next((c for c in master.columns if 'loss' in c and 'rate' in c), None)

# Create normalized columns
master['quantity_kg'] = pd.to_numeric(master[qty_col], errors='coerce') if qty_col else np.nan
master['unit_selling_price'] = pd.to_numeric(master[sell_price_col], errors='coerce') if sell_price_col else np.nan
master['wholesale_price'] = pd.to_numeric(master[wholesale_price_col], errors='coerce') if wholesale_price_col else np.nan
master['loss_rate_pct'] = pd.to_numeric(master[loss_rate_col], errors='coerce').fillna(0.0) if loss_rate_col else 0.0

# Flags
master['is_return'] = master['sale_or_return'].astype(str).str.lower().str.contains('return', na=False)
# find discount column name
discount_col = next((c for c in master.columns if 'discount' in c), None)
if discount_col:
    master['is_discounted'] = master[discount_col].astype(str).str.lower().str.contains('yes', na=False)
else:
    master['is_discounted'] = False

# Financial KPIs
master['revenue_rmb'] = master['quantity_kg'] * master['unit_selling_price']
master['cost_rmb'] = master['quantity_kg'] * master['wholesale_price']
master['gross_profit_rmb'] = master['revenue_rmb'] - master['cost_rmb']

# Adjusted Profit: (UnitPrice - WholesalePrice) * Quantity * (1 - LossRate/100)
master['adjusted_profit_rmb'] = (master['unit_selling_price'] - master['wholesale_price']) * master['quantity_kg'] * (1 - master['loss_rate_pct'] / 100.0)

# If adjusted_profit is NaN (due to missing prices), keep gross_profit as fallback in another column
master['adjusted_profit_rmb_fallback'] = master['adjusted_profit_rmb'].fillna(master['gross_profit_rmb'])

# ---------- 7. Save and quick overview ----------
out_path = "master_dataset.csv"
master.to_csv(out_path, index=False)

print("Saved master dataset to:", out_path)
print("Master shape:", master.shape)
print("\nColumns sample:", master.columns.tolist()[:30])
print("\nMissing values (top 10):")
print(master.isnull().sum().sort_values(ascending=False).head(10))
print("\nSample rows:")
print(master[['date','item_code','item_name','quantity_kg','unit_selling_price','wholesale_price','revenue_rmb','gross_profit_rmb','adjusted_profit_rmb']].head())

