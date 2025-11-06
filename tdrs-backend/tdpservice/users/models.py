"""Define user model."""

import ast
import datetime
import logging
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from tdpservice.email.helpers.account_status import send_approval_status_update_email
from tdpservice.email.helpers.profile_change_request import (
    send_change_request_status_email,
)
from tdpservice.stts.models import STT, Region
from tdpservice.users.mixins import ReviewerMixin as Reviewable

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


class RegionMeta(models.Model):
    """Meta data model representing the relationship between a Region and a User."""

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="region_metas"
    )
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="region_metas"
    )


class UserChangeRequestStatus(models.TextChoices):
    """Enum of options for change request status."""

    PENDING = "pending", _("Pending")
    APPROVED = "approved", _("Approved")
    REJECTED = "rejected", _("Rejected")


class UserChangeRequest(Reviewable):
    """Model to track user information change requests."""

    class Meta:
        """Define meta attributes."""

        ordering = ["-requested_at"]
        verbose_name = _("User Change Request")
        verbose_name_plural = _("User Change Requests")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="change_requests"
    )
    requested_by = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="requested_changes"
    )
    field_name = models.CharField(
        max_length=100,
        help_text=_(
            "The name of the field being changed, possible values include: first_name, last_name, regions and has_fra_access"
        ),
    )
    current_value = models.TextField(
        blank=True, help_text=_("The current value of the field")
    )
    requested_value = models.TextField(
        blank=True, help_text=_("The requested new value for the field")
    )
    status = models.CharField(
        max_length=20,
        choices=UserChangeRequestStatus.choices,
        default=UserChangeRequestStatus.PENDING,
        help_text=_("The current status of this change request"),
    )
    requested_at = models.DateTimeField(
        auto_now_add=True, help_text=_("When this change was requested")
    )
    reviewed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_changes",
        help_text=_("The admin who reviewed this change request"),
    )
    notes = models.TextField(
        blank=True, help_text=_("Admin notes on approval/rejection")
    )

    def __str__(self):
        """Return string representation."""
        return f"{self.user.username} - {self.field_name} - {self.get_status_display()}"

    def __apply_change(self, user, field_name, new_value):
        """Apply the change to the user."""
        if field_name == "regions":
            field_name = None
            user.regions.remove(*user.regions.all())  # Clear existing regions
            regions = ast.literal_eval(new_value)
            for region in regions:
                user.regions.add(region)
        elif field_name == "has_fra_access":
            field_name = None
            fra_permission = Permission.objects.get(codename="has_fra_access")
            if new_value == "True":
                user.user_permissions.add(fra_permission)
            else:
                user.user_permissions.remove(fra_permission)
        elif field_name == "stt":
            stt = STT.objects.get(id=new_value)
            user.stt = stt
        else:
            setattr(user, field_name, new_value)
        return field_name

    def approve(self, admin_user, notes=None):
        """Approve the change request and apply changes to the user."""
        if self.status != UserChangeRequestStatus.PENDING:
            return False

        user = self.user
        field_name = self.field_name
        new_value = self.requested_value

        # Apply the change to the user
        updated_fields = []
        try:
            updated_field = self.__apply_change(user, field_name, new_value)
            if updated_field:
                updated_fields.append(updated_field)
        except Region.DoesNotExist:
            logger.error("Region not found: %s", new_value)
            return False
        except Permission.DoesNotExist:
            logger.error("Permission not found: %s", new_value)
            return False
        if updated_fields:
            user.save(updated_fields=updated_fields)

        # Update the change request
        self.status = UserChangeRequestStatus.APPROVED
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        if notes:
            self.notes = notes
        self.save()

        # Send email
        try:
            send_change_request_status_email(
                self, isApproved=True, url=settings.FRONTEND_BASE_URL
            )

        except Exception as e:
            logger.exception(
                "Failed to send a, UserChangeRequestpproval email for profile change request %s: %s",
                self.id,
                e,
            )

        return True

    def reject(self, admin_user, notes=None):
        """Reject the change request."""
        if self.status != UserChangeRequestStatus.PENDING:
            return False

        # Update the change request
        self.status = UserChangeRequestStatus.REJECTED
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        if notes:
            self.notes = notes
        self.save()

        # Send email
        try:
            send_change_request_status_email(
                self, isApproved=False, url=settings.FRONTEND_BASE_URL
            )
        except Exception as e:
            logger.exception(
                "Failed to send rejection email for profile change request %s: %s",
                self.id,
                e,
            )

        return True


