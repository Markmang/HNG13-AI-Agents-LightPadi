from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PowerReport
from .ai_engine import predict_light_status, NIGERIAN_CITIES
from django.views.decorators.csrf import csrf_exempt
import re
from django.utils.timezone import now

@api_view(["POST"])
def report_status(request):
    try:
        # Extract text from Telex-style payload
        message_data = request.data.get("message", {})
        parts = message_data.get("parts", [])
        text = parts[0].get("text", "").strip() if parts else ""

        # Find any Nigerian city mentioned in the message
        location = None
        for city in NIGERIAN_CITIES:
            pattern = r"\b" + re.escape(city) + r"\b"
            if re.search(pattern, text, re.IGNORECASE):
                location = city
                break

        if not location:
            return Response({
                "text": f"🇳🇬 Sorry, LightPadi currently supports only major Nigerian cities. '{text.split()[0]}' isn’t in my list yet."
            }, status=status.HTTP_200_OK)

        # Detect whether the user said ON or OFF
        status_text = "on" if "light" in text.lower() and "no" not in text.lower() else "off"

        PowerReport.objects.create(location=location, status=status_text)

        if status_text == "on":
            message = f"✅ LightPadi: Got it! Power is currently ON in {location}. Thanks for the update 💡."
        else:
            message = f"⚡ LightPadi: Thanks for the report! Power is OFF in {location}. I’ll remember that."

        return Response({"text": message}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "text": f"⚠️ LightPadi ran into an error while saving your report: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(["POST", "GET"])
def predict(request):
    """
    Handles light prediction requests from Telex or direct API calls.
    Detects cities automatically, validates Nigerian locations,
    and returns chat-friendly responses.
    """
    try:
        location = None
        text = ""

        # 🔹 Step 1: Extract location from direct API or Telex message
        if request.method == "POST":
            location = request.data.get("location")

            # If Telex message
            if not location and "message" in request.data:
                parts = request.data["message"].get("parts", [])
                for part in parts:
                    if part.get("kind") == "text":
                        text += " " + part.get("text", "")

        elif request.method == "GET":
            location = request.GET.get("location")

        # 🔹 Step 2: If no location, try to detect from text
        if not location and text:
            # Detect one or two-word cities (e.g., "Port Harcourt", "Benin City")
            match = re.search(r"\b([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\b", text)
            if match:
                location = match.group(1).title()

        # 🔹 Step 3: Handle missing location
        if not location:
            return Response(
                {"text": "🤔 LightPadi couldn’t find any Nigerian city in your request. Try: 'Predict light in Lagos' or 'Check Enugu status'."},
                status=status.HTTP_200_OK,
            )

        # 🔹 Step 4: Validate Nigerian city support
        if location not in NIGERIAN_CITIES:
            return Response(
                {"text": f"🇳🇬 Sorry, LightPadi currently supports only major Nigerian cities. '{location}' isn’t in my list yet."},
                status=status.HTTP_200_OK,
            )

        # 🔹 Step 5: Predict power status
        data = predict_light_status(location)

        # 🔹 Step 6: Prepare user-friendly Telex message
        prediction = data.get("prediction")
        confidence = data.get("confidence", 0)
        message = data.get("message", "")

        if prediction == "unsupported":
            final_message = message
        elif prediction == "unknown":
            final_message = f"💡 LightPadi doesn’t have enough recent data for {location}. You can help by reporting the current light status."
        elif prediction == "on":
            final_message = f"🔆 LightPadi: Power looks stable in {location} right now. (Confidence: {confidence})"
        elif prediction == "off":
            final_message = f"⚡ LightPadi: {message} (Confidence: {confidence})"
        else:
            final_message = f"🤖 LightPadi: Something unexpected happened while checking {location}."

        # 🔹 Step 7: Send chat-friendly response
        return Response({"text": final_message}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"text": f"⚠️ LightPadi encountered an error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)