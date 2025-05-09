"""User app configuration."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Define User properties."""

    name = "tdpservice.users"
    verbose_name = "Users"

    def ready(self):
        """Import signals."""
        import tdpservice.users.signals  # noqa
        import tdpservice.users.change_request_signals  # noqa