class ChangeRequestAuditLog(models.Model):
    """Model to track audit logs for change requests."""

    class Meta:
        """Define meta attributes."""

        ordering = ["-timestamp"]
        verbose_name = _("Change Request Audit Log")
        verbose_name_plural = _("Change Request Audit Logs")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    change_request = models.ForeignKey(
        UserChangeRequest, on_delete=models.CASCADE, related_name="audit_logs"
    )
    action = models.CharField(
        max_length=50, help_text=_("The action performed (created, approved, rejected)")
    )
    performed_by = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="change_request_actions",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, help_text=_("When this action was performed")
    )
    details = models.JSONField(
        default=dict, help_text=_("Additional details about the action")
    )

    def __str__(self):
        """Return string representation."""
        return f"{self.action} by {self.performed_by} at {self.timestamp}"


class UserChangeRequestMixin:
    """Mixin to add change request functionality to the User model."""

    def request_change(
        self, field_name, requested_value, requested_by=None, current_value=None
    ):
        """Create a change request for this user."""
        # Default to self if no requester specified
        if requested_by is None:
            requested_by = self

        # Get the current value
        if current_value is None:
            try:
                if Permission.objects.filter(codename=field_name).exists():
                    current_value = self.user_permissions.filter(
                        codename=field_name
                    ).exists()
                else:
                    current_value = getattr(self, field_name, "")
            except (AttributeError, TypeError):
                current_value = ""

        # Create the change request
        change_request = UserChangeRequest.objects.create(
            user=self,
            requested_by=requested_by,
            field_name=field_name,
            current_value=str(current_value),
            requested_value=str(requested_value),
        )

        return change_request

    def get_pending_change_requests(self):
        """Get all pending change requests for this user."""
        return UserChangeRequest.objects.filter(
            user=self, status=UserChangeRequestStatus.PENDING
        )

    def has_pending_change_for_field(self, field_name):
        """Check if there's a pending change request for a specific field."""
        return UserChangeRequest.objects.filter(
            user=self, field_name=field_name, status=UserChangeRequestStatus.PENDING
        ).exists()


class Rating(models.IntegerChoices):
    """Likert like rating scale."""

    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    VERY_GOOD = 5


