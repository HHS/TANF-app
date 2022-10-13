"""Define user model."""

import logging
import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger()

class AccountApprovalStatusChoices(models.TextChoices):
    """Enum of options for `account_approval_status`."""

    INITIAL = 'Initial'
    ACCESS_REQUEST = 'Access request'
    PENDING = 'Pending'
    APPROVED = 'Approved'
    DENIED = 'Denied'
    DEACTIVATED = 'Deactivated'

    # is "pending", "approved", and "denied" enough to cover functionality?

class User(AbstractUser):
    """Define user fields and methods."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    limit = models.Q(app_label='stts', model='stt') | models.Q(app_label='stts', model='region')

    location_id = models.PositiveIntegerField(null=True, blank=True)
    location_type = models.ForeignKey(ContentType,
                                      on_delete=models.CASCADE,
                                      null=True, blank=True,
                                      limit_choices_to=limit)
    location = GenericForeignKey('location_type', 'location_id')

    # The unique `sub` UUID from decoded login.gov payloads for login.gov users.
    login_gov_uuid = models.UUIDField(editable=False,
                                      blank=True,
                                      null=True,
                                      unique=True)

    # Unique `hhsid` user claim for AMS OpenID users.
    # In the future, `TokenAuthorizationAMS.get_auth_options` will use `hhs_id` as the primary auth field.
    # See also: CustomAuthentication.py
    hhs_id = models.CharField(editable=False,
                              max_length=12,
                              blank=True,
                              null=True,
                              unique=True)

    # deprecated: use `account_approval_status`
    # Note this is handled differently than `is_active`, which comes from AbstractUser.
    # Django will totally prevent a user with is_active=True from authorizing.
    # This field `deactivated` helps us to notify the user client-side of their status
    # with an "Inactive Account" message.
    deactivated = models.BooleanField(
        _('deactivated'),
        default=False,
        help_text=_(
            'Deprecated: use Account Approval Status instead - '
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    # deprecated: use `account_approval_status` instead
    # This shows access request has been submitted and needs approval. When flag is True, Admin
    # sees the request and has to assign user to group
    access_request = models.BooleanField(
        default=False,
        help_text=_(
            'Deprecated: use Account Approval Status instead - '
            'Designates whether this user account has requested access to TDP. '
            'Users with this checked must have groups assigned for the application to work correctly.'
        ),
    )

    # replaces the deprecated `access_request` and `deactivated` fields above
    # Designate an account's approval status. options: INITIAL, ACCESS_REQUEST, PENDING, APPROVED, DENIED, DEACTIVATED
    # property `is_deactivated` below returns True if `account_approval_status` is `DEACTIVATED`
    account_approval_status = models.CharField(
        max_length=40,
        choices=AccountApprovalStatusChoices.choices,
        default=AccountApprovalStatusChoices.INITIAL,
        help_text=_(
            'Designates whether this user account is active and approved to access TDP. '
            'Users in an approved state are allowed access.'
        )
    )

    def __str__(self):
        """Return the username as the string representation of the object."""
        return self.username

    def is_in_group(self, group_name: str) -> bool:
        """Return whether or not the user is a member of the specified Group."""
        return self.groups.filter(name=group_name).exists()

    def validate_location(self):
        """Throw a validation error if a user has a location type incompatable with their role."""
        if (not (self.is_regional_staff or self.is_data_analyst or self.is_developer)) and self.location:
            raise ValidationError(
                _("Users other than Regional Staff, Developers, Data Analysts do not get assigned a location"))
        elif self.is_regional_staff and self.location_type and self.location_type.model != 'region':
            raise ValidationError(
                _("Regional staff cannot have a location type other than region"))
        elif self.is_data_analyst and self.location_type and self.location_type.model != 'stt':
            raise ValidationError(
                _("Data Analyst cannot have a location type other than stt"))

    def clean(self, *args, **kwargs):
        """Prevent save if attributes are not necessary for a user given their role."""
        super().clean(*args, **kwargs)
        self.validate_location()

    @property
    def is_developer(self) -> bool:
        """Return whether or not the user is in the OFA Regional Staff Group."""
        return self.is_in_group("Developer")

    @property
    def is_regional_staff(self) -> bool:
        """Return whether or not the user is in the OFA Regional Staff Group."""
        return self.is_in_group("OFA Regional Staff")

    @property
    def is_data_analyst(self) -> bool:
        """Return whether or not the user is in the Data Analyst Group."""
        return self.is_in_group('Data Analyst')

    @property
    def is_ocio_staff(self) -> bool:
        """Return whether or not the user is in the ACF OCIO Group."""
        return self.is_in_group('ACF OCIO')

    @property
    def stt(self):
        """Return the location if the location is an STT."""
        if self.location and self.location_type.model == 'stt':
            return self.location
        else:
            return None

    @stt.setter
    def stt(self, value):
        if self.is_regional_staff:
            raise ValidationError(
                _("Regional staff cannot have an sst assigned to them"))
        self.location = value

    @property
    def region(self):
        """Return the location if the location is a Region."""
        if self.location and self.location_type.model == 'region':
            return self.location
        else:
            return None

    @region.setter
    def region(self, value):
        if self.is_data_analyst:
            raise ValidationError(
                _("Data Analyst cannot have a region assigned to them"))
        self.location = value

    @property
    def is_deactivated(self):
        """Check if the user's account status has been set to 'Deactivated'."""
        return self.account_approval_status == AccountApprovalStatusChoices.DEACTIVATED
