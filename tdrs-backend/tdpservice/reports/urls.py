"""Routing for Reports."""

from rest_framework.routers import DefaultRouter
from . import views
from django.urls import path

router = DefaultRouter()

router.register("", views.ReportFileViewSet)

urlpatterns = [
    path(
        "<str:year>/<str:quarter>/<str:section>",
        views.GetReport.as_view(),
        name="get-report",
    ),
    path(
        "years/<int:stt>",
        views.GetList.as_view(),
        name="get-report",
    )
]

urlpatterns += router.urls
