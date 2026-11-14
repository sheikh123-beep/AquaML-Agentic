from pathlib import Path
import pandas as pd
import numpy as np

project_dir = Path(__file__).resolve().parents[1]

inflow_path = project_dir / "data" / "raw" / "BWDF" / "InflowData.xlsx"
weather_path = project_dir / "data" / "raw" / "BWDF" / "WeatherData.xlsx"

output_dir = project_dir / "data" / "processed"
docs_dir = project_dir / "docs"

output_dir.mkdir(parents=True, exist_ok=True)

date_col = "Date-time CET-CEST (DD/MM/YYYY HH:mm)"
target = "DMA 3 (L/s)"

# 1. Load and integrate data using UTC timestamps

inflow = pd.read_excel(inflow_path)
weather = pd.read_excel(weather_path)

inflow_dates = pd.to_datetime(
    inflow[date_col],
    format="%d/%m/%Y %H:%M"
)

weather_dates = pd.to_datetime(
    weather[date_col],
    format="%d/%m/%Y %H:%M"
)

inflow_utc = pd.DatetimeIndex(inflow_dates).tz_localize(
    "Europe/Rome",
    ambiguous="infer",
    nonexistent="NaT"
).tz_convert("UTC")

weather_utc = pd.DatetimeIndex(weather_dates).tz_localize(
    "Europe/Rome",
    ambiguous="infer",
    nonexistent="NaT"
).tz_convert("UTC")

if not inflow_utc.equals(weather_utc):
    raise ValueError("Inflow and weather UTC timestamps do not match.")

data = pd.DataFrame(
    { "target_dma3_l_s": inflow[target].to_numpy() },
    index=inflow_utc
)

weather_data = weather.drop(columns=[date_col]).copy()
weather_data.index = weather_utc

data = data.join(weather_data).sort_index()
data.index.name = "timestamp_utc"

print("\n========== AQUAML FEATURE ENGINEERING ==========")

print("\n1. DATA INTEGRATION")
print("Combined rows:", len(data))
print("Combined columns:", len(data.columns))
print("Duplicate UTC timestamps:", data.index.duplicated().sum())

intervals = data.index.to_series().diff().dropna()
bad_intervals = int(
    (intervals != pd.Timedelta(hours=1)).sum()
)

print("Non-hourly intervals:", bad_intervals)

# 2. Calendar features

local_time = data.index.tz_convert("Europe/Rome")

features = pd.DataFrame(index=data.index)

features["target_dma3_l_s"] = data["target_dma3_l_s"]

features["local_hour"] = local_time.hour
features["local_dayofweek"] = local_time.dayofweek
features["local_month"] = local_time.month
features["is_weekend"] = (
    local_time.dayofweek >= 5
).astype(int)

features["hour_sin"] = np.sin(
    2 * np.pi * local_time.hour / 24
)
features["hour_cos"] = np.cos(
    2 * np.pi * local_time.hour / 24
)

features["weekday_sin"] = np.sin(
    2 * np.pi * local_time.dayofweek / 7
)
features["weekday_cos"] = np.cos(
    2 * np.pi * local_time.dayofweek / 7
)

features["month_sin"] = np.sin(
    2 * np.pi * (local_time.month - 1) / 12
)
features["month_cos"] = np.cos(
    2 * np.pi * (local_time.month - 1) / 12
)

# 3. Flow lag and rolling features

past_flow = data["target_dma3_l_s"].shift(1)

features["flow_lag_1"] = data["target_dma3_l_s"].shift(1)
features["flow_lag_24"] = data["target_dma3_l_s"].shift(24)
features["flow_lag_168"] = data["target_dma3_l_s"].shift(168)

features["flow_rolling_mean_24"] = (
    past_flow.rolling(24, min_periods=18).mean()
)

features["flow_rolling_mean_168"] = (
    past_flow.rolling(168, min_periods=144).mean()
)

# 4. Weather features - previous hour only

weather_mapping = {
    "Rainfall depth (mm)": "rainfall_lag_1_mm",
    "Air temperature (°C)": "temperature_lag_1_c",
    "Air humidity (%)": "humidity_lag_1_pct",
    "Windspeed (km/h)": "windspeed_lag_1_kmh"
}

for source, feature_name in weather_mapping.items():
    features[feature_name] = data[source].shift(1)

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

# 5. Chronological split labels

n = len(features)

train_end = int(n * 0.70)
val_end = int(n * 0.85)

split_labels = np.full(n, "test", dtype=object)
split_labels[:train_end] = "train"
split_labels[train_end:val_end] = "validation"

features["split"] = split_labels

# Preserve full feature dataset with missing values

full_path = output_dir / "dma3_features.csv"

features.reset_index().to_csv(
    full_path,
    index=False
)

# Model-ready rows: no target or required feature is missing

model_ready = features.dropna(
    subset=["target_dma3_l_s"] + feature_columns
).copy()

model_path = output_dir / "dma3_model_ready.csv"

model_ready.reset_index().to_csv(
    model_path,
    index=False
)

# Report

split_counts = model_ready["split"].value_counts().reindex(
    ["train", "validation", "test"],
    fill_value=0
)

report = f"""# AquaML Agentic - Feature Engineering Report

## Data Integration

- Combined observations: {len(data)}
- Timezone: UTC
- Duplicate UTC timestamps: {data.index.duplicated().sum()}
- Non-hourly intervals: {bad_intervals}

## Feature Engineering

- Target: DMA 3 net inflow (L/s)
- Forecast horizon: One hour ahead
- Total input features: {len(feature_columns)}
- Flow lag features: 1, 24 and 168 hours
- Rolling windows: 24 and 168 hours
- Weather features: Previous hour
- Calendar features: Hour, weekday, month and cyclical encodings

## Missing Data Policy

- Target values are not imputed.
- Weather values are not imputed.
- Rolling averages require at least 18 of 24 or 144 of 168 previous observations.
- Incomplete model rows are excluded from the model-ready CSV.
- The full feature dataset preserves missing values.

## Chronological Split

- Training: 70%
- Validation: 15%
- Testing: 15%

Model-ready row counts:

{split_counts.to_string()}

## Output Files

- data/processed/dma3_features.csv
- data/processed/dma3_model_ready.csv

No original raw data was modified.
"""

report_path = docs_dir / "feature_engineering_report.md"
report_path.write_text(report, encoding="utf-8")

print("\n2. FEATURE ENGINEERING")
print("Total features:", len(feature_columns))
print("Flow lag features: 3")
print("Rolling features: 2")
print("Weather features: 4")
print("Calendar features: 10")

print("\n3. MODEL-READY DATA")
print("Original rows:", len(features))
print("Model-ready rows:", len(model_ready))
print("Excluded incomplete rows:", len(features) - len(model_ready))

print("\n4. CHRONOLOGICAL SPLITS")
print(split_counts.to_string())

print("\nOUTPUT FILES")
print(full_path)
print(model_path)
print(report_path)

print("\nFEATURE ENGINEERING COMPLETED!")
