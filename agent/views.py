from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PowerReport
from .ai_engine import predict_light_status, NIGERIAN_CITIES
from .utils import extract_city_from_text, extract_message_text


@api_view(["POST"])
def report_status(request):
    """
    Handles user reports like 'There is light in Lagos' or 'No light in Enugu'.
    Extracts the city and status, stores it, and responds with a friendly message.
    """
    try:
        message = request.data.get("message", {})
        text = extract_message_text(message)

        if not text:
            return Response({
                "text": "🤔 I didn’t quite catch that. Please say something like 'There is light in Lagos'."
            }, status=status.HTTP_200_OK)

        location = extract_city_from_text(text)
        if not location:
            return Response({
                "text": "🤔 I couldn’t find any Nigerian city in your message. Try again with a valid city name!"
            }, status=status.HTTP_200_OK)

        if location not in NIGERIAN_CITIES:
            return Response({
                "text": f"🇳🇬 Sorry, LightPadi currently supports only major Nigerian cities. '{location}' isn’t in my list yet."
            }, status=status.HTTP_200_OK)

        # Detect ON or OFF based on message content
        status_ = "off" if any(word in text.lower() for word in ["no light", "off", "dark"]) else "on"

        # Save report to DB
        PowerReport.objects.create(location=location, status=status_)

        message = (
            f"✅ LightPadi: Got it! Power is currently ON in {location}. Thanks for the update 💡."
            if status_ == "on"
            else f"⚡ LightPadi: Thanks for the report! Power is OFF in {location}. I’ll remember that."
        )

        return Response({"text": message}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "text": f"⚠️ LightPadi ran into an error while saving your report: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def predict(request):
    """
    Predicts power status for a given city.
    Handles messages like 'Check light in Lagos' or 'Predict Enugu'.
    """
    try:
        message = request.data.get("message", {})
        text = extract_message_text(message)
        location = extract_city_from_text(text)

        if not text:
            return Response({
                "text": "🤔 Please tell me which city you’d like to check. Example: 'Predict light in Lagos'."
            }, status=status.HTTP_200_OK)

        if not location:
            return Response({
                "text": "🤔 LightPadi couldn’t find any Nigerian city in your request. Try: 'Predict light in Lagos' or 'Check Enugu status'."
            }, status=status.HTTP_200_OK)

        if location not in NIGERIAN_CITIES:
            return Response({
                "text": f"🇳🇬 Sorry, LightPadi currently supports only major Nigerian cities. '{location}' isn’t in my list yet."
            }, status=status.HTTP_200_OK)

        data = predict_light_status(location)

        message = f"🔆 LightPadi: {data['message']} (Confidence: {data['confidence']})"

        return Response({"text": message}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "text": f"⚠️ LightPadi ran into an error while processing your request: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def ping(request):
    """
    Simple health check endpoint to verify deployment and version.
    """
    return Response({
        "status": "ok",
        "message": "LightPadi is live and connected ⚡",
        "version": "v1.2.3"
    }, status=status.HTTP_200_OK)
