from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import PowerReport
from .ai_engine import predict_light_status


@api_view(["POST"])
def report_status(request):
    try:
        location = request.data.get("location")
        status_ = request.data.get("status")

        # Validate input fields
        if not location or not status_:
            return Response({
                "success": False,
                "error": "Missing 'location' or 'status' field.",
                "status": 400
            }, status=status.HTTP_200_OK)

        # Validate status field value
        if status_.lower() not in ["on", "off"]:
            return Response({
                "success": False,
                "error": "Invalid status value. Must be 'on' or 'off'.",
                "status": 422
            }, status=status.HTTP_200_OK)

        # Save new report
        PowerReport.objects.create(location=location.strip(), status=status_.lower())

        return Response({
            "success": True,
            "message": f"Report received: {location.title()} light is {status_.lower()}.",
            "status": 200
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "success": False,
            "error": f"Internal error: {str(e)}",
            "status": 500
        }, status=status.HTTP_200_OK)



@api_view(["GET"])
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
