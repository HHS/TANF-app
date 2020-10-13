"""Define API views for user class."""
import datetime
import logging
import time
from django.contrib.auth.models import Group, Permission
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import User
from .permissions import IsAdmin, IsUserOrReadOnly
from .serializers import (
    CreateUserSerializer,
    SetUserProfileSerializer,
    UserSerializer,
    GroupSerializer,
    PermissionSerializer,
)

logger = logging.getLogger(__name__)


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """User accounts viewset."""

    queryset = User.objects.all()

    def get_permissions(self):
        """Get permissions for the viewset."""
        if self.action == "create":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsUserOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "create": CreateUserSerializer,
            "set_profile": SetUserProfileSerializer,
        }.get(self.action, UserSerializer)

    @action(methods=["POST"], detail=False)
    def set_profile(self, request, pk=None):
        """Set a user's profile data."""
        serializer = self.get_serializer(self.request.user, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        datetime_time = datetime.datetime.fromtimestamp(time.time())
        logger.info(
            f"Profile update for user:  {self.request.user} on {datetime_time}(UTC)"
        )
        return Response(serializer.data)


class PermissionViewSet(viewsets.ModelViewSet):
    """CRUD for permissions."""

    pagination_class = None
    queryset = Permission.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = PermissionSerializer

    def get_queryset(self):
        """Get list of custom permissions."""
        queryset = Permission.objects.all()
        return queryset


class GroupViewSet(viewsets.ModelViewSet):
    """CRUD for groups (roles)."""

    pagination_class = None
    queryset = Group.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = GroupSerializer
