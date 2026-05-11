"""Unit tests for the SecurityEventHandler class."""

import logging
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from tdpservice.security.event_handler import SecurityEventHandler
from tdpservice.security.models import SecurityEventToken, SecurityEventType
from tdpservice.users.models import AccountApprovalStatusChoices


@pytest.fixture
def mock_security_event(mock_user):
    """Mock security event model."""
    event = MagicMock(spec=SecurityEventToken)
    event.user = mock_user
    event.email = mock_user.email
    event.event_type = SecurityEventType.UNKNOWN_EVENT
    event.event_data = {"subject": {"sub": str(uuid.uuid4())}}
    event.jwt_id = "test-jwt-id"
    event.issuer = "test-issuer"
    event.issued_at = timezone.now()
    event.processed = False
    event.processed_at = None
    return event


@pytest.fixture
def event_data(stt_data_analyst):
    """Mock event data."""
    return {"subject": {"sub": str(stt_data_analyst.login_gov_uuid)}}


@pytest.fixture
def decoded_jwt():
    """Mock jwt."""
    return {
        "jti": "test-jwt-id",
        "iss": "test-issuer",
        "iat": int(datetime.now().timestamp()),
    }


@pytest.fixture
def email_changed_event_data(stt_data_analyst):
    """Mock event data for email changed: includes old and new emails."""
    old_email = stt_data_analyst.email
    new_email = "new_email@example.com"
    return {
        "subject": {"email": old_email, "subject_type": "email"},
        "new-value": new_email,
    }


@pytest.fixture
def email_changed_event_data_without_new_value(stt_data_analyst):
    """Mock Login.gov event data for email changed without a new email."""
    return {"subject": {"email": stt_data_analyst.email, "subject_type": "email"}}


@pytest.fixture
def email_recycled_event_data(stt_data_analyst):
    """Mock event data for email recycled: includes the recycled email."""
    return {
        "subject": {
            "email": stt_data_analyst.email,
            "subject_type": "email",
        }
    }


