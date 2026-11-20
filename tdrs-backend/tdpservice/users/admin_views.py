"""Bounded, read-only user queries for the admin console."""

from django.db.models import Count, Q, QuerySet

from rest_framework import permissions, serializers, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response

from tdpservice.users.authorization import is_authorized_admin_user
from tdpservice.users.models import AccountApprovalStatusChoices, User
from tdpservice.users.oidc import ADMIN_SESSION_SCOPE


class AdminUserPermission(permissions.BasePermission):
    """Retain Django's admin authorization for every read."""

    def has_permission(self, request: Request, view: object) -> bool:
        """Require an approved admin and an admin-scoped session."""
        return request.session.get(
            "session_scope"
        ) == ADMIN_SESSION_SCOPE and is_authorized_admin_user(request.user)


class AdminUserPagination(PageNumberPagination):
    """Keep even direct API requests bounded."""

    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class AdminUserSerializer(serializers.ModelSerializer):
    """Expose only fields needed by the read-only list and detail screens."""

    stt_name = serializers.CharField(source="stt.name", default=None, read_only=True)
    roles = serializers.SlugRelatedField(
        source="groups", slug_field="name", many=True, read_only=True
    )

    class Meta:
        """Explicitly exclude credentials and identity-provider identifiers."""

        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "account_approval_status",
            "stt_name",
            "roles",
            "is_active",
            "last_login",
            "date_joined",
            "access_requested_date",
        )
        read_only_fields = fields


class AdminUserQuerySerializer(serializers.Serializer):
    """Validate filters before building database queries."""

    search = serializers.CharField(required=False, allow_blank=True, max_length=150)
    status = serializers.ChoiceField(
        required=False, choices=AccountApprovalStatusChoices.choices
    )
    active = serializers.ChoiceField(required=False, choices=("true", "false"))


class AdminUserViewSet(viewsets.ReadOnlyModelViewSet):
    """Reference admin list/detail API, isolated from the public user API."""

    permission_classes = [AdminUserPermission]
    serializer_class = AdminUserSerializer
    pagination_class = AdminUserPagination
    queryset = User.objects.select_related("stt").prefetch_related("groups")
    filter_backends = []

    def get_queryset(self) -> QuerySet:
        """Apply allowlisted filters and stable ordering in the database."""
        queryset = self.queryset.order_by("last_name", "first_name", "id")
        if self.action != "list":
            return queryset
        query = AdminUserQuerySerializer(data=self.request.query_params)
        query.is_valid(raise_exception=True)
        filters = query.validated_data
        if search := filters.get("search"):
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        if approval_status := filters.get("status"):
            queryset = queryset.filter(account_approval_status=approval_status)
        if active := filters.get("active"):
            queryset = queryset.filter(is_active=active == "true")
        return queryset

    @action(detail=False, methods=["get"])
    def summary(self, request: Request) -> Response:
        """Aggregate counts without transferring user records."""
        return Response(
            User.objects.aggregate(
                total=Count("id"),
                approved=Count("id", filter=Q(account_approval_status="Approved")),
                access_requests=Count(
                    "id", filter=Q(account_approval_status="Access request")
                ),
                pending=Count("id", filter=Q(account_approval_status="Pending")),
            )
        )
