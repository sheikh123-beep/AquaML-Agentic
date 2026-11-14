from pathlib import Path

import numpy as np
import pandas as pd
from xgboost import XGBRegressor

from src.agents.state import AquaMLState


PROJECT_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    PROJECT_DIR / "artifacts" / "models" / "dma3_xgboost.json"
)

DATA_PATH = (
    PROJECT_DIR / "data" / "processed" / "dma3_model_ready.csv"
)

FEATURE_COLUMNS = [
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


def run_forecasting_agent(state: AquaMLState) -> dict:

    try:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found: {MODEL_PATH}"
            )

        # Use explicitly supplied features when available.
        if state.get("forecast_input") is not None:

            input_df = pd.DataFrame([
                state["forecast_input"]
            ])

            prediction_timestamp = state.get(
                "prediction_timestamp_utc"
            )

            data_source = "provided_features"

        else:
            # Demo mode: use latest available dataset row.
            if not DATA_PATH.exists():
                raise FileNotFoundError(
                    f"Model-ready data not found: {DATA_PATH}"
                )

            df = pd.read_csv(DATA_PATH)

            if df.empty:
                raise ValueError("Model-ready dataset is empty.")

            df = df.sort_values("timestamp_utc")

            latest_row = df.iloc[-1]

            input_df = pd.DataFrame([
                latest_row[FEATURE_COLUMNS].to_dict()
            ])

            prediction_timestamp = str(
                latest_row["timestamp_utc"]
            )

            data_source = "latest_available_dataset_row"

        missing_features = [
            feature
            for feature in FEATURE_COLUMNS
            if feature not in input_df.columns
        ]

        if missing_features:
            raise ValueError(
                f"Missing features: {missing_features}"
            )

        input_df = input_df[FEATURE_COLUMNS].apply(
            pd.to_numeric,
            errors="raise"
        )

        if not np.isfinite(input_df.to_numpy(dtype=float)).all():
            raise ValueError(
                "Invalid or missing feature values detected."
            )

        # Load the already trained XGBoost model.
        model = XGBRegressor()
        model.load_model(str(MODEL_PATH))

        prediction = float(
            model.predict(input_df)[0]
        )

        result = {
            "status": "success",
            "agent": "Forecasting Agent",
            "dma_id": state.get("dma_id", "DMA3"),
            "predicted_flow_l_s": round(prediction, 4),
            "prediction_timestamp_utc": prediction_timestamp,
            "forecast_horizon": "one_hour_ahead_rolling",
            "data_source": data_source,
            "note": (
                "Dataset demo prediction, not a live future forecast. "
                "Live forecasting requires the latest observations."
            )
        }

        return {
            "forecast_result": result,
            "errors": list(state.get("errors", []))
        }

    except Exception as error:

        error_message = str(error)

        return {
            "forecast_result": {
                "status": "error",
                "agent": "Forecasting Agent",
                "message": error_message
            },
            "errors": (
                list(state.get("errors", []))
                + [error_message]
            )
        }
