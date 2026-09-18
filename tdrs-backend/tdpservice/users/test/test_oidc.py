"""Tests for KeycloakOIDCBackend authentication backend."""

from importlib import import_module
import logging
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from django.core.exceptions import SuspiciousOperation, ValidationError
from django.test import RequestFactory
from django.urls import reverse

import pytest

from tdpservice.users.models import AccountApprovalStatusChoices
from tdpservice.users.oidc import (
    ADMIN_OIDC_CALLBACK_URL_NAME,
    ADMIN_OIDC_CLIENT,
    KeycloakOIDCBackend,
)
from tdpservice.users.test.factories import UserFactory

logger = logging.getLogger(__name__)


def _session_cookie(settings, data):
    """Return a signed session cookie with the provided data."""
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore()
    session.update(data)
    session.save()
    return session.session_key


@pytest.fixture
def backend():
    """Return a KeycloakOIDCBackend instance."""
    return KeycloakOIDCBackend()


@pytest.fixture
def request_factory():
    """Return a Django RequestFactory."""
    return RequestFactory()


class TestAuthenticateClientSelection:
    """Tests for request-scoped OIDC client selection."""

    def test_admin_client_is_scoped_to_one_authenticate_call(
        self, backend, request_factory, settings
    ):
        """Admin client credentials are restored and the session marker is cleared."""
        settings.KEYCLOAK_DJANGO_CLIENT_ID = "tdp-django"
        settings.KEYCLOAK_DJANGO_CLIENT_SECRET = "django-secret"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_SECRET = "admin-secret"

        backend.OIDC_RP_CLIENT_ID = "original-client"
        backend.OIDC_RP_CLIENT_SECRET = "original-secret"

        request = request_factory.get("/oidc/callback/", {"state": "admin-state"})
        request.session = {"oidc_clients": {"admin-state": "tdp-admin"}}

        seen_clients = []

        def fake_super_authenticate(self, request, **kwargs):
            seen_clients.append((self.OIDC_RP_CLIENT_ID, self.OIDC_RP_CLIENT_SECRET))
            return None

        with patch(
            "mozilla_django_oidc.auth.OIDCAuthenticationBackend.authenticate",
            fake_super_authenticate,
        ):
            backend.authenticate(request)

        assert seen_clients == [("tdp-admin", "admin-secret")]
        assert "oidc_clients" not in request.session
        assert backend.OIDC_RP_CLIENT_ID == "original-client"
        assert backend.OIDC_RP_CLIENT_SECRET == "original-secret"

    def test_default_client_is_used_after_admin_marker_is_consumed(
        self, backend, request_factory, settings
    ):
        """A reused backend instance does not leak admin credentials into later calls."""
        settings.KEYCLOAK_DJANGO_CLIENT_ID = "tdp-django"
        settings.KEYCLOAK_DJANGO_CLIENT_SECRET = "django-secret"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_SECRET = "admin-secret"

        seen_clients = []

        def fake_super_authenticate(self, request, **kwargs):
            seen_clients.append((self.OIDC_RP_CLIENT_ID, self.OIDC_RP_CLIENT_SECRET))
            return None

        admin_request = request_factory.get("/oidc/callback/", {"state": "admin-state"})
        admin_request.session = {"oidc_clients": {"admin-state": "tdp-admin"}}
        standard_request = request_factory.get(
            "/oidc/callback/", {"state": "standard-state"}
        )
        standard_request.session = {}

        with patch(
            "mozilla_django_oidc.auth.OIDCAuthenticationBackend.authenticate",
            fake_super_authenticate,
        ):
            backend.authenticate(admin_request)
            backend.authenticate(standard_request)

        assert seen_clients == [
            ("tdp-admin", "admin-secret"),
            ("tdp-django", "django-secret"),
        ]

    def test_admin_client_marker_is_scoped_to_callback_state(
        self, backend, request_factory, settings
    ):
        """Admin credentials are used only for the matching OIDC state."""
        settings.KEYCLOAK_DJANGO_CLIENT_ID = "tdp-django"
        settings.KEYCLOAK_DJANGO_CLIENT_SECRET = "django-secret"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_SECRET = "admin-secret"

        request = request_factory.get("/oidc/callback/", {"state": "admin-state"})
        request.session = {
            "oidc_clients": {
                "admin-state": "tdp-admin",
                "abandoned-state": "tdp-admin",
            }
        }

        seen_clients = []

        def fake_super_authenticate(self, request, **kwargs):
            seen_clients.append((self.OIDC_RP_CLIENT_ID, self.OIDC_RP_CLIENT_SECRET))
            return None

        with patch(
            "mozilla_django_oidc.auth.OIDCAuthenticationBackend.authenticate",
            fake_super_authenticate,
        ):
            backend.authenticate(request)

        assert seen_clients == [("tdp-admin", "admin-secret")]
        assert request.session["oidc_clients"] == {"abandoned-state": "tdp-admin"}

    def test_stale_admin_state_does_not_affect_standard_callback(
        self, backend, request_factory, settings
    ):
        """An abandoned admin state does not change credentials for a later login."""
        settings.KEYCLOAK_DJANGO_CLIENT_ID = "tdp-django"
        settings.KEYCLOAK_DJANGO_CLIENT_SECRET = "django-secret"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_SECRET = "admin-secret"

        request = request_factory.get("/oidc/callback/", {"state": "standard-state"})
        request.session = {"oidc_clients": {"abandoned-admin-state": "tdp-admin"}}

        seen_clients = []

        def fake_super_authenticate(self, request, **kwargs):
            seen_clients.append((self.OIDC_RP_CLIENT_ID, self.OIDC_RP_CLIENT_SECRET))
            return None

        with patch(
            "mozilla_django_oidc.auth.OIDCAuthenticationBackend.authenticate",
            fake_super_authenticate,
        ):
            backend.authenticate(request)

        assert seen_clients == [("tdp-django", "django-secret")]
        assert request.session["oidc_clients"] == {
            "abandoned-admin-state": "tdp-admin"
        }

    def test_admin_token_request_uses_admin_callback_uri(
        self, backend, request_factory, settings
    ):
        """Admin callbacks must exchange tokens with the admin redirect_uri."""
        settings.KEYCLOAK_DJANGO_CLIENT_ID = "tdp-django"
        settings.KEYCLOAK_DJANGO_CLIENT_SECRET = "django-secret"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_ID = "tdp-admin"
        settings.KEYCLOAK_TDP_ADMIN_CLIENT_SECRET = "admin-secret"

        request = request_factory.get(
            "/admin-auth/oidc/callback/",
            {"state": "admin-state", "code": "authorization-code"},
            secure=True,
            HTTP_HOST="auth.example.gov",
        )
        request.session = {}
        request._oidc_client = ADMIN_OIDC_CLIENT
        request._oidc_callback_url = ADMIN_OIDC_CALLBACK_URL_NAME
        token_payloads = []
        authenticated_user = object()

        def capture_token_payload(payload):
            token_payloads.append(payload.copy())
            return {"id_token": "id-token", "access_token": "access-token"}

        with (
            patch.object(backend, "get_token", side_effect=capture_token_payload),
            patch.object(
                backend,
                "verify_token",
                return_value={"email": "admin@example.gov"},
            ),
            patch.object(
                backend, "get_or_create_user", return_value=authenticated_user
            ),
        ):
            user = backend.authenticate(request, nonce="nonce")

        assert user is authenticated_user
        assert token_payloads == [
            {
                "client_id": "tdp-admin",
                "client_secret": "admin-secret",
                "grant_type": "authorization_code",
                "code": "authorization-code",
                "redirect_uri": "https://auth.example.gov/admin-auth/oidc/callback/",
            }
        ]
        assert not hasattr(backend, "_oidc_callback_url")


