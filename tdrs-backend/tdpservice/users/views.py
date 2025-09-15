"""Define API views for user class."""

import datetime
import logging

from django.contrib.auth.models import AnonymousUser, Group
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tdpservice.users.models import (
    User,
    AccountApprovalStatusChoices,
    UserChangeRequest,
    ChangeRequestAuditLog,
    Feedback,
)
from tdpservice.users.permissions import (
    CypressAdminAccountPermissions,
    DjangoModelCRUDPermissions,
    FeedbackPermissions,
    IsApprovedPermission,
    UserPermissions,
    IsOwnerOrAdmin
    )
from tdpservice.users.serializers import (
    FeedbackSerializer,
    GroupSerializer,
    UserProfileSerializer,
    UserSerializer,
    UserProfileChangeRequestSerializer,
    UserChangeRequestSerializer,
    ChangeRequestAuditLogSerializer
)

logger = logging.getLogger(__name__)


class UserViewSet(
    ListAPIView,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """User accounts viewset."""

    queryset = User.objects.select_related("stt").prefetch_related(
        "groups__permissions"
    )

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "request_access": UserProfileSerializer,
            "profile": UserProfileSerializer,
            "update_profile": UserProfileChangeRequestSerializer,
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
        if self.action in ["list", "retrieve"]:
            permission_classes = [
                IsAuthenticated,
                IsApprovedPermission,
                UserPermissions,
            ]
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
        serializer.save(
            account_approval_status=AccountApprovalStatusChoices.ACCESS_REQUEST,
            access_requested_date=datetime.datetime.now(),
        )
        logger.info(
            "Access request for user: %s on %s", self.request.user, timezone.now()
        )
        return Response(serializer.data)

    @action(methods=["GET"], detail=False)
    def profile(self, request):
        """Get the current user's profile."""
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data)

    @action(methods=["PATCH"], detail=False)
    def update_profile(self, request):
        """Update the current user's profile through change requests."""
        serializer = self.get_serializer(self.request.user, request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Check if any change requests were created
        user = self.request.user
        pending_requests = user.get_pending_change_requests()

        if pending_requests.exists():
            logger.info(
                "Change requests created for user: %s on %s", user, timezone.now()
            )
            # Return the updated serializer data with pending change request info
            return Response({
                'user': self.get_serializer(user).data,
                'message': 'Your requested changes have been submitted for approval.',
                'pending_requests': pending_requests.count()
            })

        return Response(serializer.data)


class CypressAdminUserViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """User accounts viewset for Cypress test updates."""

    queryset = User.objects.select_related("stt").prefetch_related(
        "groups__permissions"
    )
    permission_classes = [
        IsAuthenticated,
        IsApprovedPermission,
        CypressAdminAccountPermissions,
    ]
    serializer_class = UserSerializer

    def set_status(self, pk, approval_status):
        """Update the user with the provided approval status."""
        u = get_object_or_404(self.queryset, pk=pk)
        u.account_approval_status = approval_status
        u.save()
        return Response(status=status.HTTP_200_OK)

    @action(methods=["PATCH"], detail=True)
    def set_initial(self, request, pk):
        """Update user with initial approval status."""
        return self.set_status(pk, AccountApprovalStatusChoices.INITIAL)

    @action(methods=["PATCH"], detail=True)
    def set_pending(self, request, pk):
        """Update user with pending approval status."""
        return self.set_status(pk, AccountApprovalStatusChoices.PENDING)

    @action(methods=["PATCH"], detail=True)
    def set_approved(self, request, pk):
        """Update user with approved status."""
        return self.set_status(pk, AccountApprovalStatusChoices.APPROVED)


class GroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """GET for groups (roles)."""

    pagination_class = None
    queryset = Group.objects.all()
    permission_classes = [DjangoModelCRUDPermissions, IsApprovedPermission]
    serializer_class = GroupSerializer


class UserChangeRequestViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for user change requests."""

    serializer_class = UserChangeRequestSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        if user.is_ofa_sys_admin:
            return UserChangeRequest.objects.all()

        return UserChangeRequest.objects.filter(user=user)

    def perform_create(self, serializer):
        """Set user to current user if not specified."""
        data = serializer.validated_data
        if 'user' not in data:
            data['user'] = self.request.user
        serializer.save()

class ChangeRequestAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for change request audit logs."""

    serializer_class = ChangeRequestAuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only allow admins to access audit logs."""
        user = self.request.user
        if not user.is_ofa_sys_admin:
            return ChangeRequestAuditLog.objects.none()
        return ChangeRequestAuditLog.objects.all()

class FeedbackViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Feedback viewset."""

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (FeedbackPermissions,)

    def post(self, request, *args, **kwargs):
        """Create feedback with user."""
        response = self.create(request, *args, **kwargs)
        if response.status_code != status.HTTP_201_CREATED:
            return response

        try:
            feedback_id = response.data["id"]
            feedback = Feedback.objects.get(id=feedback_id)

            # Force anonymity if user is None to prevent us from know if authenticated users chose to remain anonymous
            if request.user is None or isinstance(request.user, AnonymousUser):
                feedback.anonymous = True

            if not feedback.anonymous:
                feedback.user = request.user
            feedback.save()
        except ObjectDoesNotExist:
            logger.exception(
                "Failed to update the user field on the Feedback model because it does not exist."
            )
        finally:
            return response
