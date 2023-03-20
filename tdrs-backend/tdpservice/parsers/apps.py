"""Register the parser module with Django."""

from django.apps import AppConfig


class ParsersConfig(AppConfig):
    """Parser module configuration."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tdpservice.parsers'
