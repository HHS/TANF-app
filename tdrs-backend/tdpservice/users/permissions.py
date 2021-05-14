"""Set permissions for users."""

from rest_framework import permissions


def is_own_stt(request, view):
    """Verify user belongs to requested STT."""
    return is_in_group(request.user, "Data Prepper") and (
        request.user.stt.id == request.data['stt']
    )


def is_in_group(user, group_name):
    """Take a user and a group name, and returns `True` if the user is in that group."""
    return user.groups.filter(name=group_name).exists()


class IsUser(permissions.BasePermission):
    """Object-level permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        """Check if user has required permissions."""
        return obj == request.user


class IsAdmin(permissions.BasePermission):
    """Permission for admin-only views."""

    def has_object_permission(self, request, view, obj):
        """Check if a user is admin or superuser."""
        return request.user.is_authenticated and request.user.is_admin

    def has_permission(self, request, view):
        """Check if a user is admin or superuser."""
        return request.user.is_authenticated and request.user.is_admin


class IsOFAAdmin(permissions.BasePermission):
    """Permission for OFA Analyst only views."""

    def has_permission(self, request, view):
        """Check if a user is a OFA Admin."""
        return is_in_group(request.user, "OFA Admin")


class IsDataPrepper(permissions.BasePermission):
    """Permission for Data Prepper only views."""

    def has_permission(self, request, view):
        """Check if a user is a data prepper."""
        return is_in_group(request.user, "Data Prepper")


class CanUploadReport(permissions.BasePermission):
    """Permission for report uploads."""

    def has_permission(self, request, view):
        """
        Check if a user is a data prepper or an admin.

        If they are a data prepper, ensures the STT is their own.
        """
        return is_in_group(request.user, "OFA Admin") or is_own_stt(request, view)
