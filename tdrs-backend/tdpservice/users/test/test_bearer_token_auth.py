"""Tests for KeycloakBearerTokenAuthentication and KeycloakClientRateThrottle."""

import logging
from unittest.mock import patch

from django.core.exceptions import SuspiciousOperation
from django.test import RequestFactory

import pytest

from rest_framework.exceptions import AuthenticationFailed

from tdpservice.users.authentication import KeycloakBearerTokenAuthentication
from tdpservice.users.models import AccountApprovalStatusChoices
from tdpservice.users.test.factories import UserFactory
from tdpservice.users.throttling import KeycloakClientRateThrottle

logger = logging.getLogger(__name__)


@pytest.fixture
def auth():
    """Return a KeycloakBearerTokenAuthentication instance."""
    return KeycloakBearerTokenAuthentication()


@pytest.fixture
def request_with_token():
    """Return a factory that builds a Django request with a Bearer token header."""
    factory = RequestFactory()

    def _build(token="dummy-jwt", path="/v1/users/me/"):
        return factory.get(path, HTTP_AUTHORIZATION=f"Bearer {token}")

    return _build


def _claims(**overrides):
    """Build a minimal valid Keycloak access-token payload."""
    base = {
        "email": "grantee@example.com",
        "identity_provider": "login-gov",
        "azp": "tdp-cli",
    }
    base.update(overrides)
    return base


class TestBearerHeaderParsing:
    """No JWKS calls — these requests never reach token verification."""

    def test_no_authorization_header_returns_none(self, auth):
        """A request without an Authorization header is not handled by this class."""
        request = RequestFactory().get("/v1/users/me/")
        assert auth.authenticate(request) is None

    def test_non_bearer_scheme_returns_none(self, auth):
        """Token / Basic / other schemes are ignored — let other auth classes handle."""
        request = RequestFactory().get(
            "/v1/users/me/", HTTP_AUTHORIZATION="Token abc123"
        )
        assert auth.authenticate(request) is None

    def test_empty_bearer_returns_none(self, auth):
        """A bare ``Bearer`` header with no token is not handled."""
        request = RequestFactory().get(
            "/v1/users/me/", HTTP_AUTHORIZATION="Bearer "
        )
        assert auth.authenticate(request) is None


