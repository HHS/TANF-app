"""Routing for Users."""

from django.conf import settings

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register("users", views.UserViewSet)
router.register("roles", views.GroupViewSet)
router.register("feedback", views.FeedbackViewSet)

if settings.DEBUG:
    router.register("cypress-users", views.CypressAdminUserViewSet)

urlpatterns = []

urlpatterns += router.urls
