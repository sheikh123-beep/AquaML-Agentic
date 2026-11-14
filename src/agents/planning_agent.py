from src.agents.state import AquaMLState


def run_planning_agent(state: AquaMLState) -> dict:

    try:
        forecast = state.get("forecast_result", {})
        anomaly = state.get("anomaly_result", {})
        weather = state.get("weather_result", {})

        if forecast.get("status") != "success":
            raise ValueError("Valid forecasting result required.")

        if anomaly.get("status") != "success":
            raise ValueError("Valid anomaly result required.")

        if weather.get("status") != "success":
            raise ValueError("Valid weather result required.")

        predicted_flow = forecast["predicted_flow_l_s"]

        anomaly_detected = anomaly["anomaly_detected"]

        weather_data = weather["weather"]

        if anomaly_detected:

            priority = "high"

            recommendation = (
                "Flag DMA3 for operator review. Verify sensor "
                "readings and investigate the unusual flow pattern "
                "before considering any physical leak."
            )

        else:

            priority = "routine"

            recommendation = (
                "Continue routine monitoring of DMA3. "
                "The latest observation was not flagged as unusual."
            )

        result = {
            "status": "success",
            "agent": "Water Planning Agent",
            "dma_id": state.get("dma_id", "DMA3"),
            "priority": priority,
            "predicted_flow_l_s": predicted_flow,
            "anomaly_detected": anomaly_detected,
            "weather_context": weather_data,
            "recommendation": recommendation,
            "approval_required": True,
            "automatic_infrastructure_action": False,
            "note": (
                "This is a planning recommendation, not an "
                "operational water supply command. Human review "
                "is required before consequential action."
            )
        }

        return {
            "planning_result": result,
            "approval_required": True,
            "errors": list(state.get("errors", []))
        }

    except Exception as error:

        error_message = str(error)

        return {
            "planning_result": {
                "status": "error",
                "agent": "Water Planning Agent",
                "message": error_message
            },
            "approval_required": True,
            "errors": (
                list(state.get("errors", []))
                + [error_message]
            )
        }
