"""Request throttling stays closed when Redis is unavailable."""

from unittest.mock import Mock, patch

from django.core.cache.backends.locmem import LocMemCache
from django.test import RequestFactory

import pytest
from redis.exceptions import ConnectionError, TimeoutError
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from tdpservice.users.throttling import KeycloakClientRateThrottle


class ThrottledView(APIView):
    """Minimal endpoint exercising DRF's throttle exception handling."""

    authentication_classes = []
    permission_classes = []
    throttle_classes = [KeycloakClientRateThrottle]

    def get(self, request) -> Response:
        """Return only after rate limiting succeeds."""
        return Response({"allowed": True})


@pytest.mark.parametrize("error", [ConnectionError, TimeoutError])
@pytest.mark.parametrize("operation", ["get", "set"])
def test_cache_failure_rejects_bearer_request(error, operation) -> None:
    """Rate-limit read and write failures return 503 before the view executes."""
    request = APIRequestFactory().get("/test/")
    request._keycloak_throttle_ident = "tdp-cli:123"
    failing_cache = Mock()
    failing_cache.get.return_value = []
    getattr(failing_cache, operation).side_effect = error
    with patch.object(KeycloakClientRateThrottle, "cache", failing_cache):
        response = ThrottledView.as_view()(request)
    assert response.status_code == 503
    assert response.data["detail"].code == "throttle_cache_unavailable"


def test_session_request_skips_unavailable_throttle_cache() -> None:
    """A Redis outage does not add throttling to browser-session requests."""
    request = RequestFactory().get("/v1/users/me/")
    failing_cache = Mock()
    failing_cache.get.side_effect = ConnectionError
    with patch.object(KeycloakClientRateThrottle, "cache", failing_cache):
        assert KeycloakClientRateThrottle().allow_request(request, view=None)
    failing_cache.get.assert_not_called()


def test_healthy_cache_enforces_rate_limit() -> None:
    """A healthy cache still allows the first request and rejects excess traffic."""
    request = APIRequestFactory().get("/test/")
    request._keycloak_throttle_ident = "tdp-cli:123"
    cache = LocMemCache("throttle-resilience-test", {})
    cache.clear()
    with (
        patch.object(KeycloakClientRateThrottle, "cache", cache),
        patch.object(KeycloakClientRateThrottle, "get_rate", return_value="1/min"),
    ):
        assert ThrottledView.as_view()(request).status_code == 200
        assert ThrottledView.as_view()(request).status_code == 429
    cache.clear()
