from unittest.mock import patch

from fastapi.testclient import TestClient
from src.api import main as api_main

client = TestClient(api_main.app, raise_server_exceptions=False)

print("\n========== AQUAML API ERROR TEST ==========")

# Test 1: Empty query
response = client.post(
    "/analyze",
    json={
        "query": "",
        "request_type": "full_analysis",
        "dma_id": "DMA3"
    }
)

assert response.status_code == 422
assert response.json()["status"] == "error"
print("EMPTY QUERY REJECTED: PASSED")


# Test 2: Unsupported DMA
response = client.post(
    "/analyze",
    json={
        "query": "Analyse water flow",
        "request_type": "full_analysis",
        "dma_id": "DMA1"
    }
)

assert response.status_code == 422
print("UNSUPPORTED DMA REJECTED: PASSED")


# Test 3: Invalid request type
response = client.post(
    "/analyze",
    json={
        "query": "Analyse water flow",
        "request_type": "invalid",
        "dma_id": "DMA3"
    }
)

assert response.status_code == 422
print("INVALID REQUEST TYPE REJECTED: PASSED")


# Test 4: Unexpected extra field
response = client.post(
    "/analyze",
    json={
        "query": "Analyse water flow",
        "request_type": "forecast",
        "dma_id": "DMA3",
        "unexpected_field": "test"
    }
)

assert response.status_code == 422
print("EXTRA FIELD REJECTED: PASSED")


# Test 5: Unexpected server error
class BrokenWorkflow:
    def invoke(self, state):
        raise RuntimeError("Sensitive internal details")


with patch.object(api_main, "workflow", BrokenWorkflow()):
    response = client.post(
        "/analyze",
        json={
            "query": "Analyse water flow",
            "request_type": "forecast",
            "dma_id": "DMA3"
        }
    )

assert response.status_code == 500
assert response.json()["status"] == "error"
assert "Sensitive internal details" not in response.text

print("INTERNAL ERROR HANDLED SAFELY: PASSED")

print("\n========== ALL ERROR TESTS PASSED! ==========")