@pytest.mark.django_db
class TestAdminOIDCAuthenticationCallback:
    """Tests for the admin OIDC callback view."""

    def test_failed_callbacks_return_to_admin_frontend_login(
        self, api_client, settings
    ):
        """Generic OIDC failures should not redirect to the Django root."""
        settings.ADMIN_FRONTEND_BASE_URL = "http://localhost:3001"

        response = api_client.get(
            reverse("admin_oidc_authentication_callback"),
            {"state": "admin-state", "code": "authorization-code"},
        )

        assert response.status_code == 302
        parsed_url = urlparse(response.url)
        assert (
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            == "http://localhost:3001/login"
        )
        query_params = parse_qs(parsed_url.query)
        assert query_params["error"] == ["admin_login_failed"]
        assert query_params["message"] == ["Unable to complete admin sign in."]

    def test_validation_errors_return_to_admin_frontend_login(
        self, api_client, settings
    ):
        """Validation failures during admin login should render in the admin UI."""
        settings.ADMIN_FRONTEND_BASE_URL = "http://localhost:3001"
        message = (
            "Users other than Regional Staff, Developers, Data Analysts "
            "do not get assigned a location"
        )

        with patch(
            "mozilla_django_oidc.views.OIDCAuthenticationCallbackView.get",
            side_effect=ValidationError(message),
        ):
            response = api_client.get(
                reverse("admin_oidc_authentication_callback"),
                {"state": "admin-state", "code": "authorization-code"},
            )

        assert response.status_code == 302
        parsed_url = urlparse(response.url)
        assert (
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            == "http://localhost:3001/login"
        )
        query_params = parse_qs(parsed_url.query)
        assert query_params["error"] == ["admin_login_validation"]
        assert query_params["message"] == [message]

    def test_stale_callback_state_returns_to_admin_frontend_login(
        self, api_client, settings
    ):
        """Stale admin callback URLs should not render a backend error page."""
        settings.ADMIN_FRONTEND_BASE_URL = "http://localhost:3001"

        with patch(
            "mozilla_django_oidc.views.OIDCAuthenticationCallbackView.get",
            side_effect=SuspiciousOperation("OIDC callback state not found"),
        ):
            response = api_client.get(
                reverse("admin_oidc_authentication_callback"),
                {"state": "stale-state", "code": "authorization-code"},
            )

        assert response.status_code == 302
        parsed_url = urlparse(response.url)
        assert (
            f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            == "http://localhost:3001/login"
        )
        query_params = parse_qs(parsed_url.query)
        assert query_params["error"] == ["admin_login_failed"]


