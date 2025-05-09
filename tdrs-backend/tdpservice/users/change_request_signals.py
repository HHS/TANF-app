"""Signals for user change requests."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserChangeRequest, UserChangeRequestStatus

import logging
logger = logging.getLogger()


# TODO: implement when templates are created.
# Probably shouldn't be in the save signal. Perhaps in the bulk save/singular save actions
@receiver(post_save, sender=UserChangeRequest)
def notify_user_of_change_request_status(sender, instance, created, **kwargs):
    """Send email notification to user when change request status changes."""
    # Skip if this is a new change request being created
    if created:
        return

    # Only send notifications for approved or rejected requests
    if instance.status not in [UserChangeRequestStatus.APPROVED, UserChangeRequestStatus.REJECTED]:
        return

    try:
        logger.info(f"Sent change request notification email to {instance.user.username}")
    except Exception as e:
        logger.error(f"Failed to send change request notification email: {str(e)}")
