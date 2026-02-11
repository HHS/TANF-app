"""Test the Login.gov UUID change handling in TokenAuthorizationOIDC._handle_user."""
import uuid
from datetime import datetime
from datetime import timezone as dt_timezone
from unittest.mock import MagicMock, patch

from django.urls import reverse
from django.utils import timezone

import pytest

from tdpservice.security.models import SecurityEventToken, SecurityEventType
from tdpservice.users.api.login import TokenAuthorizationOIDC


@pytest.mark.django_db
def test_login_gov_uuid_change_with_account_purged(user):
    """Test handling of Login.gov UUID changes with account_purged security event."""
    original_login_gov_uuid = uuid.uuid4()
    new_login_gov_uuid = uuid.uuid4()
    user.login_gov_uuid = original_login_gov_uuid
    user.save()

    # Create a security event with account_purged
    SecurityEventToken.objects.create(
        user=user,
        email=user.email,
        event_type=SecurityEventType.ACCOUNT_PURGED,
        event_data={},
        jwt_id="test-jwt-id",
        issuer="test-issuer",
        issued_at=timezone.now(),
    )

    auth_options = {"login_gov_uuid": True}

    token_auth = TokenAuthorizationOIDC()

    result_user, login_msg = token_auth._handle_user(
        user.email, new_login_gov_uuid, auth_options
    )

    user.refresh_from_db()
    assert user.login_gov_uuid == new_login_gov_uuid
    assert result_user == user
    assert login_msg == "User updated Login.gov UUID."


@pytest.mark.django_db
def test_login_gov_uuid_change_without_account_purged(user):
    """Test handling of Login.gov UUID changes without account_purged security event."""
    original_login_gov_uuid = uuid.uuid4()
    new_login_gov_uuid = uuid.uuid4()
    user.login_gov_uuid = original_login_gov_uuid
    user.save()

    # Create a security event with a different event type
    SecurityEventToken.objects.create(
        user=user,
        email=user.email,
        event_type=SecurityEventType.PASSWORD_RESET,
        event_data={},
        jwt_id="test-jwt-id",
        issuer="test-issuer",
        issued_at=timezone.now(),
    )

    auth_options = {"login_gov_uuid": True}

    token_auth = TokenAuthorizationOIDC()
    result_user, login_msg = token_auth._handle_user(
        user.email, new_login_gov_uuid, auth_options
    )

    user.refresh_from_db()
    assert user.login_gov_uuid == original_login_gov_uuid
    assert result_user is None
    assert (
        login_msg
        == "User Login.gov UUID changed without account purge. Preventing login."
    )


@pytest.mark.django_db(transaction=True)
@patch("tdpservice.security.views.requests.get")
@patch("tdpservice.security.views.jwt.get_unverified_header")
@patch("tdpservice.security.views.jwt.decode")
@patch("tdpservice.security.views.jwt.algorithms.RSAAlgorithm.from_jwk")
def test_user_changed_login_gov_email(
    mock_from_jwk,
    mock_decode,
    mock_get_unverified_header,
    mock_requests_get,
    user,
    client,
):
    """Test EMAIL_CHANGED SET updates user email and username."""
    old_email = user.email
    new_email = "new_email@example.com"

    # Configure external dependencies and JWT decoding
    mock_requests_get.side_effect = [
        MagicMock(json=lambda: {"jwks_uri": "https://login.gov/jwks"}),
        MagicMock(json=lambda: {"keys": [{"kid": "test_kid"}]}),
    ]
    mock_get_unverified_header.return_value = {"kid": "test_kid"}
    mock_from_jwk.return_value = MagicMock()

    iat = int(timezone.now().timestamp())
    decoded_jwt = {
        "events": {
            SecurityEventType.EMAIL_CHANGED: {
                "subject": {"email": old_email, "subject_type": new_email}
            }
        },
        "iss": "https://login.gov",
        "iat": iat,
        "jti": "test_jti_email_change_e2e",
    }
    mock_decode.return_value = decoded_jwt

    # Post mocked SET to the event-token endpoint
    url = reverse("event-token")
    jwt_token = "header.payload.signature"
    response = client.post(url, data=jwt_token, content_type="application/secevent+jwt")

    assert response.status_code == 200

    # User should be updated
    user.refresh_from_db()
    assert user.email == new_email
    assert user.username == new_email

    # Token should be recorded with correct metadata
    assert SecurityEventToken.objects.count() == 1
    token = SecurityEventToken.objects.first()
    assert token.user == user
    assert token.event_type == SecurityEventType.EMAIL_CHANGED
    assert token.event_data == {
        "subject": {"email": old_email, "subject_type": new_email}
    }
    assert token.jwt_id == "test_jti_email_change_e2e"
    assert token.issuer == "https://login.gov"
    assert token.issued_at == datetime.fromtimestamp(iat, tz=dt_timezone.utc)
    assert token.processed is True


@pytest.mark.django_db
def test_login_gov_uuid_change_no_security_events(user):
    """Test handling of Login.gov UUID changes when no security events exist."""
    original_login_gov_uuid = uuid.uuid4()
    new_login_gov_uuid = uuid.uuid4()
    user.login_gov_uuid = original_login_gov_uuid
    user.save()

    # No security events created

    auth_options = {"login_gov_uuid": True}

    token_auth = TokenAuthorizationOIDC()
    result_user, login_msg = token_auth._handle_user(
        user.email, new_login_gov_uuid, auth_options
    )

    user.refresh_from_db()
    assert user.login_gov_uuid == original_login_gov_uuid
    assert result_user is None
    assert (
        login_msg
        == "User Login.gov UUID changed without account purge. Preventing login."
    )
