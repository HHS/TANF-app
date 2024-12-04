"""Routing for STTs."""

from django.urls import path
from . import views

urlpatterns = [
    path("by_region", views.RegionAPIView.as_view(), name="stts-by-region"),
    path("alpha", views.STTApiAlphaView.as_view(), name="stts-alpha"),
    path("", views.STTApiView.as_view(), name="stts"),
]
