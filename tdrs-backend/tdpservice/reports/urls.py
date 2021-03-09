"""Routing for Reports."""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register("", views.ReportFileViewSet)

urlpatterns = []

urlpatterns += router.urls
