"""Define user model."""

import uuid

from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from tdpservice.stts.models import STT, Region
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Define user fields and methods."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stt = models.ForeignKey(STT, on_delete=models.CASCADE, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)

    # Note this is handled differently than `is_active`, which comes from AbstractUser.
    # Django will totally prevent a user with is_active=True from authorizing.
    # This field `deactivated` helps us to notify the user client-side of their status
    # with an "Inactive Account" message.
    deactivated = models.BooleanField(
        _('deactivated'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    def __str__(self):
        """Return the username as the string representation of the object."""
        return self.username

    @property
    def is_admin(self):
        """Check if the user is an admin."""
        return (
            self.is_superuser
            or Group.objects.get(name="OFA Admin") in self.groups.all()
        )
