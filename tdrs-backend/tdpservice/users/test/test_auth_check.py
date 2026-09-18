"""Test the authorization check."""

from importlib import import_module
from urllib.parse import parse_qs, urlparse

from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse

import pytest
from mozilla_django_oidc.middleware import SessionRefresh
from rest_framework import status
from rest_framework.test import APIRequestFactory

from ..api.login import CypressLoginDotGovAuthenticationOverride
from ..models import AccountApprovalStatusChoices
from ..oidc import STANDARD_SESSION_SCOPE
from ..serializers import UserProfileSerializer


class AuthenticatedUser:
    """Minimal authenticated user for middleware tests."""

    is_authenticated = True


def _create_admin_session_from_standard(api_client, settings):
    """Create an independently signed admin session for the current user."""
    engine = import_module(settings.SESSION_ENGINE)
    standard_session = engine.SessionStore(
        api_client.cookies[settings.SESSION_COOKIE_NAME].value
    )
    admin_session = engine.SessionStore()
    admin_session.update(dict(standard_session.items()))
    admin_session["session_scope"] = "admin"
    admin_session["oidc_id_token"] = "admin-id-token"
    admin_session.save()
    api_client.cookies[settings.ADMIN_SESSION_COOKIE_NAME] = admin_session.session_key


def _login_standard_session(api_client, user, settings):
    """Create a Keycloak-originated standard app session."""
    assert api_client.login(username=user.username, password="test_password") is True
    session = api_client.session
    session["session_scope"] = "standard"
    session["auth_flow"] = "keycloak"
    session["oidc_id_token"] = "standard-id-token"
    session.save()
    api_client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key


def _login_admin_session(api_client, user, settings):
    """Create an admin-scoped session from a valid admin user login."""
    _login_standard_session(api_client, user, settings)
    _create_admin_session_from_standard(api_client, settings)


def _client_session_from_cookie(api_client, cookie_name, settings):
    """Return a session store loaded from the named test client cookie."""
    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore(api_client.cookies[cookie_name].value)


def _assert_auth_state(api_client, standard_authenticated, admin_authenticated):
    """Assert the standard and admin auth_check states."""
    standard_response = api_client.get(reverse("authorization-check"))
    admin_response = api_client.get(reverse("admin-authorization-check"))

    assert standard_response.status_code == status.HTTP_200_OK
    assert standard_response.data["authenticated"] is standard_authenticated
    assert admin_response.data["authenticated"] is admin_authenticated

    if admin_authenticated:
        assert admin_response.status_code == status.HTTP_200_OK
        assert admin_response.data["authorized"] is True


def _url_without_query(url):
    """Return scheme, host, and path without query parameters."""
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"


@pytest.mark.parametrize(
    "path",
    [
        "/admin-auth/login/dotgov",
        "/admin-auth/oidc/callback/",
        "/admin-auth/auth_check",
        "/admin-api/v1/users/",
    ],
)
def test_session_refresh_exempts_admin_paths(path):
    """Expired OIDC sessions should not hijack admin routes."""
    request = APIRequestFactory().get(path)
    request.user = AuthenticatedUser()
    request.session = {"oidc_id_token_expiration": 0}

    assert SessionRefresh(lambda request: None).is_refreshable_url(request) is False


@pytest.mark.django_db
def test_auth_check_endpoint_with_no_user(api_client):
    """If there is no user auth_check should return 200 with unauthorized message."""
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_cypress_login_creates_standard_scoped_session(user, settings):
    """Cypress E2E login should follow the standard frontend session contract."""
    settings.CYPRESS_TOKEN = "cypress-test-token"
    request = APIRequestFactory().get(
        "/v1/login/cypress",
        {"username": user.username},
        HTTP_X_CYPRESS_TOKEN=settings.CYPRESS_TOKEN,
    )
    SessionMiddleware(lambda request: None).process_request(request)
    request.session.save()

    response = CypressLoginDotGovAuthenticationOverride.as_view()(request)

    assert response.status_code == status.HTTP_200_OK
    assert request.session["session_scope"] == STANDARD_SESSION_SCOPE


