import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.api.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    APIErrorResponse
)
from src.agents.orchestrator import build_aquaml_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AquaML Agentic API",
    description="Intelligent Urban Water Management System",
    version="1.0.0"
)

workflow = build_aquaml_graph()


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = []

    for error in exc.errors():
        location = ".".join(str(item) for item in error["loc"])
        errors.append(f"{location}: {error['msg']}")

    response = APIErrorResponse(
        message="Request validation failed.",
        errors=errors
    )

    return JSONResponse(
        status_code=422,
        content=response.model_dump()
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(
    request: Request,
    exc: Exception
):
    logger.exception("Unexpected API error")

    response = APIErrorResponse(
        message="An unexpected server error occurred.",
        errors=["Please retry later or contact the administrator."]
    )

    return JSONResponse(
        status_code=500,
        content=response.model_dump()
    )


@app.get("/")
def root():
    return {
        "project": "AquaML Agentic",
        "message": "Welcome to AquaML API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AquaML Backend",
        "version": "1.0.0"
    }


@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    responses={
        422: {"model": APIErrorResponse},
        500: {"model": APIErrorResponse}
    }
)
def analyze_water(request: AnalysisRequest):

    initial_state = {
        "user_query": request.query,
        "request_type": request.request_type,
        "dma_id": request.dma_id,
        "errors": []
    }

    result = workflow.invoke(initial_state)

    required_agents = {
        "forecast": ["forecast_result"],
        "anomaly": ["anomaly_result"],
        "weather": ["weather_result"],
        "full_analysis": [
            "forecast_result",
            "anomaly_result",
            "weather_result",
            "planning_result"
        ],
        "planning": [
            "forecast_result",
            "anomaly_result",
            "weather_result",
            "planning_result"
        ]
    }

    failed_agents = []

    for key in required_agents[request.request_type]:
        agent_result = result.get(key, {})

        if agent_result.get("status") != "success":
            failed_agents.append(key)

    analyst = result.get("analyst_result", {})

    if analyst.get("status") != "success":
        failed_agents.append("analyst_result")

    if failed_agents:
        error_response = APIErrorResponse(
            message="Analysis could not be completed.",
            errors=failed_agents
        )

        return JSONResponse(
            status_code=500,
            content=error_response.model_dump()
        )

    agent_keys = [
        "forecast_result",
        "anomaly_result",
        "weather_result",
        "planning_result"
    ]

    agent_results = {
        key: result[key]
        for key in agent_keys
        if key in result
    }

    return AnalysisResponse(
        status="success",
        dma_id=request.dma_id,
        request_type=request.request_type,
        workflow_status="completed",
        analyst_response=result.get("analyst_response", ""),
        sources_used=analyst.get("sources_used", []),
        agent_results=agent_results,
        errors=[]
    )
