"""Define user model."""

import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models


class User(AbstractUser):
    """Define user fields and methods."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    def __str__(self):
        """Return the username as the string representation of the object."""
        return self.username

    @property
    def is_admin(self):
        """Check if the user is an admin."""
        # TODO: Probably better to change this to check for a permission
        # rather than the admin group directly.
        return self.is_superuser or Group.objects.get(name="admin") in self.groups.all()


class TDRSAdmin(models.Model):
    """Define model for custom admin permission."""

    class Meta:
        permissions = [("tdrs_can_admin", "Can Admin Applicable STT")]


class TDRSRead(models.Model):
    """Define model for custom read permission."""

    class Meta:
        permissions = [("tdrs_can_read_data", "Can Read STT Data")]


class TDRSEdit(models.Model):
    """Define model for custom edit permission."""

    class Meta:
        permissions = [("tdrs_can_edit_data", "Can Prepare STT Data")]
