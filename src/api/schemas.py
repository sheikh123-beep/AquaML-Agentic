from typing import Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class AnalysisRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True
    )

    query: str = Field(
        ...,
        min_length=3,
        max_length=500
    )

    request_type: Literal[
        "forecast",
        "anomaly",
        "weather",
        "full_analysis",
        "planning"
    ] = "full_analysis"

    dma_id: Literal["DMA3"] = "DMA3"


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["success", "error"]
    project: str = "AquaML Agentic"
    dma_id: str
    request_type: str
    workflow_status: str
    analyst_response: str
    sources_used: list[str] = Field(default_factory=list)
    agent_results: dict[str, Any] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class APIErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    message: str
    errors: list[str] = Field(default_factory=list)
