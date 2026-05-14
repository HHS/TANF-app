"""DRF throttling for Keycloak-issued bearer tokens.

External API clients (Postman, CLI tools, CI/CD) can generate significantly
more traffic than browser users. Rate limit per Keycloak client and Django user
so a runaway script or compromised token does not throttle every other bearer
client. Browser sessions and other auth paths are unaffected: the throttle
returns ``None`` (skip) when no bearer-token throttle identity is present on the
request.
"""

from django.core.cache import caches

from rest_framework.throttling import SimpleRateThrottle


class KeycloakClientRateThrottle(SimpleRateThrottle):
    """Rate limit DRF requests by Keycloak client_id and Django user.

    The rate is configured via DRF's ``DEFAULT_THROTTLE_RATES['keycloak_client']``
    (see ``KEYCLOAK_CLIENT_RATE`` in settings). Counters live in the dedicated
    Redis-backed ``throttle`` cache so they're shared across web workers.
    """

    cache = caches["throttle"]
    scope = "keycloak_client"

    def get_cache_key(self, request, view):
        """Return a bearer-token cache key, or None for non-bearer requests."""
        ident = getattr(request, "_keycloak_throttle_ident", None)
        if not ident:
            return None
        return self.cache_format % {"scope": self.scope, "ident": ident}
