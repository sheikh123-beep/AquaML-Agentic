from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
data_dir = project_dir / "data" / "raw" / "BWDF"

inflow = pd.read_excel(data_dir / "InflowData.xlsx")
weather = pd.read_excel(data_dir / "WeatherData.xlsx")

date_col = "Date-time CET-CEST (DD/MM/YYYY HH:mm)"

print("\n========== DATA QUALITY REPORT ==========")

for name, df in [("INFLOW", inflow), ("WEATHER", weather)]:
    print(f"\n--- {name} ---")
    print("Total rows:", len(df))
    print("Duplicate complete rows:", df.duplicated().sum())
    print("Duplicate timestamps:", df[date_col].duplicated().sum())

    missing = df.isnull().sum()
    report = pd.DataFrame({
        "Missing Count": missing,
        "Missing Percentage": (missing / len(df) * 100).round(2)
    })
    print("\nMissing values:")
    print(report.to_string())

    dates = pd.to_datetime(
        df[date_col],
        format="%d/%m/%Y %H:%M",
        errors="coerce"
    )
    print("\nDate range:", dates.min(), "to", dates.max())

print("\n========== TIMESTAMP MATCH ==========")
print("Inflow and Weather timestamps match:",
      inflow[date_col].equals(weather[date_col]))

print("\nQuality check completed.")
