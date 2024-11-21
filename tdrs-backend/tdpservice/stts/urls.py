"""Routing for STTs."""

from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()

router.register("", views.STTApiViewSet, basename="stts")

urlpatterns = [
    path("by_region", views.RegionAPIView.as_view(), name="stts-by-region"),
    path("alpha", views.STTApiAlphaView.as_view(), name="stts-alpha"),
]

urlpatterns += router.urls
