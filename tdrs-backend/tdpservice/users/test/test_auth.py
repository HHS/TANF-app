"""Test the custom authorization class."""
import os
import uuid
import time
import secrets
import pytest
import jwt
import datetime
from rest_framework import status
from django.core.exceptions import SuspiciousOperation
from rest_framework.test import APIRequestFactory
from ..api.login import TokenAuthorizationOIDC
from ..api.logout_redirect_oidc import LogoutRedirectOIDC

from ..api.utils import (
    generate_client_assertion,
    generate_jwt_from_jwks,
    generate_token_endpoint_parameters,
    response_internal,
    validate_nonce_and_state,
)
from ..authentication import CustomAuthentication
from ..models import User

test_private_key = os.environ["JWT_CERT_TEST"]


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


def test_oidc_logout_without_token(api_client):
    """Test logout redirect with token missing."""
    response = api_client.get("/v1/logout/oidc")
    assert response.status_code == status.HTTP_302_FOUND


def test_oidc_logout_with_token(api_client):
    """Test logout redirect with token present."""
    factory = APIRequestFactory()
    view = LogoutRedirectOIDC.as_view()
    request = factory.get("/v1/logout/oidc")
    request.session = api_client.session
    request.session["token"] = "testtoken"
    response = view(request)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_auth_update(api_client, user):
    """Test session update."""
    api_client.login(username=user.username, password="test_password")

    api_client.get("/v1/auth_check")
    c1 = api_client.cookies.get('id_token')
    e1 = datetime.datetime.strptime(c1["expires"], "%a, %d %b %Y %H:%M:%S %Z")
    time.sleep(1)

    api_client.get("/v1/auth_check")
    c2 = api_client.cookies.get('id_token')
    e2 = datetime.datetime.strptime(c2["expires"], "%a, %d %b %Y %H:%M:%S %Z")

    assert e1 < e2


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
def test_login_with_valid_state_and_code(mocker, api_client):
    """Test login with state and code."""
    os.environ["JWT_KEY"] = test_private_key
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    decoded_token = {
        "email": "test@example.com",
        "email_verified": True,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": "b2d2d115-1d7e-4579-b9d6-f8e84f4f56ca",
        "verified_at": 1577854800,
    }
    mock_post.return_value = MockRequest(data=token)
    mock_decode.return_value = decoded_token
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_with_existing_token(mocker, api_client):
    """Login should proceed when token already exists."""
    os.environ["JWT_KEY"] = test_private_key
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    decoded_token = {
        "email": "test@example.com",
        "email_verified": True,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": "b2d2d115-1d7e-4579-b9d6-f8e84f4f56ca",
        "verified_at": 1577854800,
    }
    mock_post.return_value = MockRequest(data=token)
    mock_decode.return_value = decoded_token
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["token"] = "testtoken"
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_with_general_exception(mocker):
    """Test login with state and code."""
    os.environ["JWT_KEY"] = test_private_key
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    decoded_token = {
        "email": "test@example.com",
        "email_verified": True,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": "b2d2d115-1d7e-4579-b9d6-f8e84f4f56ca",
        "verified_at": 1577854800,
    }
    mock_post.return_value = MockRequest(data=token)
    mock_decode.return_value = decoded_token
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    # A custom session will throw a general exception
    request.session = {}
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "error": (
            "Email verified, but experienced internal issue " "with login/registration."
        )
    }


@pytest.mark.django_db
def test_login_with_inactive_user(mocker, api_client, inactive_user):
    """Login with inactive user should error and return message."""
    os.environ["JWT_KEY"] = test_private_key
    inactive_user.username = "test_inactive@example.com"
    inactive_user.save()
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    decoded_token = {
        "email": "test_inactive@example.com",
        "email_verified": True,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": inactive_user.login_gov_uuid,
        "verified_at": 1577854800,
    }
    mock_post.return_value = MockRequest(data=token)
    mock_decode.return_value = decoded_token
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {
        "error": f'Login failed, user account is inactive: {inactive_user.username}'
    }


@pytest.mark.django_db
def test_login_with_existing_user(mocker, api_client, user):
    """Login should work with existing user."""
    os.environ["JWT_KEY"] = test_private_key
    user.username = "test_existing@example.com"
    user.save()
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    decoded_token = {
        "email": "test_existing@example.com",
        "email_verified": True,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": user.login_gov_uuid,
        "verified_at": 1577854800,
    }
    mock_post.return_value = MockRequest(data=token)
    mock_decode.return_value = decoded_token
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_with_old_email(mocker, api_client, user):
    """Login should work with existing user."""
    os.environ["JWT_KEY"] = test_private_key
    user.username = "test_old_email@example.com"
    user.save()
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    decoded_token = {
        "email": "test_new_email@example.com",
        "email_verified": True,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": user.login_gov_uuid,
        "verified_at": 1577854800,
    }
    mock_post.return_value = MockRequest(data=token)
    mock_decode.return_value = decoded_token
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)
    # Ensure the user's username was updated with new email.
    assert User.objects.filter(username="test_new_email@example.com").exists()
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_with_initial_superuser(mocker, api_client, user):
    """Login should work with existing user."""
    # How to set os vars for sudo su??
    os.environ["JWT_KEY"] = test_private_key
    os.environ["DJANGO_SU_NAME"] = "test_superuser@example.com"
    user.username = "test_superuser@example.com"
    user.login_gov_uuid = None
    user.save()
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    decoded_token = {
        "email": "test_superuser@example.com",
        "email_verified": True,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": "b2d2d115-1d7e-4579-b9d6-f8e84f4f66ca",
        "verified_at": 1577854800,
    }
    mock_post.return_value = MockRequest(data=token)
    mock_decode.return_value = decoded_token
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)

    user = User.objects.get(username="test_superuser@example.com")
    assert str(user.login_gov_uuid) == decoded_token["sub"]
    assert response.status_code == status.HTTP_302_FOUND


