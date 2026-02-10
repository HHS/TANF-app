"""Core models."""

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.db import models
from django.db.models.signals import post_delete, post_migrate, post_save
from django.dispatch import receiver


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

    def __str__(self) -> str:
        """Return string representation of the feature flag."""
        status = "enabled" if self.enabled else "disabled"
        return f"{self.feature_name} ({status})"


@receiver([post_delete, post_migrate, post_save], sender=FeatureFlag)
def clear_feature_flag_cache(sender, instance, **kwargs):
    """
    FeatureFlag post-save signal invalidates the cache after any changes to feature flags.

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
