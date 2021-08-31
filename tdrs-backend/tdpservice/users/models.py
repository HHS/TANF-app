"""Define user model."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.functional import cached_property
from tdpservice.stts.models import STT, Region
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Define user fields and methods."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stt = models.ForeignKey(STT, on_delete=models.CASCADE, blank=True, null=True)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, blank=True, null=True)

    # The unique `sub` UUID from decoded login.gov payloads.
    login_gov_uuid = models.UUIDField(editable=False,
                                      blank=True,
                                      null=True,
                                      unique=True)

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

    def is_in_group(self, group_name: str) -> bool:
        """Return whether or not the user is a member of the specified Group."""
        return self.groups.filter(name=group_name).exists()

    @cached_property
    def is_data_analyst(self) -> bool:
        """Return whether or not the user is in the Data Analyst Group.

        Uses a cached_property to prevent repeated calls to the database.
        """
        return self.is_in_group('Data Analyst')
