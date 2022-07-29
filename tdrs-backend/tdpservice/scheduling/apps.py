"""Scheduling app configuration."""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Scheduling task config."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tdpservice.scheduling'
