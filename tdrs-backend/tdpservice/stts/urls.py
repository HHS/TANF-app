"""Routing for STTs."""

from django.urls import path
from . import views

urlpatterns = [
    path("by_region", views.RegionAPIView.as_view(), name="stts-all"),
    path("alpha", views.STTApiView.as_view(), name="stts-alpha"),
]