@pytest.mark.django_db
def test_auth_check_endpoint_with_authenticated_user(api_client, user):
    """If user is authenticated auth_check should response status OK."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_200_OK
    assert user.is_authenticated is True
    assert response.data["authenticated"] is True
    assert response.data["user"]["first_name"] == user.first_name
    assert response.data["user"]["last_name"] == user.last_name
    assert response.data["user"]["email"] == user.username
    assert response.data["user"]["roles"] == []


@pytest.mark.django_db
def test_auth_check_endpoint_with_bad_user(api_client):
    """If the user doesn't exist, auth_check should not authenticate."""
    api_client.login(username="nonexistent", password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_auth_check_endpoint_with_unauthorized_email(api_client):
    """If the user has an email address not in the system it should not authenticate."""
    api_client.login(username="bademail@example.com", password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_auth_check_returns_authenticated(api_client, user):
    """If user is authenticated auth_check should return authenticated true."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert user.is_authenticated is True
    assert response.data["authenticated"] is True


@pytest.mark.django_db
def test_auth_check_returns_user_email(api_client, user):
    """If user is authenticated auth_check should return user data."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get(reverse("authorization-check"))
    assert response.data["user"]["email"] == user.username


@pytest.mark.django_db
def test_auth_check_returns_user_stt(api_client, user):
    """If user is authenticated auth_check should return user data."""
    api_client.login(username=user.username, password="test_password")
    serializer = UserProfileSerializer(user)
    response = api_client.get(reverse("authorization-check"))
    assert response.data["user"]["stt"] == serializer.data["stt"]


@pytest.mark.django_db
def test_auth_check_deactivated_user(api_client, deactivated_user):
    """If user is deactivated, return a response indicating the user is inactive."""
    user_authentication = api_client.login(
        username=deactivated_user.username, password="test_password"
    )
    response = api_client.get(reverse("authorization-check"))

    assert user_authentication is True
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_standard_session_authenticates_frontend_but_not_admin(
    api_client, admin_user
):
    """A regular TDP session should not authenticate the admin frontend."""
    api_client.login(username=admin_user.username, password="test_password")
    frontend_response = api_client.get(reverse("authorization-check"))
    admin_response = api_client.get(reverse("admin-authorization-check"))

    assert frontend_response.status_code == status.HTTP_200_OK
    assert frontend_response.data["authenticated"] is True
    assert frontend_response.data["user"]["email"] == admin_user.username
    assert admin_response.status_code == status.HTTP_200_OK
    assert admin_response.data["authenticated"] is False


@pytest.mark.django_db
def test_admin_session_authenticates_admin_but_not_frontend(
    api_client, admin_console_user, settings
):
    """An admin session should not authenticate the regular TDP frontend."""
    api_client.login(username=admin_console_user.username, password="test_password")
    _create_admin_session_from_standard(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    admin_response = api_client.get(reverse("admin-authorization-check"))
    frontend_response = api_client.get(reverse("authorization-check"))

    assert admin_response.status_code == status.HTTP_200_OK
    assert admin_response.data["authenticated"] is True
    assert admin_response.data["authorized"] is True
    assert frontend_response.status_code == status.HTTP_200_OK
    assert frontend_response.data["authenticated"] is False


@pytest.mark.django_db
def test_standard_and_admin_login_logout_end_to_end_state_sequence(
    api_client, admin_console_user, settings
):
    """Standard and admin app sessions should remain independently scoped."""
    settings.KEYCLOAK_DJANGO_CLIENT_ID = "tdp-django"
    settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
    settings.OIDC_OP_LOGOUT_ENDPOINT = (
        "https://keycloak.example.gov/realms/tdp/protocol/openid-connect/logout"
    )
    settings.KEYCLOAK_TDP_ADMIN_LOGOUT_ENDPOINT = (
        "https://keycloak.example.gov/realms/tdp-admin/protocol/openid-connect/logout"
    )

    _assert_auth_state(api_client, False, False)

    _login_standard_session(api_client, admin_console_user, settings)
    _assert_auth_state(api_client, True, False)

    _create_admin_session_from_standard(api_client, settings)
    assert (
        api_client.cookies[settings.SESSION_COOKIE_NAME].value
        != api_client.cookies[settings.ADMIN_SESSION_COOKIE_NAME].value
    )
    _assert_auth_state(api_client, True, True)

    response = api_client.get(reverse("canary-oidc-logout"))
    assert response.status_code == status.HTTP_302_FOUND
    assert _url_without_query(response.url) == settings.OIDC_OP_LOGOUT_ENDPOINT
    query_params = parse_qs(urlparse(response.url).query)
    assert query_params["id_token_hint"] == ["standard-id-token"]
    _assert_auth_state(api_client, False, True)

    _login_standard_session(api_client, admin_console_user, settings)
    _assert_auth_state(api_client, True, True)

    response = api_client.get(reverse("admin-oidc-logout"))
    assert response.status_code == status.HTTP_302_FOUND
    assert (
        _url_without_query(response.url) == settings.KEYCLOAK_TDP_ADMIN_LOGOUT_ENDPOINT
    )
    query_params = parse_qs(urlparse(response.url).query)
    assert query_params["id_token_hint"] == ["admin-id-token"]
    _assert_auth_state(api_client, True, False)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "initial_state,logout_route,expected_standard,expected_admin",
    [
        ("none", "canary-oidc-logout", False, False),
        ("none", "admin-oidc-logout", False, False),
        ("standard", "canary-oidc-logout", False, False),
        ("standard", "admin-oidc-logout", True, False),
        ("admin", "canary-oidc-logout", False, True),
        ("admin", "admin-oidc-logout", False, False),
        ("both", "canary-oidc-logout", False, True),
        ("both", "admin-oidc-logout", True, False),
    ],
)
def test_logout_state_matrix(
    api_client,
    admin_console_user,
    settings,
    initial_state,
    logout_route,
    expected_standard,
    expected_admin,
):
    """Each logout endpoint should clear only its matching session scope."""
    settings.KEYCLOAK_DJANGO_CLIENT_ID = "tdp-django"
    settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
    settings.OIDC_OP_LOGOUT_ENDPOINT = (
        "https://keycloak.example.gov/realms/tdp/protocol/openid-connect/logout"
    )
    settings.KEYCLOAK_TDP_ADMIN_LOGOUT_ENDPOINT = (
        "https://keycloak.example.gov/realms/tdp-admin/protocol/openid-connect/logout"
    )
    initial_auth_states = {
        "none": (False, False),
        "standard": (True, False),
        "admin": (False, True),
        "both": (True, True),
    }

    if initial_state == "standard":
        _login_standard_session(api_client, admin_console_user, settings)
    elif initial_state == "admin":
        _login_admin_session(api_client, admin_console_user, settings)
        del api_client.cookies[settings.SESSION_COOKIE_NAME]
    elif initial_state == "both":
        _login_admin_session(api_client, admin_console_user, settings)

    _assert_auth_state(api_client, *initial_auth_states[initial_state])

    response = api_client.get(reverse(logout_route))

    assert response.status_code == status.HTTP_302_FOUND
    if logout_route == "canary-oidc-logout" and initial_state in ("standard", "both"):
        assert _url_without_query(response.url) == settings.OIDC_OP_LOGOUT_ENDPOINT
        query_params = parse_qs(urlparse(response.url).query)
        assert query_params["client_id"] == ["tdp-django"]
        assert query_params["id_token_hint"] == ["standard-id-token"]
    elif logout_route == "admin-oidc-logout" and initial_state in ("admin", "both"):
        assert (
            _url_without_query(response.url)
            == settings.KEYCLOAK_TDP_ADMIN_LOGOUT_ENDPOINT
        )
        query_params = parse_qs(urlparse(response.url).query)
        assert query_params["client_id"] == ["tdp-admin"]
        assert query_params["id_token_hint"] == ["admin-id-token"]
    elif logout_route == "canary-oidc-logout":
        assert response.url == settings.FRONTEND_BASE_URL
    else:
        assert response.url == settings.ADMIN_FRONTEND_BASE_URL
    _assert_auth_state(api_client, expected_standard, expected_admin)


@pytest.mark.django_db
def test_forged_service_header_does_not_use_admin_session(
    api_client, admin_user, settings
):
    """A regular API request cannot opt into the admin session by header."""
    api_client.login(username=admin_user.username, password="test_password")
    _create_admin_session_from_standard(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    response = api_client.get(
        reverse("authorization-check"), HTTP_X_SERVICE_NAME="tdp-admin"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_standard_cookie_cannot_authenticate_admin(
    api_client, admin_user, settings
):
    """A standard signed session cannot be replayed as an admin session."""
    _login_standard_session(api_client, admin_user, settings)
    api_client.cookies[settings.ADMIN_SESSION_COOKIE_NAME] = api_client.cookies[
        settings.SESSION_COOKIE_NAME
    ].value

    response = api_client.get(reverse("admin-authorization-check"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_admin_cookie_cannot_authenticate_frontend(
    api_client, admin_user, settings
):
    """An admin signed session cannot be replayed as a standard session."""
    _login_admin_session(api_client, admin_user, settings)
    api_client.cookies[settings.SESSION_COOKIE_NAME] = api_client.cookies[
        settings.ADMIN_SESSION_COOKIE_NAME
    ].value

    response = api_client.get(reverse("authorization-check"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False


@pytest.mark.django_db
def test_admin_api_path_uses_admin_session(api_client, admin_console_user, settings):
    """Admin API traffic should use the admin session on the backend path."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"
    api_client.login(username=admin_console_user.username, password="test_password")
    _create_admin_session_from_standard(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    response = api_client.get(
        "/admin-api/v1/auth_check", HTTP_X_ADMIN_PROXY_TOKEN="server-only-token"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is True
    assert response.data["user"]["email"] == admin_console_user.username


@pytest.mark.django_db
def test_admin_api_path_rejects_missing_proxy_token(
    api_client, admin_user, settings
):
    """Admin API traffic should not be directly browser-callable."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"
    api_client.login(username=admin_user.username, password="test_password")
    _create_admin_session_from_standard(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    response = api_client.get("/admin-api/v1/auth_check")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_api_path_rejects_unauthenticated_session(api_client, settings):
    """Admin API traffic should require an authenticated admin session."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"

    response = api_client.get(
        "/admin-api/v1/auth_check", HTTP_X_ADMIN_PROXY_TOKEN="server-only-token"
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {
        "authenticated": False,
        "detail": "An admin-scoped session is required.",
    }


@pytest.mark.django_db
def test_admin_api_path_rejects_non_admin_session(api_client, user, settings):
    """Admin API traffic should require Django staff-superuser authorization."""
    settings.ADMIN_API_PROXY_TOKEN = "server-only-token"
    api_client.login(username=user.username, password="test_password")
    _create_admin_session_from_standard(api_client, settings)
    del api_client.cookies[settings.SESSION_COOKIE_NAME]

    response = api_client.get(
        "/admin-api/v1/auth_check", HTTP_X_ADMIN_PROXY_TOKEN="server-only-token"
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {
        "authenticated": True,
        "authorized": False,
        "detail": "User is not authorized for the admin console.",
    }


@pytest.mark.django_db
def test_admin_auth_check_allows_django_superuser_without_admin_group(
    api_client, admin_console_user, settings
):
    """Admin auth_check should authorize independently of the assigned role."""
    api_client.login(username=admin_console_user.username, password="test_password")
    _create_admin_session_from_standard(api_client, settings)
    response = api_client.get(reverse("admin-authorization-check"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is True
    assert response.data["authorized"] is True
    assert response.data["csrf"]


@pytest.mark.django_db
def test_admin_auth_check_rejects_non_admin(api_client, user, settings):
    """Admin auth_check should keep Django authoritative for admin authz."""
    api_client.login(username=user.username, password="test_password")
    _create_admin_session_from_standard(api_client, settings)
    response = api_client.get(reverse("admin-authorization-check"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["authenticated"] is True
    assert response.data["authorized"] is False


@pytest.mark.django_db
def test_admin_auth_check_rejects_unapproved_django_superuser(
    api_client, admin_console_user, settings
):
    """Admin auth_check should require Django superusers to be approved."""
    _login_admin_session(api_client, admin_console_user, settings)
    admin_console_user.account_approval_status = AccountApprovalStatusChoices.PENDING
    admin_console_user.save()

    response = api_client.get(reverse("admin-authorization-check"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["authenticated"] is True
    assert response.data["authorized"] is False


@pytest.mark.django_db
def test_admin_auth_check_rejects_staff_without_superuser(
    api_client, staff_user, settings
):
    """Staff status without superuser status should not grant admin access."""
    staff_user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    staff_user.save()
    _login_admin_session(api_client, staff_user, settings)

    response = api_client.get(reverse("admin-authorization-check"))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.data["authenticated"] is True
    assert response.data["authorized"] is False


@pytest.mark.django_db
def test_admin_auth_check_rejects_inactive_django_superuser(
    api_client, admin_console_user, settings
):
    """Admin auth_check should require Django superusers to be active."""
    _login_admin_session(api_client, admin_console_user, settings)
    admin_console_user.is_active = False
    admin_console_user.save()

    response = api_client.get(reverse("admin-authorization-check"))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["authenticated"] is False
    assert "authorized" not in response.data


@pytest.mark.django_db
def test_admin_login_uses_admin_keycloak_client(api_client, settings):
    """Admin login should initialize OIDC with the dedicated admin realm/client."""
    settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
    settings.KEYCLOAK_TDP_ADMIN_AUTHORIZATION_ENDPOINT = (
        "https://keycloak.example.gov/realms/tdp-admin/protocol/openid-connect/auth"
    )
    settings.ADMIN_FRONTEND_BASE_URL = "http://localhost:3001"
    response = api_client.get(reverse("admin-login-ams"))

    assert response.status_code == status.HTTP_302_FOUND
    assert _url_without_query(response["Location"]) == (
        settings.KEYCLOAK_TDP_ADMIN_AUTHORIZATION_ENDPOINT
    )
    query_params = parse_qs(urlparse(response["Location"]).query)
    assert query_params["client_id"] == ["tdp-admin"]
    assert query_params["kc_idp_hint"] == ["ams"]
    assert "/admin-auth/oidc/callback/" in query_params["redirect_uri"][0]
    state = query_params["state"][0]
    session = _client_session_from_cookie(
        api_client, settings.ADMIN_SESSION_COOKIE_NAME, settings
    )
    assert session["session_scope"] == "admin"
    assert "oidc_client" not in session
    assert session["oidc_clients"][state] == "tdp-admin"
    assert session["oidc_login_next"] == settings.ADMIN_FRONTEND_BASE_URL


@pytest.mark.django_db
def test_admin_login_preserves_allowed_admin_next_url(api_client, settings):
    """Admin login should return to the admin frontend when next is supplied."""
    settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
    settings.ADMIN_FRONTEND_BASE_URL = "http://localhost:3001"
    settings.OIDC_REDIRECT_ALLOWED_HOSTS = {"localhost:3001"}

    response = api_client.get(
        reverse("admin-login-dotgov"),
        {"next": "http://localhost:3001/users"},
    )

    assert response.status_code == status.HTTP_302_FOUND
    session = _client_session_from_cookie(
        api_client, settings.ADMIN_SESSION_COOKIE_NAME, settings
    )
    assert session["oidc_login_next"] == "http://localhost:3001/users"


@pytest.mark.django_db
def test_standard_login_clears_legacy_admin_client_marker(api_client):
    """Standard login should not inherit a stale unscoped admin client marker."""
    session = api_client.session
    session["oidc_client"] = "tdp-admin"
    session.save()

    response = api_client.get(reverse("v2-login-ams"))

    assert response.status_code == status.HTTP_302_FOUND
    query_params = parse_qs(urlparse(response["Location"]).query)
    assert query_params["client_id"] != ["tdp-admin"]
    assert api_client.session["session_scope"] == "standard"
    assert "oidc_client" not in api_client.session