@pytest.mark.django_db
class TestTokenVerification:
    """Cover JWT signature / claim-verification failure modes."""

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_invalid_signature_raises_authentication_failed(
        self, mock_verify, auth, request_with_token
    ):
        """A signature-verification error is surfaced as 401, not 500."""
        mock_verify.side_effect = SuspiciousOperation("bad signature")
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token())

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_missing_email_in_claims_rejects(
        self, mock_verify, auth, request_with_token
    ):
        """Claims without an email are rejected by ``verify_claims``."""
        mock_verify.return_value = {"azp": "tdp-cli"}  # no email
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token())

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_acf_user_via_login_gov_rejected(
        self, mock_verify, auth, request_with_token
    ):
        """An @acf.hhs.gov account using Login.gov is rejected by shared rules."""
        UserFactory(
            username="staff@acf.hhs.gov",
            email="staff@acf.hhs.gov",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        mock_verify.return_value = _claims(
            email="staff@acf.hhs.gov", identity_provider="login-gov"
        )
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token())

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_deactivated_user_rejected(
        self, mock_verify, auth, request_with_token
    ):
        """A deactivated user gets 401 even with a valid token."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.DEACTIVATED,
        )
        mock_verify.return_value = _claims(
            email=user.email, login_gov_uuid=str(user.login_gov_uuid)
        )
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token())

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_inactive_user_rejected(
        self, mock_verify, auth, request_with_token
    ):
        """A Django-inactive user gets 401."""
        user = UserFactory(is_active=False)
        mock_verify.return_value = _claims(
            email=user.email, login_gov_uuid=str(user.login_gov_uuid)
        )
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token())


@pytest.mark.django_db
class TestUserResolution:
    """Happy paths and user-resolution edge cases."""

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_existing_user_resolved_by_login_gov_uuid(
        self, mock_verify, auth, request_with_token
    ):
        """A valid token resolves to the existing user keyed by login_gov_uuid."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        mock_verify.return_value = _claims(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
        )
        result = auth.authenticate(request_with_token())
        assert result is not None
        resolved_user, token = result
        assert str(resolved_user.id) == str(user.id)
        assert token == "dummy-jwt"

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_existing_user_resolved_by_hhs_id(
        self, mock_verify, auth, request_with_token
    ):
        """``hhs_id`` claim takes priority over ``login_gov_uuid`` and email."""
        user = UserFactory(
            hhs_id="HHS999000111",
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        mock_verify.return_value = _claims(
            email="someone-else@test.com",
            hhs_id="HHS999000111",
            identity_provider="ams",
        )
        result = auth.authenticate(request_with_token())
        assert result is not None
        resolved_user, _ = result
        assert str(resolved_user.id) == str(user.id)

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_new_user_is_created_from_claims(
        self, mock_verify, auth, request_with_token
    ):
        """Tokens for users not yet in the system create a new Django user."""
        from tdpservice.users.models import User

        assert not User.objects.filter(username="brandnew@example.com").exists()
        mock_verify.return_value = _claims(
            email="brandnew@example.com",
            login_gov_uuid="550e8400-e29b-41d4-a716-446655440000",
            identity_provider="login-gov",
        )
        result = auth.authenticate(request_with_token())
        assert result is not None
        user, _ = result
        assert user.username == "brandnew@example.com"
        assert str(user.login_gov_uuid) == "550e8400-e29b-41d4-a716-446655440000"

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_multiple_user_match_raises_authentication_failed(
        self, mock_verify, auth, request_with_token
    ):
        """Two users sharing an email is treated as a security failure, not a guess."""
        UserFactory(username="dup@example.com", email="dup@example.com", hhs_id=None, login_gov_uuid=None)
        # A second account that would also match the email-fallback lookup.
        UserFactory.create(username="dup-alt", email="dup@example.com", hhs_id=None, login_gov_uuid=None)
        # filter_users_by_claims falls back to username lookup, which is unique,
        # so simulate the multi-match by patching the helper directly:
        with patch(
            "tdpservice.users.authentication.filter_users_by_claims"
        ) as mock_filter:
            from tdpservice.users.models import User

            mock_filter.return_value = list(User.objects.all())
            mock_verify.return_value = _claims(email="dup@example.com")
            with pytest.raises(AuthenticationFailed):
                auth.authenticate(request_with_token())


@pytest.mark.django_db
class TestAuditAndThrottleHook:
    """Audit logging + the request attribute used by KeycloakClientRateThrottle."""

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_authenticate_stashes_client_id_on_request(
        self, mock_verify, auth, request_with_token
    ):
        """``request._keycloak_client_id`` is set so the throttle can key off it."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        mock_verify.return_value = _claims(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
            azp="tdp-cli",
        )
        request = request_with_token()
        auth.authenticate(request)
        assert request._keycloak_client_id == "tdp-cli"

    @patch(
        "tdpservice.users.authentication.OIDCAuthenticationBackend.verify_token"
    )
    def test_audit_log_contains_client_id(
        self, mock_verify, auth, request_with_token, caplog
    ):
        """Each successful auth emits a log line tagged with the client_id."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        mock_verify.return_value = _claims(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
            azp="tdp-cli",
        )
        with caplog.at_level(logging.INFO, logger="tdpservice.users.authentication"):
            auth.authenticate(request_with_token())
        # The log line is queryable by client_id in Loki via the structured extra.
        record = next(
            (r for r in caplog.records if "Bearer token auth" in r.getMessage()),
            None,
        )
        assert record is not None
        assert getattr(record, "client_id", None) == "tdp-cli"
        assert str(getattr(record, "user_id", None)) == str(user.id)


class TestAuthenticateHeader:
    """``authenticate_header`` controls 401-vs-403 for denied requests."""

    def test_returns_none_for_non_bearer_request(self, auth):
        """No Bearer header → None so DRF preserves the historical 403."""
        request = RequestFactory().get("/v1/users/me/")
        assert auth.authenticate_header(request) is None

    def test_returns_bearer_challenge_when_token_present(
        self, auth, request_with_token
    ):
        """Invalid bearer token → Bearer realm challenge so DRF returns 401."""
        header = auth.authenticate_header(request_with_token())
        assert header is not None
        assert header.startswith("Bearer realm=")


class TestKeycloakClientRateThrottle:
    """Throttle keys off ``_keycloak_client_id``; non-bearer paths skip."""

    def test_returns_none_when_no_client_id(self):
        """Sessions and other auth paths pass through without throttling."""
        throttle = KeycloakClientRateThrottle()
        request = RequestFactory().get("/v1/users/me/")  # no _keycloak_client_id
        assert throttle.get_cache_key(request, view=None) is None

    def test_cache_key_uses_client_id(self):
        """The cache key is scoped per Keycloak client_id, not per user."""
        throttle = KeycloakClientRateThrottle()
        request = RequestFactory().get("/v1/users/me/")
        request._keycloak_client_id = "tdp-cli"
        key = throttle.get_cache_key(request, view=None)
        assert key is not None
        assert "tdp-cli" in key
        assert "keycloak_client" in key
