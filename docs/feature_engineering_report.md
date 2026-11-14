# AquaML Agentic - Feature Engineering Report

## Data Integration

- Combined observations: 19679
- Timezone: UTC
- Duplicate UTC timestamps: 0
- Non-hourly intervals: 0

## Feature Engineering

- Target: DMA 3 net inflow (L/s)
- Forecast horizon: One hour ahead
- Total input features: 19
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

split
train         12458
validation     2896
test           2889

## Output Files

- data/processed/dma3_features.csv
- data/processed/dma3_model_ready.csv

No original raw data was modified.
