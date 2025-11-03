from django.urls import path
from . import views

urlpatterns = [
    path("report/", views.report_status, name="report"),
    path("predict/", views.predict, name="predict"),
    path("ping/", views.ping, name="ping"),
]
