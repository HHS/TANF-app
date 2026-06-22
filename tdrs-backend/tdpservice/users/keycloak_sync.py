"""Django signal handlers that sync user/group changes to Keycloak."""

import logging

from django.conf import settings
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from tdpservice.users.models import User

logger = logging.getLogger(__name__)


def _get_client():
    """Lazily import and return the KeycloakSyncClient singleton."""
    from tdpservice.users.keycloak_client import KeycloakSyncClient

    return KeycloakSyncClient.get_instance()


@receiver(post_save, sender=User)
def sync_user_to_keycloak(sender, instance, **kwargs):
    """Sync user attributes to Keycloak after save."""
    sync = getattr(settings, "KEYCLOAK_SYNC_ENABLED", False)
    print(f"Keycloak Sync Enabled?: {sync}")
    if not getattr(settings, "KEYCLOAK_SYNC_ENABLED", False):
        return

    try:
        _get_client().sync_user(instance)
    except Exception:
        logger.exception(
            "Failed to sync user %s to Keycloak on post_save", instance.email
        )


@receiver(m2m_changed, sender=User.groups.through)
def sync_user_groups_to_keycloak(sender, instance, action, **kwargs):
    """Sync user group memberships to Keycloak after group changes."""
    sync = getattr(settings, "KEYCLOAK_SYNC_ENABLED", False)
    print(f"Keycloak Sync Enabled?: {sync}")
    if not getattr(settings, "KEYCLOAK_SYNC_ENABLED", False):
        return

    # Only fire after the M2M change is committed
    if action not in ("post_add", "post_remove", "post_clear"):
        return

    try:
        if not getattr(settings, "KEYCLOAK_SYNC_ENABLED", False):
            return
        _get_client().sync_user_groups(instance)
    except Exception:
        logger.exception(
            "Failed to sync groups for user %s to Keycloak on m2m_changed",
            instance.email,
        )
