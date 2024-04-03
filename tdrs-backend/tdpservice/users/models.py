"""Define user model."""

import datetime
import logging
import uuid

from tdpservice.email.helpers.account_status import send_approval_status_update_email

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from tdpservice.stts.models import STT, Region

logger = logging.getLogger()


class AccountApprovalStatusChoices(models.TextChoices):
    """Enum of options for `account_approval_status`."""

    INITIAL = "Initial"
    ACCESS_REQUEST = "Access request"
    PENDING = "Pending"
    APPROVED = "Approved"
    DENIED = "Denied"
    DEACTIVATED = "Deactivated"

    # is "pending", "approved", and "denied" enough to cover functionality?


class User(AbstractUser):
    """Define user fields and methods."""

    class Meta:
        """Define meta user model attributes."""

        ordering = ['pk']

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    stt = models.ForeignKey(
        STT,
        on_delete=models.deletion.SET_NULL,
        related_name='users',
        null=True,
        blank=True
    )

    region = models.ForeignKey(
        Region,
        on_delete=models.deletion.SET_NULL,
        related_name='users',
        null=True,
        blank=True
    )

    # The unique `sub` UUID from decoded login.gov payloads for login.gov users.
    login_gov_uuid = models.UUIDField(
        editable=False, blank=True, null=True, unique=True
    )

    # Unique `hhsid` user claim for AMS OpenID users.
    # In the future, `TokenAuthorizationAMS.get_auth_options` will use `hhs_id` as the primary auth field.
    # See also: CustomAuthentication.py
    hhs_id = models.CharField(
        editable=False, max_length=12, blank=True, null=True, unique=True
    )

    # deprecated: use `account_approval_status`
    # Note this is handled differently than `is_active`, which comes from AbstractUser.
    # Django will totally prevent a user with is_active=True from authorizing.
    # This field `deactivated` helps us to notify the user client-side of their status
    # with an "Inactive Account" message.
    deactivated = models.BooleanField(
        _("deactivated"),
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
            "Designates whether this user account is active and approved to access TDP. "
            "Users in an approved state are allowed access."
        ),
    )

    access_requested_date = models.DateTimeField(default=datetime.datetime(year=1, month=1, day=1, hour=0, minute=0,
                                                                           second=0))

    _loaded_values = None
    _adding = True

    def __str__(self):
        """Return the username as the string representation of the object."""
        return self.username

    def is_in_group(self, group_name: str) -> bool:
        """Return whether or not the user is a member of the specified Group."""
        return self.groups.filter(name=group_name).exists()

    def validate_location(self):
        """Throw a validation error if a user has a location type incompatable with their role."""
        if self.region and self.stt:
            raise ValidationError(
                _("A user may only have a Region or STT assigned, not both.")
            )

        if self.groups.count() == 0 and (self.stt or self.region):
            return

        if (
            not (self.is_regional_staff or self.is_data_analyst or self.is_developer)
        ) and (self.stt or self.region):
            raise ValidationError(
                _(
                    "Users other than Regional Staff, Developers, Data Analysts do not get assigned a location"
                )
            )
        elif (
            self.is_regional_staff
            and self.stt
        ):
            raise ValidationError(
                _("Regional staff cannot have a location type other than region")
            )
        elif (
            self.is_data_analyst
            and self.region
        ):
            raise ValidationError(
                _("Data Analyst cannot have a location type other than stt")
            )

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
        return self.is_in_group("Data Analyst")

    @property
    def is_ocio_staff(self) -> bool:
        """Return whether or not the user is in the ACF OCIO Group."""
        return self.is_in_group("ACF OCIO")

    @property
    def is_ofa_sys_admin(self) -> bool:
        """Return whether or not the user is in the OFA System Admin Group."""
        return self.is_in_group("OFA System Admin")

    @property
    def is_digit_team(self) -> bool:
        """Return whether or not the user is in the DIGIT Team Group."""
        return self.is_in_group("DIGIT Team")

    @property
    def is_deactivated(self):
        """Check if the user's account status has been set to 'Deactivated'."""
        return self.account_approval_status == AccountApprovalStatusChoices.DEACTIVATED

    @property
    def location(self):
        """Return the STT or Region based on which is not null."""
        return self.stt if self.stt else self.region

    @classmethod
    def from_db(cls, db, field_names, values):
        """Override the django Model from_db method.

        Populates instances of User with a `_loaded_values` member,
        useful for accessing current values for the object before updates
        https://docs.djangoproject.com/en/4.1/ref/models/instances/#customizing-model-loading
        """
        instance = super().from_db(db, field_names, values)
        instance._adding = False
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    def save(self, *args, **kwargs):
        """Override the django Model save method.

        The existing values can be accessed using `self._loaded_values`
        which are set by `from_db`
        """
        if not self._adding:
            current_status = self._loaded_values["account_approval_status"]
            new_status = self.account_approval_status

            if new_status != current_status:
                """Send account status update emails after save."""

                super(User, self).save(*args, **kwargs)

                send_approval_status_update_email(
                    new_status,
                    self,
                    {
                        "first_name": self.first_name,
                        "stt_name": str(self.stt),
                        "group_permission": str(self.groups.first()),
                        "url": settings.FRONTEND_BASE_URL
                    }
                )

                return

        super(User, self).save(*args, **kwargs)
