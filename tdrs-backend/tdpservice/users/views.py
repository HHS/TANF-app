"""Define API views for user class."""
import logging

from django.contrib.auth.models import Group
from django.utils import timezone

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tdpservice.users.models import User, AccountApprovalStatusChoices
from tdpservice.users.permissions import DjangoModelCRUDPermissions, UserPermissions
from tdpservice.users.serializers import (
    GroupSerializer,
    UserProfileSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """User accounts viewset."""

    permission_classes = [IsAuthenticated, UserPermissions]
    queryset = User.objects\
        .select_related("location_type")\
        .prefetch_related("groups__permissions")

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "set_profile": UserProfileSerializer,
            "request_access": UserProfileSerializer,
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

    @action(methods=["PATCH"], detail=False)
    def request_access(self, request, pk=None):
        """Update request.user with provided data, set `account_approval_status` to 'Access Request'."""
        serializer = self.get_serializer(self.request.user, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(account_approval_status=AccountApprovalStatusChoices.ACCESS_REQUEST)
        logger.info(
            "Access request for user: %s on %s", self.request.user, timezone.now()
        )
        return Response(serializer.data)


class GroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """GET for groups (roles)."""

    pagination_class = None
    queryset = Group.objects.all()
    permission_classes = [DjangoModelCRUDPermissions]
    serializer_class = GroupSerializer