@pytest.mark.django_db
class TestKeycloakLogout:
    """Tests for app-scoped Keycloak logout behavior."""

    def test_standard_logout_does_not_end_keycloak_sso_or_admin_session(
        self, api_client, settings
    ):
        """Standard logout must only clear the standard Django session."""
        settings.FRONTEND_BASE_URL = "https://tdp.example.gov"
        settings.OIDC_OP_LOGOUT_ENDPOINT = (
            "https://keycloak.example.gov/realms/tdp/protocol/openid-connect/logout"
        )
        api_client.cookies[settings.SESSION_COOKIE_NAME] = _session_cookie(
            settings, {"oidc_id_token": "standard-id-token"}
        )
        api_client.cookies[settings.ADMIN_SESSION_COOKIE_NAME] = _session_cookie(
            settings, {"oidc_id_token": "admin-id-token"}
        )

        response = api_client.get(reverse("v2-oidc-logout"))

        assert response.status_code == 302
        assert response.url == settings.FRONTEND_BASE_URL
        assert settings.OIDC_OP_LOGOUT_ENDPOINT not in response.url
        assert "id_token_hint" not in response.url
        assert settings.SESSION_COOKIE_NAME in response.cookies
        assert settings.ADMIN_SESSION_COOKIE_NAME not in response.cookies

    def test_admin_logout_does_not_end_keycloak_sso_or_standard_session(
        self, api_client, settings
    ):
        """Admin logout must only clear the admin Django session."""
        settings.ADMIN_FRONTEND_BASE_URL = "https://admin.example.gov"
        settings.OIDC_OP_LOGOUT_ENDPOINT = (
            "https://keycloak.example.gov/realms/tdp/protocol/openid-connect/logout"
        )
        api_client.cookies[settings.SESSION_COOKIE_NAME] = _session_cookie(
            settings, {"oidc_id_token": "standard-id-token"}
        )
        api_client.cookies[settings.ADMIN_SESSION_COOKIE_NAME] = _session_cookie(
            settings, {"oidc_id_token": "admin-id-token"}
        )

        response = api_client.get(reverse("admin-oidc-logout"))

        assert response.status_code == 302
        assert response.url == settings.ADMIN_FRONTEND_BASE_URL
        assert settings.OIDC_OP_LOGOUT_ENDPOINT not in response.url
        assert "id_token_hint" not in response.url
        assert settings.ADMIN_SESSION_COOKIE_NAME in response.cookies
        assert settings.SESSION_COOKIE_NAME not in response.cookies


