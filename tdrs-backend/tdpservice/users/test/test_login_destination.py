"""Regression coverage for destinations carried through OIDC authentication."""

from unittest.mock import Mock, patch
from urllib.parse import parse_qs, urlsplit

from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends.signed_cookies import SessionStore
from django.core.exceptions import SuspiciousOperation
from django.test import RequestFactory
from django.urls import resolve

import pytest

from tdpservice.users.api.login import InactiveUser, TokenAuthorizationLoginDotGov
from tdpservice.users.api.login_redirect_oidc import (
    LoginRedirectAMS,
    LoginRedirectLoginDotGov,
)
from tdpservice.users.login_destination import (
    KeycloakOIDCCallbackView,
    frontend_login_url,
    validate_login_destination,
)
from tdpservice.users.views import KeycloakLoginAMSView, KeycloakLoginDotGovView


@pytest.mark.parametrize(
    "destination",
    ["/profile", "/data-files?type=tanf", "/fra-data-files/2026/1?a=a%26b%2Bc#history"],
)
def test_local_destinations_preserved(destination: str):
    """Preserve the path, query encoding and fragment exactly."""
    assert validate_login_destination(destination) == destination


@pytest.mark.parametrize(
    "destination",
    [
        None,
        "",
        "https://example.com",
        "//example.com",
        "///example.com",
        "/\\example.com",
        "/%5cexample.com",
        "/%2fexample.com",
        "/\n/example.com",
        "/%0d%0aLocation:evil",
        "javascript:alert(1)",
        "profile",
        "/",
        "/?a=b",
        "/login",
        "/LOGIN/",
        "/%6cogin",
        "/data-files/../login",
        "/profile/..",
        "/%invalid",
        "/%ff",
    ],
)
def test_invalid_destinations_fall_back_to_home(destination: str | None):
    """Reject external URLs, malformed paths and authentication loops."""
    assert validate_login_destination(destination) == "/home"


def authenticated_user(ocio: bool = False) -> Mock:
    """Build an authenticated user without database access."""
    user = Mock(is_active=True)
    user.groups.filter.return_value.exists.return_value = ocio
    return user


@pytest.mark.parametrize("ocio, path", [(False, "/profile"), (True, "/login")])
def test_frontend_redirect_preserves_admin_handoff(settings, ocio: bool, path: str):
    """OCIO users still visit the existing frontend admin handoff."""
    settings.FRONTEND_BASE_URL = "https://frontend.example.com"
    assert frontend_login_url(authenticated_user(ocio), "/profile") == (
        settings.FRONTEND_BASE_URL + path
    )


@pytest.mark.parametrize("view", [LoginRedirectLoginDotGov, LoginRedirectAMS])
def test_legacy_login_binds_destination_to_state(view):
    """Both legacy providers retain the destination alongside their nonce and state."""
    request = RequestFactory().get("/login", {"next": "/profile?tab=a#contact"})
    request.session = SessionStore()
    with patch.object(
        LoginRedirectAMS,
        "get_ams_configuration",
        return_value={
            "authorization_endpoint": "https://identity.example.com/authorize"
        },
    ):
        response = view.as_view()(request)
    params = parse_qs(urlsplit(response.url).query)
    tracker = request.session["state_nonce_tracker"]
    assert tracker["state"] == params["state"][0]
    assert tracker["next"] == "/profile?tab=a#contact"
    assert "next" not in params


def test_legacy_callback_redirects_and_consumes_destination(settings):
    """The validated login redirects to its destination and consumes it once."""
    request = RequestFactory().get("/login", {"state": "state"})
    request.session = SessionStore()
    request.session["state_nonce_tracker"] = {"state": "state", "next": "/profile"}
    view = TokenAuthorizationLoginDotGov()
    with patch.object(view, "validate_and_decode_payload", return_value={}), patch.object(
        view, "handle_user", return_value=authenticated_user()
    ):
        response = view._get_user_id_token(request, "state", {"id_token": "token"})
    assert response.url == settings.FRONTEND_BASE_URL.rstrip("/") + "/profile"
    assert "next" not in request.session["state_nonce_tracker"]
    assert response.cookies["id_token"]["httponly"]


