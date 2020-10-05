"""Routing for Users."""

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

router.register("", views.UserViewSet)

urlpatterns = []

urlpatterns += router.urls
