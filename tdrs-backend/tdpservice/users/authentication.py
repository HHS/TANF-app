"""Define custom authentication class."""

import hashlib
import json
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

import jwt
import requests
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


def _expected_keycloak_issuer():
    """Return the Keycloak issuer expected for bearer access tokens."""
    return getattr(
        settings,
        "KEYCLOAK_ISSUER",
        f"{settings.KEYCLOAK_SERVER_URL}/realms/{settings.KEYCLOAK_REALM}",
    )


def _expected_keycloak_audience():
    """Return the API audience expected in bearer access tokens."""
    return getattr(
        settings,
        "KEYCLOAK_API_AUDIENCE",
        settings.KEYCLOAK_DJANGO_CLIENT_ID,
    )


def _expected_keycloak_bearer_client_id():
    """Return the Keycloak client allowed to use bearer auth."""
    return getattr(settings, "KEYCLOAK_BEARER_CLIENT_ID", "tdp-cli")


def _jwks_cache_key(key_id):
    """Return a cache key for a JWKS key scoped to the configured endpoint."""
    cache_identity = f"{settings.OIDC_OP_JWKS_ENDPOINT}:{key_id}".encode("utf-8")
    return f"keycloak-jwks:{hashlib.sha256(cache_identity).hexdigest()}"


def _jwks_cache_ttl():
    """Return the TTL for cached JWKS keys."""
    return getattr(
        settings,
        "KEYCLOAK_JWKS_CACHE_TTL",
        getattr(settings, "DEFAULT_CACHE_TIMEOUT", 300),
    )


def _matching_jwks_key(token):
    """Return the JWKS key matching the token's key id."""
    header = jwt.get_unverified_header(token)
    key_id = header.get("kid")
    if not key_id:
        raise jwt.InvalidTokenError("Token missing kid header.")

    cache_key = _jwks_cache_key(key_id)
    cached_jwk = cache.get(cache_key)
    if cached_jwk:
        return jwt.algorithms.RSAAlgorithm.from_jwk(cached_jwk)

    response = requests.get(
        settings.OIDC_OP_JWKS_ENDPOINT,
        verify=getattr(settings, "OIDC_VERIFY_SSL", True),
        timeout=getattr(settings, "OIDC_TIMEOUT", None),
        proxies=getattr(settings, "OIDC_PROXY", None),
    )
    response.raise_for_status()

    for key in response.json().get("keys", []):
        if key.get("kid") == key_id:
            jwk = json.dumps(key)
            cache.set(cache_key, jwk, timeout=_jwks_cache_ttl())
            return jwt.algorithms.RSAAlgorithm.from_jwk(jwk)

    raise jwt.InvalidTokenError("No matching JWKS key found.")


def _verify_keycloak_bearer_token(token):
    """Verify bearer JWT signature and prove the token is meant for this API."""
    payload = jwt.decode(
        token,
        _matching_jwks_key(token),
        algorithms=[settings.OIDC_RP_SIGN_ALGO],
        audience=_expected_keycloak_audience(),
        issuer=_expected_keycloak_issuer(),
        options={"require": ["aud", "exp", "iss"]},
    )

    expected_client_id = _expected_keycloak_bearer_client_id()
    if payload.get("azp") != expected_client_id:
        raise jwt.InvalidTokenError(
            f"Token azp must be {expected_client_id}."
        )

    return payload


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

        try:
            payload = _verify_keycloak_bearer_token(token)
        except jwt.ExpiredSignatureError as exc:
            logger.info("Bearer token expired: %s", exc)
            raise AuthenticationFailed(_("Bearer token has expired."))
        except (jwt.InvalidTokenError, requests.RequestException) as exc:
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
        # Stashed for KeycloakClientRateThrottle to key on; safe attr names.
        request._keycloak_client_id = client_id
        request._keycloak_throttle_ident = f"{client_id}:{user.id}"
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
