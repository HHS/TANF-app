"""Tests for the views in the security app."""

import logging
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import Group
from django.test import Client
from django.urls import reverse

import jwt
import pytest
from rest_framework import status
from rest_framework.authtoken.models import Token

from tdpservice.security.models import SecurityEventType
from tdpservice.security.views import token_is_valid
from tdpservice.users.models import AccountApprovalStatusChoices, User

client = Client()

logger = logging.getLogger(__name__)


@pytest.fixture
def token():
    """Return a DRF token."""
    user = User.objects.create(username="testuser")
    token = Token.objects.create(user=user)
    return token


@pytest.mark.django_db
def test_token_is_valid(token):
    """Test token_is_valid function."""
    logger.info(token.__dict__)
    assert token_is_valid(token) is True
    token.created = token.created.replace(year=2000)
    # token.save()
    assert token_is_valid(token) is False


@pytest.mark.django_db
def test_generate_new_token(client):
    """Test generate_new_token function."""
    url = reverse("get-new-token")
    # assert if user is not authenticated
    response = client.get(url)
    assert response.status_code == 302

    # assert if user is not ofa_sys_admin
    user = User.objects.create_user(username="testuser", password="testpassword")
    user.save()
    client.login(username="testuser", password="testpassword")
    response = client.get(url)
    assert response.status_code == 302

    # assert if user is not approved
    user.account_approval_status = AccountApprovalStatusChoices.PENDING
    user.groups.add(Group.objects.get(name="OFA System Admin"))
    user.save()
    client.login(username="testuser", password="testpassword")
    response = client.get(url)
    assert response.status_code == 302

    # assert if token is valid
    user.account_approval_status = AccountApprovalStatusChoices.APPROVED
    user.save()

    client.login(username="testuser", password="testpassword")
    url = reverse("get-new-token")
    response = client.get(url)
    assert response.status_code == 200
    assert response.data == str(Token.objects.get(user=user))


