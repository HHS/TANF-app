"""App configuration for tdpservice.security."""
from django.apps import AppConfig


class SecurityConfig(AppConfig):
    """App configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tdpservice.security'
    verbose_name = 'Security'
