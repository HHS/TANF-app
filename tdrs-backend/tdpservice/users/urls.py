"""Routing for Users."""

from django.urls import path
from . import views

urlpatterns = [
    path("me", views.UserViewSet.set_profile, name="update-user"),
]
