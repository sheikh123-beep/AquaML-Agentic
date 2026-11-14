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
model_path = project_dir / "artifacts" / "models" / "dma3_xgboost.json"

docs_dir = project_dir / "docs"
output_dir = project_dir / "data" / "processed"

target = "target_dma3_l_s"

features = [
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

print("\n========== AQUAML FINAL TEST EVALUATION ==========")

# Load test data
df = pd.read_csv(data_path)

test = df[df["split"] == "test"].copy()

X_test = test[features]
y_test = test[target]

if X_test.empty:
    raise ValueError("Test dataset is empty.")

if X_test.isna().any().any() or y_test.isna().any():
    raise ValueError("Missing values found in test dataset.")

# Load previously trained model
model = XGBRegressor()
model.load_model(str(model_path))

# Generate predictions
xgb_predictions = model.predict(X_test)

# Persistence baseline
baseline_predictions = test["flow_lag_1"].to_numpy()

# Calculate metrics
def evaluate(name, actual, predicted):
    return {
        "model": name,
        "MAE": mean_absolute_error(actual, predicted),
        "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
        "R2": r2_score(actual, predicted)
    }

results = pd.DataFrame([
    evaluate("Persistence Baseline", y_test, baseline_predictions),
    evaluate("XGBoost", y_test, xgb_predictions)
])

print("\n1. TEST DATASET")
print("Test rows:", len(test))
print("Test period:",
      test["timestamp_utc"].min(),
      "to",
      test["timestamp_utc"].max())

print("\n2. FINAL TEST RESULTS")
print(results.round(4).to_string(index=False))

# Save metrics
metrics_path = docs_dir / "dma3_test_metrics.csv"
results.to_csv(metrics_path, index=False)

# Save predictions
predictions = pd.DataFrame({
    "timestamp_utc": test["timestamp_utc"].to_numpy(),
    "actual_flow_l_s": y_test.to_numpy(),
    "baseline_prediction_l_s": baseline_predictions,
    "xgboost_prediction_l_s": xgb_predictions
})

prediction_path = output_dir / "dma3_test_predictions.csv"
predictions.to_csv(prediction_path, index=False)

print("\n3. OUTPUT FILES")
print("Metrics:", metrics_path)
print("Predictions:", prediction_path)

print("\nFINAL TEST EVALUATION COMPLETED!")