@pytest.mark.django_db
def test_login_with_expired_token(mocker, api_client):
    """Login should proceed when token already exists."""
    os.environ["JWT_KEY"] = test_private_key
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    mock_decode.side_effect = jwt.ExpiredSignatureError()
    mock_post.return_value = MockRequest(data=token)
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.data == {"error": "The token is expired."}


@pytest.mark.django_db
def test_login_with_bad_validation_code(mocker, api_client):
    """Login should error with a bad validatino code."""
    os.environ["JWT_KEY"] = test_private_key
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    mock_post.return_value = MockRequest(
        data={}, status_code=status.HTTP_400_BAD_REQUEST
    )
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {
        "error": "Invalid Validation Code Or OpenID Connect Authenticator Down!"
    }


@pytest.mark.django_db
def test_login_with_bad_nonce_and_state(mocker, api_client):
    """Login should error with a bad nonce and state."""
    os.environ["JWT_KEY"] = test_private_key
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    decoded_token = {
        "email": "test@example.com",
        "email_verified": True,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": "b2d2d115-1d7e-4579-b9d6-f8e84f4f56ca",
        "verified_at": 1577854800,
    }
    mock_post.return_value = MockRequest(data=token)
    mock_decode.return_value = decoded_token
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["state_nonce_tracker"] = {
        "nonce": "badnonce",
        "state": "badstate",
        "added_on": time.time(),
    }
    with pytest.raises(SuspiciousOperation):
        view(request)


@pytest.mark.django_db
def test_login_with_email_unverified(mocker, api_client):
    """Login should faild with unverified email."""
    os.environ["JWT_KEY"] = test_private_key
    nonce = "testnonce"
    state = "teststate"
    code = secrets.token_hex(32)
    mock_post = mocker.patch("tdpservice.users.api.login.requests.post")
    token = {
        "access_token": "hhJES3wcgjI55jzjBvZpNQ",
        "token_type": "Bearer",
        "expires_in": 3600,
        "id_token": os.environ["MOCK_TOKEN"],
    }
    mock_decode = mocker.patch("tdpservice.users.api.login.jwt.decode")
    decoded_token = {
        "email": "test@example.com",
        "email_verified": False,
        "nonce": nonce,
        "iss": "https://idp.int.identitysandbox.gov",
        "sub": "b2d2d115-1d7e-4579-b9d6-f8e84f4f56ca",
        "verified_at": 1577854800,
    }
    mock_post.return_value = MockRequest(data=token)
    mock_decode.return_value = decoded_token
    factory = APIRequestFactory()
    view = TokenAuthorizationOIDC.as_view()
    request = factory.get("/v1/login", {"state": state, "code": code})
    request.session = api_client.session
    request.session["state_nonce_tracker"] = {
        "nonce": nonce,
        "state": state,
        "added_on": time.time(),
    }
    response = view(request)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data == {"error": "Unverified email!"}


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


@pytest.mark.django_db
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


@pytest.mark.django_db
def test_validate_nonce_and_state():
    """Test nonece and state validation."""
    assert validate_nonce_and_state("x", "y", "x", "y") is True
    assert validate_nonce_and_state("x", "z", "x", "y") is False
    assert validate_nonce_and_state("x", "y", "y", "x") is False
    assert validate_nonce_and_state("x", "z", "y", "y") is False


@pytest.mark.django_db
def test_generate_client_assertion_base64():
    """Test client assertion generation with base64 encoded key."""
    os.environ["JWT_KEY"] = test_private_key
    assert generate_client_assertion() is not None


@pytest.mark.django_db
def test_generate_client_assertion_pem():
    """Test client assertion generation with PEM key."""
    from base64 import b64decode
    os.environ["JWT_KEY"] = b64decode(test_private_key).decode("utf-8")
    utf8_jwt_key = generate_client_assertion()
    assert utf8_jwt_key is not None


@pytest.mark.django_db
def test_generate_token_endpoint_parameters():
    """Test token endpoint parameter generation."""
    os.environ["JWT_KEY"] = test_private_key
    params = generate_token_endpoint_parameters("test_code")
    assert "client_assertion" in params
    assert "client_assertion_type" in params
    assert "code=test_code" in params
    assert "grant_type=authorization_code" in params


def test_token_auth_decode_payload():
    """Test ID token decoding functionality."""
    decoded_token = TokenAuthorizationOIDC.decode_payload(
        os.environ['MOCK_TOKEN'],
        # Since these tokens are short lived our MOCK_TOKEN used for tests
        # is expired and would need to be refreshed on each test run, to work
        # around that we will disable signature verification for this test.
        # TODO: Consider writing code to generate MOCK_TOKEN on demand
        options={'verify_signature': False}
    )

    # Assert the token was decoded correctly and contains necessary properties
    assert decoded_token is not None
    assert 'nonce' in decoded_token
    assert 'sub' in decoded_token
    assert 'login.gov' in decoded_token.get('iss', '')
