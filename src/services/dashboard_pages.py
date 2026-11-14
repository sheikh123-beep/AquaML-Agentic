import requests
import streamlit as st


def call_analysis_api(api_base_url, query, request_type):

    try:
        response = requests.post(
            f"{api_base_url}/analyze",
            json={
                "query": query,
                "request_type": request_type,
                "dma_id": "DMA3"
            },
            timeout=60
        )

        try:
            data = response.json()
        except ValueError:
            st.error("API returned an invalid response.")
            return None

        if response.status_code != 200:

            st.error(
                data.get("message", "Analysis request failed.")
            )

            if data.get("errors"):
                st.write(data["errors"])

            return None

        if data.get("status") != "success":
            st.error("Analysis was not successful.")
            return None

        return data

    except requests.RequestException as error:

        st.error(f"Backend connection failed: {error}")
        return None


# ==========================================
# AI ANALYST PAGE
# ==========================================

def render_ai_analyst_page(api_base_url):

    st.header("🤖 AquaML AI Analyst")

    st.write(
        "Ask questions about DMA3 water flow, "
        "forecasting, anomalies and historical weather."
    )

    st.info(
        "Current version uses the existing rule-based Analyst Agent "
        "through LangGraph. LLM-powered conversation is a future upgrade."
    )

    if "aqua_ai_messages" not in st.session_state:
        st.session_state.aqua_ai_messages = []

    if st.button("Clear Conversation"):

        st.session_state.aqua_ai_messages = []

        st.rerun()

    # Display previous conversation

    for message in st.session_state.aqua_ai_messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])

            if message.get("agent_results"):

                with st.expander("View Agent Results"):

                    st.json(message["agent_results"])

    # User input

    prompt = st.chat_input(
        "Ask something about DMA3 water management..."
    )

    if prompt:

        st.session_state.aqua_ai_messages.append({
            "role": "user",
            "content": prompt
        })

        with st.spinner(
            "Running AquaML multi-agent analysis..."
        ):

            data = call_analysis_api(
                api_base_url,
                prompt,
                "full_analysis"
            )

        if data:

            answer = data.get(
                "analyst_response",
                "No analysis report returned."
            )

            st.session_state.aqua_ai_messages.append({
                "role": "assistant",
                "content": answer,
                "agent_results": data.get("agent_results", {})
            })

            st.rerun()


# ==========================================
# WATER PLANNING PAGE
# ==========================================

def render_water_planning_page(api_base_url):

    st.header("💧 Intelligent Water Planning")

    st.write(
        "Generate explainable water planning recommendations "
        "using the AquaML multi-agent system."
    )

    st.warning(
        "Recommendations use historical DMA3 data. "
        "They are not live water supply commands."
    )

    if st.button(
        "Generate Planning Recommendation",
        type="primary"
    ):

        query = (
            "Generate a DMA3 water supply planning recommendation "
            "using the latest available historical data."
        )

        with st.spinner(
            "Analyzing water conditions and generating recommendations..."
        ):

            data = call_analysis_api(
                api_base_url,
                query,
                "planning"
            )

        if data:

            st.session_state.aqua_planning_result = data

    # Display latest planning result

    data = st.session_state.get(
        "aqua_planning_result"
    )

    if not data:

        st.info(
            "Click Generate Planning Recommendation to start."
        )

        return

    results = data.get("agent_results", {})

    planning = results.get("planning_result", {})

    if not planning:

        st.error("Planning Agent result is missing.")

        st.json(data)

        return

    st.divider()

    st.subheader("Planning Overview")

    priority = planning.get("priority", "unknown")

    predicted_flow = planning.get("predicted_flow_l_s")

    anomaly = planning.get("anomaly_detected", False)

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Planning Priority",
            priority.upper()
        )

    with col2:

        st.metric(
            "Predicted Flow",
            (
                f"{float(predicted_flow):.3f} L/s"
                if predicted_flow is not None
                else "N/A"
            )
        )

    with col3:

        st.metric(
            "Unusual Pattern",
            "Detected" if anomaly else "Not Detected"
        )

    st.divider()

    st.subheader("AI Planning Recommendation")

    st.success(
        planning.get(
            "recommendation",
            "No recommendation available."
        )
    )

    st.divider()

    st.subheader("Weather Context")

    weather = planning.get("weather_context", {})

    if weather:

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Rainfall",
                f"{weather.get('rainfall_mm', 0)} mm"
            )

            st.metric(
                "Temperature",
                f"{weather.get('temperature_c', 0)} °C"
            )

        with col2:

            st.metric(
                "Humidity",
                f"{weather.get('humidity_pct', 0)}%"
            )

            st.metric(
                "Windspeed",
                f"{weather.get('windspeed_kmh', 0)} km/h"
            )

    st.divider()

    st.subheader("Safety & Approval")

    if planning.get("approval_required", False):

        st.warning(
            "Human approval is required before consequential action."
        )

    else:

        st.info("No additional approval requirement was returned.")

    if not planning.get(
        "automatic_infrastructure_action",
        True
    ):

        st.success(
            "Automatic infrastructure control is disabled."
        )

    st.divider()

    with st.expander("View Complete Planning Agent Result"):

        st.json(planning)

    with st.expander("View Complete Analysis Report"):

        st.text(
            data.get(
                "analyst_response",
                "No report available."
            )
        )

    st.caption(
        "Source: AquaML Agentic | LangGraph Multi-Agent Workflow | DMA3"
    )
