from src.agents.orchestrator import build_aquaml_graph


print("\n========== AQUAML LANGGRAPH WORKFLOW TEST ==========")

app = build_aquaml_graph()

test_cases = [
    "forecast",
    "anomaly",
    "weather",
    "full_analysis"
]

for request_type in test_cases:
    print(f"\nTesting request: {request_type.upper()}")

    initial_state = {
        "user_query": f"Analyse {request_type} for DMA3",
        "request_type": request_type,
        "dma_id": "DMA3",
        "errors": []
    }

    result = app.invoke(initial_state)

    analyst_result = result.get("analyst_result", {})

    if analyst_result.get("status") != "success":
        raise SystemExit(
            f"WORKFLOW FAILED for {request_type}: {analyst_result}"
        )

    print("WORKFLOW SUCCESS")
    print("Status:", result.get("workflow_status"))
    print("Agents used:", analyst_result.get("sources_used"))

    if request_type == "full_analysis":
        print("\n========== FINAL ANALYST REPORT ==========")
        print(result.get("analyst_response"))

        required_results = [
            "forecast_result",
            "anomaly_result",
            "weather_result",
            "planning_result"
        ]

        for key in required_results:
            if result.get(key, {}).get("status") != "success":
                raise SystemExit(f"Missing successful result: {key}")

print("\n========== ALL LANGGRAPH TESTS PASSED! ==========")
