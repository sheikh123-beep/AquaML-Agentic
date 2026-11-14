from pydantic import ValidationError
from src.api.schemas import AnalysisRequest, AnalysisResponse

print("\n========== AQUAML API SCHEMA TEST ==========")

# Test 1: Valid request
request = AnalysisRequest(
    query="Analyse water conditions for DMA3",
    request_type="full_analysis"
)

print("\nTEST 1: Valid Request")
print(request.model_dump())
print("PASSED")

# Test 2: Invalid empty query
print("\nTEST 2: Empty Query Validation")

try:
    AnalysisRequest(query="")
    raise AssertionError("Empty query should have been rejected.")
except ValidationError:
    print("Empty query rejected successfully.")
    print("PASSED")

# Test 3: Unsupported DMA
print("\nTEST 3: Unsupported DMA Validation")

try:
    AnalysisRequest(
        query="Analyse water flow",
        dma_id="DMA1"
    )
    raise AssertionError("DMA1 should have been rejected.")
except ValidationError:
    print("Unsupported DMA rejected successfully.")
    print("PASSED")

# Test 4: Response model
print("\nTEST 4: API Response")

response = AnalysisResponse(
    status="success",
    dma_id="DMA3",
    request_type="full_analysis",
    workflow_status="completed",
    analyst_response="Water analysis completed.",
    sources_used=["Forecasting Agent", "Anomaly Detection Agent"]
)

print(response.model_dump())
print("PASSED")

print("\n========== ALL SCHEMA TESTS PASSED! ==========")
