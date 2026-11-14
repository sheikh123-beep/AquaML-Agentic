from src.agents.state import AquaMLState


def run_analyst_agent(state: AquaMLState) -> dict:
    try:
        request_type = state.get("request_type", "full_analysis").lower()
        dma_id = state.get("dma_id", "DMA3")

        forecast = state.get("forecast_result", {})
        anomaly = state.get("anomaly_result", {})
        weather = state.get("weather_result", {})
        planning = state.get("planning_result", {})

        lines = [
            "AQUAML WATER ANALYSIS REPORT",
            f"Area: {dma_id}",
            ""
        ]

        sources_used = []

        if forecast.get("status") == "success":
            predicted_flow = forecast.get("predicted_flow_l_s")
            if predicted_flow is not None:
                lines.append(
                    f"Predicted next-hour flow: {float(predicted_flow):.3f} L/s"
                )
            else:
                lines.append("Predicted flow value is unavailable.")

            sources_used.append("Forecasting Agent")

        if anomaly.get("status") == "success":
            detected = anomaly.get("anomaly_detected")

            if detected is True:
                lines.append("Flow pattern: An unusual pattern was detected.")
            elif detected is False:
                lines.append("Flow pattern: No unusual pattern was detected.")
            else:
                lines.append("Flow pattern: Anomaly result is unavailable.")

            score = anomaly.get("anomaly_score")
            if score is not None:
                lines.append(f"Anomaly score: {float(score):.5f}")

            lines.append(
                "Note: This result concerns the latest observed record only. "
                "An anomaly is not proof of a water leak."
            )
            sources_used.append("Anomaly Detection Agent")

        if weather.get("status") == "success":
            weather_data = weather.get("weather", {})

            lines.append("")
            lines.append("Previous-hour historical weather:")

            for key, value in weather_data.items():
                lines.append(f"- {key}: {value}")

            lines.append(
                "These are historical observations, not live weather data "
                "or a future weather forecast."
            )
            sources_used.append("Weather Analysis Agent")

        if planning.get("status") == "success":
            lines.append("")
            lines.append("WATER PLANNING RECOMMENDATION")
            lines.append(
                f"Priority: {planning.get('priority', 'not available')}"
            )
            lines.append(
                f"Recommendation: {planning.get('recommendation', 'Not available')}"
            )
            lines.append("Human review is required before consequential action.")
            sources_used.append("Water Planning Agent")

        if not sources_used:
            raise ValueError("No successful agent results are available.")

        lines.extend([
            "",
            "IMPORTANT LIMITATIONS",
            "- Current pilot analysis covers DMA3, not the entire city.",
            "- The dataset contains historical observations, not live sensor feeds.",
            "- An unusual flow pattern should be investigated; it does not confirm leakage.",
            "- AquaML provides decision support and does not control water infrastructure."
        ])

        response = "\n".join(lines)

        result = {
            "status": "success",
            "agent": "AquaML Analyst Agent",
            "dma_id": dma_id,
            "request_type": request_type,
            "sources_used": sources_used,
            "response": response
        }

        return {
            "analyst_result": result,
            "analyst_response": response,
            "workflow_status": "completed",
            "errors": list(state.get("errors", []))
        }

    except Exception as error:
        error_message = str(error)

        return {
            "analyst_result": {
                "status": "error",
                "agent": "AquaML Analyst Agent",
                "message": error_message
            },
            "analyst_response": "Unable to generate the analysis report.",
            "workflow_status": "failed",
            "errors": list(state.get("errors", [])) + [error_message]
        }
