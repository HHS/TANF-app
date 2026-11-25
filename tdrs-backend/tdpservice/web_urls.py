"""Helpers for URLs served by the public TDP frontend."""

from django.conf import settings


def help_url(path: str = "") -> str:
    """Return an environment-aware URL for content proxied under ``/help``."""
    base_url = f"{settings.FRONTEND_BASE_URL.rstrip('/')}/help/"
    return f"{base_url}{path.lstrip('/')}"
