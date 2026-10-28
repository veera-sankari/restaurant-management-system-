import pandas as pd
import numpy as np


# ==========================================
# 1. SETTINGS
# ==========================================

np.random.seed(42)

start_date = "2026-01-01"
end_date = "2026-06-30"


# ==========================================
# 2. MENU ITEMS
# ==========================================

menu_items = {
    1: {
        "item_name": "Chicken Biryani",
        "category": "Main Course",
        "base_demand": 18
    },
    2: {
        "item_name": "Veg Fried Rice",
        "category": "Main Course",
        "base_demand": 14
    },
    4: {
        "item_name": "Plain Dosa",
        "category": "Breakfast",
        "base_demand": 12
    },
    6: {
        "item_name": "muffins",
        "category": "desert",
        "base_demand": 8
    },
    7: {
        "item_name": "French fries",
        "category": "Snacks",
        "base_demand": 10
    },
    9: {
        "item_name": "Meals",
        "category": "Lunch",
        "base_demand": 16
    }
}


# ==========================================
# 3. CREATE DATE RANGE
# ==========================================

dates = pd.date_range(
    start=start_date,
    end=end_date,
    freq="D"
)


# ==========================================
# 4. GENERATE DAILY DEMAND
# ==========================================

records = []

for date in dates:

    day_of_week = date.dayofweek
    month = date.month
    is_weekend = 1 if day_of_week >= 5 else 0

    for menu_id, item in menu_items.items():

        demand = item["base_demand"]

        # Weekend effect
        if is_weekend:
            demand *= 1.25

        # Small monthly variation
        demand *= np.random.uniform(0.90, 1.10)

        # Food-specific patterns
        if menu_id == 4 and day_of_week < 5:
            demand *= 1.15

        if menu_id == 9 and day_of_week < 5:
            demand *= 1.20

        if menu_id == 7 and is_weekend:
            demand *= 1.15

        # Random variation
        demand += np.random.normal(0, 2)

        # Ensure demand is not negative
        demand = max(0, demand)

        # Convert to realistic whole-number quantity
        demand = int(round(demand))

        records.append({
            "date": date,
            "menu_id": menu_id,
            "item_name": item["item_name"],
            "category": item["category"],
            "day_of_week": day_of_week,
            "day_name": date.day_name(),
            "month": month,
            "is_weekend": is_weekend,
            "daily_demand": demand
        })


# ==========================================
# 5. CREATE DATAFRAME
# ==========================================

df = pd.DataFrame(records)


# ==========================================
# 6. SAVE DATASET
# ==========================================

df.to_csv(
    "ml/synthetic_demand_dataset.csv",
    index=False
)


# ==========================================
# 7. DISPLAY INFORMATION
# ==========================================

print("✅ Synthetic demand dataset created!")

print("\nTotal records:", len(df))

print("\nDataset preview:")
print(df.head(15))

print("\nDemand statistics:")
print(
    df.groupby("item_name")["daily_demand"]
    .agg(["mean", "min", "max"])
    .round(2)
)

print("\n📁 Saved to:")
print("ml/synthetic_demand_dataset.csv")