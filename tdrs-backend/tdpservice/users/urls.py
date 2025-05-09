"""Routing for Users."""

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

# User and role endpoints
router.register("users", views.UserViewSet)
router.register("roles", views.GroupViewSet)

# User change request endpoints
router.register("change-requests", views.UserChangeRequestViewSet, basename="change-request")
router.register("admin/change-requests", views.AdminChangeRequestViewSet, basename="admin-change-request")
router.register("admin/change-request-logs", views.ChangeRequestAuditLogViewSet, basename="change-request-log")

urlpatterns = []

urlpatterns += router.urls
