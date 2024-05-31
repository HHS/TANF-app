"""URL patterns for the security app."""

from . import views
from django.urls import path

urlpatterns = [
    path(
        "get-token",
        views.generate_new_token,
        name="get-new-token",
    ),
]
