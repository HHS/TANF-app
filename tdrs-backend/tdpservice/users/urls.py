"""Routing for Users."""

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("", views.UserViewSet)
router.register("roles", views.GroupViewSet)
router.register("permissions", views.PermissionViewSet)

urlpatterns = []

urlpatterns += router.urls