@pytest.mark.django_db
class TestFilterUsersByClaims:
    """Tests for KeycloakOIDCBackend.filter_users_by_claims."""

    def test_filter_by_hhs_id(self, backend):
        """Returns the user that matches the provided HHS ID."""
        user = UserFactory(hhs_id="ABC123456789")
        claims = {"hhs_id": "ABC123456789", "email": "other@test.com"}
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert str(result[0].id) == str(user.id)

    def test_filter_by_login_gov_uuid(self, backend):
        """Returns the user that matches the provided Login.gov UUID."""
        user = UserFactory(hhs_id=None)
        claims = {"login_gov_uuid": str(user.login_gov_uuid), "email": "other@test.com"}
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert str(result[0].id) == str(user.id)

    def test_filter_by_email_fallback(self, backend):
        """Falls back to an email lookup when stronger identifiers are missing."""
        user = UserFactory(login_gov_uuid=None, hhs_id=None)
        claims = {"email": user.email}
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert str(result[0].id) == str(user.id)

    def test_filter_returns_empty_for_unknown_user(self, backend):
        """Returns an empty list when no user matches the claims."""
        claims = {"email": "nonexistent@test.com"}
        result = backend.filter_users_by_claims(claims)
        assert result == []

    def test_hhs_id_takes_priority_over_login_gov_uuid(self, backend):
        """When both hhs_id and login_gov_uuid are in claims, hhs_id is checked first."""
        user_ams = UserFactory(hhs_id="AMS123456789", login_gov_uuid=None)
        user_logingov = UserFactory(hhs_id=None)

        claims = {
            "hhs_id": "AMS123456789",
            "login_gov_uuid": str(user_logingov.login_gov_uuid),
            "email": "someone@test.com",
        }
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert str(result[0].id) == str(user_ams.id)

    def test_hhs_id_falls_back_to_email_when_no_match(self, backend):
        """When hhs_id doesn't match, falls back to email lookup."""
        user = UserFactory(hhs_id="DIFFERENT123", login_gov_uuid=None)
        claims = {"hhs_id": "NOMATCH999999", "email": user.email}
        result = backend.filter_users_by_claims(claims)
        assert len(result) == 1
        assert str(result[0].id) == str(user.id)


@pytest.mark.django_db
class TestCreateUser:
    """Tests for KeycloakOIDCBackend.create_user."""

    def test_create_user_with_login_gov_uuid(self, backend):
        """Creates a user and stores the Login.gov UUID from claims."""
        claims = {
            "email": "newuser@test.com",
            "login_gov_uuid": "550e8400-e29b-41d4-a716-446655440000",
        }
        user = backend.create_user(claims)
        assert user is not None
        assert user.username == "newuser@test.com"
        assert user.email == "newuser@test.com"
        assert str(user.login_gov_uuid) == "550e8400-e29b-41d4-a716-446655440000"
        assert not user.has_usable_password()

    def test_create_user_with_hhs_id(self, backend):
        """Creates a user and stores the HHS ID from claims."""
        claims = {"email": "acfuser@acf.hhs.gov", "hhs_id": "HHS123456789"}
        user = backend.create_user(claims)
        assert user is not None
        assert user.hhs_id == "HHS123456789"

    def test_create_user_without_email_returns_none(self, backend):
        """Returns no user when the claims do not include an email address."""
        claims = {"login_gov_uuid": "some-uuid"}
        user = backend.create_user(claims)
        assert user is None


