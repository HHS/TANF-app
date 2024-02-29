"""Shared celery database tasks file for beat."""

from __future__ import absolute_import
from celery import shared_task
import logging
from .db_backup import run_backup

logger = logging.getLogger(__name__)

@shared_task
def postgres_backup(*args):
    """Run nightly postgres backup."""
    arg = ''.join(args)
    logger.debug("postgres_backup::run_backup() run with arg: " + arg)
    logger.info("Begining database backup.")
    result = run_backup(arg)
    if result:
        logger.info("Finished database backup.")
    else:
        logger.error("Failed to complete database backup.")
    return result
