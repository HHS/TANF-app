"""URL patterns for the security app."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "get-token",
        views.generate_new_token,
        name="get-new-token",
    ),
]
