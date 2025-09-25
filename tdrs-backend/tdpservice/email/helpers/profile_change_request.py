"""Helper methods for sending emails to users about their profile change request."""

import ast
from tdpservice.email.email import automated_email
from tdpservice.email.email_enums import EmailType
from tdpservice.stts.models import Region

FIELD_LABELS = {
    "first_name": "First name",
    "last_name": "Last name",
    "regions": "Regions",
    "has_fra_access": "FRA access",
}


def _readable_field_values(field_name: str, current_value: str, requested_value: str):
    """Turn DB values into human readble strings for the email."""
    if field_name == "regions":

        def ids_to_names(s: str) -> str:
            try:
                ids = ast.literal_eval(s) if s else []
            except Exception:
                ids = []
            names = list(
                Region.objects.filter(id__in=ids)
                .order_by("pk")
                .values_list("name", flat=True)
            )
            return ", ".join(names) if names else "None"

        return ids_to_names(current_value), ids_to_names(requested_value)
    elif field_name == "has_fra_access":

        def yesOrNo(s: str) -> str:
            return "Yes" if s == "True" else "No"

        return yesOrNo(current_value), yesOrNo(requested_value)

    # For basic fields
    return (current_value or "", requested_value or "")


def send_change_request_status_email(change_request, isApproved: bool, url):
    """Send an email to a user when their profile change request is approved/denied."""
    from tdpservice.users.models import User

    user: User = change_request.user

    field_label = FIELD_LABELS.get(
        change_request.field_name, change_request.field_name.title()
    )

    current_value, requested_value = _readable_field_values(
        change_request.field_name,
        change_request.current_value,
        change_request.requested_value,
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
        "current_value": current_value,
        "requested_value": requested_value,
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
