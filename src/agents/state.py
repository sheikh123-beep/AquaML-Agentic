from typing import TypedDict, Any

class AquaMLState(TypedDict, total=False):
    user_query: str
    request_type: str
    dma_id: str
    forecast_input: dict[str, float]
    prediction_timestamp_utc: str
    forecast_result: dict[str, Any]
    anomaly_result: dict[str, Any]
    weather_result: dict[str, Any]
    planning_result: dict[str, Any]
    analyst_result: dict[str, Any]
    analyst_response: str
    approval_required: bool
    workflow_status: str
    errors: list[str]
