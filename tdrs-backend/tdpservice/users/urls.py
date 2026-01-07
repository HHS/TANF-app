"""Routing for Users."""

from django.conf import settings

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

# User and role endpoints
router.register("users", views.UserViewSet)
router.register("roles", views.GroupViewSet)
router.register("feedback", views.FeedbackViewSet)

# User change request endpoints
router.register("change-requests", views.UserChangeRequestViewSet, basename="change-request")
router.register("change-request-logs", views.ChangeRequestAuditLogViewSet, basename="change-request-log")
if settings.DEBUG:
    router.register("cypress-users", views.CypressAdminUserViewSet)

urlpatterns = []

urlpatterns += router.urls
