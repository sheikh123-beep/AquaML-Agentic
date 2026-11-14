from src.agents.forecasting_agent import run_forecasting_agent


print("\n========== AQUAML FORECASTING AGENT ==========")

initial_state = {
    "user_query": "Predict water flow for DMA3",
    "request_type": "forecast",
    "dma_id": "DMA3",
    "errors": []
}

result = run_forecasting_agent(initial_state)

print("\nFORECASTING AGENT OUTPUT:")

for key, value in result.items():
    print(f"\n{key}:")
    print(value)

if result["forecast_result"]["status"] != "success":
    raise SystemExit("Forecasting Agent test failed.")

print("\nFORECASTING AGENT TEST PASSED!")
