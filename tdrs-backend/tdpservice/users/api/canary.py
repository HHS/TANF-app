"""Canary routing utilities for gradual Keycloak migration.

Controls what percentage of new login requests are routed through Keycloak
vs. the legacy direct OIDC flow. The percentage is controlled by the
KEYCLOAK_AUTH_PERCENTAGE Django setting (0-100, default 0).
"""

import logging
import random

from django.conf import settings

logger = logging.getLogger(__name__)


def normalize_idp(idp: str | None) -> str | None:
    """Normalize auth provider names across legacy and Keycloak flows."""
    if idp == "dotgov":
        return "login-gov"
    return idp


def should_use_keycloak() -> bool:
    """Return True if this request should use the Keycloak flow based on canary percentage."""
    percentage = getattr(settings, "KEYCLOAK_AUTH_PERCENTAGE", 0)
    if percentage <= 0:
        return False
    if percentage >= 100:
        return True
    return random.randint(1, 100) <= percentage


def set_auth_flow(request, flow: str, idp: str) -> None:
    """Record which auth flow and IdP this login request uses in the session.

    Args
    ----
        request: The Django request object.
        flow: "legacy" or "keycloak".
        idp: "dotgov" or "ams".
    """
    normalized_idp = normalize_idp(idp)
    request.session["auth_flow"] = flow
    request.session["auth_idp"] = normalized_idp
    logger.info(
        "Login initiated",
        extra={"auth_flow": flow, "auth_idp": normalized_idp},
    )


def get_auth_flow(request) -> str | None:
    """Return the auth flow marker from the session, or None if not set."""
    return request.session.get("auth_flow")
