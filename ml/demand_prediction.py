import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. LOAD SYNTHETIC HISTORICAL DATA
# ==========================================

df = pd.read_csv("ml/synthetic_demand_dataset.csv")

print("✅ Synthetic demand dataset loaded!")

print("\nTotal records:", len(df))


# ==========================================
# 2. CONVERT DATE
# ==========================================

df["date"] = pd.to_datetime(df["date"])


# ==========================================
# 3. SELECT FEATURES AND TARGET
# ==========================================

features = [
    "day_of_week",
    "month",
    "is_weekend",
    "menu_id"
]

X = df[features]

y = df["daily_demand"]


# ==========================================
# 4. DEFINE FEATURE TYPES
# ==========================================

categorical_features = [
    "menu_id"
]

numeric_features = [
    "day_of_week",
    "month",
    "is_weekend"
]


# ==========================================
# 5. PREPROCESSING
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "menu",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numbers",
            "passthrough",
            numeric_features
        )
    ]
)


# ==========================================
# 6. RANDOM FOREST MODEL
# ==========================================

model = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),

        (
            "random_forest",
            RandomForestRegressor(
                n_estimators=200,
                random_state=42,
                max_depth=10,
                min_samples_split=2
            )
        )
    ]
)


# ==========================================
# 7. DATE-BASED TRAIN / TEST SPLIT
# ==========================================

# Sort by date

df = df.sort_values("date").reset_index(drop=True)


# Get unique dates

unique_dates = sorted(df["date"].unique())


# Use first 80% of dates for training

split_date_index = int(len(unique_dates) * 0.8)

split_date = unique_dates[split_date_index]


train_df = df[
    df["date"] < split_date
].copy()


test_df = df[
    df["date"] >= split_date
].copy()


X_train = train_df[features]

y_train = train_df["daily_demand"]

X_test = test_df[features]

y_test = test_df["daily_demand"]


print("\nTraining records:", len(X_train))

print("Testing records:", len(X_test))


print(
    "\nTraining date range:",
    train_df["date"].min().date(),
    "to",
    train_df["date"].max().date()
)


print(
    "Testing date range:",
    test_df["date"].min().date(),
    "to",
    test_df["date"].max().date()
)

# ==========================================
# 8. TRAIN MODEL
# ==========================================

model.fit(X_train, y_train)

print("\n✅ Random Forest model trained successfully!")


# ==========================================
# 9. PREDICT TEST DATA
# ==========================================

test_predictions = model.predict(X_test)


# ==========================================
# 10. MODEL EVALUATION
# ==========================================

mae = mean_absolute_error(
    y_test,
    test_predictions
)

mse = mean_squared_error(
    y_test,
    test_predictions
)

r2 = r2_score(
    y_test,
    test_predictions
)


print("\n📊 MODEL PERFORMANCE")

print("--------------------------------")

print("MAE :", round(mae, 2))

print("MSE :", round(mse, 2))

print("R²  :", round(r2, 2))


# ==========================================
# 11. ACTUAL VS PREDICTED
# ==========================================

results = pd.DataFrame({

    "Date": test_df["date"].dt.date,

    "Food Item": test_df["item_name"],

    "Actual Demand": y_test.values,

    "Predicted Demand": test_predictions.round(2)

})


print("\n📈 ACTUAL VS PREDICTED")

print("--------------------------------")

print(results.head(20))


# ==========================================
# 12. TRAIN FINAL MODEL
# ==========================================

# Train using complete historical dataset
# before predicting future demand

X_full = df[features]

y_full = df["daily_demand"]


model.fit(X_full, y_full)


print("\n✅ Final model trained using complete historical data!")


# ==========================================
# 13. CREATE NEXT-DAY DATA
# ==========================================

# Use the current date for future prediction

today = pd.Timestamp.today().normalize()

next_date = today + pd.Timedelta(days=1)


print("\n🔮 FUTURE PREDICTION DATE:")

print(next_date.date())


future_records = []


for menu_id in sorted(df["menu_id"].unique()):

    item = df[
        df["menu_id"] == menu_id
    ].iloc[0]

    day_of_week = next_date.dayofweek

    month = next_date.month

    is_weekend = (
        1
        if day_of_week >= 5
        else 0
    )

    future_records.append({

        "date": next_date,

        "menu_id": menu_id,

        "item_name": item["item_name"],

        "category": item["category"],

        "day_of_week": day_of_week,

        "month": month,

        "is_weekend": is_weekend

    })


future_df = pd.DataFrame(
    future_records
)


# ==========================================
# 14. PREDICT FUTURE DEMAND
# ==========================================

future_X = future_df[features]


future_predictions = model.predict(
    future_X
)


future_df["predicted_demand"] = (
    future_predictions
    .round(0)
    .astype(int)
)


# Prevent negative values

future_df["predicted_demand"] = (
    future_df["predicted_demand"]
    .clip(lower=0)
)


# ==========================================
# 15. ADD SMART RECOMMENDATION
# ==========================================

def recommendation(demand):

    if demand >= 18:

        return "🟢 Prepare More"

    elif demand >= 10:

        return "🟡 Normal Stock"

    else:

        return "🔴 Prepare Less"


future_df["recommendation"] = (
    future_df["predicted_demand"]
    .apply(recommendation)
)


# ==========================================
# 16. DISPLAY FUTURE PREDICTIONS
# ==========================================

print("\n🔮 NEXT-DAY DEMAND PREDICTION")

print("--------------------------------")

print(
    future_df[
        [
            "date",
            "item_name",
            "category",
            "predicted_demand",
            "recommendation"
        ]
    ]
)


# ==========================================
# 17. SAVE FUTURE PREDICTIONS
# ==========================================

future_df.to_csv(
    "ml/demand_predictions.csv",
    index=False
)


print("\n✅ Future predictions saved successfully!")

print(
    "File: ml/demand_predictions.csv"
)