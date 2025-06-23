"""Define API views for user class."""
import datetime
import logging

from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from tdpservice.users.models import User, Feedback, AccountApprovalStatusChoices
from tdpservice.users.permissions import DjangoModelCRUDPermissions, IsApprovedPermission, UserPermissions
from tdpservice.users.serializers import (
    GroupSerializer,
    UserProfileSerializer,
    UserSerializer,
    FeedbackSerializer,
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
        .prefetch_related("groups__permissions")

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "request_access": UserProfileSerializer,
        }.get(self.action, UserSerializer)

    def get_queryset(self):
        """Return the queryset based on user's group status."""
        queryset = None
        is_admin = self.request.user.groups.filter(name="OFA System Admin").exists()
        if is_admin:
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


class FeedbackViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Feedback viewset."""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = ()

    def retrieve(self, request, *args, **kwargs):
        """Return a specific feedback."""
        item = get_object_or_404(self.queryset, pk=pk)
        self.check_object_permissions(request, item)
        serializer = self.get_serializer_class()(item)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """List feedback by user."""
        admin = request.user.groups.filter(name__in=["OFA System Admin", "OFA Admin"]).exists()
        if admin:
            return super().list(request, *args, **kwargs)

        if request.user.is_anonymous:
            return Response()

        users_feedback = self.queryset.filter(user=request.user)
        page = self.paginate_queryset(users_feedback)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(users_feedback, many=True)
        return Response(serializer.data)

