"""Define custom authentication class."""

import logging

from django.contrib.auth import get_user_model
from django.core.exceptions import SuspiciousOperation
from django.utils.translation import gettext_lazy as _

from mozilla_django_oidc.auth import OIDCAuthenticationBackend

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from tdpservice.users.oidc import (
    KeycloakOIDCBackend,
    apply_user_updates,
    filter_users_by_claims,
    verify_claims,
)

logger = logging.getLogger(__name__)


def _bearer_token_from_request(request):
    """Return the bearer token from an Authorization header, if present."""
    header = request.META.get("HTTP_AUTHORIZATION", "")
    if not header.lower().startswith("bearer "):
        return None
    return header[7:].strip() or None


class KeycloakBearerTokenAuthentication(BaseAuthentication):
    """DRF authentication for Keycloak-issued JWT bearer tokens.

    Verifies the JWT signature against the Keycloak JWKS endpoint, then runs
    the claims through the shared Keycloak helpers (``verify_claims`` /
    ``filter_users_by_claims`` / ``apply_user_updates``) so token-authenticated
    requests resolve to the same Django users — and obey the same approval and
    domain rules — as browser-based OIDC logins.

    Used for non-browser clients (Postman, CLI, CI/CD) that authenticate via
    OAuth2 Authorization Code + PKCE or Device Authorization Grant against the
    public ``tdp-cli`` Keycloak client.
    """

    www_authenticate_realm = "api"

    def authenticate(self, request):
        """Validate a bearer token and resolve the Django user, or return None."""
        token = _bearer_token_from_request(request)
        if not token:
            return None

        # OIDCAuthenticationBackend.verify_token retrieves JWKS, verifies the
        # RS256 signature and the ``exp`` claim. Access tokens have no nonce,
        # so the nonce branch is a no-op (None == None).
        backend = OIDCAuthenticationBackend()
        try:
            payload = backend.verify_token(token)
        except (SuspiciousOperation, Exception) as exc:
            logger.info("Bearer token verification failed: %s", exc)
            raise AuthenticationFailed(_("Invalid bearer token."))

        if not verify_claims(payload):
            raise AuthenticationFailed(_("Token claims rejected."))

        users = filter_users_by_claims(payload)
        if len(users) > 1:
            logger.warning(
                "Multiple users matched bearer token claims for email=%s",
                payload.get("email"),
            )
            raise AuthenticationFailed(_("Ambiguous user identity."))

        if users:
            user = apply_user_updates(users[0], payload)
        else:
            # Reuse the OIDC create-user path so all OIDC fields are applied.
            user = KeycloakOIDCBackend().create_user(payload)

        if user is None:
            raise AuthenticationFailed(_("Could not resolve user from token."))

        client_id = payload.get("azp", "unknown")
        logger.info(
            "Bearer token auth client=%s user=%s path=%s",
            client_id,
            user.username,
            request.path,
            extra={
                "client_id": client_id,
                "user_id": user.id,
                "username": user.username,
                "path": request.path,
            },
        )
        # Stashed for KeycloakClientRateThrottle to key on; safe attr name.
        request._keycloak_client_id = client_id
        return user, token

    def authenticate_header(self, request):
        """Return WWW-Authenticate only when the client attempted bearer auth.

        DRF promotes a denied request from 403 to 401 whenever the first
        authenticator's ``authenticate_header`` returns a value. Returning None
        for requests without a Bearer header preserves the historical 403 for
        session/anonymous callers — only requests that actually presented a
        (rejected) bearer token get the 401 + Bearer challenge.
        """
        if _bearer_token_from_request(request) is None:
            return None
        return f'Bearer realm="{self.www_authenticate_realm}"'


class CustomAuthentication(BaseAuthentication):
    """Define authentication and get user functions for custom authentication."""

    @staticmethod
    def authenticate(username=None, login_gov_uuid=None, hhs_id=None):
        """Authenticate user with the request and username."""
        # TODO: Provide separate implementations for two unrelated workflows
        # both using this method. (The latter appears to always fail.)
        # References:
        #   tdpservice/users/api/login.py:TokenAuthorizationOIDC.handleUser
        #   https://www.django-rest-framework.org/api-guide/authentication
        User = get_user_model()
        logging.debug(
            f"CustomAuthentication::authenticate: {username}, {login_gov_uuid}, {hhs_id}"
        )
        try:
            if hhs_id:
                try:
                    return User.objects.get(hhs_id=hhs_id)
                except User.DoesNotExist:
                    # If below line also fails with User.DNE, will bubble up and return None
                    user = User.objects.filter(username=username)
                    user.update(hhs_id=hhs_id)
                    logging.debug(
                        "Updated user {} with hhs_id {}.".format(username, hhs_id)
                    )
                return User.objects.get(hhs_id=hhs_id)

            elif login_gov_uuid:
                return User.objects.get(login_gov_uuid=login_gov_uuid)
            else:
                return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @staticmethod
    def get_user(user_id):
        """Get user by the user id."""
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
