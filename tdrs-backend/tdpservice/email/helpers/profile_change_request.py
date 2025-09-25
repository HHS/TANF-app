from tdpservice.email.email import automated_email, log
from tdpservice.email.email_enums import EmailType

FIELD_LABELS = {
    "first_name": "First name",
    "last_name": "Last name",
    "regions": "Regions",
    "has_fra_access": "FRA access",
}


def send_change_request_status_email(change_request, isApproved: bool, url):
    """Send an email to a user when their profile change request is approved/denied."""
    from tdpservice.users.models import User
    user: User = change_request.user

    field_label = FIELD_LABELS.get(
        change_request.field_name, change_request.field_name.title()
    )

    template_path = (
        EmailType.PROFILE_CHANGE_REQUEST_APPROVED.value
        if isApproved
        else EmailType.PROFILE_CHANGE_REQUEST_REJECTED.value
    )
    recipient_email = user.email
    subject = field_label + (" change approved" if isApproved else " change denied")

    email_context = {
        "first_name": user.first_name,
        "field_label": field_label,
        "current_value": change_request.current_value,
        "requested_value": change_request.requested_value,
        "notes": change_request.notes or "",
        "url": url,
    }

    text_message = subject

    logger_context = {
        "user_id": user.id,
        "object_id": user.id,
        "object_repr": user.email,
        "content_type": type(change_request),
    }

    automated_email(
        email_path=template_path,
        recipient_email=recipient_email,
        subject=subject,
        email_context=email_context,
        text_message=text_message,
        logger_context=logger_context,
    )
