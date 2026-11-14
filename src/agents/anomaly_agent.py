from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.agents.state import AquaMLState


PROJECT_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_DIR / "artifacts" / "models" / "dma3_isolation_forest.joblib"
)

DATA_PATH = (
    PROJECT_DIR / "data" / "processed" / "dma3_model_ready.csv"
)

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


def run_anomaly_agent(state: AquaMLState) -> dict:

    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                "Anomaly model not found. Train it first."
            )

        if not DATA_PATH.exists():
            raise FileNotFoundError("Model-ready dataset not found.")

        df = pd.read_csv(DATA_PATH)
        df = df.sort_values("timestamp_utc")

        if df.empty:
            raise ValueError("Dataset is empty.")

        latest = df.iloc[-1]

        input_df = pd.DataFrame([
            latest[FEATURES].to_dict()
        ])

        input_df = input_df.apply(
            pd.to_numeric,
            errors="raise"
        )

        values = input_df.to_numpy(dtype=float)

        if not np.isfinite(values).all():
            raise ValueError("Invalid input values detected.")

        model = joblib.load(MODEL_PATH)

        prediction = int(model.predict(input_df)[0])
        score = float(model.decision_function(input_df)[0])

        anomaly_detected = prediction == -1

        result = {
            "status": "success",
            "agent": "Anomaly Detection Agent",
            "dma_id": state.get("dma_id", "DMA3"),
            "observation_timestamp_utc": str(
                latest["timestamp_utc"]
            ),
            "observed_flow_l_s": round(
                float(latest["target_dma3_l_s"]), 4
            ),
            "anomaly_detected": anomaly_detected,
            "classification": (
                "unusual_pattern"
                if anomaly_detected
                else "normal_pattern"
            ),
            "anomaly_score": round(score, 6),
            "risk_indicator": (
                "review_recommended"
                if anomaly_detected
                else "no_unusual_pattern_detected"
            ),
            "method": "IsolationForest",
            "note": (
                "An unusual pattern is an indicator for investigation, "
                "not confirmation of a physical water leak."
            )
        }

        return {
            "anomaly_result": result,
            "errors": list(state.get("errors", []))
        }

    except Exception as error:

        error_message = str(error)

        return {
            "anomaly_result": {
                "status": "error",
                "agent": "Anomaly Detection Agent",
                "message": error_message
            },
            "errors": (
                list(state.get("errors", []))
                + [error_message]
            )
        }
