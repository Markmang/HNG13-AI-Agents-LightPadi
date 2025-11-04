from django.urls import path
from .views import PingView, RouterView, ReportStatusView, PredictView

urlpatterns = [
    path("ping", PingView.as_view(), name="ping"),
    path("router", RouterView.as_view(), name="router"),
    path("report", ReportStatusView.as_view(), name="report"),
    path("predict", PredictView.as_view(), name="predict"),
]
