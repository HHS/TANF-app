"""Core models."""

import uuid

from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.db import models
from django.db.models.signals import post_delete, post_migrate, post_save
from django.dispatch import receiver

from simple_history import register
from simple_history.models import HistoricalRecords

# Register Django Group models for change tracking
register(Group, app=__package__, m2m_fields=["permissions"])


class BaseLogQuerySet(models.QuerySet):
    """QuerySet helpers shared by concrete log models."""

    def for_object(self, obj):
        """Return logs attached to a model instance through the generic relation."""
        return self.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=str(obj.pk),
        )


class BaseLogManager(models.Manager.from_queryset(BaseLogQuerySet)):
    """Manager for models that inherit from BaseLog."""

    def create_for_object(self, obj, **kwargs):
        """Create a log attached to a model instance through the generic relation."""
        kwargs["content_type"] = ContentType.objects.get_for_model(obj)
        kwargs["object_id"] = str(obj.pk)
        return self.create(**kwargs)


class BaseLog(models.Model):
    """Concrete base model for application logs tied to any model instance.

    Subclasses use Django multi-table inheritance so all log types remain
    queryable through this base table.
    """

    id = models.BigAutoField(primary_key=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.TextField()
    content_object = GenericForeignKey("content_type", "object_id")
    event_id = models.UUIDField(default=uuid.uuid4, db_index=True)
    event_type = models.CharField(max_length=100, db_index=True)
    note = models.TextField(blank=True, default="")
    metadata = models.JSONField(blank=True, default=dict)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="logs",
        blank=True,
        null=True,
    )
    source = models.CharField(max_length=64, blank=True, null=True)
    task_name = models.CharField(max_length=255, blank=True, null=True)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = BaseLogManager()

    class Meta:
        """Metadata."""

        default_permissions = ()
        ordering = ["-created_at", "-id"]
        indexes = [
            models.Index(
                fields=["content_type", "object_id", "-created_at"],
                name="baselog_object_created_idx",
            ),
            models.Index(
                fields=["event_id", "-created_at"],
                name="baselog_event_created_idx",
            ),
            models.Index(
                fields=["event_type", "-created_at"],
                name="baselog_type_created_idx",
            ),
            models.Index(fields=["source"], name="baselog_source_idx"),
            models.Index(fields=["task_name"], name="baselog_task_name_idx"),
        ]

    def __str__(self):
        """Return a string representation of the log."""
        return f"{self.event_type}: {self.content_type} {self.object_id}"


class FeatureFlag(models.Model):
    """Model for storing feature flags that can be toggled on/off via Django admin."""

    class Meta:
        """Metadata."""

        ordering = ["feature_name"]
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"

    feature_name = models.CharField(max_length=100, unique=True, db_index=True)
    enabled = models.BooleanField(default=False)
    config = models.JSONField(null=False, blank=True, default=dict)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Model versioning/change tracking
    history = HistoricalRecords()

    def __str__(self) -> str:
        """Return string representation of the feature flag."""
        status = "enabled" if self.enabled else "disabled"
        return f"{self.feature_name} ({status})"


@receiver([post_delete, post_migrate, post_save], sender=FeatureFlag)
def clear_feature_flag_cache(sender, instance, **kwargs):
    """Invalidate the cache after any changes to feature flags.

    This depends on the cache being separated by feature, so the entire cache can be deleted.
    There are too many options for headers/cookies to determine the key programatically,
    so we segment the different featuers into separate caches to be able to invalidate efficiently
    """
    cache = caches["feature-flags"]
    cache.clear()


"""Global permissions

Allows for the creation of permissions that are
not related to a specific model. This allows us
broader flexibility is assigning permissions
where needed.

NOTE: At this moment, the GlobalPermission and GlobalPermissionManager classes
are not directly in use, but are included as they make up part of the core
permission architecture addressed in this PR.
"""


class GlobalPermissionManager(models.Manager):
    """Manager for global permissions."""

    def get_queryset(self):
        """Return global permissions."""
        return super().get_queryset().filter(content_type__model="global_permission")


class GlobalPermission(Permission):
    """A global permission, not attached to a model."""

    objects = GlobalPermissionManager()

    class Meta:
        """Metadata."""

        proxy = True
        verbose_name = "global_permission"

    def save(self, *args, **kwargs):
        """Save the permission using the global permission content type."""
        content_type, _ = ContentType.objects.get_or_create(
            model=self._meta.verbose_name,
            app_label=self._meta.app_label,
        )
        self.content_type = content_type
        super().save(*args, **kwargs)
