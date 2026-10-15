"""Canary routing utilities for gradual Keycloak migration."""

import logging

from tdpservice.core.utils import get_feature_flag
from tdpservice.users.oidc import STANDARD_SESSION_SCOPE

logger = logging.getLogger(__name__)

KEYCLOAK_AUTH_FEATURE_FLAG = "keycloak_auth"


def normalize_idp(idp: str | None) -> str | None:
    """Normalize auth provider names across legacy and Keycloak flows."""
    if idp == "dotgov":
        return "login-gov"
    return idp


def should_use_keycloak(random_value: float | None = None) -> bool:
    """Return whether this request should use the Keycloak flow."""
    enabled, _ = get_feature_flag(
        KEYCLOAK_AUTH_FEATURE_FLAG,
        random_value=random_value,
    )

    return enabled


def set_auth_flow(request, flow: str, idp: str) -> None:
    """Record which auth flow and IdP this login request uses in the session.

    Args
    ----
        request: The Django request object.
        flow: "legacy" or "keycloak".
        idp: "dotgov" or "ams".
    """
    normalized_idp = normalize_idp(idp)
    request.session["session_scope"] = STANDARD_SESSION_SCOPE
    request.session["auth_flow"] = flow
    request.session["auth_idp"] = normalized_idp
    logger.info(
        "Login initiated",
        extra={"auth_flow": flow, "auth_idp": normalized_idp},
    )


def get_auth_flow(request) -> str | None:
    """Return the auth flow marker from the session, or None if not set."""
    return request.session.get("auth_flow")
