"""Routing for DataFiles."""

from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("", views.DataFileViewSet)

urlpatterns = [
    path(
        "years",
        views.GetYearList.as_view(),
        name="get-year-list",
    ),
    path(
        "years/<int:stt>",
        views.GetYearList.as_view(),
        name="get-year-list-admin",
    ),
]

urlpatterns += router.urls
