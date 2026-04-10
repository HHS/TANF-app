"""Keycloak OIDC authentication backend using mozilla-django-oidc."""

import logging
from typing import Optional

from django.contrib.auth import get_user_model

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from tdpservice.users.models import AccountApprovalStatusChoices

logger = logging.getLogger(__name__)

User = get_user_model()


class KeycloakOIDCBackend(OIDCAuthenticationBackend):
    """Custom OIDC authentication backend for Keycloak-brokered login.

    Handles user lookup by login_gov_uuid or hhs_id from Keycloak token claims,
    enforces ACF email domain restrictions, and checks account approval status.
    """

    def filter_users_by_claims(self, claims: dict) -> list:
        """Look up existing users by identity provider-specific claims.

        Keycloak passes through the upstream IdP identity via custom attributes:
        - login_gov_uuid: from Login.gov 'sub' claim
        - hhs_id: from AMS 'hhsid' claim

        Falls back to email-based lookup if neither IdP-specific claim is present.
        """
        login_gov_uuid = claims.get("login_gov_uuid")
        hhs_id = claims.get("hhs_id")
        email = claims.get("email", "").lower()

        if hhs_id:
            users = User.objects.filter(hhs_id=hhs_id)
            if users.exists():
                return list(users)
            # Fall back to email lookup for AMS users who may not have hhs_id set yet
            if email:
                users = User.objects.filter(username=email)
                if users.exists():
                    return list(users)

        if login_gov_uuid:
            users = User.objects.filter(login_gov_uuid=login_gov_uuid)
            if users.exists():
                return list(users)

        # Final fallback: lookup by email
        if email:
            users = User.objects.filter(username=email)
            if users.exists():
                return list(users)

        return []

    def create_user(self, claims: dict) -> Optional[User]:
        """Create a new Django user from Keycloak token claims."""
        email = claims.get("email", "").lower()
        if not email:
            logger.error("Cannot create user: no email in claims")
            return None

        login_gov_uuid = claims.get("login_gov_uuid")
        hhs_id = claims.get("hhs_id")

        create_kwargs = {}
        if login_gov_uuid:
            create_kwargs["login_gov_uuid"] = login_gov_uuid
        if hhs_id:
            create_kwargs["hhs_id"] = hhs_id

        user = User.objects.create_user(
            username=email,
            email=email,
            **create_kwargs,
        )
        user.set_unusable_password()
        user.save()

        logger.info("Created new user via Keycloak OIDC: %s", email)
        return user

    def update_user(self, user: User, claims: dict) -> User:
        """Update existing user attributes from Keycloak claims on each login."""
        login_gov_uuid = claims.get("login_gov_uuid")
        hhs_id = claims.get("hhs_id")
        changed = False

        if login_gov_uuid and str(user.login_gov_uuid) != login_gov_uuid:
            user.login_gov_uuid = login_gov_uuid
            changed = True

        if hhs_id and user.hhs_id != hhs_id:
            user.hhs_id = hhs_id
            changed = True

        if changed:
            user.save()
            logger.info(
                "Updated user attributes from Keycloak claims: %s", user.username
            )

        return user

    def verify_claims(self, claims: dict) -> bool:
        """Verify that the claims allow authentication.

        Checks:
        1. Email is present
        2. ACF email domain check: @acf.hhs.gov users must not authenticate via Login.gov
        3. Account is not deactivated or inactive
        """
        email = claims.get("email", "").lower()
        if not email:
            logger.warning("OIDC claims missing email, rejecting authentication")
            return False

        # ACF email domain check: ACF staff must use AMS, not Login.gov
        identity_provider = claims.get("identity_provider", "")
        if "@acf.hhs.gov" in email and identity_provider == "login-gov":
            logger.warning(
                "ACF user %s attempted Login.gov authentication, rejecting. "
                "ACF staff must use AMS.",
                email,
            )
            return False

        # Check if the user already exists and is deactivated/inactive
        users = self.filter_users_by_claims(claims)
        if users:
            user = users[0]
            if not user.is_active:
                logger.warning("Login rejected for inactive user: %s", user.username)
                return False
            if user.account_approval_status == AccountApprovalStatusChoices.DEACTIVATED:
                logger.warning("Login rejected for deactivated user: %s", user.username)
                return False

        return True

    def get_userinfo(self, access_token: str, id_token: str, payload: dict) -> dict:
        """Return claims from the ID token payload directly.

        Keycloak includes all needed attributes (email, login_gov_uuid, hhs_id,
        identity_provider) in the ID token via protocol mappers, so there is no
        need to make a separate userinfo endpoint call. This also avoids token
        validation issues when the realm signing key is rotated.
        """
        return payload