@pytest.mark.django_db
class TestUpdateUser:
    """Tests for KeycloakOIDCBackend.update_user."""

    def test_update_user_sets_hhs_id(self, backend):
        """Updates the user with a new HHS ID from claims."""
        user = UserFactory(hhs_id=None)
        claims = {"hhs_id": "NEWHHS123456"}
        updated = backend.update_user(user, claims)
        assert updated.hhs_id == "NEWHHS123456"

    def test_update_user_no_change_when_same(self, backend):
        """Leaves the HHS ID unchanged when the claim matches the current value."""
        user = UserFactory(hhs_id="EXISTING1234")
        claims = {"hhs_id": "EXISTING1234"}
        updated = backend.update_user(user, claims)
        assert updated.hhs_id == "EXISTING1234"

    def test_update_user_syncs_email_from_claims(self, backend):
        """Updates the stored email when the IdP reports a new one for the same user."""
        user = UserFactory(
            username="old_email@example.com",
            email="old_email@example.com",
            hhs_id=None,
        )
        claims = {
            "email": "new_email@example.com",
            "login_gov_uuid": str(user.login_gov_uuid),
        }

        updated = backend.update_user(user, claims)
        updated.refresh_from_db()

        assert updated.username == "new_email@example.com"
        assert updated.email == "new_email@example.com"


@pytest.mark.django_db
class TestVerifyClaims:
    """Tests for KeycloakOIDCBackend.verify_claims."""

    def test_rejects_missing_email(self, backend):
        """Rejects claims that do not include an email address."""
        claims = {"login_gov_uuid": "some-uuid"}
        assert backend.verify_claims(claims) is False

    def test_rejects_acf_user_via_login_gov(self, backend):
        """ACF staff (@acf.hhs.gov) must not authenticate via Login.gov."""
        UserFactory(
            username="staff@acf.hhs.gov",
            email="staff@acf.hhs.gov",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        claims = {
            "email": "staff@acf.hhs.gov",
            "identity_provider": "login-gov",
        }
        assert backend.verify_claims(claims) is False

    def test_rejects_hhs_user_via_login_gov(self, backend):
        """HHS staff (@hhs.gov) must not authenticate via Login.gov."""
        UserFactory(
            username="staff@hhs.gov",
            email="staff@hhs.gov",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        claims = {
            "email": "staff@hhs.gov",
            "identity_provider": "login-gov",
        }
        assert backend.verify_claims(claims) is False

    def test_allows_acf_user_via_ams(self, backend):
        """ACF staff authenticating via AMS should be allowed."""
        UserFactory(
            username="staff@acf.hhs.gov",
            email="staff@acf.hhs.gov",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        claims = {
            "email": "staff@acf.hhs.gov",
            "identity_provider": "ams",
        }
        assert backend.verify_claims(claims) is True

    def test_allows_hhs_user_via_ams(self, backend):
        """HHS staff authenticating via AMS should be allowed."""
        UserFactory(
            username="staff@hhs.gov",
            email="staff@hhs.gov",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        claims = {
            "email": "staff@hhs.gov",
            "identity_provider": "ams",
        }
        assert backend.verify_claims(claims) is True

    def test_allows_non_acf_user_via_login_gov(self, backend):
        """Non-ACF users should be able to use Login.gov."""
        claims = {
            "email": "grantee@example.com",
            "identity_provider": "login-gov",
        }
        assert backend.verify_claims(claims) is True

    def test_rejects_deactivated_user(self, backend):
        """Rejects users whose approval status is deactivated."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.DEACTIVATED,
        )
        claims = {
            "email": user.email,
            "login_gov_uuid": str(user.login_gov_uuid),
        }
        assert backend.verify_claims(claims) is False

    def test_rejects_inactive_user(self, backend):
        """Rejects users marked inactive in Django."""
        user = UserFactory(is_active=False)
        claims = {
            "email": user.email,
            "login_gov_uuid": str(user.login_gov_uuid),
        }
        assert backend.verify_claims(claims) is False

    def test_allows_approved_active_user(self, backend):
        """Allows users who are both approved and active."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
            is_active=True,
        )
        claims = {
            "email": user.email,
            "login_gov_uuid": str(user.login_gov_uuid),
        }
        assert backend.verify_claims(claims) is True

    def test_allows_new_user_not_yet_in_system(self, backend):
        """New users not yet in the system should pass verify_claims."""
        claims = {
            "email": "brandnew@test.com",
            "identity_provider": "login-gov",
        }
        assert backend.verify_claims(claims) is True
