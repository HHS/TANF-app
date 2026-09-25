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


class MultiRealmKeycloakSyncClient:
    """Fan out Django-authoritative user sync to each configured Keycloak realm."""

    def __init__(self, clients: list["KeycloakSyncClient"]) -> None:
        """Initialize the aggregate sync client."""
        self.clients = clients

    def sync_user(self, user: Any) -> bool:
        """Sync user attributes to all configured realms where the user exists."""
        synced = False
        for client in self.clients:
            try:
                synced = client.sync_user(user) or synced
            except Exception:
                logger.exception(
                    "Failed to sync user %s to Keycloak realm %s",
                    user.email,
                    client.realm_name,
                )
        return synced

    def sync_user_groups(self, user: Any) -> bool:
        """Sync group memberships to all configured realms where the user exists."""
        synced = False
        for client in self.clients:
            try:
                synced = client.sync_user_groups(user) or synced
            except Exception:
                logger.exception(
                    "Failed to sync groups for user %s to Keycloak realm %s",
                    user.email,
                    client.realm_name,
                )
        return synced

    def bulk_sync_all_users(self) -> dict[str, int]:
        """Sync all active Django users to all configured realms."""
        from tdpservice.users.models import User

        stats = {"synced": 0, "skipped": 0, "failed": 0}

        users = (
            User.objects.filter(is_active=True)
            .select_related("stt")
            .prefetch_related("groups", "regions")
        )

        for user in users:
            user_synced = False
            user_failed = False
            for client in self.clients:
                try:
                    attr_ok = client.sync_user(user)
                    group_ok = client.sync_user_groups(user) if attr_ok else False
                    user_synced = (attr_ok and group_ok) or user_synced
                    user_failed = (attr_ok and not group_ok) or user_failed
                except Exception:
                    logger.exception(
                        "Unexpected error syncing user %s to Keycloak realm %s",
                        user.email,
                        client.realm_name,
                    )
                    user_failed = True

            if user_failed:
                stats["failed"] += 1
            elif user_synced:
                stats["synced"] += 1
            else:
                stats["skipped"] += 1

        logger.info("Bulk multi-realm Keycloak sync complete: %s", stats)
        return stats


class KeycloakSyncClient:
    """Client for syncing Django user state to Keycloak via the Admin REST API.

    Uses each realm's configured service account client credentials to
    authenticate with Keycloak's Admin REST API. Syncs are idempotent --
    they set absolute state, not deltas.
    """

    _instances: dict[tuple[str, str], "KeycloakSyncClient"] = {}
    _lock = threading.Lock()

    def __init__(
        self,
        realm_name: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        """Initialize the realm-specific sync client."""
        self.realm_name = realm_name or settings.KEYCLOAK_REALM
        self.client_id = client_id or settings.KEYCLOAK_ADMIN_CLIENT_ID
        self.client_secret = client_secret or settings.KEYCLOAK_ADMIN_CLIENT_SECRET
        connection = KeycloakOpenIDConnection(
            server_url=settings.KEYCLOAK_SERVER_URL,
            realm_name=self.realm_name,
            client_id=self.client_id,
            client_secret_key=self.client_secret,
            verify=True,
        )
        self.admin = KeycloakAdmin(connection=connection)
        self._kc_group_cache: dict[str, str] | None = None

    @classmethod
    def _sync_realm_configs(cls) -> list[tuple[str, str, str]]:
        """Return the Keycloak realms Django should sync into."""
        configs = [
            (
                settings.KEYCLOAK_REALM,
                settings.KEYCLOAK_ADMIN_CLIENT_ID,
                settings.KEYCLOAK_ADMIN_CLIENT_SECRET,
            ),
            (
                settings.KEYCLOAK_TDP_ADMIN_REALM,
                settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID,
                settings.KEYCLOAK_TDP_ADMIN_CLIENT_SECRET,
            ),
        ]

        return configs

    @classmethod
    def get_instance(
        cls,
        realm_name: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> "KeycloakSyncClient":
        """Return a singleton instance of a realm-specific client."""
        realm_name = realm_name or settings.KEYCLOAK_REALM
        client_id = client_id or settings.KEYCLOAK_ADMIN_CLIENT_ID
        client_secret = client_secret or settings.KEYCLOAK_ADMIN_CLIENT_SECRET
        key = (realm_name, client_id)

        if key not in cls._instances:
            with cls._lock:
                if key not in cls._instances:
                    cls._instances[key] = cls(
                        realm_name=realm_name,
                        client_id=client_id,
                        client_secret=client_secret,
                    )
        return cls._instances[key]

    @classmethod
    def get_sync_client(cls) -> MultiRealmKeycloakSyncClient:
        """Return a client that syncs to the standard and admin realms."""
        return MultiRealmKeycloakSyncClient(
            [
                cls.get_instance(
                    realm_name=realm_name,
                    client_id=client_id,
                    client_secret=client_secret,
                )
                for realm_name, client_id, client_secret in cls._sync_realm_configs()
            ]
        )

    @classmethod
    def reset_instance(cls) -> None:
        """Reset cached clients (useful for tests)."""
        with cls._lock:
            cls._instances = {}

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
