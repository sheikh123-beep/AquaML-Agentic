from src.agents.anomaly_agent import run_anomaly_agent


print("\n========== AQUAML ANOMALY DETECTION AGENT ==========")

initial_state = {
    "user_query": "Check unusual water flow patterns in DMA3",
    "request_type": "anomaly",
    "dma_id": "DMA3",
    "errors": []
}

result = run_anomaly_agent(initial_state)

print("\nANOMALY AGENT OUTPUT:")

for key, value in result.items():
    print(f"\n{key}:")
    print(value)

if result["anomaly_result"]["status"] != "success":
    raise SystemExit("Anomaly Agent test failed.")

print("\nANOMALY AGENT TEST PASSED!")
