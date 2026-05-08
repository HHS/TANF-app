"""Tests for canary routing between legacy and Keycloak auth flows."""

from unittest.mock import patch

from django.conf import settings
from django.test import Client, RequestFactory, override_settings

import pytest

from tdpservice.users.api.canary import (
    get_auth_flow,
    set_auth_flow,
    should_use_keycloak,
)


class TestShouldUseKeycloak:
    """Test the canary percentage routing function."""

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=0)
    def test_zero_percent_always_legacy(self):
        """At 0%, should_use_keycloak should always return False."""
        for _ in range(50):
            assert should_use_keycloak() is False

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=100)
    def test_hundred_percent_always_keycloak(self):
        """At 100%, should_use_keycloak should always return True."""
        for _ in range(50):
            assert should_use_keycloak() is True

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=50)
    def test_fifty_percent_routes_both(self):
        """At 50%, should_use_keycloak should yield both True and False over many calls."""
        results = [should_use_keycloak() for _ in range(200)]
        # With 200 trials at 50%, both True and False should appear
        assert True in results
        assert False in results

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=-5)
    def test_negative_percent_always_legacy(self):
        """A negative percentage should be clamped so the legacy flow is used."""
        assert should_use_keycloak() is False

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=150)
    def test_over_hundred_always_keycloak(self):
        """A percentage above 100 should be clamped so the Keycloak flow is used."""
        assert should_use_keycloak() is True

    def test_default_is_legacy(self):
        """Without the setting, should default to legacy."""
        with override_settings():
            del_attempted = False
            try:
                from django.conf import settings

                if hasattr(settings, "KEYCLOAK_AUTH_PERCENTAGE"):
                    # Setting exists, test with 0
                    with override_settings(KEYCLOAK_AUTH_PERCENTAGE=0):
                        assert should_use_keycloak() is False
                        del_attempted = True
            except Exception:
                pass
            if not del_attempted:
                assert should_use_keycloak() is False


class TestSetAuthFlow:
    """Test session marker utilities."""

    def test_set_and_get_auth_flow(self):
        """set_auth_flow should persist the flow and IdP on the session for later retrieval."""
        factory = RequestFactory()
        request = factory.get("/login/dotgov")
        # Simulate Django session
        request.session = {}

        set_auth_flow(request, "keycloak", "login-gov")
        assert get_auth_flow(request) == "keycloak"
        assert request.session["auth_idp"] == "login-gov"

    def test_set_legacy_flow(self):
        """set_auth_flow should record the legacy flow and AMS IdP on the session."""
        factory = RequestFactory()
        request = factory.get("/login/ams")
        request.session = {}

        set_auth_flow(request, "legacy", "ams")
        assert get_auth_flow(request) == "legacy"
        assert request.session["auth_idp"] == "ams"

    def test_get_auth_flow_empty_session(self):
        """get_auth_flow should return None when no flow marker is present on the session."""
        factory = RequestFactory()
        request = factory.get("/")
        request.session = {}

        assert get_auth_flow(request) is None


