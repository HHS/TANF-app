"""Elasticsearch indexes app configuration."""

from django.apps import AppConfig


class SearchIndexesConfig(AppConfig):
    """Configuration class."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tdpservice.search_indexes'