def test_failed_legacy_login_does_not_redirect_or_consume_destination():
    """An inactive account cannot reach the requested destination."""
    request = RequestFactory().get("/login", {"state": "state"})
    request.session = SessionStore()
    request.session["state_nonce_tracker"] = {"state": "state", "next": "/profile"}
    view = TokenAuthorizationLoginDotGov()
    with patch.object(view, "validate_and_decode_payload", return_value={}), patch.object(
        view, "handle_user", side_effect=InactiveUser("Inactive account")
    ):
        response = view._get_user_id_token(request, "state", {"id_token": "token"})
    assert response.status_code == 401
    assert "Location" not in response
    assert request.session["state_nonce_tracker"]["next"] == "/profile"


@pytest.mark.parametrize("view", [KeycloakLoginDotGovView, KeycloakLoginAMSView])
def test_keycloak_destinations_are_scoped_to_each_state(view):
    """Starting another login does not overwrite the first login's destination."""
    session = SessionStore()
    for destination in ["/profile", "/data-files?type=tanf#history"]:
        request = RequestFactory().get("/login", {"next": destination})
        request.session = session
        response = view.as_view()(request)
        state = parse_qs(urlsplit(response.url).query)["state"][0]
        assert session["oidc_states"][state]["next"] == destination
    assert {value["next"] for value in session["oidc_states"].values()} == {
        "/profile",
        "/data-files?type=tanf#history",
    }


@pytest.mark.parametrize("succeeds", [True, False])
def test_keycloak_callback_uses_destination_only_after_authentication(settings, succeeds):
    """Exercise the real OIDC callback, including state consumption and login failure."""
    settings.LOGIN_REDIRECT_URL_FAILURE = "https://frontend.example.com/"
    request = RequestFactory().get("/oidc/callback/", {"state": "state", "code": "code"})
    request.user = AnonymousUser()
    request.session = SessionStore()
    request.session["oidc_states"] = {
        "state": {"nonce": "nonce", "next": "/profile", "added_on": 1}
    }
    request.session["oidc_login_next"] = "/wrong-tab"
    request.session.save()
    with patch(
        "mozilla_django_oidc.views.auth.authenticate",
        return_value=authenticated_user() if succeeds else None,
    ), patch("mozilla_django_oidc.views.auth.login"):
        response = KeycloakOIDCCallbackView.as_view()(request)
    expected = (
        settings.FRONTEND_BASE_URL.rstrip("/") + "/profile"
        if succeeds
        else settings.LOGIN_REDIRECT_URL_FAILURE
    )
    assert response.url == expected
    assert "state" not in request.session["oidc_states"]


def test_keycloak_callback_rejects_unknown_state():
    """A destination cannot be used to bypass OIDC state validation."""
    request = RequestFactory().get(
        "/oidc/callback/", {"state": "wrong-state", "code": "code", "next": "/profile"}
    )
    request.user = AnonymousUser()
    request.session = SessionStore()
    request.session["oidc_states"] = {
        "state": {"nonce": "nonce", "next": "/profile", "added_on": 1}
    }
    with patch("mozilla_django_oidc.views.auth.authenticate") as authenticate:
        with pytest.raises(SuspiciousOperation):
            KeycloakOIDCCallbackView.as_view()(request)
    authenticate.assert_not_called()


def test_session_refresh_keeps_existing_return_url():
    """Callbacks without a destination retain the library's refresh behavior."""
    view = KeycloakOIDCCallbackView()
    view.has_login_destination = False
    view.request = Mock(session={"oidc_login_next": "/original-refresh-target"})
    assert view.success_url == "/original-refresh-target"


@pytest.mark.parametrize("path", ["/v2/oidc/callback/", "/oidc/callback/"])
def test_standard_callback_routes_use_destination_handler(path: str):
    """Explicit and canary auth URLs both use the custom callback."""
    assert resolve(path).func.view_class is KeycloakOIDCCallbackView