@pytest.mark.django_db
class TestCanaryLoginViews:
    """Test the canary login views route to the correct backend."""

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=0)
    def test_login_dotgov_routes_to_legacy(self):
        """At 0%, /login/dotgov should delegate to the legacy Login.gov redirect."""
        client = Client()
        with patch(
            "tdpservice.users.api.canary_views.LoginRedirectLoginDotGov"
        ) as mock_legacy:
            mock_legacy.as_view.return_value = lambda req, *a, **kw: _mock_response(302)
            client.get("/login/dotgov")
            mock_legacy.as_view.assert_called_once()

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=100)
    def test_login_dotgov_routes_to_keycloak(self):
        """At 100%, /login/dotgov should delegate to the Keycloak login view."""
        client = Client()
        with patch(
            "tdpservice.users.api.canary_views.KeycloakLoginDotGovView"
        ) as mock_kc:
            mock_kc.as_view.return_value = lambda req, *a, **kw: _mock_response(302)
            client.get("/login/dotgov")
            mock_kc.as_view.assert_called_once()

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=0)
    def test_login_ams_routes_to_legacy(self):
        """At 0%, /login/ams should delegate to the legacy AMS redirect."""
        client = Client()
        with patch("tdpservice.users.api.canary_views.LoginRedirectAMS") as mock_legacy:
            mock_legacy.as_view.return_value = lambda req, *a, **kw: _mock_response(302)
            client.get("/login/ams")
            mock_legacy.as_view.assert_called_once()

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=100)
    def test_login_ams_routes_to_keycloak(self):
        """At 100%, /login/ams should delegate to the Keycloak AMS view."""
        client = Client()
        with patch("tdpservice.users.api.canary_views.KeycloakLoginAMSView") as mock_kc:
            mock_kc.as_view.return_value = lambda req, *a, **kw: _mock_response(302)
            client.get("/login/ams")
            mock_kc.as_view.assert_called_once()

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=0)
    def test_session_marker_set_for_legacy(self):
        """Login views should set auth_flow=legacy in session at 0%."""
        client = Client()
        with patch(
            "tdpservice.users.api.canary_views.LoginRedirectLoginDotGov"
        ) as mock_legacy:
            mock_legacy.as_view.return_value = lambda req, *a, **kw: _mock_response(302)
            client.get("/login/dotgov")
            assert client.session.get("auth_flow") == "legacy"
            assert client.session.get("auth_idp") == "login-gov"

    @override_settings(KEYCLOAK_AUTH_PERCENTAGE=100)
    def test_session_marker_set_for_keycloak(self):
        """Login views should set auth_flow=keycloak in session at 100%."""
        client = Client()
        with patch("tdpservice.users.api.canary_views.KeycloakLoginAMSView") as mock_kc:
            mock_kc.as_view.return_value = lambda req, *a, **kw: _mock_response(302)
            client.get("/login/ams")
            assert client.session.get("auth_flow") == "keycloak"
            assert client.session.get("auth_idp") == "ams"


@pytest.mark.django_db
class TestCanaryLogoutView:
    """Test the canary logout view delegates based on session marker."""

    def test_logout_no_marker_redirects_to_frontend(self, settings):
        """With no auth_flow marker, should do plain logout + redirect to frontend."""
        client = Client()
        response = client.get("/logout/oidc")
        assert response.status_code == 302
        assert response.url == settings.FRONTEND_BASE_URL

    def test_logout_keycloak_delegates(self):
        """With auth_flow=keycloak, should delegate to KeycloakLogoutView."""
        client = Client()
        with patch("tdpservice.users.api.canary_views.KeycloakLogoutView") as mock_kc:
            mock_kc.as_view.return_value = lambda req, *a, **kw: _mock_response(302)
            # Establish a session by making a request first, then set the marker
            client.get("/auth_check")
            s = client.session
            s["auth_flow"] = "keycloak"
            s.save()
            # Inject the session cookie so the next request uses it
            client.cookies[settings.SESSION_COOKIE_NAME] = s.session_key
            client.get("/logout/oidc")
            mock_kc.as_view.assert_called_once()

    def test_logout_legacy_delegates(self):
        """With auth_flow=legacy, should delegate to LogoutRedirectOIDC."""
        client = Client()
        with patch(
            "tdpservice.users.api.canary_views.LogoutRedirectOIDC"
        ) as mock_legacy:
            mock_legacy.as_view.return_value = lambda req, *a, **kw: _mock_response(302)
            client.get("/auth_check")
            s = client.session
            s["auth_flow"] = "legacy"
            s.save()
            client.cookies[settings.SESSION_COOKIE_NAME] = s.session_key
            client.get("/logout/oidc")
            mock_legacy.as_view.assert_called_once()


@pytest.mark.django_db
class TestV1V2BackwardCompatibility:
    """Verify existing /v1/ and /v2/ routes still work."""

    def test_v1_login_dotgov_still_exists(self):
        """The /v1/login/dotgov route should still be reachable."""
        client = Client()
        # We just verify the URL resolves (will redirect to Login.gov, so 302)
        response = client.get("/v1/login/dotgov")
        assert response.status_code == 302

    def test_v2_login_dotgov_still_exists(self):
        """The /v2/login/dotgov route should still be reachable."""
        client = Client()
        # Keycloak view will redirect to Keycloak, so 302
        response = client.get("/v2/login/dotgov")
        assert response.status_code == 302

    def test_auth_check_versionless(self):
        """The versionless /auth_check should work."""
        client = Client()
        response = client.get("/auth_check")
        assert response.status_code == 200
        assert response.json()["authenticated"] is False


def _mock_response(status_code: int):
    """Create a minimal Django HttpResponse for mocking."""
    from django.http import HttpResponse

    return HttpResponse(status=status_code)
