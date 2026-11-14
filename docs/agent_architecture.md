# AquaML Agentic - Day 4 Architecture

## 1. Project Objective
Build an intelligent water management prototype using ML,
specialized agents and LangGraph orchestration.

## 2. Current Dataset Scope
- Dataset: BWDF
- Network: 10 District Metered Areas (DMAs)
- Current ML pilot: DMA3
- Flow unit: L/s
- Time resolution: Hourly
- Current prediction: One-hour-ahead rolling prediction

The current pilot is not a verified full-city water consumption model.

## 3. Specialized Agents

### Forecasting Agent
- Loads the trained DMA3 XGBoost model.
- Produces one-hour-ahead flow predictions.
- Reports predictions in L/s.

### Anomaly Detection Agent
- Detects unusual flow patterns.
- Reports anomaly scores and risk indicators.
- Does not claim that an anomaly confirms a physical leak.

### Weather Analysis Agent
- Analyzes rainfall, temperature, humidity and wind speed.
- Explains observed weather conditions and their relationship
  with water flow.
- Does not claim to forecast future weather.

### Water Planning Agent
- Uses forecasting, anomaly and weather outputs.
- Produces explainable supply planning recommendations.
- Does not control real-world infrastructure.

### AI Analyst Agent
- Explains structured agent outputs.
- Answers questions using project data.
- Uses a provider-independent LLM integration interface.

### Orchestrator Agent
- Uses LangGraph.
- Routes user requests to relevant agents.
- Collects outputs and handles errors.

## 4. Application Architecture

User
  -> FastAPI
  -> LangGraph Orchestrator
  -> Specialized Agents
  -> Shared Agent State
  -> Human Approval Review
  -> API Response

Streamlit will be integrated as the dashboard layer.

## 5. Shared State
The shared state will contain:
- user_query
- request_type
- dma_id
- forecast_result
- anomaly_result
- weather_result
- planning_result
- analyst_response
- approval_required
- errors

## 6. Supported Request Types
- forecast
- anomaly
- weather
- planning
- full_analysis

## 7. Safety and Limitations
- Recommendations require human review before consequential action.
- No automatic valve or infrastructure control.
- Anomalies are indicators, not confirmed leaks.
- Current forecasting scope is one-hour-ahead rolling prediction.
- Current model pilot is DMA3 within a 10-DMA dataset.

## 8. Technology Stack
- Python 3.12
- Pandas and NumPy
- Scikit-learn and XGBoost
- LangGraph
- FastAPI
- Pydantic
- Streamlit (dashboard phase)
