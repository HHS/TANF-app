"""Handler for security events."""

import logging
from datetime import datetime

from django.utils import timezone

from tdpservice.security.models import SecurityEventToken, SecurityEventType
from tdpservice.users.models import User

logger = logging.getLogger(__name__)


class SecurityEventHandler:
    """Handler for security events."""

    # Should we care about these?
    # Account Locked Due to MFA (Multi-Factor Authentication) Limit Reached
    # Identifier Changed
    # Identifier Recycled
    # Reproofing Completed

    def _handle_unknown_event(security_event):
        """Handle unimplemented or unknown events."""
        logger.warning(f"No handler for event type: {security_event.event_type}")
        security_event.event_type = SecurityEventType.UNKNOWN_EVENT

    def _handle_account_disabled(security_event):
        """Handle account-disabled event."""
        user = security_event.user
        user.is_active = False
        user.save()
        logger.info(f"User {user.username} account disabled due to Login.gov event")

    def _handle_account_enabled(security_event):
        """Handle account-enabled event."""
        user = security_event.user
        user.is_active = True
        user.save()
        logger.info(f"User {user.username} account re-enabled due to Login.gov event")

    def _handle_account_purged(security_event):
        """Handle account-purged event when a user deletes their Login.gov account."""
        # Find user by Login.gov UUID
        user = security_event.user

        # Set login_gov_uuid to null and deactivate user
        user.login_gov_uuid = None
        user.is_active = False
        user.save()

        logger.info(
            f"User {user.username} Login.gov account was purged. Prepared for potential recreation."
        )

    def _handle_mfa_locked(security_event):
        """Handle mfa-locked event."""
        user = security_event.user
        logger.info(
            f"User {user.username} account locked due to multiple MFA failures."
        )

    def _get_emails(security_event):
        """Get the old and new emails from the event data."""
        event_data = security_event.event_data
        subject = event_data.get("subject")
        new_email = subject.get("subject_type")
        old_email = subject.get("email")
        return new_email, old_email

    def _handle_email_changed(security_event):
        """Handle email-changed event."""
        new_email, old_email = SecurityEventHandler._get_emails(security_event)

        user = security_event.user
        user.email = new_email
        user.username = new_email
        user.save()
        logger.info(f"User changed email from {old_email} to {new_email}")

    def _handle_email_recycled(security_event):
        """Handle email-recycled event."""
        new_email, old_email = SecurityEventHandler._get_emails(security_event)
        user = security_event.user
        logger.info(f"User {user.username} recycled extra email address {old_email}")

    def _handle_password_reset(security_event):
        """Handle password-reset event."""
        user = security_event.user
        logger.info(f"User {user.username} performed a password reset")

    def _handle_recovery_activated(security_event):
        """Handle recovery-activated event when user initiates account recovery."""
        user = security_event.user
        logger.info(f"User {user.username} initiated account recovery")

    def _handle_recovery_information_changed(security_event):
        """Handle recovery-information-changed event when user modifies their recovery methods."""
        user = security_event.user
        logger.info(f"User {user.username} changed their recovery information")

    def _handle_reproof_complete(security_event):
        """Handle reproof-complete event when user completes account recovery."""
        user = security_event.user
        logger.info(f"User {user.username} completed account re-verification.")

    handler_map = {
        SecurityEventType.ACCOUNT_DISABLED: _handle_account_disabled,
        SecurityEventType.ACCOUNT_ENABLED: _handle_account_enabled,
        SecurityEventType.ACCOUNT_PURGED: _handle_account_purged,
        SecurityEventType.MFA_LOCKED: _handle_mfa_locked,
        SecurityEventType.EMAIL_CHANGED: _handle_email_changed,
        SecurityEventType.EMAIL_RECYCLED: _handle_email_recycled,
        SecurityEventType.PASSWORD_RESET: _handle_password_reset,
        SecurityEventType.RECOVERY_ACTIVATED: _handle_recovery_activated,
        SecurityEventType.RECOVERY_INFORMATION_CHANGED: _handle_recovery_information_changed,
        SecurityEventType.REPROOF_COMPLETE: _handle_reproof_complete,
    }

    @classmethod
    def _get_user(cls, subject):
        """Get User model from email or UUID."""
        if "sub" in subject:
            user_qset = User.objects.filter(login_gov_uuid=subject.get("sub"))
            if user_qset.exists() and user_qset.count() == 1:
                return user_qset.first()
            else:
                raise ValueError(
                    "No user found with login_gov_uuid: {}".format(subject.get("sub"))
                )
        elif "email" in subject:
            # Check both emails in the subject to see if we have the user
            user_qset = User.objects.filter(email=subject.get("email"))
            if user_qset.exists() and user_qset.count() == 1:
                return user_qset.first()

            user_qset = User.objects.filter(username=subject.get("subject_type"))
            if user_qset.exists() and user_qset.count() == 1:
                return user_qset.first()

            raise ValueError(
                "No user found with the provided 'email' or 'subject_type' in subject of security event."
            )

        raise ValueError("No user info found in subject of security event.")

    @classmethod
    def handle_event(cls, event_type, event_data, decoded_jwt):
        """Handle specific event types."""
        try:
            subject = event_data.get("subject")
            user = cls._get_user(subject)

            # Convert Unix timestamp to datetime if present
            iat_timestamp = decoded_jwt.get("iat")
            issued_at = None
            if iat_timestamp:
                try:
                    issued_at = datetime.fromtimestamp(iat_timestamp, tz=timezone.utc)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error converting timestamp {iat_timestamp}: {e}")

            security_event = SecurityEventToken.objects.create(
                user=user,
                email=user.email,
                event_type=event_type,
                event_data=event_data,
                jwt_id=decoded_jwt.get("jti"),
                issuer=decoded_jwt.get("iss"),
                issued_at=issued_at,
            )

            # Call the appropriate handler
            handler = cls.handler_map.get(event_type, cls._handle_unknown_event)
            handler(security_event)

            security_event.processed = True
            security_event.processed_at = timezone.now()
            security_event.save()

        except Exception as e:
            logger.exception(f"Error handling event {event_type}: {e}")
