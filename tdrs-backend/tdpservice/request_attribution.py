"""Request attribution context shared by authentication and metrics code."""
from dataclasses import dataclass
from typing import Any

REQUEST_ATTRIBUTION_ATTRIBUTE = "tdp_attribution"


@dataclass(frozen=True)
class RequestAttribution:
    """Low-cardinality request source facts the backend can prove."""

    source: str = "unknown"
    client_id: str = "none"
    auth_method: str = "none"
    user_stt: str = "unknown"
    user_group: str = "unknown"


def set_request_attribution(request: Any, attribution: RequestAttribution) -> None:
    """Attach attribution to DRF and underlying Django requests when present."""
    setattr(request, REQUEST_ATTRIBUTION_ATTRIBUTE, attribution)

    django_request = getattr(request, "_request", None)
    if django_request is not None:
        setattr(django_request, REQUEST_ATTRIBUTION_ATTRIBUTE, attribution)
