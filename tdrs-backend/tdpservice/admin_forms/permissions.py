"""Permissions for React admin form endpoints."""

from rest_framework import permissions

from tdpservice.users.authorization import is_authorized_admin_user
from tdpservice.users.oidc import ADMIN_SESSION_SCOPE


class IsAdminConsoleFormUser(permissions.BasePermission):
    """Allow React admin form access only for admin-scoped Django superusers."""

    message = "User is not authorized for this admin form workflow."

    def has_permission(self, request, view):
        """Return whether the request may use React admin form endpoints."""
        return (
            request.session.get("session_scope") == ADMIN_SESSION_SCOPE
            and is_authorized_admin_user(request.user)
        )
