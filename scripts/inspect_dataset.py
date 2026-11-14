from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
data_dir = project_dir / "data" / "raw" / "BWDF"

inflow_path = data_dir / "InflowData.xlsx"
weather_path = data_dir / "WeatherData.xlsx"

inflow = pd.read_excel(inflow_path)
weather = pd.read_excel(weather_path)

print("\n========== INFLOW DATA ==========")
print("Rows and columns:", inflow.shape)
print("Columns:", list(inflow.columns))
print("\nFirst 5 records:")
print(inflow.head().to_string(index=False))

print("\n========== WEATHER DATA ==========")
print("Rows and columns:", weather.shape)
print("Columns:", list(weather.columns))
print("\nFirst 5 records:")
print(weather.head().to_string(index=False))
