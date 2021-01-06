"""Routing for Users."""

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("users", views.UserViewSet)
router.register("roles", views.GroupViewSet)

urlpatterns = []

urlpatterns += router.urls
