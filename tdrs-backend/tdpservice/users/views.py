"""Define API views for user class."""
import logging
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.apps import AppConfig

from .models import User
from .permissions import IsAdmin, IsUserOrReadOnly
from django.utils import timezone
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

    @action(methods=["GET"],detail = False)
    def no_roles(self,request, pk = None):
        """Get a list of all users that do not belong to a group"""
        serializer = self.get_serializer(data=User.get_groupless(),many=True)
        return Response(serializer.data)

    @action(methods=["POST"], detail=False)
    def set_profile(self, request, pk=None):
        """Set a user's profile data."""
        serializer = self.get_serializer(self.request.user, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        logger.info(
            "Profile update for user: %s on %s", self.request.user, timezone.now()
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
