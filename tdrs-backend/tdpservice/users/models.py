"""Define user model."""

import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from tdpservice.stts.models import STT, Region
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


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

    def save(self, *args, **kwargs):
        """Prevent save if attributes are not necessary for a user given their role."""
        if self.is_regional_staff and self.stt:
            raise ValidationError(
                _("Regional staff cannot have an sst assigned to them"))
        elif self.is_data_analyst and self.region:
            raise ValidationError(
                _("Data Analyst cannot have a region assigned to them"))
        super().save(*args, **kwargs)

    @property
    def is_regional_staff(self) -> bool:
        """Return whether or not the user is in the OFA Regional Staff Group.

        Uses a cached_property to prevent repeated calls to the database.
        """
        return self.is_in_group("OFA Regional Staff")

    @property
    def is_data_analyst(self) -> bool:
        """Return whether or not the user is in the Data Analyst Group.

        Uses a cached_property to prevent repeated calls to the database.
        """
        return self.is_in_group('Data Analyst')
