from langgraph.graph import StateGraph, START, END

from src.agents.state import AquaMLState
from src.agents.forecasting_agent import run_forecasting_agent
from src.agents.anomaly_agent import run_anomaly_agent
from src.agents.weather_agent import run_weather_agent
from src.agents.planning_agent import run_planning_agent
from src.agents.analyst_agent import run_analyst_agent


FULL_ANALYSIS_TYPES = {"full_analysis", "planning"}


def route_request(state: AquaMLState) -> str:
    request_type = state.get("request_type", "full_analysis").lower()

    if request_type in {"forecast", "forecast_only"}:
        return "forecast"

    if request_type in {"anomaly", "anomaly_only"}:
        return "anomaly"

    if request_type in {"weather", "weather_only"}:
        return "weather"

    return "forecast"


def after_forecast(state: AquaMLState) -> str:
    request_type = state.get("request_type", "full_analysis").lower()

    if request_type in FULL_ANALYSIS_TYPES:
        return "anomaly"

    return "analyst"


def after_anomaly(state: AquaMLState) -> str:
    request_type = state.get("request_type", "full_analysis").lower()

    if request_type in FULL_ANALYSIS_TYPES:
        return "weather"

    return "analyst"


def after_weather(state: AquaMLState) -> str:
    request_type = state.get("request_type", "full_analysis").lower()

    if request_type in FULL_ANALYSIS_TYPES:
        return "planning"

    return "analyst"


def build_aquaml_graph():
    workflow = StateGraph(AquaMLState)

    workflow.add_node("forecast", run_forecasting_agent)
    workflow.add_node("anomaly", run_anomaly_agent)
    workflow.add_node("weather", run_weather_agent)
    workflow.add_node("planning", run_planning_agent)
    workflow.add_node("analyst", run_analyst_agent)

    workflow.add_conditional_edges(
        START,
        route_request,
        {
            "forecast": "forecast",
            "anomaly": "anomaly",
            "weather": "weather"
        }
    )

    workflow.add_conditional_edges(
        "forecast",
        after_forecast,
        {
            "anomaly": "anomaly",
            "analyst": "analyst"
        }
    )

    workflow.add_conditional_edges(
        "anomaly",
        after_anomaly,
        {
            "weather": "weather",
            "analyst": "analyst"
        }
    )

    workflow.add_conditional_edges(
        "weather",
        after_weather,
        {
            "planning": "planning",
            "analyst": "analyst"
        }
    )

    workflow.add_edge("planning", "analyst")
    workflow.add_edge("analyst", END)

    return workflow.compile()
