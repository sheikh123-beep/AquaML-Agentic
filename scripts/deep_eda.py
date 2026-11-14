from pathlib import Path
import pandas as pd
import numpy as np

project_dir = Path(__file__).resolve().parents[1]

file_path = project_dir / "data" / "raw" / "BWDF" / "InflowData.xlsx"
report_path = project_dir / "docs" / "eda_findings.md"

df = pd.read_excel(file_path)

date_col = "Date-time CET-CEST (DD/MM/YYYY HH:mm)"
target = "DMA 3 (L/s)"

dates = pd.to_datetime(df[date_col], format="%d/%m/%Y %H:%M")
flow = df[target]

print("\n========== DEEP EDA ==========")

# TASK 1: Daily, weekly and monthly patterns

print("\n1. WEEKDAY FLOW PATTERN")

weekday_names = [
    "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday"
]

weekday_avg = pd.DataFrame({
    "weekday": dates.dt.dayofweek,
    "flow": flow
}).groupby("weekday")["flow"].mean()

weekday_avg.index = [weekday_names[i] for i in weekday_avg.index]
print(weekday_avg.round(2).to_string())

print("\nMONTHLY FLOW PATTERN")

monthly_avg = pd.DataFrame({
    "month": dates.dt.to_period("M"),
    "flow": flow
}).groupby("month")["flow"].mean()

print(monthly_avg.round(2).to_string())

# TASK 2: Missing value gaps

print("\n2. MISSING VALUE GAP ANALYSIS")

missing_positions = np.flatnonzero(flow.isna().to_numpy())

if len(missing_positions):
    groups = np.split(
        missing_positions,
        np.where(np.diff(missing_positions) > 1)[0] + 1
    )

    missing_runs = [
        (int(g[0]), int(g[-1]), len(g))
        for g in groups
    ]

    print("Total missing values:", len(missing_positions))
    print("Separate missing gaps:", len(missing_runs))
    print("Longest missing gap:", max(x[2] for x in missing_runs))

    for start, end, count in missing_runs[:10]:
        print(
            f"Rows {start}-{end}: {count} missing values | "
            f"{dates.iloc[start]} to {dates.iloc[end]}"
        )
else:
    missing_runs = []
    print("No missing values found.")

# TASK 3: Potential outliers

print("\n3. POTENTIAL OUTLIER ANALYSIS")

valid_flow = flow.dropna()

q1 = valid_flow.quantile(0.25)
q3 = valid_flow.quantile(0.75)
iqr = q3 - q1

lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

outliers = valid_flow[
    (valid_flow < lower) | (valid_flow > upper)
]

print("Lower IQR boundary:", round(lower, 2))
print("Upper IQR boundary:", round(upper, 2))
print("Potential outliers:", len(outliers))

print("\nHighest potential outliers:")
print(outliers.nlargest(5).to_string())

# TASK 4: Autocorrelation and split planning

print("\n4. AUTOCORRELATION")

for lag in [1, 24, 168]:
    print(
        f"Lag {lag}:",
        round(flow.autocorr(lag=lag), 4)
    )

print("\nCHRONOLOGICAL SPLIT PLAN")

n = len(df)
train_end = int(n * 0.70)
val_end = int(n * 0.85)

print("Total rows:", n)
print("Training rows:", train_end)
print("Validation rows:", val_end - train_end)
print("Testing rows:", n - val_end)

print("Training end:", dates.iloc[train_end - 1])
print("Validation end:", dates.iloc[val_end - 1])
print("Testing end:", dates.iloc[-1])

print("Timestamp order maintained:", dates.is_monotonic_increasing)

# Save findings

report = f"""# AquaML Agentic - Deep EDA Findings

## 1. Weekday Flow Pattern

{weekday_avg.round(3).to_string()}

## 2. Monthly Flow Pattern

{monthly_avg.round(3).to_string()}

## 3. Missing Value Analysis

- Total missing values: {len(missing_positions)}
- Separate missing gaps: {len(missing_runs)}
- Longest missing gap: {max((x[2] for x in missing_runs), default=0)}

## 4. Potential Outliers

- Lower IQR boundary: {lower:.3f} L/s
- Upper IQR boundary: {upper:.3f} L/s
- Potential outlier count: {len(outliers)}

Outliers are flagged for investigation only. No values were deleted.

## 5. Autocorrelation

{chr(10).join(f"- Lag {lag}: {flow.autocorr(lag=lag):.4f}" for lag in [1, 24, 168])}

## 6. Chronological Split Plan

- Training: 70%
- Validation: 15%
- Testing: 15%
- Total observations: {n}
- Timestamp order maintained: {dates.is_monotonic_increasing}

This is a preliminary split plan. Final splitting will happen after
timestamp handling and preprocessing decisions.

## 7. Important Note

No raw data was modified or deleted during this analysis.
"""

report_path.write_text(report, encoding="utf-8")

print("\nEDA findings saved to:", report_path)
print("\nDEEP EDA COMPLETED!")
