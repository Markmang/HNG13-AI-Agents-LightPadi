from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PowerReport
from .ai_engine import predict_light_status
from .utils import (
    extract_latest_message_text,
    extract_city_from_text,
    extract_power_status_from_text,
    NIGERIAN_CITIES
)


@api_view(["GET"])
def ping(request):
    """Health check endpoint."""
    return Response({
        "message": {
            "parts": [
                {"kind": "text", "text": "✅ LightPadi running live on PythonAnywhere (v1.0.0)"}
            ]
        }
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def router(request):
    """
    A universal endpoint that decides whether to use /report/ or /predict/
    based on the content of the message.
    - If the message contains 'there is light', 'no light', or 'power is off/on' → report
    - Otherwise → predict
    """
    try:
        message_data = request.data.get("message", {})
        user_text = extract_latest_message_text(message_data).lower()

        # Import the view logic directly (bypass DRF decorator)
        from django.test.client import RequestFactory
        factory = RequestFactory()

        if any(phrase in user_text for phrase in ["there is light", "no light", "power is on", "power is off"]):
            # Create a fake request to mimic DRF request for report
            fake_request = factory.post("/report/", request.data, content_type="application/json")
            return report_status(fake_request)
        else:
            # Create a fake request to mimic DRF request for predict
            fake_request = factory.post("/predict/", request.data, content_type="application/json")
            return predict(fake_request)

    except Exception as e:
        return Response({
            "message": {
                "parts": [
                    {"kind": "text", "text": f"⚠️ LightPadi encountered an unexpected error while routing: {str(e)}"}
                ]
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def report_status(request):
    """
    Handles user reports like "There is light in Lagos" or "No light in Enugu".
    Saves to the database and returns a friendly acknowledgment.
    """
    try:
        message_data = request.data.get("message", {})
        user_text = extract_latest_message_text(message_data)
        city = extract_city_from_text(user_text)
        power_status = extract_power_status_from_text(user_text)

        if not city:
            return Response({
                "message": {
                    "parts": [
                        {"kind": "text", "text": "🇳🇬 Sorry, LightPadi currently supports only major Nigerian cities. Please include one like 'Lagos' or 'Enugu'."}
                    ]
                }
            }, status=200)

        if not power_status:
            return Response({
                "message": {
                    "parts": [
                        {"kind": "text", "text": "🤔 I didn’t quite catch that. Please say something like 'There is light in Lagos'."}
                    ]
                }
            }, status=200)

        PowerReport.objects.create(location=city, status=power_status)

        emoji = "✅" if power_status == "on" else "❌"
        return Response({
            "message": {
                "parts": [
                    {"kind": "text", "text": f"{emoji} LightPadi: Got it! Power is currently {power_status.upper()} in {city}. Thanks for the update 💡."}
                ]
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "message": {
                "parts": [
                    {"kind": "text", "text": f"⚠️ LightPadi ran into an error while saving your report: {str(e)}"}
                ]
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST", "GET"])
def predict(request):
    """
    Predicts current or future power status for a city.
    Uses the latest message only, ignoring old chat history from Telex.
    """
    try:
        message_data = request.data.get("message", {})
        user_text = extract_latest_message_text(message_data)
        city = extract_city_from_text(user_text)

        if not city:
            return Response({
                "message": {
                    "parts": [
                        {"kind": "text", "text": "🤔 LightPadi couldn’t find any Nigerian city in your request. Try: 'Predict light in Lagos' or 'Check Enugu status'."}
                    ]
                }
            }, status=200)

        # Handle unsupported cities
        if city not in NIGERIAN_CITIES:
            return Response({
                "message": {
                    "parts": [
                        {"kind": "text", "text": "🇳🇬 Sorry, LightPadi currently supports only major Nigerian cities."}
                    ]
                }
            }, status=200)

        prediction_data = predict_light_status(city)

        # Format AI prediction nicely for Telex
        if prediction_data.get("prediction") == "unsupported":
            message = prediction_data["message"]
        elif prediction_data.get("prediction") == "unknown":
            message = f"🔆 LightPadi: {prediction_data['message']} (Confidence: {prediction_data['confidence']})"
        elif prediction_data.get("prediction") == "off":
            message = f"⚡ LightPadi: Based on recent reports, {city} may experience a power outage soon. (Confidence: {prediction_data['confidence']})"
        else:
            message = f"🔆 LightPadi: Power looks stable in {city} right now. (Confidence: {prediction_data['confidence']})"

        return Response({
            "message": {
                "parts": [
                    {"kind": "text", "text": message}
                ]
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "message": {
                "parts": [
                    {"kind": "text", "text": f"⚠️ LightPadi encountered an error: {str(e)}"}
                ]
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
