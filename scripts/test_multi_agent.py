from src.agents.forecasting_agent import run_forecasting_agent
from src.agents.anomaly_agent import run_anomaly_agent
from src.agents.weather_agent import run_weather_agent
from src.agents.planning_agent import run_planning_agent


print("\n========== AQUAML MULTI-AGENT TEST ==========")

state = {
    "user_query": "Analyse water conditions for DMA3",
    "request_type": "full_analysis",
    "dma_id": "DMA3",
    "errors": []
}

agents = [
    ("Forecasting Agent", run_forecasting_agent),
    ("Anomaly Detection Agent", run_anomaly_agent),
    ("Weather Analysis Agent", run_weather_agent),
    ("Water Planning Agent", run_planning_agent)
]

for name, agent in agents:

    print(f"\nRunning {name}...")

    result = agent(state)
    state.update(result)

    result_key = {
        "Forecasting Agent": "forecast_result",
        "Anomaly Detection Agent": "anomaly_result",
        "Weather Analysis Agent": "weather_result",
        "Water Planning Agent": "planning_result"
    }[name]

    if state[result_key]["status"] != "success":
        raise SystemExit(f"{name} failed: {state[result_key]}")

    print("SUCCESS")

print("\n========== FINAL AQUAML REPORT ==========")

for key in [
    "forecast_result",
    "anomaly_result",
    "weather_result",
    "planning_result"
]:
    print(f"\n{key.upper()}:")
    print(state[key])

print("\nERRORS:", state.get("errors", []))

print("\nALL FOUR AGENTS PASSED!")