class TestSecurityEventTokenView:
    """Tests for the SecurityEventTokenView class."""

    @pytest.fixture
    def mock_sub_claim(self):
        """Mock the sub claim."""
        return "67f4cbf5-1615-4aa4-9e63-2f3b270acf05"

    @pytest.fixture
    def mock_jwt_token(self):
        """Return a mock JWT token.

        Payload:
          {
            "events": {
                "https://schemas.openid.net/secevent/risc/event-type/account-disabled": {
                "subject": {
                    "sub": "67f4cbf5-1615-4aa4-9e63-2f3b270acf05"
                }
                }
            },
            "iss": "https://login.gov",
            "iat": 1620000000,
            "jti": "test_jti"
          }
        """
        return "eyJhbGciOiJSUzI1NiIsImtpZCI6InRlc3Rfa2lkIn0.eyJldmVudHMiOnsiaHR0cHM6Ly9zY2hlbWFzLm9wZW5pZC5uZXQvc2VjZXZlbnQvcmlzYy9ldmVudC10eXBlL2FjY291bnQtZGlzYWJsZWQiOnsic3ViamVjdCI6eyJzdWIiOiI2N2Y0Y2JmNS0xNjE1LTRhYTQtOWU2My0yZjNiMjcwYWNmMDUifX19LCJpc3MiOiJodHRwczovL2xvZ2luLmdvdiIsImlhdCI6MTYyMDAwMDAwMCwianRpIjoidGVzdF9qdGkifQ.signature"

    @pytest.fixture
    def mock_well_known_config(self):
        """Return a mock well-known config."""
        return {"jwks_uri": "https://login.gov/jwks"}

    @pytest.fixture
    def mock_certs(self):
        """Return mock certificates."""
        return {
            "keys": [
                {
                    "kid": "test_kid",
                    "kty": "RSA",
                    "n": "test_n",
                    "e": "AQAB",
                    "use": "sig",
                    "alg": "RS256",
                }
            ]
        }

    @pytest.fixture
    def mock_public_key(self):
        """Return a mock public key."""
        return MagicMock()

    @pytest.fixture
    def mock_decoded_jwt(self, mock_sub_claim):
        """Return a mock decoded JWT."""
        return {
            "events": {
                SecurityEventType.ACCOUNT_DISABLED: {"subject": {"sub": mock_sub_claim}}
            },
            "iss": "https://login.gov",
            "iat": 1620000000,
            "jti": "test_jti",
        }

    @pytest.mark.django_db
    @patch("tdpservice.security.views.requests.get")
    @patch("tdpservice.security.views.jwt.get_unverified_header")
    @patch("tdpservice.security.views.jwt.decode")
    @patch("tdpservice.security.views.jwt.algorithms.RSAAlgorithm.from_jwk")
    @patch("tdpservice.security.views.SecurityEventHandler.handle_event")
    def test_valid_security_event_token(
        self,
        mock_handle_event,
        mock_from_jwk,
        mock_decode,
        mock_get_unverified_header,
        mock_requests_get,
        mock_jwt_token,
        mock_well_known_config,
        mock_certs,
        mock_public_key,
        mock_decoded_jwt,
        client,
        mock_sub_claim,
    ):
        """Test valid security event token."""
        # Configure mocks
        mock_requests_get.side_effect = [
            MagicMock(json=lambda: mock_well_known_config),
            MagicMock(json=lambda: mock_certs),
        ]
        mock_get_unverified_header.return_value = {"kid": "test_kid"}
        mock_from_jwk.return_value = mock_public_key
        mock_decode.return_value = mock_decoded_jwt

        # Make request
        url = reverse("event-token")
        response = client.post(
            url, data=mock_jwt_token, content_type="application/secevent+jwt"
        )

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        mock_handle_event.assert_called_once_with(
            SecurityEventType.ACCOUNT_DISABLED,
            {"subject": {"sub": mock_sub_claim}},
            mock_decoded_jwt,
        )

    @pytest.mark.django_db
    def test_invalid_content_type(self, client):
        """Test invalid content type."""
        url = reverse("event-token")
        response = client.post(url, data="test_token", content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b"Invalid content type" in response.content

    @pytest.mark.django_db
    @patch("tdpservice.security.views.requests.get")
    @patch("tdpservice.security.views.jwt.get_unverified_header")
    def test_missing_kid(
        self,
        mock_get_unverified_header,
        mock_requests_get,
        mock_well_known_config,
        mock_certs,
        mock_jwt_token,
        client,
    ):
        """Test missing kid in JWT header."""
        # Configure mocks
        mock_requests_get.side_effect = [
            MagicMock(json=lambda: mock_well_known_config),
            MagicMock(json=lambda: mock_certs),
        ]
        mock_get_unverified_header.return_value = {}  # No kid

        # Make request
        url = reverse("event-token")
        response = client.post(
            url, data=mock_jwt_token, content_type="application/secevent+jwt"
        )

        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b"No 'kid' found in JWT header" in response.content

    @pytest.mark.django_db
    @patch("tdpservice.security.views.requests.get")
    @patch("tdpservice.security.views.jwt.get_unverified_header")
    def test_no_public_key_for_kid(
        self,
        mock_get_unverified_header,
        mock_requests_get,
        mock_well_known_config,
        mock_jwt_token,
        client,
    ):
        """Test no public key found for kid."""
        # Configure mocks
        mock_requests_get.side_effect = [
            MagicMock(json=lambda: mock_well_known_config),
            MagicMock(json=lambda: {"keys": []}),  # No keys matching the kid
        ]
        mock_get_unverified_header.return_value = {"kid": "test_kid"}

        # Make request
        url = reverse("event-token")
        response = client.post(
            url, data=mock_jwt_token, content_type="application/secevent+jwt"
        )

        # Assertions
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b"No public key found for kid" in response.content

    @pytest.mark.django_db
    @patch("tdpservice.security.views.requests.get")
    @patch("tdpservice.security.views.jwt.get_unverified_header")
    @patch("tdpservice.security.views.jwt.decode")
    @patch("tdpservice.security.views.jwt.algorithms.RSAAlgorithm.from_jwk")
    def test_invalid_jwt(
        self,
        mock_from_jwk,
        mock_decode,
        mock_get_unverified_header,
        mock_requests_get,
        mock_well_known_config,
        mock_certs,
        mock_public_key,
        mock_jwt_token,
        client,
    ):
        """Test invalid JWT token."""
        mock_requests_get.side_effect = [
            MagicMock(json=lambda: mock_well_known_config),
            MagicMock(json=lambda: mock_certs),
        ]
        mock_get_unverified_header.return_value = {"kid": "test_kid"}
        mock_from_jwk.return_value = mock_public_key
        mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")

        url = reverse("event-token")
        response = client.post(
            url, data=mock_jwt_token, content_type="application/secevent+jwt"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b"Invalid token" in response.content

    @pytest.mark.django_db
    @patch("tdpservice.security.views.requests.get")
    @patch("tdpservice.security.views.jwt.get_unverified_header")
    @patch("tdpservice.security.views.jwt.decode")
    @patch("tdpservice.security.views.jwt.algorithms.RSAAlgorithm.from_jwk")
    def test_missing_events(
        self,
        mock_from_jwk,
        mock_decode,
        mock_get_unverified_header,
        mock_requests_get,
        mock_well_known_config,
        mock_certs,
        mock_public_key,
        mock_jwt_token,
        client,
    ):
        """Test JWT with missing events."""
        mock_requests_get.side_effect = [
            MagicMock(json=lambda: mock_well_known_config),
            MagicMock(json=lambda: mock_certs),
        ]
        mock_get_unverified_header.return_value = {"kid": "test_kid"}
        mock_from_jwk.return_value = mock_public_key
        mock_decode.return_value = {
            "iss": "https://login.gov",
            "iat": 1620000000,
            "jti": "test_jti",
        }

        url = reverse("event-token")
        response = client.post(
            url, data=mock_jwt_token, content_type="application/secevent+jwt"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert b"No events found in JWT" in response.content

    @pytest.mark.django_db
    @patch("tdpservice.security.views.requests.get")
    @patch("tdpservice.security.views.jwt.get_unverified_header")
    @patch("tdpservice.security.views.jwt.decode")
    @patch("tdpservice.security.views.jwt.algorithms.RSAAlgorithm.from_jwk")
    @patch("tdpservice.security.views.SecurityEventHandler.handle_event")
    def test_handler_exception(
        self,
        mock_handle_event,
        mock_from_jwk,
        mock_decode,
        mock_get_unverified_header,
        mock_requests_get,
        mock_well_known_config,
        mock_certs,
        mock_public_key,
        mock_decoded_jwt,
        mock_jwt_token,
        client,
    ):
        """Test exception in event handler."""
        mock_requests_get.side_effect = [
            MagicMock(json=lambda: mock_well_known_config),
            MagicMock(json=lambda: mock_certs),
        ]
        mock_get_unverified_header.return_value = {"kid": "test_kid"}
        mock_from_jwk.return_value = mock_public_key
        mock_decode.return_value = mock_decoded_jwt
        mock_handle_event.side_effect = Exception("Handler error")

        url = reverse("event-token")
        response = client.post(
            url, data=mock_jwt_token, content_type="application/secevent+jwt"
        )

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
