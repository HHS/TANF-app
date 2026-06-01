"""Tests for KeycloakBearerTokenAuthentication and KeycloakClientRateThrottle."""

import json
import logging
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from django.core.cache import cache
from django.test import RequestFactory, override_settings

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import jwt
import pytest

from rest_framework.exceptions import AuthenticationFailed

from tdpservice.users.authentication import KeycloakBearerTokenAuthentication
from tdpservice.users.models import AccountApprovalStatusChoices
from tdpservice.users.test.factories import UserFactory
from tdpservice.users.throttling import (
    KeycloakClientRateThrottle,
    get_keycloak_throttle_cache,
)

logger = logging.getLogger(__name__)

KEYCLOAK_TEST_ISSUER = "http://keycloak:8080/realms/tdp"
KEYCLOAK_TEST_JWKS_ENDPOINT = (
    f"{KEYCLOAK_TEST_ISSUER}/protocol/openid-connect/certs"
)
KEYCLOAK_TEST_KEY_ID = "bearer-token-test-key"


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


@pytest.fixture
def bearer_signing_key():
    """Return an RSA private key used to sign test Keycloak tokens."""
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture
def keycloak_jwks(settings, requests_mock, bearer_signing_key):
    """Mock Keycloak's JWKS endpoint for real signature verification."""
    jwk = json.loads(
        jwt.algorithms.RSAAlgorithm.to_jwk(bearer_signing_key.public_key())
    )
    jwk.update({"kid": KEYCLOAK_TEST_KEY_ID, "alg": "RS256", "use": "sig"})

    settings.OIDC_OP_JWKS_ENDPOINT = KEYCLOAK_TEST_JWKS_ENDPOINT
    settings.OIDC_RP_SIGN_ALGO = "RS256"
    settings.KEYCLOAK_ISSUER = KEYCLOAK_TEST_ISSUER
    requests_mock.get(KEYCLOAK_TEST_JWKS_ENDPOINT, json={"keys": [jwk]})

    return {"keys": [jwk]}