class FeedbackAttachment(models.Model):
    """Generic many-to-many attachment between DataFile and any model."""

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.IntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    feedback = models.ForeignKey(
        "users.Feedback", on_delete=models.CASCADE, related_name="attachments"
    )

    attached_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Meta model attributes."""

        unique_together = ("content_type", "object_id", "feedback")

    def __str__(self):
        """Convert to string representation."""
        return f"{self.feedback} attached to {self.content_object}"


class Feedback(Reviewable):
    """Model to capture and review user feedback."""

    class Meta:
        """Meta feedback model attributes."""

        ordering = ["created_at"]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        related_name="feedback",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    rating = models.IntegerField(choices=Rating.choices)

    feedback = models.TextField(null=True, blank=True)

    anonymous = models.BooleanField(default=False)

    acked = models.BooleanField(default=False, verbose_name="Marked as read")

    # --- Metadata for fields ---
    page_url = models.URLField(blank=True, null=True)
    feedback_type = models.CharField(max_length=30, blank=True, null=True)
    component = models.CharField(max_length=100, blank=True)
    widget_id = models.CharField(max_length=100, blank=True)

    def __str__(self):
        """Return a string representation of the object."""
        return (
            f"User: {self.user.username if self.user is not None else 'Anonymous'} - "
            f"Rating: {self.rating} - Acked: {self.acked}"
        )

    def attached_data_files(self):
        """Return a list of attached data files."""
        from tdpservice.data_files.models import DataFile

        return [
            a.content_object
            for a in self.attachments.all()
            if isinstance(a.content_object, DataFile)
        ]

    def acknowledge(self, admin_user):
        """Acknowledge the feedback."""
        if self.acked:
            return False

        self.acked = True
        self.reviewed_at = timezone.now()
        self.reviewed_by = admin_user
        self.save()
        return True


class User(AbstractUser, UserChangeRequestMixin):
    """Define user fields and methods."""

    class Meta:  # type: ignore[overrride]
        """Define meta user model attributes."""

        ordering = ["pk"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    stt = models.ForeignKey(
        STT,
        on_delete=models.deletion.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    regions = models.ManyToManyField(
        Region,
        through=RegionMeta,
        help_text="Regions this user is associated with.",
        related_name="regions",
        blank=True,
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
            "Deprecated: use Account Approval Status instead - "
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    # deprecated: use `account_approval_status` instead
    # This shows access request has been submitted and needs approval. When flag is True, Admin
    # sees the request and has to assign user to group
    access_request = models.BooleanField(
        default=False,
        help_text=_(
            "Deprecated: use Account Approval Status instead - "
            "Designates whether this user account has requested access to TDP. "
            "Users with this checked must have groups assigned for the application to work correctly."
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

    access_requested_date = models.DateTimeField(
        default=datetime.datetime(year=1, month=1, day=1, hour=0, minute=0, second=0)
    )

    _loaded_values = None
    _adding = True

    feature_flags = models.JSONField(
        default=dict,
        help_text="Feature flags for this user. This is a JSON field that can be used to store key-value pairs. "
        + 'E.g: {"some_feature": true}',
        blank=True,
    )

    def __str__(self):
        """Return the username as the string representation of the object."""
        return self.username

    def is_in_group(self, group_names: str | list[str]) -> bool:
        """Return whether or not the user is a member of the specified Group(s)."""
        if type(group_names) == str:
            group_names = [group_names]
        return self.groups.filter(name__in=group_names).exists()

    def validate_location(self):
        """Throw a validation error if a user has a location type incompatable with their role."""
        regional = self.regions.count()
        if regional and self.stt:
            raise ValidationError(
                _("A user may only have a Region or STT assigned, not both.")
            )

        if self.groups.count() == 0 and (self.stt or regional):
            return

        if (
            not (self.is_regional_staff or self.is_data_analyst or self.is_developer)
        ) and (self.stt or regional):
            raise ValidationError(
                _(
                    "Users other than Regional Staff, Developers, Data Analysts do not get assigned a location"
                )
            )
        elif self.is_regional_staff and self.stt:
            raise ValidationError(
                _("Regional staff cannot have a location type other than region")
            )
        elif self.is_data_analyst and regional:
            raise ValidationError(
                _("Data Analyst cannot have a location type other than stt")
            )

    def clean(self, *args, **kwargs):
        """Prevent save if attributes are not necessary for a user given their role."""
        super().clean(*args, **kwargs)
        self.validate_location()

    @property
    def has_fra_access(self) -> bool:
        """Return whether or not the user has FRA access."""
        return self.has_perm("users.has_fra_access")

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
    def is_an_admin(self) -> bool:
        """Return whether or not the user is in the OFA Admin Group or OFA System Admin."""
        return self.is_in_group(["OFA Admin", "OFA System Admin"])

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
        return self.stt if self.stt else self.regions.all()

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
        # kwargs are passed via the serializer. Kwargs that do not exist in the base model must be removed befor the
        # call to super(User, self).save(*args, **kwargs) below.
        regions = kwargs.pop("regions", [])
        updated_fields = kwargs.pop("updated_fields", None)

        if not self._adding:
            if self._loaded_values is None:
                raise RuntimeError(
                    "Expects `_loaded_values` to be set by `from_db()` before "
                    "calling `save()`."
                )

            current_status = self._loaded_values["account_approval_status"]
            new_status = self.account_approval_status

            if new_status != current_status:
                """Send account status update emails after save."""

                super(User, self).save(*args, **kwargs)

                for region in regions:
                    self.regions.add(region)

                send_approval_status_update_email(
                    new_status,
                    self,
                    {
                        "first_name": self.first_name,
                        "stt_name": str(self.stt) if self.stt else None,
                        "group_permission": str(self.groups.first()),
                        "url": settings.FRONTEND_BASE_URL,
                    },
                )

                return

        logger.debug("------------ updated_fields: %s", updated_fields)
        if updated_fields and isinstance(updated_fields, list):
            super(User, self).save(update_fields=updated_fields, *args, **kwargs)
        else:
            super(User, self).save(*args, **kwargs)
