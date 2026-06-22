"""Keycloak Admin REST API client for syncing Django user data to Keycloak."""

import logging
import threading
from typing import Any

from django.conf import settings

from keycloak.exceptions import KeycloakGetError

from keycloak import KeycloakAdmin, KeycloakOpenIDConnection

logger = logging.getLogger(__name__)

# Maps Django group names to Keycloak group names (kebab-case)
DJANGO_TO_KC_GROUP: dict[str, str] = {
    "OFA Admin": "ofa-admin",
    "OFA System Admin": "ofa-system-admin",
    "Data Analyst": "data-analyst",
    "OFA Regional Staff": "ofa-regional-staff",
    "Developer": "developer",
    "ACF OCIO": "acf-ocio",
    "DIGIT Team": "digit-team",
}


class KeycloakSyncClient:
    """Client for syncing Django user state to Keycloak via the Admin REST API.

    Uses the tdp-django service account (client credentials grant) to
    authenticate with Keycloak's Admin REST API. Syncs are idempotent --
    they set absolute state, not deltas.
    """

    _instance: "KeycloakSyncClient | None" = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        connection = KeycloakOpenIDConnection(
            server_url=settings.KEYCLOAK_SERVER_URL,
            realm_name=settings.KEYCLOAK_REALM,
            client_id=settings.KEYCLOAK_ADMIN_CLIENT_ID,
            client_secret_key=settings.KEYCLOAK_ADMIN_CLIENT_SECRET,
            verify=True,
        )
        self.admin = KeycloakAdmin(connection=connection)
        self._kc_group_cache: dict[str, str] | None = None

    @classmethod
    def get_instance(cls) -> "KeycloakSyncClient":
        """Return a singleton instance of the client."""
        if cls._instance is None and getattr(settings, "KEYCLOAK_SYNC_ENABLED", False):
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton (useful for tests)."""
        with cls._lock:
            cls._instance = None

    def _get_kc_group_ids(self) -> dict[str, str]:
        """Return a mapping of Keycloak group name -> group id, cached per instance."""
        if self._kc_group_cache is None:
            groups = self.admin.get_groups()
            self._kc_group_cache = {g["name"]: g["id"] for g in groups}
        return self._kc_group_cache

    def _find_kc_user_by_email(self, email: str) -> dict[str, Any] | None:
        """Find a Keycloak user by exact email match."""
        users = self.admin.get_users(query={"email": email, "exact": True})
        if users:
            return users[0]
        return None

    def sync_user(self, user: Any) -> bool:
        """Sync a Django user's attributes to Keycloak.

        Finds the Keycloak user by email, then updates custom attributes:
        login_gov_uuid, hhs_id, stt_id, account_approval_status, region_ids.

        Returns True if the user was synced, False if not found in Keycloak.
        """
        kc_user = self._find_kc_user_by_email(user.email)
        if kc_user is None:
            logger.info(
                "Keycloak user not found for email=%s, skipping sync", user.email
            )
            return False

        kc_user_id = kc_user["id"]

        region_ids = (
            ",".join(str(r.id) for r in user.regions.all())
            if user.regions.exists()
            else ""
        )

        attributes = {
            "login_gov_uuid": str(user.login_gov_uuid) if user.login_gov_uuid else "",
            "hhs_id": user.hhs_id or "",
            "stt_id": str(user.stt_id) if user.stt_id else "",
            "account_approval_status": user.account_approval_status or "",
            "region_ids": region_ids,
        }

        try:
            self.admin.update_user(
                user_id=kc_user_id,
                payload={
                    "email": user.email,
                    "firstName": user.first_name or "",
                    "lastName": user.last_name or "",
                    "attributes": attributes,
                },
            )
            logger.info("Synced user attributes to Keycloak for email=%s", user.email)
            return True
        except KeycloakGetError:
            logger.exception(
                "Failed to sync user attributes to Keycloak for email=%s", user.email
            )
            return False

    def sync_user_groups(self, user: Any) -> bool:
        """Sync a Django user's group memberships to Keycloak.

        Removes all current Keycloak groups for the user, then adds
        the groups that match the user's current Django groups.

        Returns True if the groups were synced, False if user not found.
        """
        kc_user = self._find_kc_user_by_email(user.email)
        if kc_user is None:
            logger.info(
                "Keycloak user not found for email=%s, skipping group sync",
                user.email,
            )
            return False

        kc_user_id = kc_user["id"]
        kc_group_ids = self._get_kc_group_ids()

        # Remove all current KC group memberships
        current_kc_groups = self.admin.get_user_groups(user_id=kc_user_id)
        for group in current_kc_groups:
            try:
                self.admin.group_user_remove(user_id=kc_user_id, group_id=group["id"])
            except KeycloakGetError:
                logger.exception(
                    "Failed to remove Keycloak group %s from user %s",
                    group["name"],
                    user.email,
                )

        # Add correct groups based on Django state
        django_groups = user.groups.values_list("name", flat=True)
        for django_group_name in django_groups:
            kc_group_name = DJANGO_TO_KC_GROUP.get(django_group_name)
            if kc_group_name is None:
                logger.warning(
                    "No Keycloak group mapping for Django group '%s'",
                    django_group_name,
                )
                continue
            kc_group_id = kc_group_ids.get(kc_group_name)
            if kc_group_id is None:
                logger.warning("Keycloak group '%s' not found in realm", kc_group_name)
                continue
            try:
                self.admin.group_user_add(user_id=kc_user_id, group_id=kc_group_id)
            except KeycloakGetError:
                logger.exception(
                    "Failed to add Keycloak group %s to user %s",
                    kc_group_name,
                    user.email,
                )

        logger.info("Synced group memberships to Keycloak for email=%s", user.email)
        return True

    def bulk_sync_all_users(self) -> dict[str, int]:
        """Sync all active Django users to Keycloak.

        Returns a stats dict with counts of synced, skipped, and failed users.
        """
        from tdpservice.users.models import User

        stats = {"synced": 0, "skipped": 0, "failed": 0}

        users = (
            User.objects.filter(is_active=True)
            .select_related("stt")
            .prefetch_related("groups", "regions")
        )

        for user in users:
            try:
                attr_ok = self.sync_user(user)
                group_ok = self.sync_user_groups(user)
                if attr_ok and group_ok:
                    stats["synced"] += 1
                elif not attr_ok:
                    stats["skipped"] += 1
                else:
                    stats["failed"] += 1
            except Exception:
                logger.exception(
                    "Unexpected error syncing user %s to Keycloak", user.email
                )
                stats["failed"] += 1

        logger.info("Bulk Keycloak sync complete: %s", stats)
        return stats