@pytest.fixture
def signed_bearer_token(bearer_signing_key, keycloak_jwks):
    """Return a factory that builds signed Keycloak-like access tokens."""

    def _build(omit_claims=(), **claim_overrides):
        now = datetime.now(timezone.utc)
        claims = _claims(
            aud="tdp-django",
            azp="tdp-cli",
            iss=KEYCLOAK_TEST_ISSUER,
            exp=now + timedelta(minutes=5),
            iat=now,
            typ="Bearer",
            login_gov_uuid="550e8400-e29b-41d4-a716-446655440000",
        )
        claims.update(claim_overrides)
        for claim in omit_claims:
            claims.pop(claim, None)

        private_key_pem = bearer_signing_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        return jwt.encode(
            claims,
            private_key_pem,
            algorithm="RS256",
            headers={"kid": KEYCLOAK_TEST_KEY_ID},
        )

    return _build


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

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
    def test_invalid_signature_raises_authentication_failed(
        self, mock_verify, auth, request_with_token
    ):
        """A signature-verification error is surfaced as 401, not 500."""
        mock_verify.side_effect = jwt.InvalidTokenError("bad signature")
        with pytest.raises(AuthenticationFailed) as exc_info:
            auth.authenticate(request_with_token())
        assert str(exc_info.value.detail) == "Invalid bearer token."

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
    def test_missing_email_in_claims_rejects(
        self, mock_verify, auth, request_with_token
    ):
        """Claims without an email are rejected by ``verify_claims``."""
        mock_verify.return_value = {"azp": "tdp-cli"}  # no email
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token())

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
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

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
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

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
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
class TestBearerTokenIntentVerification:
    """Use signed JWTs to prove bearer tokens are meant for this API flow."""

    def setup_method(self):
        """Keep JWKS cache assertions isolated from other signed-token tests."""
        cache.clear()

    def teardown_method(self):
        """Clear cached JWKS keys between tests."""
        cache.clear()

    def test_signed_tdp_cli_token_is_accepted(
        self, auth, request_with_token, signed_bearer_token
    ):
        """A signed token for tdp-cli and the Django API authenticates."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        token = signed_bearer_token(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
        )

        result = auth.authenticate(request_with_token(token))

        assert result is not None
        resolved_user, returned_token = result
        assert str(resolved_user.id) == str(user.id)
        assert returned_token == token

    def test_signed_token_with_wrong_azp_is_rejected(
        self, auth, request_with_token, signed_bearer_token
    ):
        """A token signed by Keycloak but issued to Grafana is not enough."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        token = signed_bearer_token(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
            azp="tdp-grafana",
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token(token))

    def test_signed_token_missing_azp_is_rejected(
        self, auth, request_with_token, signed_bearer_token
    ):
        """A bearer token must say which Keycloak client received it."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        token = signed_bearer_token(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
            omit_claims=("azp",),
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token(token))

    def test_signed_token_with_wrong_audience_is_rejected(
        self, auth, request_with_token, signed_bearer_token
    ):
        """A token must be intended for the Django API audience."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        token = signed_bearer_token(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
            aud="tdp-grafana",
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token(token))

    def test_signed_token_missing_audience_is_rejected(
        self, auth, request_with_token, signed_bearer_token
    ):
        """A token without an audience does not prove API intent."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        token = signed_bearer_token(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
            omit_claims=("aud",),
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token(token))

    def test_signed_token_with_wrong_issuer_is_rejected(
        self, auth, request_with_token, signed_bearer_token
    ):
        """A token must come from the expected Keycloak realm issuer."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        token = signed_bearer_token(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
            iss="http://keycloak:8080/realms/other",
        )

        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request_with_token(token))

    def test_expired_signed_token_is_rejected(
        self, auth, request_with_token, signed_bearer_token
    ):
        """A previously valid token cannot be used after expiration."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        token = signed_bearer_token(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
            exp=datetime.now(timezone.utc) - timedelta(minutes=5),
        )

        with pytest.raises(AuthenticationFailed) as exc_info:
            auth.authenticate(request_with_token(token))
        assert str(exc_info.value.detail) == "Bearer token has expired."

    def test_matching_jwks_key_is_cached_by_kid(
        self, auth, request_with_token, signed_bearer_token, requests_mock
    ):
        """Repeat bearer auth with the same kid should not refetch JWKS."""
        user = UserFactory(
            account_approval_status=AccountApprovalStatusChoices.APPROVED,
        )
        token = signed_bearer_token(
            email=user.email,
            login_gov_uuid=str(user.login_gov_uuid),
        )

        auth.authenticate(request_with_token(token))
        auth.authenticate(request_with_token(token))

        jwks_calls = [
            request
            for request in requests_mock.request_history
            if request.url == KEYCLOAK_TEST_JWKS_ENDPOINT
        ]
        assert len(jwks_calls) == 1


@pytest.mark.django_db
class TestUserResolution:
    """Happy paths and user-resolution edge cases."""

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
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

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
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

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
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

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
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

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
    def test_authenticate_stashes_throttle_identity_on_request(
        self, mock_verify, auth, request_with_token
    ):
        """The throttle identity scopes bearer limits by client and user."""
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
        assert request._keycloak_throttle_ident == f"tdp-cli:{user.id}"

    @patch("tdpservice.users.authentication._verify_keycloak_bearer_token")
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
    """Throttle keys off bearer client + user identity; non-bearer paths skip."""

    def test_returns_none_when_no_throttle_identity(self):
        """Sessions and other auth paths pass through without throttling."""
        throttle = KeycloakClientRateThrottle()
        request = RequestFactory().get("/v1/users/me/")
        assert throttle.get_cache_key(request, view=None) is None

    def test_cache_key_uses_client_and_user_identity(self):
        """The cache key is scoped per Keycloak client and Django user."""
        throttle = KeycloakClientRateThrottle()
        request = RequestFactory().get("/v1/users/me/")
        request._keycloak_throttle_ident = "tdp-cli:123"
        key = throttle.get_cache_key(request, view=None)
        assert key is not None
        assert "tdp-cli" in key
        assert "123" in key
        assert "keycloak_client" in key

    def test_same_client_different_users_get_different_cache_keys(self):
        """One noisy tdp-cli user should not throttle every other tdp-cli user."""
        throttle = KeycloakClientRateThrottle()
        first_request = RequestFactory().get("/v1/users/me/")
        second_request = RequestFactory().get("/v1/users/me/")
        first_request._keycloak_throttle_ident = "tdp-cli:123"
        second_request._keycloak_throttle_ident = "tdp-cli:456"

        first_key = throttle.get_cache_key(first_request, view=None)
        second_key = throttle.get_cache_key(second_request, view=None)

        assert first_key != second_key

    @override_settings(
        CACHES={
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            }
        }
    )
    def test_cache_falls_back_to_default_when_throttle_alias_is_missing(self):
        """Management commands should not fail if settings omit throttle cache."""
        cache = get_keycloak_throttle_cache()

        assert cache is not None
