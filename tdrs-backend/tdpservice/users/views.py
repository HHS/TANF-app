"""Define API views for user class."""
import logging
from django.contrib.auth.models import Group, Permission
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import User
from .permissions import IsAdmin, IsUserOrAdmin
from django.utils import timezone
from .serializers import (
    CreateUserSerializer,
    UserProfileSerializer,
    UserSerializer,
    GroupSerializer
)

logger = logging.getLogger(__name__)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """User accounts viewset."""

    queryset = User.objects.select_related("stt").prefetch_related("groups__permissions")

    def get_permissions(self):
        """Get permissions for the viewset."""
        permission_classes = {"create": [AllowAny], "list": [IsAdmin]}.get(
            self.action, [IsUserOrAdmin]
        )
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "create": CreateUserSerializer,
            "set_profile": UserProfileSerializer,
        }.get(self.action, UserSerializer)

    @action(methods=["PATCH"], detail=False)
    def set_profile(self, request, pk=None):
        """Set a user's profile data."""
        serializer = self.get_serializer(self.request.user, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(
            "Profile update for user: %s on %s", self.request.user, timezone.now()
        )
        return Response(serializer.data)


class GroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """GET for groups (roles)."""

    pagination_class = None
    queryset = Group.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = GroupSerializer
