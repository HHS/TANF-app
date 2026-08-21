"""Routing for ETL pipeline APIs."""

from rest_framework.routers import DefaultRouter

from tdpservice.etl import views

router = DefaultRouter()

router.register("pipelines", views.PipelineViewSet, basename="etl-pipeline")
router.register("runs", views.PipelineRunViewSet, basename="etl-run")

urlpatterns = []

urlpatterns += router.urls
