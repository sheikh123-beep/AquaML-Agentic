from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import IsolationForest

PROJECT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = PROJECT_DIR / "data" / "processed" / "dma3_model_ready.csv"
MODEL_DIR = PROJECT_DIR / "artifacts" / "models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
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
    "windspeed_lag_1_kmh",
    "target_dma3_l_s"
]

print("\n========== AQUAML ANOMALY MODEL TRAINING ==========")

df = pd.read_csv(DATA_PATH)

train = df[df["split"] == "train"].copy()

X_train = train[FEATURES]

if X_train.isna().any().any():
    raise ValueError("Missing values found in training data.")

if not np.isfinite(X_train.to_numpy(dtype=float)).all():
    raise ValueError("Invalid numerical values found.")

model = IsolationForest(
    n_estimators=300,
    contamination=0.03,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train)

model_path = MODEL_DIR / "dma3_isolation_forest.joblib"

joblib.dump(model, model_path)

dates = pd.to_datetime(train["timestamp_utc"])

print("\nTraining rows:", len(train))
print("Features:", len(FEATURES))
print("Training period:", dates.min(), "to", dates.max())
print("Contamination setting: 3%")
print("Model saved:", model_path)

print("\nANOMALY MODEL TRAINING COMPLETED!")
