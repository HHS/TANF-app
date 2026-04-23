"""Celery tasks for Keycloak user synchronization."""

from __future__ import absolute_import

import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def reconcile_keycloak_users():
    """Periodic task to reconcile all active Django users with Keycloak.

    Runs via Celery Beat to ensure Keycloak stays in sync with Django
    even if individual signal-based syncs were missed.
    """
    from tdpservice.users.keycloak_client import KeycloakSyncClient

    logger.info("Starting periodic Keycloak user reconciliation")
    client = KeycloakSyncClient.get_instance()
    stats = client.bulk_sync_all_users()
    logger.info("Keycloak reconciliation complete: %s", stats)
    return stats
