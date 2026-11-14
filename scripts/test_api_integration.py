from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

print("\n========== AQUAML API INTEGRATION TEST ==========")

# Test 1: Health endpoint
print("\nTEST 1: Health API")

response = client.get("/health")

assert response.status_code == 200
assert response.json()["status"] == "healthy"

print("HEALTH API PASSED")


# Test 2: Full analysis endpoint
print("\nTEST 2: Full Analysis API")

payload = {
    "query": "Analyse water conditions for DMA3",
    "request_type": "full_analysis",
    "dma_id": "DMA3"
}

response = client.post("/analyze", json=payload)

assert response.status_code == 200, response.text

data = response.json()

assert data["status"] == "success"
assert data["workflow_status"] == "completed"
assert data["dma_id"] == "DMA3"

print("ANALYSIS API PASSED")
print("Workflow:", data["workflow_status"])
print("Agents:", data["sources_used"])


# Test 3: Verify all agent results
print("\nTEST 3: Agent Results")

required_agents = [
    "forecast_result",
    "anomaly_result",
    "weather_result",
    "planning_result"
]

for agent in required_agents:
    assert agent in data["agent_results"]
    assert data["agent_results"][agent]["status"] == "success"

print("ALL FOUR AGENT RESULTS VERIFIED")


# Test 4: Invalid request
print("\nTEST 4: Request Validation")

invalid_payload = {
    "query": "",
    "request_type": "full_analysis",
    "dma_id": "DMA3"
}

response = client.post("/analyze", json=invalid_payload)

assert response.status_code == 422

print("INVALID REQUEST REJECTED SUCCESSFULLY")

print("\n========== ALL API INTEGRATION TESTS PASSED! ==========")
