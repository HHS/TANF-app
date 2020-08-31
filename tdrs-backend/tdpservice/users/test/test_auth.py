"""Test the custom authorization class."""
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

test_private_key = """
-----BEGIN RSA PRIVATE KEY-----
MIICWwIBAAKBgQCNPblYH0LCEubHfT8C/yDuv/V+iZic0B6kpjiO3LnZqv3fgldS
+XhkLFipCDm5QAe/r6JUEVEuIOmynX60rnRdSMDA5v6hI9fwl4ajc0zr7dlauQ7q
PSZ3P4oQwSgkv9hmglIVXlbs9Zghvjf9w0FAxGPL75KhKbcQ+5X5+E0WbwIDAQAB
AoGAPcz4QHrNNyYWHMvMun7v5gfQX2HNiS/3eIvSy5ABMiEDnLzngMLvzsUoti2H
NGuz+Efde3NoVgrItwL64gxDlbWaq9dwFC083dFbsruxoqA6Zj/DmboloPu24niv
HCjhJh8OAYXBHPf/5oy00VjQvAIvppcMVYIUgcDeHg3/UuECQQDbRQq8w4aPVmSR
P1xOsT8L6qXCBVe9Y0vL0ZsEHsRl4bMBJQRXzPjB4acTHsUw9q8NhoZgC60xcedP
elxuHbILAkEApOaTnYBP2Ly5yLO56wqaecJemb+Il4zvYIKXPNN7xrj3/kO8nGMm
OIabH2jMdv2k3Tgb+I7N2K9mQjse4LtvrQJAezQYDGhwuyl36IUJgM3m9vMpoBMQ
ccHRXPyxdWc0Q2rGAeaiwhLR017PWdb4RcLWKWtlJaJp9lZh+i5usRDOcQJAKm6q
zXyXD06BAAQ/cxvnZC1/6lA+9cBuWIdCI4TH9Prj1anYfuWEkEcS46Iz+uqJ4eLu
T6dvkLKRvbk42NtigQJAEZasjEA9FtBZL7ZSSTAs9X5OzPgMHOOukCjmyFaLfSO7
0wBNH/N1oe6U/mTeKdJktsnX1okYbcXxMkGnS2/rUQ==
-----END RSA PRIVATE KEY-----
"""


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

def test_generate_client_assertion():
    """Test client assertion generation."""
    os.environ["JWT_KEY"] = test_private_key
    assert generate_client_assertion() is not None

def test_generate_token_endpoint_parameters():
    """Test token endpoint parameter generation."""
    os.environ["JWT_KEY"] = test_private_key
    params = generate_token_endpoint_parameters("test_code")
    assert "client_assertion" in params
    assert "client_assertion_type" in params
    assert "code=test_code" in params
    assert "grant_type=authorization_code" in params
