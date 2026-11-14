from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parents[1]
file_path = project_dir / "data" / "raw" / "BWDF" / "InflowData.xlsx"

df = pd.read_excel(file_path)

date_col = "Date-time CET-CEST (DD/MM/YYYY HH:mm)"

dates = pd.to_datetime(
    df[date_col],
    format="%d/%m/%Y %H:%M"
)

print("\n===== REPEATED TIMESTAMPS =====")

duplicates = df.loc[
    dates.duplicated(keep=False), date_col
]

print(duplicates.to_string(index=False))

print("\n===== MISSING HOURLY TIMESTAMPS =====")

unique_dates = pd.DatetimeIndex(dates.drop_duplicates())

expected = pd.date_range(
    start=dates.min(),
    end=dates.max(),
    freq="h"
)

missing = expected.difference(unique_dates)

print(missing.to_list())

print("\nTimestamp audit completed.")
