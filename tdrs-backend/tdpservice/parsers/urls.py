"""Routing for DataFiles."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ParsingErrorViewSet, DataFileSummaryViewSet

router = DefaultRouter()

router.register("parsing_errors", ParsingErrorViewSet)
router.register("dfs", DataFileSummaryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
