from pathlib import Path
import pandas as pd
import numpy as np

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

from xgboost import XGBRegressor

project_dir = Path(__file__).resolve().parents[1]

data_path = project_dir / "data" / "processed" / "dma3_model_ready.csv"

artifact_dir = project_dir / "artifacts" / "models"
output_dir = project_dir / "data" / "processed"
docs_dir = project_dir / "docs"

artifact_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(data_path)

target = "target_dma3_l_s"

feature_columns = [
    "local_hour",
    "local_dayofweek",
    "local_month",
    "is_weekend",
    "hour_sin",
    "hour_cos",
    "weekday_sin",
    "weekday_cos",
    "month_sin",
    "month_cos",
    "flow_lag_1",
    "flow_lag_24",
    "flow_lag_168",
    "flow_rolling_mean_24",
    "flow_rolling_mean_168",
    "rainfall_lag_1_mm",
    "temperature_lag_1_c",
    "humidity_lag_1_pct",
    "windspeed_lag_1_kmh"
]

print("\n========== AQUAML ML TRAINING ==========")

# TASK 1: Prepare chronological datasets

train = df[df["split"] == "train"].copy()
validation = df[df["split"] == "validation"].copy()

X_train = train[feature_columns]
y_train = train[target]

X_val = validation[feature_columns]
y_val = validation[target]

if X_train.isna().any().any() or X_val.isna().any().any():
    raise ValueError("Missing feature values detected.")

print("\n1. DATA PREPARATION")
print("Training rows:", len(train))
print("Validation rows:", len(validation))
print("Features:", len(feature_columns))

for split_name in ["train", "validation"]:
    dates = pd.to_datetime(
        df.loc[df["split"] == split_name, "timestamp_utc"]
    )
    print(
        split_name,
        "period:",
        dates.min(),
        "to",
        dates.max()
    )

# TASK 2: Persistence baseline

baseline_predictions = validation["flow_lag_1"].to_numpy()

# TASK 3: Train XGBoost

model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.03,
    max_depth=6,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    objective="reg:squarederror",
    eval_metric="rmse",
    tree_method="hist",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

xgb_predictions = model.predict(X_val)

# TASK 4: Evaluate and save

def evaluate_model(name, actual, predicted):
    return {
        "model": name,
        "MAE": mean_absolute_error(actual, predicted),
        "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
        "R2": r2_score(actual, predicted)
    }

results = pd.DataFrame([
    evaluate_model(
        "Persistence Baseline",
        y_val,
        baseline_predictions
    ),
    evaluate_model(
        "XGBoost",
        y_val,
        xgb_predictions
    )
])

print("\n2. VALIDATION MODEL COMPARISON")
print(results.round(4).to_string(index=False))

# Save trained model

model_path = artifact_dir / "dma3_xgboost.json"
model.save_model(str(model_path))

# Save metrics

metrics_path = docs_dir / "dma3_validation_metrics.csv"
results.to_csv(metrics_path, index=False)

# Save validation predictions

predictions = pd.DataFrame({
    "timestamp_utc": validation["timestamp_utc"].to_numpy(),
    "actual_flow_l_s": y_val.to_numpy(),
    "baseline_prediction_l_s": baseline_predictions,
    "xgboost_prediction_l_s": xgb_predictions
})

prediction_path = output_dir / "dma3_validation_predictions.csv"
predictions.to_csv(prediction_path, index=False)

# Save feature importance

importance = pd.DataFrame({
    "feature": feature_columns,
    "importance": model.feature_importances_
}).sort_values("importance", ascending=False)

importance_path = docs_dir / "dma3_feature_importance.csv"
importance.to_csv(importance_path, index=False)

print("\n3. TOP 10 IMPORTANT FEATURES")
print(importance.head(10).round(4).to_string(index=False))

print("\n4. FILES SAVED")
print("Model:", model_path)
print("Metrics:", metrics_path)
print("Predictions:", prediction_path)
print("Feature importance:", importance_path)

print("\nML TRAINING COMPLETED!")
print("Test dataset has NOT been used.")
