from django.urls import path
from . import views

urlpatterns = [
    # Health check endpoint
    path("ping/", views.ping, name="ping"),

    # Universal router endpoint (Telex can send all messages here)
    path("router/", views.router, name="router"),

    # Dedicated endpoints (optional if you want to call directly)
    path("report/", views.report_status, name="report_status"),
    path("predict/", views.predict, name="predict"),
]