class TestSecurityEventHandler:
    """Tests for the SecurityEventHandler class."""

    @pytest.mark.django_db
    def test_handle_unknown_event(self, event_data, decoded_jwt):
        """Test handling of unknown event types."""
        event_type = SecurityEventType.UNKNOWN_EVENT
        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    def test_account_disabled(self, stt_data_analyst, event_data, decoded_jwt):
        """Test handling of account-disabled event."""
        event_type = SecurityEventType.ACCOUNT_DISABLED
        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        previous_status = stt_data_analyst.account_approval_status

        stt_data_analyst.refresh_from_db()

        assert stt_data_analyst.account_approval_status == previous_status
        assert stt_data_analyst.is_active is False
        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    def test_account_enabled(self, stt_data_analyst, event_data, decoded_jwt):
        """Test handling of account-enabled event."""
        stt_data_analyst.is_active = False
        stt_data_analyst.save()

        event_type = SecurityEventType.ACCOUNT_ENABLED
        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        stt_data_analyst.refresh_from_db()

        assert (
            stt_data_analyst.account_approval_status
            == AccountApprovalStatusChoices.APPROVED
        )
        assert stt_data_analyst.is_active is True
        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    def test_account_purged(self, stt_data_analyst, event_data, decoded_jwt):
        """Test handling of account-purged event."""
        event_type = SecurityEventType.ACCOUNT_PURGED
        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        previous_status = stt_data_analyst.account_approval_status

        stt_data_analyst.refresh_from_db()

        assert stt_data_analyst.account_approval_status == previous_status
        assert stt_data_analyst.is_active is False
        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    def test_password_reset(self, stt_data_analyst, event_data, decoded_jwt):
        """Test handling of password-reset event."""
        event_type = SecurityEventType.PASSWORD_RESET
        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        stt_data_analyst.refresh_from_db()

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    def test_recovery_activated(self, stt_data_analyst, event_data, decoded_jwt):
        """Test handling of recovery-activated event."""
        event_type = SecurityEventType.RECOVERY_ACTIVATED
        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        stt_data_analyst.refresh_from_db()

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    def test_recovery_information_changed(
        self, stt_data_analyst, event_data, decoded_jwt
    ):
        """Test handling of recovery-information-changed event."""
        event_type = SecurityEventType.RECOVERY_INFORMATION_CHANGED
        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        stt_data_analyst.refresh_from_db()

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "event_type",
        [
            SecurityEventType.MFA_LOCKED,
            SecurityEventType.EMAIL_CHANGED,
            SecurityEventType.EMAIL_RECYCLED,
            SecurityEventType.PASSWORD_RESET,
            SecurityEventType.RECOVERY_ACTIVATED,
            SecurityEventType.RECOVERY_INFORMATION_CHANGED,
            SecurityEventType.REPROOF_COMPLETE,
        ],
    )
    def test_non_mutating_events_do_not_update_user(
        self, stt_data_analyst, event_type, decoded_jwt
    ):
        """Test only account status and purge events mutate the user model."""
        prev_email = stt_data_analyst.email
        prev_username = stt_data_analyst.username
        prev_active = stt_data_analyst.is_active
        prev_login_gov_uuid = str(stt_data_analyst.login_gov_uuid)
        prev_status = stt_data_analyst.account_approval_status
        event_data = {"subject": {"sub": str(stt_data_analyst.login_gov_uuid)}}

        if event_type in {
            SecurityEventType.EMAIL_CHANGED,
            SecurityEventType.EMAIL_RECYCLED,
        }:
            event_data = {
                "subject": {
                    "email": stt_data_analyst.email,
                    "subject_type": "email",
                }
            }

        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        stt_data_analyst.refresh_from_db()

        assert stt_data_analyst.email == prev_email
        assert stt_data_analyst.username == prev_username
        assert stt_data_analyst.is_active == prev_active
        assert str(stt_data_analyst.login_gov_uuid) == prev_login_gov_uuid
        assert stt_data_analyst.account_approval_status == prev_status

        token = SecurityEventToken.objects.first()
        assert token.processed is True
        assert token.event_type == event_type

    @pytest.mark.django_db
    def test_mfa_locked(self, stt_data_analyst, event_data, decoded_jwt):
        """Test handling of mfa-locked event."""
        prev_email = stt_data_analyst.email
        prev_username = stt_data_analyst.username
        prev_active = stt_data_analyst.is_active

        event_type = SecurityEventType.MFA_LOCKED
        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        stt_data_analyst.refresh_from_db()

        assert stt_data_analyst.email == prev_email
        assert stt_data_analyst.username == prev_username
        assert stt_data_analyst.is_active == prev_active

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    def test_email_changed(
        self, stt_data_analyst, email_changed_event_data, decoded_jwt
    ):
        """Test handling email-changed event does not update user's email and username."""
        prev_email = stt_data_analyst.email
        prev_username = stt_data_analyst.username

        event_type = SecurityEventType.EMAIL_CHANGED
        SecurityEventHandler.handle_event(
            event_type, email_changed_event_data, decoded_jwt
        )

        stt_data_analyst.refresh_from_db()

        assert stt_data_analyst.email == prev_email
        assert stt_data_analyst.username == prev_username

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == email_changed_event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    def test_email_changed_without_new_value_does_not_update_user(
        self, stt_data_analyst, email_changed_event_data_without_new_value, decoded_jwt
    ):
        """Test Login.gov identifier-changed payload does not set email to subject_type."""
        prev_email = stt_data_analyst.email
        prev_username = stt_data_analyst.username

        event_type = SecurityEventType.EMAIL_CHANGED
        SecurityEventHandler.handle_event(
            event_type, email_changed_event_data_without_new_value, decoded_jwt
        )

        stt_data_analyst.refresh_from_db()

        assert stt_data_analyst.email == prev_email
        assert stt_data_analyst.username == prev_username

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == email_changed_event_data_without_new_value

    @pytest.mark.django_db
    def test_email_changed_for_unknown_email_records_processed_event(
        self, caplog, decoded_jwt
    ):
        """Test Login.gov identifier-changed can arrive with a new unknown email."""
        event_type = SecurityEventType.EMAIL_CHANGED
        event_data = {
            "subject": {
                "email": "new_login_email@example.com",
                "subject_type": "email",
            }
        }

        with caplog.at_level(logging.WARNING):
            SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        assert "No user found with the provided 'email'" not in caplog.text
        assert "unmatched subject" in caplog.text

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user is None
        assert token.email == "new_login_email@example.com"
        assert token.processed is True
        assert token.processed_at is not None
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]

    @pytest.mark.django_db
    def test_non_mutating_event_for_unknown_sub_records_processed_event(
        self, caplog, decoded_jwt
    ):
        """Test non-mutating events with an unknown sub are recorded for audit."""
        event_type = SecurityEventType.PASSWORD_RESET
        event_data = {"subject": {"sub": str(uuid.uuid4())}}

        with caplog.at_level(logging.WARNING):
            SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        assert "No user found with login_gov_uuid" not in caplog.text
        assert "unmatched subject" in caplog.text

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user is None
        assert token.email is None
        assert token.processed is True
        assert token.processed_at is not None
        assert token.event_type == event_type
        assert token.event_data == event_data

    @pytest.mark.django_db
    def test_email_recycled(
        self, stt_data_analyst, email_recycled_event_data, decoded_jwt
    ):
        """Test handling of email-recycled event."""
        prev_email = stt_data_analyst.email
        prev_username = stt_data_analyst.username
        prev_active = stt_data_analyst.is_active

        event_type = SecurityEventType.EMAIL_RECYCLED
        SecurityEventHandler.handle_event(
            event_type, email_recycled_event_data, decoded_jwt
        )

        stt_data_analyst.refresh_from_db()

        assert stt_data_analyst.email == prev_email
        assert stt_data_analyst.username == prev_username
        assert stt_data_analyst.is_active == prev_active

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == email_recycled_event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    @pytest.mark.django_db
    def test_reproof_complete(self, stt_data_analyst, event_data, decoded_jwt):
        """Test handling of reproof-complete event."""
        prev_email = stt_data_analyst.email
        prev_username = stt_data_analyst.username
        prev_active = stt_data_analyst.is_active

        event_type = SecurityEventType.REPROOF_COMPLETE
        SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        stt_data_analyst.refresh_from_db()

        assert stt_data_analyst.email == prev_email
        assert stt_data_analyst.username == prev_username
        assert stt_data_analyst.is_active == prev_active

        assert SecurityEventToken.objects.count() == 1
        token = SecurityEventToken.objects.first()
        assert token.user == stt_data_analyst
        assert token.processed is True
        assert token.event_type == event_type
        assert token.event_data == event_data
        assert token.jwt_id == decoded_jwt["jti"]
        assert token.issuer == decoded_jwt["iss"]
        assert token.issued_at == datetime.fromtimestamp(
            decoded_jwt["iat"], tz=timezone.utc
        )

    def test_handle_event_no_sub(self, caplog):
        """Test handling event with missing subject sub."""
        event_type = "test-event"
        event_data = {"subject": {}}  # Missing "sub"
        decoded_jwt = {}

        with caplog.at_level(logging.WARNING):
            SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        assert "No user info found in subject of security event." in caplog.text

    @pytest.mark.django_db
    def test_handle_event_user_not_found(self, caplog):
        """Test handling user-mutating event when user is not found."""

        event_type = SecurityEventType.ACCOUNT_DISABLED
        login_gov_uuid = uuid.uuid4()
        event_data = {"subject": {"sub": str(login_gov_uuid)}}
        decoded_jwt = {}

        with caplog.at_level(logging.ERROR):
            SecurityEventHandler.handle_event(event_type, event_data, decoded_jwt)

        assert f"No user found with login_gov_uuid: {login_gov_uuid}" in caplog.text
