"""Define API views for user class."""
import datetime
import logging

from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from tdpservice.users.models import User, AccountApprovalStatusChoices
from tdpservice.users.permissions import DjangoModelCRUDPermissions, IsApprovedPermission, UserPermissions
from tdpservice.users.serializers import (
    GroupSerializer,
    UserProfileSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class UserViewSet(
    ListAPIView,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """User accounts viewset."""

    queryset = User.objects\
        .select_related("stt")\
        .select_related("region")\
        .prefetch_related("groups__permissions")

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "request_access": UserProfileSerializer,
        }.get(self.action, UserSerializer)

    def get_queryset(self):
        """Return the queryset based on user's group status."""
        queryset = None
        # This is not a great way to make sure regional users can access what they need. This should be revisited.
        is_admin = self.request.user.groups.filter(name="OFA System Admin").exists()
        is_regional = self.request.user.groups.filter(name="OFA Regional Staff").exists()
        if is_admin or is_regional:
            queryset = self.queryset
        else:
            queryset = self.queryset.filter(id=self.request.user.id)
        return queryset

    def get_permissions(self):
        """Determine the permissions to apply based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAuthenticated, IsApprovedPermission, UserPermissions]
        else:
            permission_classes = [IsAuthenticated, UserPermissions]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, pk=None):
        """Return a specific user."""
        item = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(request, item)
        serializer = self.get_serializer_class()(item)
        return Response(serializer.data)

    @action(methods=["GET", "PATCH"], detail=False)
    def request_access(self, request):
        """Update request.user with provided data, set `account_approval_status` to 'Access Request'."""
        if request.method == "GET":
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        serializer = self.get_serializer(self.request.user, request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(account_approval_status=AccountApprovalStatusChoices.ACCESS_REQUEST,
                        access_requested_date=datetime.datetime.now())
        logger.info(
            "Access request for user: %s on %s", self.request.user, timezone.now()
        )
        return Response(serializer.data)


class GroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """GET for groups (roles)."""

    pagination_class = None
    queryset = Group.objects.all()
    permission_classes = [DjangoModelCRUDPermissions, IsApprovedPermission]
    serializer_class = GroupSerializer
