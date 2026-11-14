from pathlib import Path

import joblib
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st


# ==========================================
# PROJECT CONFIGURATION
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

PREDICTIONS_FILE = PROJECT_DIR / "data/processed/dma3_test_predictions.csv"
METRICS_FILE = PROJECT_DIR / "docs/dma3_test_metrics.csv"
MODEL_READY_FILE = PROJECT_DIR / "data/processed/dma3_model_ready.csv"

ANOMALY_MODEL_FILE = PROJECT_DIR / "artifacts/models/dma3_isolation_forest.joblib"

API_BASE_URL = "http://127.0.0.1:8000"


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AquaML Agentic",
    page_icon="💧",
    layout="wide"
)


# ==========================================
# DATA LOADING
# ==========================================

@st.cache_data
def load_prediction_data():

    df = pd.read_csv(PREDICTIONS_FILE)

    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        utc=True
    )

    return df.sort_values("timestamp_utc")


@st.cache_data
def load_model_metrics():

    return pd.read_csv(METRICS_FILE)


@st.cache_data
def load_monitoring_data():

    df = pd.read_csv(MODEL_READY_FILE)

    df["timestamp_utc"] = pd.to_datetime(
        df["timestamp_utc"],
        utc=True
    )

    model = joblib.load(ANOMALY_MODEL_FILE)

    feature_names = list(model.feature_names_in_)

    missing_features = [
        feature for feature in feature_names
        if feature not in df.columns
    ]

    if missing_features:

        raise ValueError(
            f"Missing anomaly features: {missing_features}"
        )

    X = df[feature_names]

    if X.isna().any().any():

        raise ValueError(
            "Missing values found in anomaly features."
        )

    predictions = model.predict(X)

    scores = model.decision_function(X)

    df["anomaly_flag"] = predictions == -1

    df["anomaly_score"] = scores

    df["anomaly_status"] = df["anomaly_flag"].map({
        True: "Unusual Pattern",
        False: "Normal Pattern"
    })

    return df.sort_values("timestamp_utc")


# ==========================================
# LOAD ALL PROJECT DATA
# ==========================================

try:

    predictions = load_prediction_data()

    model_metrics = load_model_metrics()

    monitoring_data = load_monitoring_data()

except Exception as error:

    st.error(f"Unable to load project data: {error}")

    st.stop()


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_model_row(model_name):

    row = model_metrics[
        model_metrics["model"].str.lower() == model_name.lower()
    ]

    if row.empty:

        raise ValueError(
            f"{model_name} metrics not found."
        )

    return row.iloc[0]


def filter_period(data, selected_range):

    if selected_range == "Last 7 Days":

        return data.tail(168)

    elif selected_range == "Last 30 Days":

        return data.tail(720)

    return data.copy()


def create_flow_chart(data, show_baseline=True):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["timestamp_utc"],
            y=data["actual_flow_l_s"],
            name="Actual Flow",
            mode="lines"
        )
    )

    if show_baseline:

        fig.add_trace(
            go.Scatter(
                x=data["timestamp_utc"],
                y=data["baseline_prediction_l_s"],
                name="Persistence Baseline",
                mode="lines"
            )
        )

    fig.add_trace(
        go.Scatter(
            x=data["timestamp_utc"],
            y=data["xgboost_prediction_l_s"],
            name="XGBoost Prediction",
            mode="lines"
        )
    )

    fig.update_layout(
        title="Actual vs Predicted Water Flow",
        xaxis_title="Timestamp (UTC)",
        yaxis_title="Water Flow (L/s)",
        hovermode="x unified",
        height=450
    )

    return fig


def create_weather_chart(data, column, title, y_title):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["timestamp_utc"],
            y=data[column],
            mode="lines",
            name=title
        )
    )

    fig.update_layout(
        title=title,
        xaxis_title="Timestamp (UTC)",
        yaxis_title=y_title,
        hovermode="x unified",
        height=330
    )

    return fig


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.title("💧 AquaML Agentic")

    st.divider()

    selected_page = st.radio(
        "Navigation",
        [
            "Overview",
            "Forecasting",
            "Anomaly Monitoring",
            "Weather Analysis",
            "AI Analyst",
            "Water Planning"
        ]
    )

    st.divider()

    st.caption("Pilot Dataset: DMA3")
    st.caption("Data Mode: Historical")
    st.caption("Architecture: Multi-Agent AI")

    try:

        response = requests.get(
            f"{API_BASE_URL}/health",
            timeout=3
        )

        response.raise_for_status()

        st.success("API Connected")

    except requests.RequestException:

        st.warning("API Disconnected")


