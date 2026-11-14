# 💧 AquaML Agentic
### Intelligent Urban Water Management System

An AI-powered multi-agent system for water flow forecasting, unusual pattern detection, historical weather analysis, and intelligent water planning recommendations.

AquaML Agentic combines Machine Learning, Agentic AI, LangGraph, FastAPI, and Streamlit to demonstrate how intelligent systems can support water distribution monitoring and decision-making.

---

## 🚀 Project Overview

Water distribution networks face challenges such as changing demand, unusual flow patterns, and inefficient monitoring.

AquaML Agentic aims to address these challenges through specialized AI agents that analyze historical water network data and generate explainable recommendations.

The current research prototype uses historical data from the Battle of Water Demand Forecasting (BWDF) dataset.

**Current pilot scope:** DMA3 (District Metered Area 3).

---

## ✨ Key Features

- **Water Flow Forecasting:** XGBoost-based one-hour-ahead flow prediction.
- **Anomaly Monitoring:** Isolation Forest identifies unusual flow patterns.
- **Weather Analysis:** Evaluates historical rainfall, temperature, humidity, and windspeed.
- **Water Planning:** Generates advisory recommendations based on agent outputs.
- **AI Analyst:** Combines analytical results into understandable reports.
- **Multi-Agent Orchestration:** LangGraph coordinates specialized agents.
- **REST API:** FastAPI provides analysis endpoints.
- **Interactive Dashboard:** Streamlit displays forecasts, anomalies, weather insights, and planning results.
- **Human-in-the-loop:** Recommendations require human review; no automatic infrastructure control.

---

## 🧠 System Architecture

```text
                User
                  |
                  v
          Streamlit Dashboard
                  |
                  v
             FastAPI
                  |
                  v
          LangGraph Orchestrator
                  |
       +----------+----------+
       |          |          |
       v          v          v
  Forecasting  Anomaly    Weather
    Agent      Agent      Agent
       |          |          |
       +----------+----------+
                  |
                  v
            Planning Agent
                  |
                  v
             AI Analyst
                  |
                  v
       Explainable Recommendations
                  |
                  v
            Human Review
```

---

## 🤖 Specialized AI Agents

| Agent | Responsibility |
|---|---|
| Forecasting Agent | Predicts next-hour water flow |
| Anomaly Agent | Identifies unusual flow patterns |
| Weather Agent | Analyzes historical weather observations |
| Planning Agent | Generates advisory planning recommendations |
| Analyst Agent | Combines agent outputs into a readable report |

LangGraph manages the workflow and routes requests to the appropriate agents.

---

## 📊 Machine Learning Results

The current forecasting model uses DMA3 historical data.

### Test Dataset Performance

| Metric | Persistence Baseline | XGBoost |
|---|---:|---:|
| MAE | 0.3111 L/s | **0.1872 L/s** |
| RMSE | 0.4306 L/s | **0.2340 L/s** |
| R² | 0.7343 | **0.9215** |

**Test samples:** 2,889

The XGBoost model achieved approximately 39.8% lower MAE and 45.7% lower RMSE than the persistence baseline.

R² is a statistical goodness-of-fit metric, not prediction accuracy.

### Anomaly Detection

- Algorithm: Isolation Forest
- Estimators: 300
- Contamination setting: 0.03
- Training data: Training split only

The contamination value is a model configuration, not a verified real-world anomaly rate.

---

## 🛠️ Technology Stack

**Programming**
- Python 3.12

**Machine Learning & Data**
- Pandas
- NumPy
- Scikit-learn
- XGBoost

**Agentic AI**
- LangGraph
- Python-based specialized agents

**Backend**
- FastAPI
- Uvicorn
- Pydantic

**Frontend**
- Streamlit

**Testing**
- Pytest-compatible testing
- FastAPI TestClient

---

## 📁 Project Structure

```text
AquaML-Agentic/
│
├── artifacts/
│   └── models/
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── docs/
│   ├── agent_architecture.md
│   ├── data_quality_report.md
│   ├── eda_findings.md
│   ├── feature_engineering_report.md
│   └── dma3_test_metrics.csv
│
├── scripts/
│   ├── train_dma3_model.py
│   ├── train_dma3_anomaly_model.py
│   └── test_*.py
│
├── src/
│   ├── agents/
│   ├── api/
│   ├── services/
│   └── utils/
│
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd AquaML-Agentic
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Start the FastAPI backend

```bash
uvicorn src.api.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Start the Streamlit dashboard

Open another terminal, activate the virtual environment, and run:

```bash
streamlit run dashboard/app.py
```

Dashboard:

```text
http://localhost:8501
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Health check |
| POST | `/analyze` | Execute agentic analysis |

Example request:

```json
{
  "query": "Analyze DMA3 water conditions and provide recommendations.",
  "request_type": "full_analysis",
  "dma_id": "DMA3"
}
```

Supported request types:

- `forecast`
- `anomaly`
- `weather`
- `full_analysis`
- `planning`

---

## 🧪 Testing

The project includes API integration, validation, error handling, and agent workflow tests.

Run:

```bash
python -m scripts.test_api_integration
```

```bash
python -m scripts.test_api_error_handling
```

```bash
python -m scripts.test_langgraph_workflow
```

---

## ⚠️ Current Limitations

This project is a functional research prototype, not a production-deployed water management system.

- Current forecasting and analysis focus on DMA3, not the entire city.
- The dataset contains historical observations, not live sensor feeds.
- Weather analysis uses historical observations, not future weather forecasts.
- Anomaly detection identifies unusual patterns; it does not confirm water leakage.
- Ground-truth anomaly labels are not available for verified detection performance.
- The AI Analyst currently uses a rule-based reporting approach, not an LLM-powered conversational engine.
- Planning recommendations require human review.
- No automatic valve control or physical infrastructure operation is implemented.

---

## 📚 Dataset & Attribution

This project uses the Battle of Water Demand Forecasting (BWDF) supplementary dataset.

The dataset includes historical hourly water inflow measurements across ten District Metered Areas (DMAs), together with weather observations.

The original dataset is distributed under the Creative Commons Attribution 4.0 International (CC BY 4.0) license.

Please retain attribution to the original dataset and its accompanying publication when redistributing the data or derived materials.

Raw dataset files are excluded from this repository.

---

## 🎯 Future Improvements

- LLM-powered conversational AI Analyst.
- Live IoT sensor integration.
- Real-time anomaly monitoring.
- Multi-DMA forecasting and evaluation.
- Weather forecast integration.
- Improved anomaly validation using labelled data.
- Human approval and audit workflows.
- Cloud deployment and monitoring.

---

## 👨‍💻 Project Goal

AquaML Agentic explores the application of Machine Learning and Agentic AI to intelligent water network monitoring and decision support.

**Built with Python, Machine Learning, and Agentic AI.**