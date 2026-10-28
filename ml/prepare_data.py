import pymysql
import pandas as pd


# ==========================================
# 1. CONNECT TO DATABASE
# ==========================================

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="Reera07&19",
    database="dineflow_db"
)

print("✅ Database connected successfully!")


# ==========================================
# 2. GET PAID ORDER DATA
# ==========================================

query = """
SELECT
    o.order_id,
    o.order_date,
    o.menu_id,
    m.item_name,
    m.category,
    o.quantity,
    o.total_amount
FROM orders o
JOIN menu m
    ON o.menu_id = m.menu_id
WHERE o.order_status = 'Paid'
ORDER BY o.order_date;
"""

df = pd.read_sql(query, connection)

connection.close()

print("\n✅ Order data loaded!")
print(df)


# ==========================================
# 3. BASIC FEATURE ENGINEERING
# ==========================================

df["order_date"] = pd.to_datetime(df["order_date"])

df["date"] = df["order_date"].dt.normalize()
df["day_of_week"] = df["order_date"].dt.dayofweek
df["day_name"] = df["order_date"].dt.day_name()
df["hour"] = df["order_date"].dt.hour
df["month"] = df["order_date"].dt.month
df["is_weekend"] = (
    df["day_of_week"] >= 5
).astype(int)


# ==========================================
# 4. CREATE ORDER-LEVEL ML DATASET
# ==========================================

ml_data = df[
    [
        "date",
        "day_of_week",
        "day_name",
        "hour",
        "month",
        "is_weekend",
        "menu_id",
        "item_name",
        "category",
        "quantity"
    ]
]

ml_data.to_csv(
    "ml/demand_dataset.csv",
    index=False
)

print("\n✅ Order-level ML dataset created!")


# ==========================================
# 5. CREATE DAILY DEMAND
# ==========================================

daily_demand = df.groupby(
    [
        "date",
        "menu_id",
        "item_name",
        "category"
    ],
    as_index=False
)["quantity"].sum()

daily_demand.rename(
    columns={
        "quantity": "daily_demand"
    },
    inplace=True
)


# ==========================================
# 6. CREATE COMPLETE DATE RANGE
# ==========================================

min_date = df["date"].min()
max_date = df["date"].max()

all_dates = pd.date_range(
    start=min_date,
    end=max_date,
    freq="D"
)

print(
    f"\n📅 Date range: {min_date.date()} "
    f"to {max_date.date()}"
)


# ==========================================
# 7. GET ALL SOLD MENU ITEMS
# ==========================================

menu_items = df[
    [
        "menu_id",
        "item_name",
        "category"
    ]
].drop_duplicates()


# ==========================================
# 8. CREATE DATE × MENU COMBINATIONS
# ==========================================

date_menu = pd.MultiIndex.from_product(
    [
        all_dates,
        menu_items["menu_id"]
    ],
    names=["date", "menu_id"]
).to_frame(index=False)


# ==========================================
# 9. ADD MENU INFORMATION
# ==========================================

date_menu = date_menu.merge(
    menu_items,
    on="menu_id",
    how="left"
)


# ==========================================
# 10. ADD ACTUAL DAILY DEMAND
# ==========================================

daily_demand = date_menu.merge(
    daily_demand,
    on=[
        "date",
        "menu_id",
        "item_name",
        "category"
    ],
    how="left"
)


# ==========================================
# 11. FILL MISSING DEMAND WITH ZERO
# ==========================================

daily_demand["daily_demand"] = (
    daily_demand["daily_demand"]
    .fillna(0)
    .astype(int)
)


# ==========================================
# 12. ADD DATE FEATURES
# ==========================================

daily_demand["day_of_week"] = (
    daily_demand["date"].dt.dayofweek
)

daily_demand["day_name"] = (
    daily_demand["date"].dt.day_name()
)

daily_demand["month"] = (
    daily_demand["date"].dt.month
)

daily_demand["is_weekend"] = (
    daily_demand["day_of_week"] >= 5
).astype(int)


# ==========================================
# 13. SORT DATA
# ==========================================

daily_demand.sort_values(
    [
        "date",
        "menu_id"
    ],
    inplace=True
)

daily_demand.reset_index(
    drop=True,
    inplace=True
)


# ==========================================
# 14. SAVE DAILY DEMAND DATASET
# ==========================================

daily_demand.to_csv(
    "ml/daily_demand.csv",
    index=False
)

print("\n✅ Improved daily demand dataset created!")

print(
    "\nTotal daily records:",
    len(daily_demand)
)

print("\nDaily demand dataset:")
print(daily_demand)


# ==========================================
# 15. SHOW ZERO-DEMAND RECORDS
# ==========================================

zero_demand = daily_demand[
    daily_demand["daily_demand"] == 0
]

print(
    "\n🟡 Zero-demand records:",
    len(zero_demand)
)

print("\nSample zero-demand records:")
print(zero_demand.head(10))


print("\n🎯 Data preparation completed successfully!")