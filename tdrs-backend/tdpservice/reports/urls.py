"""Routing for Reports."""

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("report-sources", views.ReportSourceViewSet, basename="report-source")
router.register("", views.ReportFileViewSet, basename="report")

urlpatterns = []

urlpatterns += router.urls