# ==========================================
# DASHBOARD HEADER
# ==========================================

st.title("💧 AquaML Agentic")

st.markdown(
    "### Intelligent Urban Water Management System"
)

st.caption(
    "AI-powered water flow forecasting, anomaly monitoring "
    "and intelligent water planning."
)

st.divider()


# ==========================================
# OVERVIEW
# ==========================================

if selected_page == "Overview":

    st.header("System Overview")

    xgb = get_model_row("XGBoost")

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Test Samples",
            f"{len(predictions):,}"
        )

    with col2:

        st.metric(
            "XGBoost MAE",
            f"{xgb['MAE']:.4f} L/s"
        )

    with col3:

        st.metric(
            "XGBoost RMSE",
            f"{xgb['RMSE']:.4f} L/s"
        )

    with col4:

        st.metric(
            "XGBoost R²",
            f"{xgb['R2']:.4f}"
        )

    st.divider()

    st.subheader("Water Flow Performance")

    st.plotly_chart(
        create_flow_chart(
            predictions.tail(168),
            show_baseline=False
        ),
        use_container_width=True
    )

    st.subheader("ML Model Comparison")

    st.dataframe(
        model_metrics.round(4),
        hide_index=True,
        use_container_width=True
    )

    st.info(
        "XGBoost achieved better test performance than the "
        "Persistence Baseline. R² is not prediction accuracy."
    )


# ==========================================
# FORECASTING
# ==========================================

elif selected_page == "Forecasting":

    st.header("Water Flow Forecasting")

    selected_range = st.selectbox(
        "Select Historical Period",
        [
            "Last 7 Days",
            "Last 30 Days",
            "Full Test Period"
        ]
    )

    chart_data = filter_period(
        predictions,
        selected_range
    )

    st.plotly_chart(
        create_flow_chart(chart_data),
        use_container_width=True
    )

    st.caption(
        f"Displaying {len(chart_data):,} hourly observations."
    )

    xgb = get_model_row("XGBoost")

    baseline = get_model_row("Persistence Baseline")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "XGBoost MAE",
            f"{xgb['MAE']:.4f} L/s"
        )

        st.metric(
            "XGBoost RMSE",
            f"{xgb['RMSE']:.4f} L/s"
        )

    with col2:

        st.metric(
            "Baseline MAE",
            f"{baseline['MAE']:.4f} L/s"
        )

        st.metric(
            "Baseline RMSE",
            f"{baseline['RMSE']:.4f} L/s"
        )

    st.info(
        "These are historical one-hour-ahead rolling predictions, "
        "not live forecasts."
    )


# ==========================================
# ANOMALY MONITORING
# ==========================================

