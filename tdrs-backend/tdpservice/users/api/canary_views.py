"""Canary auth views that route between legacy and Keycloak flows.

These views sit at versionless paths (/login/dotgov, /login/ams, /logout/oidc)
and use the KEYCLOAK_AUTH_PERCENTAGE setting to decide which auth flow handles
each new login request. The frontend is unaware of the routing — it always hits
the same endpoints.

During the transition period, legacy callbacks still arrive at /v1/login and
/v1/oidc/ams (because those redirect URIs are registered with Login.gov/AMS),
while Keycloak callbacks arrive at /oidc/callback/ via mozilla-django-oidc.
"""

import logging

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views import View

from tdpservice.users.views import (
    KeycloakLoginAMSView,
    KeycloakLoginDotGovView,
    KeycloakLogoutView,
)

from .canary import get_auth_flow, set_auth_flow, should_use_keycloak
from .login_redirect_oidc import LoginRedirectAMS, LoginRedirectLoginDotGov
from .logout_redirect_oidc import LogoutRedirectOIDC

logger = logging.getLogger(__name__)


class CanaryLoginDotGovView(View):
    """Route Login.gov requests to legacy or Keycloak based on canary percentage."""

    def get(self, request, *args, **kwargs):
        """Get Keycloak or legacy auth view."""
        if should_use_keycloak():
            set_auth_flow(request, "keycloak", "dotgov")
            return KeycloakLoginDotGovView.as_view()(request, *args, **kwargs)
        else:
            set_auth_flow(request, "legacy", "dotgov")
            return LoginRedirectLoginDotGov.as_view()(request, *args, **kwargs)


class CanaryLoginAMSView(View):
    """Route AMS requests to legacy or Keycloak based on canary percentage."""

    def get(self, request, *args, **kwargs):
        """Get Keycloak or legacy auth view."""
        if should_use_keycloak():
            set_auth_flow(request, "keycloak", "ams")
            return KeycloakLoginAMSView.as_view()(request, *args, **kwargs)
        else:
            set_auth_flow(request, "legacy", "ams")
            return LoginRedirectAMS.as_view()(request, *args, **kwargs)


class CanaryLogoutView(View):
    """Logout via the correct flow based on the session's auth_flow marker."""

    def get(self, request, *args, **kwargs):
        """Get Keycloak or legacy logout view."""
        flow = get_auth_flow(request)

        if flow == "keycloak":
            return KeycloakLogoutView.as_view()(request, *args, **kwargs)
        elif flow == "legacy":
            return LogoutRedirectOIDC.as_view()(request, *args, **kwargs)
        else:
            # No marker (e.g., old session or direct hit) — plain logout + redirect
            logout(request)
            return HttpResponseRedirect(settings.FRONTEND_BASE_URL)
