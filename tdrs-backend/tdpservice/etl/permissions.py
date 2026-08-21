"""Permissions for ETL pipeline APIs."""

from rest_framework import permissions

from tdpservice.users.models import AccountApprovalStatusChoices


class ETLPermissions(permissions.BasePermission):
    """Allow approved operational users to inspect and run ETL pipelines."""

    def has_permission(self, request, view):
        """Return whether the user can access the ETL API action."""
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.account_approval_status != AccountApprovalStatusChoices.APPROVED:
            return False

        action = getattr(view, "action", None)
        if action in ("create", "retry"):
            return user.is_ofa_sys_admin

        return user.is_ofa_sys_admin or user.is_digit_team

    def has_object_permission(self, request, view, obj):
        """Apply the same group-level rules to run detail access."""
        return self.has_permission(request, view)
