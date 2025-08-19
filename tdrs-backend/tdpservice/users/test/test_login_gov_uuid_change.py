"""Test the Login.gov UUID change handling in TokenAuthorizationOIDC._handle_user."""
import uuid

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
