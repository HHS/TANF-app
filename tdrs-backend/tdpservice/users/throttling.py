"""DRF throttling for Keycloak-issued bearer tokens.

External API clients (Postman, CLI tools, CI/CD) can generate significantly
more traffic than browser users. Rate limit per Keycloak client_id (the ``azp``
claim, e.g. ``tdp-cli``) so a runaway script or compromised token can't
saturate the API. Browser sessions and other auth paths are unaffected: the
throttle returns ``None`` (skip) when no Keycloak client_id is present on the
request.
"""

from django.core.cache import caches

from rest_framework.throttling import SimpleRateThrottle


class KeycloakClientRateThrottle(SimpleRateThrottle):
    """Rate limit DRF requests by Keycloak client_id (azp claim).

    The rate is configured via DRF's ``DEFAULT_THROTTLE_RATES['keycloak_client']``
    (see ``KEYCLOAK_CLIENT_RATE`` in settings). Counters live in the dedicated
    Redis-backed ``throttle`` cache so they're shared across web workers.
    """

    cache = caches["throttle"]
    scope = "keycloak_client"

    def get_cache_key(self, request, view):
        """Return a per-client cache key, or None to skip throttling for non-bearer requests."""
        client_id = getattr(request, "_keycloak_client_id", None)
        if not client_id:
            return None
        return self.cache_format % {"scope": self.scope, "ident": client_id}
