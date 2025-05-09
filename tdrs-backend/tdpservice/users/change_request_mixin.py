"""Extensions to the User model for change requests."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class UserChangeRequestMixin:
    """Mixin to add change request functionality to the User model."""

    def request_change(self, field_name, requested_value, requested_by=None):
        """Create a change request for this user.

        Args:
            field_name: The name of the field to change
            requested_value: The new value for the field
            requested_by: The user requesting the change (defaults to self)

        Returns:
            The created change request object
        """
        from .models import UserChangeRequest

        # Default to self if no requester specified
        if requested_by is None:
            requested_by = self

        # Get the current value
        try:
            current_value = str(getattr(self, field_name, ''))
        except (AttributeError, TypeError):
            current_value = ''

        # Create the change request
        change_request = UserChangeRequest.objects.create(
            user=self,
            requested_by=requested_by,
            field_name=field_name,
            current_value=current_value,
            requested_value=str(requested_value)
        )

        return change_request

    def get_pending_change_requests(self):
        """Get all pending change requests for this user."""
        from .models import UserChangeRequest, UserChangeRequestStatus

        return UserChangeRequest.objects.filter(
            user=self,
            status=UserChangeRequestStatus.PENDING
        )

    def has_pending_change_for_field(self, field_name):
        """Check if there's a pending change request for a specific field."""
        from .models import UserChangeRequest, UserChangeRequestStatus

        return UserChangeRequest.objects.filter(
            user=self,
            field_name=field_name,
            status=UserChangeRequestStatus.PENDING
        ).exists()
