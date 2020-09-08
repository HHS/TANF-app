"""Test the custom authorization class."""
import base64
import os
import uuid
import pytest
from rest_framework import status

from ..api.utils import (
    generate_client_assertion,
    generate_jwt_from_jwks,
    generate_token_endpoint_parameters,
    response_internal,
    validate_nonce_and_state,
)
from ..authentication import CustomAuthentication

test_private_key = base64.b64decode(os.environ["JWT_CERT_TEST"]).decode("utf-8")


class MockRequest:
    """Mock request class."""

    def __init__(self, status_code=status.HTTP_200_OK, data=None):
        self.status_code = status_code
        self.data = data

    def json(self):
        """Return data."""
        return self.data


@pytest.mark.django_db
def test_authentication(user):
    """Test authentication method."""
    auth = CustomAuthentication()
    authenticated_user = auth.authenticate(username=user.username)
    assert authenticated_user.username == user.username


@pytest.mark.django_db
def test_get_user(user):
    """Test get_user method."""
    auth = CustomAuthentication()
    found_user = auth.get_user(user.pk)
    assert found_user.username == user.username


@pytest.mark.django_db
def test_get_non_user(user):
    """Test that an invalid user does not return a user."""
    test_uuid = uuid.uuid1()
    auth = CustomAuthentication()
    nonuser = auth.get_user(test_uuid)
    assert nonuser is None


def test_oidc_auth(api_client):
    """Test login url redirects."""
    response = api_client.get("/v1/login/oidc")
    assert response.status_code == status.HTTP_302_FOUND


def test_oidc_logout(api_client):
    """Test logout url redirects."""
    response = api_client.get("/v1/logout/oidc")
    assert response.status_code == status.HTTP_302_FOUND


def test_oidc_logout_with_token(api_client):
    """Test logging out with token redirects and token is removed."""
    session = api_client.session
    session["token"] = "abcd"
    session.save()
    response = api_client.get("/v1/logout/oidc")
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_logout(api_client, user):
    """Test logout."""
    api_client.login(username=user.username, password="test_password")
    response = api_client.get("/v1/logout")
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_without_code(api_client):
    """Test login redirects without code."""
    response = api_client.get("/v1/login", {"state": "dummy"})
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_fails_without_state(api_client):
    """Test login redirects without state."""
    response = api_client.get("/v1/login", {"code": "dummy"})
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_fails_with_bad_data(api_client):
    """Test login fails with bad data."""
    response = api_client.get("/v1/login", {"code": "dummy", "state": "dummy"})
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_response_internal(user):
    """Test response internal works."""
    response = response_internal(
        user, status_message="hello", id_token={"fake": "stuff"}
    )
    assert response.status_code == status.HTTP_200_OK


def test_generate_jwt_from_jwks(mocker):
    """Test JWT generation."""
    mock_get = mocker.patch("requests.get")
    jwk = {
        "kty": "EC",
        "crv": "P-256",
        "x": "f83OJ3D2xF1Bg8vub9tLe1gHMzV76e8Tus9uPHvRVEU",
        "y": "x_FEzRu9m36HLN_tue659LNpXW6pCyStikYjKIWI5a0",
        "kid": "Public key used in JWS spec Appendix A.3 example",
    }
    mock_get.return_value = MockRequest(data={"keys": [jwk]})
    assert generate_jwt_from_jwks() is not None


def test_validate_nonce_and_state():
    """Test nonece and state validation."""
    assert validate_nonce_and_state("x", "y", "x", "y") is True
    assert validate_nonce_and_state("x", "z", "x", "y") is False
    assert validate_nonce_and_state("x", "y", "y", "x") is False
    assert validate_nonce_and_state("x", "z", "y", "y") is False


@pytest.mark.skipif(not test_private_key, reason="No test private key set")
def test_generate_client_assertion():
    """Test client assertion generation."""
    os.environ["JWT_KEY"] = test_private_key
    assert generate_client_assertion() is not None


@pytest.mark.skipif(not test_private_key, reason="No test private key set")
def test_generate_token_endpoint_parameters():
    """Test token endpoint parameter generation."""
    os.environ["JWT_KEY"] = test_private_key
    params = generate_token_endpoint_parameters("test_code")
    assert "client_assertion" in params
    assert "client_assertion_type" in params
    assert "code=test_code" in params
    assert "grant_type=authorization_code" in params
