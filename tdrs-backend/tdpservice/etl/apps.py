"""Configuration for the ETL Django app."""

from django.apps import AppConfig


class EtlConfig(AppConfig):
    """Django app configuration for ETL pipelines."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "tdpservice.etl"
