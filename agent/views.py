from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import PowerReport
from .ai_engine import predict_light_status
from .utils import (
    extract_latest_message_text,
    extract_city_from_text,
    extract_power_status_from_text,
    NIGERIAN_CITIES,
)


# ---------------------- 🩵 PING ----------------------
class PingView(APIView):
    """
    Health check endpoint for uptime monitoring.
    Allows both GET and POST for Telex compatibility.
    """

    def get(self, request):
        return Response({
            "status": "ok",
            "app": "LightPadi running live on PythonAnywhere",
            "version": "v2.0.0"
        }, status=status.HTTP_200_OK)

    def post(self, request):
        return self.get(request)


# ---------------------- 🧭 ROUTER ----------------------
class RouterView(APIView):
    """
    Routes Telex messages to the appropriate handler (report or predict).
    Accepts both GET and POST requests.
    """

    def get(self, request):
        return Response({
            "message": {"parts": [
                {"kind": "text", "text": "👋 LightPadi is online and ready to process your messages."}
            ]}
        }, status=status.HTTP_200_OK)

    def post(self, request):
        print("📩 Incoming Telex payload:", request.data)
        try:
            message_data = request.data.get("message", {})
            user_text = extract_latest_message_text(message_data).lower()

            if any(word in user_text for word in ["there is light", "no light", "light is on", "light is off"]):
                print("🔧 Routed to ReportStatusView")
                return ReportStatusView().post(request)
            else:
                print("🔧 Routed to PredictView")
                return PredictView().post(request)

        except Exception as e:
            print("⚠️ Router error:", e)
            return Response({
                "message": {"parts": [
                    {"kind": "text", "text": f"⚠️ LightPadi router error: {str(e)}"}
                ]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------- 💡 REPORT STATUS ----------------------
class ReportStatusView(APIView):
    """
    Handles user reports like “There is light in Lagos” or “No light in Enugu”.
    Saves the info in the database and responds in Telex format.
    """

    def get(self, request):
        return Response({
            "message": {"parts": [
                {"kind": "text", "text": "💡 Use POST to report electricity status in a Nigerian city."}
            ]}
        }, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            message_data = request.data.get("message", {})
            user_text = extract_latest_message_text(message_data)
            city = extract_city_from_text(user_text)
            power_status = extract_power_status_from_text(user_text)

            if not city:
                return Response({
                    "message": {"parts": [
                        {"kind": "text", "text": "🇳🇬 Please include a valid Nigerian city, e.g., Lagos, Abuja, or Enugu."}
                    ]}
                }, status=status.HTTP_200_OK)

            if not power_status:
                return Response({
                    "message": {"parts": [
                        {"kind": "text", "text": "🤔 I didn’t catch that. Try 'There is light in Lagos' or 'No light in Enugu'."}
                    ]}
                }, status=status.HTTP_200_OK)

            PowerReport.objects.create(location=city, status=power_status)

            emoji = "✅" if power_status == "on" else "❌"
            response_text = f"{emoji} LightPadi: Got it! Power is currently {power_status.upper()} in {city}. Thanks for the update 💡."

            return Response({
                "message": {"parts": [{"kind": "text", "text": response_text}]}
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("⚠️ Report error:", e)
            return Response({
                "message": {"parts": [
                    {"kind": "text", "text": f"⚠️ LightPadi ran into an error while saving your report: {str(e)}"}
                ]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------- ⚡ PREDICT STATUS ----------------------
class PredictView(APIView):
    """
    Predicts or reports current electricity status for a Nigerian city.
    """

    def get(self, request):
        return Response({
            "message": {"parts": [
                {"kind": "text", "text": "⚡ Send a POST request like: 'Predict light in Lagos' to get a forecast."}
            ]}
        }, status=status.HTTP_200_OK)

    def post(self, request):
        try:
            message_data = request.data.get("message", {})
            user_text = extract_latest_message_text(message_data)
            city = extract_city_from_text(user_text)

            if not city:
                return Response({
                    "message": {"parts": [
                        {"kind": "text", "text": "🤔 Please mention a Nigerian city (e.g., 'Predict Lagos' or 'Check Enugu status')."}
                    ]}
                }, status=status.HTTP_200_OK)

            if city not in NIGERIAN_CITIES:
                return Response({
                    "message": {"parts": [
                        {"kind": "text", "text": f"🇳🇬 Sorry, '{city}' isn’t yet supported by LightPadi."}
                    ]}
                }, status=status.HTTP_200_OK)

            prediction_data = predict_light_status(city)
            prediction = prediction_data.get("prediction", "unknown")
            confidence = prediction_data.get("confidence", 0.0)

            if prediction == "off":
                message = f"⚡ LightPadi: {city} may experience a power outage soon. (Confidence: {confidence})"
            elif prediction == "on":
                message = f"🔆 LightPadi: Power looks stable in {city}. (Confidence: {confidence})"
            else:
                message = f"🔆 LightPadi: No recent data for {city}. Help me learn — tell me if there’s light 💡."

            return Response({
                "message": {"parts": [{"kind": "text", "text": message}]}
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print("⚠️ Predict error:", e)
            return Response({
                "message": {"parts": [
                    {"kind": "text", "text": f"⚠️ LightPadi encountered an error: {str(e)}"}
                ]}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
