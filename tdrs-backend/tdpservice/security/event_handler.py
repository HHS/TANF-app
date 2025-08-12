"""Handler for security events."""

import logging
from datetime import datetime

from django.utils import timezone

from tdpservice.security.models import SecurityEventToken
from tdpservice.users.models import AccountApprovalStatusChoices, User

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
        # Return false because we do not want to create DB records for events we don't handle.
        return False

    def _handle_account_disabled(security_event):
        """Handle account-disabled event."""
        user = security_event.user
        if user:
            user.account_approval_status = AccountApprovalStatusChoices.DEACTIVATED
            user.is_active = False
            user.save()
            logger.info(f"User {user.username} account disabled due to Login.gov event")
            return True
        return False

    def _handle_account_enabled(security_event):
        """Handle account-enabled event."""
        user = security_event.user
        if (
            user
            and user.account_approval_status == AccountApprovalStatusChoices.DEACTIVATED
        ):
            # Only re-enable if previously deactivated, don't override other statuses
            user.account_approval_status = AccountApprovalStatusChoices.APPROVED
            user.is_active = True
            user.save()
            logger.info(
                f"User {user.username} account re-enabled due to Login.gov event"
            )
            return True
        return False

    def _handle_account_purged(security_event):
        """Handle account-purged event when a user deletes their Login.gov account."""
        # Find user by Login.gov UUID
        user = security_event.user

        # Set login_gov_uuid to null and deactivate user
        user.login_gov_uuid = None
        user.account_approval_status = AccountApprovalStatusChoices.DEACTIVATED
        user.is_active = False
        user.save()

        logger.info(
            f"User {user.username} Login.gov account was purged. Prepared for potential recreation."
        )
        return True

    def _handle_password_reset(security_event):
        """Handle password-reset event."""
        user = security_event.user
        logger.info(f"User {user.username} performed a password reset")
        return True

    def _handle_recovery_activated(security_event):
        """Handle recovery-activated event when user initiates account recovery."""
        user = security_event.user
        logger.info(f"User {user.username} initiated account recovery")
        return True

    def _handle_recovery_information_changed(security_event):
        """Handle recovery-information-changed event when user modifies their recovery methods."""
        user = security_event.user
        logger.info(f"User {user.username} changed their recovery information")
        return True

    handler_map = {
        "https://schemas.openid.net/secevent/risc/event-type/account-disabled": _handle_account_disabled,
        "https://schemas.openid.net/secevent/risc/event-type/account-enabled": _handle_account_enabled,
        "https://schemas.openid.net/secevent/risc/event-type/account-purged": _handle_account_purged,
        "https://schemas.login.gov/secevent/risc/event-type/password-reset": _handle_password_reset,
        "https://schemas.openid.net/secevent/risc/event-type/recovery-activated": _handle_recovery_activated,
        "https://schemas.openid.net/secevent/risc/event-type/recovery-information-changed": _handle_recovery_information_changed,
    }

    @classmethod
    def handle_event(cls, event_type, event_data, decoded_jwt):
        """Handle specific event types."""
        try:
            subject = event_data.get("subject")
            if "sub" not in subject:
                logger.warning(
                    f"No 'sub' found in subject: {subject} for event: {event_type}. SKIPPING."
                )
                return

            user = User.objects.get(login_gov_uuid=subject.get("sub"))

            # Convert Unix timestamp to datetime if present
            iat_timestamp = decoded_jwt.get("iat")
            issued_at = None
            if iat_timestamp:
                try:
                    # Convert Unix timestamp to datetime with timezone awareness
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
            handled = handler(security_event)
            if handled:
                security_event.processed = handled
                security_event.processed_at = timezone.now()
                security_event.save()

        except Exception as e:
            logger.exception(f"Error handling event {event_type}: {e}")
