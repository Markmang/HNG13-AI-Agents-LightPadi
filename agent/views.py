from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PowerReport
from .ai_engine import predict_light_status, NIGERIAN_CITIES


@api_view(["POST"])
def report_status(request):
    try:
        # Try direct JSON fields first
        location = request.data.get("location")
        status_ = request.data.get("status")

        # Fallback: parse Telex text message
        if not location or not status_:
            text = ""
            if isinstance(request.data, dict):
                message = request.data.get("message", {})
                parts = message.get("parts", [])
                if parts:
                    for part in parts:
                        if part.get("kind") == "text":
                            text += part.get("text", " ")
            else:
                text = str(request.data)

            text_lower = text.lower()

            # Detect city from master list
            for city in NIGERIAN_CITIES:
                if city.lower() in text_lower:
                    location = city
                    break

            # Detect light status
            if any(word in text_lower for word in [
                "light is on", "light dey", "power is back", "there is light", "nepa bring light"
            ]):
                status_ = "on"
            elif any(word in text_lower for word in [
                "no light", "light is off", "power is out", "nepa take light", "light don go"
            ]):
                status_ = "off"

        # Handle missing data gracefully
        if not location or not status_:
            return Response({
                "success": False,
                "message": (
                    "😕 LightPadi couldn't understand your report.\n\n"
                    "Try something like:\n"
                    "- 'There is light in Lagos'\n"
                    "- 'No light in Enugu'\n"
                    "- 'NEPA take light for Abuja'\n\n"
                    "I currently support major Nigerian cities only 🇳🇬."
                ),
                "status": 400
            }, status=status.HTTP_200_OK)  # <-- Return 200 so Telex shows message, not error

        # Save valid report
        PowerReport.objects.create(location=location.title(), status=status_.lower())

        return Response({
            "success": True,
            "message": f"✅ LightPadi: Report received — {location.title()} light is {status_.lower()}.",
            "status": 200
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "success": False,
            "message": f"❌ LightPadi encountered an error: {str(e)}",
            "status": 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(["GET", "POST"])
def predict(request):
    try:
        location = request.GET.get("location")

        # Validate location parameter
        if not location:
            return Response({
                "success": False,
                "error": "Missing 'location' query parameter.",
                "status": 400
            }, status=status.HTTP_200_OK)

        # Run prediction logic
        data = predict_light_status(location)

        return Response({
            "success": True,
            "data": data,
            "status": 200
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "success": False,
            "error": f"Internal error: {str(e)}",
            "status": 500
        }, status=status.HTTP_200_OK)
