from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]

inflow_path = project_dir / "data" / "raw" / "BWDF" / "InflowData.xlsx"
weather_path = project_dir / "data" / "raw" / "BWDF" / "WeatherData.xlsx"

inflow = pd.read_excel(inflow_path)
weather = pd.read_excel(weather_path)

date_col = "Date-time CET-CEST (DD/MM/YYYY HH:mm)"
dates = pd.to_datetime(inflow[date_col], format="%d/%m/%Y %H:%M")

flow_cols = [c for c in inflow.columns if "(L/s)" in c]
weather_cols = [c for c in weather.columns if c != date_col]

target = "DMA 3 (L/s)"

print("\n========== AQUAML AGENTIC: EDA ==========")

print("\n1. DATASET SHAPE")
print("Inflow:", inflow.shape)
print("Weather:", weather.shape)

print("\n2. FLOW STATISTICS")
print(inflow[flow_cols].describe().round(2).to_string())

print("\n3. FLOW MISSING VALUES")
print(inflow[flow_cols].isna().sum().to_string())

print("\n4. WEATHER STATISTICS")
print(weather[weather_cols].describe().round(2).to_string())

print("\n5. DMA 3 ANALYSIS")
print("Target:", target)
print("Valid observations:", inflow[target].count())
print("Missing values:", inflow[target].isna().sum())
print("Mean:", round(inflow[target].mean(), 2), "L/s")
print("Minimum:", round(inflow[target].min(), 2), "L/s")
print("Maximum:", round(inflow[target].max(), 2), "L/s")

print("\n6. HOURLY FLOW PATTERN")
hourly_pattern = inflow[target].groupby(dates.dt.hour).mean()
print(hourly_pattern.round(2).to_string())

print("\n7. WEATHER CORRELATION WITH DMA 3")
combined = pd.concat(
    [inflow[target], weather[weather_cols]],
    axis=1
)
print(combined.corr(numeric_only=True)[target].round(3).to_string())

print("\nEDA STEP 1 COMPLETED!")
