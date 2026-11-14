from pathlib import Path

import numpy as np
import pandas as pd

from src.agents.state import AquaMLState


PROJECT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_DIR / "data" / "processed" / "dma3_model_ready.csv"
)


def run_weather_agent(state: AquaMLState) -> dict:

    try:
        if not DATA_PATH.exists():
            raise FileNotFoundError("Weather dataset not found.")

        df = pd.read_csv(DATA_PATH)
        df = df.sort_values("timestamp_utc")

        if df.empty:
            raise ValueError("Dataset is empty.")

        latest = df.iloc[-1]

        weather_features = {
            "rainfall_lag_1_mm": "rainfall_mm",
            "temperature_lag_1_c": "temperature_c",
            "humidity_lag_1_pct": "humidity_pct",
            "windspeed_lag_1_kmh": "windspeed_kmh"
        }

        weather = {}

        for source, destination in weather_features.items():
            value = float(latest[source])

            if not np.isfinite(value):
                raise ValueError(
                    f"Invalid weather value: {source}"
                )

            weather[destination] = round(value, 3)

        observation_time = pd.to_datetime(
            latest["timestamp_utc"], utc=True
        )

        weather_time = observation_time - pd.Timedelta(hours=1)

        result = {
            "status": "success",
            "agent": "Weather Analysis Agent",
            "dma_id": state.get("dma_id", "DMA3"),
            "weather_observation_timestamp_utc": str(weather_time),
            "weather": weather,
            "data_source": "BWDF historical weather dataset",
            "note": (
                "These are previous-hour historical weather "
                "observations, not live or future weather forecasts."
            )
        }

        return {
            "weather_result": result,
            "errors": list(state.get("errors", []))
        }

    except Exception as error:

        error_message = str(error)

        return {
            "weather_result": {
                "status": "error",
                "agent": "Weather Analysis Agent",
                "message": error_message
            },
            "errors": (
                list(state.get("errors", []))
                + [error_message]
            )
        }