elif selected_page == "Anomaly Monitoring":

    st.header("🚨 Anomaly Monitoring")

    st.write(
        "Isolation Forest identifies unusual historical water-flow patterns."
    )

    selected_range = st.selectbox(
        "Select Monitoring Period",
        [
            "Last 7 Days",
            "Last 30 Days",
            "Full Historical Dataset"
        ],
        key="anomaly_period"
    )

    anomaly_data = filter_period(
        monitoring_data,
        selected_range
    )

    total_observations = len(anomaly_data)

    unusual_data = anomaly_data[
        anomaly_data["anomaly_flag"]
    ]

    unusual_count = len(unusual_data)

    normal_count = total_observations - unusual_count

    unusual_percentage = (
        unusual_count / total_observations * 100
        if total_observations else 0
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Observations",
            f"{total_observations:,}"
        )

    with col2:

        st.metric(
            "Normal Patterns",
            f"{normal_count:,}"
        )

    with col3:

        st.metric(
            "Unusual Patterns",
            f"{unusual_count:,}",
            delta=f"{unusual_percentage:.2f}% flagged"
        )

    st.divider()

    st.subheader("Water Flow Anomaly Timeline")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=anomaly_data["timestamp_utc"],
            y=anomaly_data["target_dma3_l_s"],
            mode="lines",
            name="Observed Water Flow"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=unusual_data["timestamp_utc"],
            y=unusual_data["target_dma3_l_s"],
            mode="markers",
            name="Unusual Pattern",
            marker=dict(
                symbol="x",
                size=9
            )
        )
    )

    fig.update_layout(
        xaxis_title="Timestamp (UTC)",
        yaxis_title="Observed Flow (L/s)",
        hovermode="x unified",
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.divider()

    st.subheader("Isolation Forest Anomaly Score")

    score_fig = go.Figure()

    score_fig.add_trace(
        go.Scatter(
            x=anomaly_data["timestamp_utc"],
            y=anomaly_data["anomaly_score"],
            mode="lines",
            name="Anomaly Score"
        )
    )

    score_fig.add_hline(
        y=0,
        line_dash="dash",
        annotation_text="Anomaly Threshold"
    )

    score_fig.update_layout(
        xaxis_title="Timestamp (UTC)",
        yaxis_title="Decision Function Score",
        height=380
    )

    st.plotly_chart(
        score_fig,
        use_container_width=True
    )

    st.caption(
        "Lower decision-function scores indicate more unusual observations. "
        "Negative scores are classified as anomalies by this model."
    )

    st.divider()

    st.subheader("Most Unusual Observations")

    if not unusual_data.empty:

        top_anomalies = unusual_data.sort_values(
            "anomaly_score"
        ).head(20)

        st.dataframe(
            top_anomalies[
                [
                    "timestamp_utc",
                    "target_dma3_l_s",
                    "anomaly_score",
                    "split",
                    "anomaly_status"
                ]
            ],
            hide_index=True,
            use_container_width=True
        )

    else:

        st.success(
            "No unusual patterns detected in this period."
        )

    st.warning(
        "An unusual pattern is not proof of a water leak. "
        "The Isolation Forest model has no verified leak labels, "
        "so these results require human investigation."
    )

    st.caption(
        "Model trained on the training split and applied to historical "
        "model-ready observations. Contamination setting is not the "
        "verified real-world anomaly rate."
    )


# ==========================================
# WEATHER ANALYSIS
# ==========================================

elif selected_page == "Weather Analysis":

    st.header("🌦️ Weather Analysis")

    st.write(
        "Historical weather observations associated with the DMA3 dataset."
    )

    selected_range = st.selectbox(
        "Select Weather Period",
        [
            "Last 7 Days",
            "Last 30 Days",
            "Full Historical Dataset"
        ],
        key="weather_period"
    )

    weather_data = filter_period(
        monitoring_data,
        selected_range
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Average Rainfall",
            f"{weather_data['rainfall_lag_1_mm'].mean():.2f} mm"
        )

    with col2:

        st.metric(
            "Average Temperature",
            f"{weather_data['temperature_lag_1_c'].mean():.2f} °C"
        )

    with col3:

        st.metric(
            "Average Humidity",
            f"{weather_data['humidity_lag_1_pct'].mean():.2f}%"
        )

    with col4:

        st.metric(
            "Average Windspeed",
            f"{weather_data['windspeed_lag_1_kmh'].mean():.2f} km/h"
        )

    st.divider()

    st.subheader("Rainfall Analysis")

    st.plotly_chart(
        create_weather_chart(
            weather_data,
            "rainfall_lag_1_mm",
            "Historical Rainfall",
            "Rainfall (mm)"
        ),
        use_container_width=True
    )

    st.subheader("Temperature Analysis")

    st.plotly_chart(
        create_weather_chart(
            weather_data,
            "temperature_lag_1_c",
            "Air Temperature",
            "Temperature (°C)"
        ),
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.plotly_chart(
            create_weather_chart(
                weather_data,
                "humidity_lag_1_pct",
                "Air Humidity",
                "Humidity (%)"
            ),
            use_container_width=True
        )

    with col2:

        st.plotly_chart(
            create_weather_chart(
                weather_data,
                "windspeed_lag_1_kmh",
                "Windspeed",
                "Windspeed (km/h)"
            ),
            use_container_width=True
        )

    st.info(
        "Weather values are previous-hour historical observations "
        "used as model features. They are not live weather readings "
        "or future weather forecasts."
    )


# ==========================================
# AI ANALYST
# ==========================================

elif selected_page == "AI Analyst":

    from src.services.dashboard_pages import render_ai_analyst_page

    render_ai_analyst_page(API_BASE_URL)


# ==========================================
# WATER PLANNING
# ==========================================

elif selected_page == "Water Planning":

    from src.services.dashboard_pages import render_water_planning_page

    render_water_planning_page(API_BASE_URL)


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "AquaML Agentic | DMA3 Research Prototype | Historical Dataset"
)