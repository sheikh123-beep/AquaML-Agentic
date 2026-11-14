from pathlib import Path
import pandas as pd
import numpy as np

project_dir = Path(__file__).resolve().parents[1]

file_path = project_dir / "data" / "raw" / "BWDF" / "InflowData.xlsx"
output_dir = project_dir / "data" / "processed"
report_path = project_dir / "docs" / "dma3_quality_review.md"

output_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_excel(file_path)

date_col = "Date-time CET-CEST (DD/MM/YYYY HH:mm)"
target = "DMA 3 (L/s)"

dates = pd.to_datetime(
    df[date_col],
    format="%d/%m/%Y %H:%M"
)

flow = df[target]

print("\n========== DMA 3 QUALITY REVIEW ==========")

# TASK 1: Convert local timestamps to UTC

local_dates = pd.DatetimeIndex(dates)

utc_dates = local_dates.tz_localize(
    "Europe/Rome",
    ambiguous="infer",
    nonexistent="NaT"
).tz_convert("UTC")

print("\n1. TIMEZONE CONVERSION")
print("Timezone: Europe/Rome")
print("UTC conversion successful")
print("Invalid timestamps:", utc_dates.isna().sum())

# TASK 2: Check hourly continuity

utc_diff = pd.Series(utc_dates).diff().dropna()

bad_intervals = utc_diff[
    utc_diff != pd.Timedelta(hours=1)
]

print("\n2. UTC HOURLY CONTINUITY")
print("Total intervals:", len(utc_diff))
print("Non-hourly intervals:", len(bad_intervals))

if len(bad_intervals):
    print(bad_intervals.head(10).to_string())
else:
    print("All UTC intervals are exactly one hour.")

# TASK 3: Identify potential outliers

valid_flow = flow.dropna()

q1 = valid_flow.quantile(0.25)
q3 = valid_flow.quantile(0.75)
iqr = q3 - q1

lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

outlier_mask = (
    (flow < lower) | (flow > upper)
).fillna(False)

print("\n3. POTENTIAL OUTLIERS")
print("Lower boundary:", round(lower, 2))
print("Upper boundary:", round(upper, 2))
print("Outlier count:", int(outlier_mask.sum()))
print("Outlier percentage:", round(outlier_mask.mean() * 100, 2), "%")

# TASK 4: Save review dataset

review = pd.DataFrame({
    "row_number": np.arange(1, len(df) + 1),
    "local_timestamp": dates.astype(str),
    "utc_timestamp": utc_dates.astype(str),
    "dma3_flow_l_s": flow,
    "is_missing": flow.isna(),
    "is_potential_outlier": outlier_mask
})

csv_path = output_dir / "dma3_quality_review.csv"
review.to_csv(csv_path, index=False)

print("\nTOP 10 POTENTIAL OUTLIERS")

print(
    review.loc[outlier_mask]
    .sort_values("dma3_flow_l_s", ascending=False)
    [["local_timestamp", "utc_timestamp", "dma3_flow_l_s"]]
    .head(10)
    .to_string(index=False)
)

report = f"""# DMA 3 Quality Review

- Timezone used: Europe/Rome
- UTC conversion invalid timestamps: {utc_dates.isna().sum()}
- Non-hourly UTC intervals: {len(bad_intervals)}
- IQR lower boundary: {lower:.3f} L/s
- IQR upper boundary: {upper:.3f} L/s
- Potential outliers: {int(outlier_mask.sum())}
- Potential outlier percentage: {outlier_mask.mean() * 100:.2f}%

No raw observations were deleted or modified.

Review CSV: data/processed/dma3_quality_review.csv
"""

report_path.write_text(report, encoding="utf-8")

print("\nReview CSV saved:", csv_path)
print("Review report saved:", report_path)
print("\nQUALITY REVIEW COMPLETED!")
