# AquaML Agentic - Deep EDA Findings

## 1. Weekday Flow Pattern

Monday       4.161
Tuesday      4.089
Wednesday    4.130
Thursday     4.118
Friday       4.082
Saturday     4.270
Sunday       4.380

## 2. Monthly Flow Pattern

month
2021-01    4.163
2021-02    4.247
2021-03    4.394
2021-04    4.469
2021-05    4.735
2021-06    5.881
2021-07    5.881
2021-08    5.883
2021-09    4.894
2021-10    3.779
2021-11    3.604
2021-12    3.599
2022-01    3.677
2022-02    3.631
2022-03    3.758
2022-04    3.568
2022-05    4.535
2022-06    5.385
2022-07    5.350
2022-08    4.722
2022-09    3.657
2022-10    3.596
2022-11    3.226
2022-12    3.055
2023-01    2.895
2023-02    2.956
2023-03    3.062
Freq: M

## 3. Missing Value Analysis

- Total missing values: 105
- Separate missing gaps: 47
- Longest missing gap: 31

## 4. Potential Outliers

- Lower IQR boundary: 0.569 L/s
- Upper IQR boundary: 7.519 L/s
- Potential outlier count: 667

Outliers are flagged for investigation only. No values were deleted.

## 5. Autocorrelation

- Lag 1: 0.9108
- Lag 24: 0.9074
- Lag 168: 0.8576

## 6. Chronological Split Plan

- Training: 70%
- Validation: 15%
- Testing: 15%
- Total observations: 19679
- Timestamp order maintained: True

This is a preliminary split plan. Final splitting will happen after
timestamp handling and preprocessing decisions.

## 7. Important Note

No raw data was modified or deleted during this analysis.
