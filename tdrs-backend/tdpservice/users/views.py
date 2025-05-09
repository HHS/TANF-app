"""Define API views for user class."""
import datetime
import logging

from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from tdpservice.users.models import User, AccountApprovalStatusChoices, UserChangeRequest, ChangeRequestAuditLog
from tdpservice.users.permissions import DjangoModelCRUDPermissions, IsApprovedPermission, UserPermissions
from tdpservice.users.serializers import (
    GroupSerializer,
    UserProfileSerializer,
    UserSerializer,
    UserChangeRequestSerializer,
    AdminChangeRequestSerializer,
    ChangeRequestAuditLogSerializer
)
from tdpservice.users.serializers import UserProfileChangeRequestSerializer

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

    @action(methods=["GET"], detail=False)
    def profile(self, request):
        """Get the current user's profile."""
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data)

    @action(methods=["PATCH"], detail=False)
    def update_profile(self, request):
        """Update the current user's profile through change requests."""
        print("\n\nIn update_profile\n\n")
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


class GroupViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """GET for groups (roles)."""

    pagination_class = None
    queryset = Group.objects.all()
    permission_classes = [DjangoModelCRUDPermissions, IsApprovedPermission]
    serializer_class = GroupSerializer


class IsOwnerOrAdmin(BasePermission):
    """Permission to only allow owners of a change request or admins to view it."""

    def has_object_permission(self, request, view, obj):
        """Check if user is owner or admin."""
        if request.user.is_ofa_sys_admin:
            return True

        # Allow owners
        return obj.user == request.user


class UserChangeRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for user change requests."""

    serializer_class = UserChangeRequestSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        """Filter queryset based on user permissions."""
        user = self.request.user
        # Admins can see all change requests
        if user.is_an_admin or user.is_ofa_sys_admin:
            return UserChangeRequest.objects.all()
        # Regular users can only see their own
        return UserChangeRequest.objects.filter(user=user)

    def perform_create(self, serializer):
        """Set user to current user if not specified."""
        data = serializer.validated_data
        if 'user' not in data:
            data['user'] = self.request.user
        serializer.save()


class AdminChangeRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for admin management of change requests."""

    serializer_class = AdminChangeRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'user', 'field_name']

    def get_queryset(self):
        """Only allow admins to access this viewset."""
        user = self.request.user
        if not (user.is_an_admin or user.is_ofa_sys_admin):
            return UserChangeRequest.objects.none()
        return UserChangeRequest.objects.all()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a change request."""
        change_request = self.get_object()
        if change_request.status != 'pending':
            return Response(
                {'detail': 'This change request has already been processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notes = request.data.get('notes', '')
        success = change_request.approve(request.user, notes)

        if success:
            # Create audit log entry
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action='approved',
                performed_by=request.user,
                details={
                    'field': change_request.field_name,
                    'new_value': change_request.requested_value,
                    'api_action': True
                }
            )

            return Response({'status': 'approved'}, status=status.HTTP_200_OK)
        return Response(
            {'detail': 'Could not approve change request.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a change request."""
        change_request = self.get_object()
        if change_request.status != 'pending':
            return Response(
                {'detail': 'This change request has already been processed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        notes = request.data.get('notes', '')
        success = change_request.reject(request.user, notes)

        if success:
            # Create audit log entry
            ChangeRequestAuditLog.objects.create(
                change_request=change_request,
                action='rejected',
                performed_by=request.user,
                details={
                    'field': change_request.field_name,
                    'api_action': True
                }
            )

            return Response({'status': 'rejected'}, status=status.HTTP_200_OK)
        return Response(
            {'detail': 'Could not reject change request.'},
            status=status.HTTP_400_BAD_REQUEST
        )


class ChangeRequestAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for change request audit logs."""

    serializer_class = ChangeRequestAuditLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Only allow admins to access audit logs."""
        user = self.request.user
        if not (user.is_an_admin or user.is_ofa_sys_admin):
            return ChangeRequestAuditLog.objects.none()
        return ChangeRequestAuditLog.objects.all()
