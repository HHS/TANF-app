"""Command to facilitate backup of the Postgres DB."""

import logging

from django.core.management.base import BaseCommand

from tdpservice.scheduling.datafile_retention_tasks import remove_all_old_versions

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command class."""

    help = "Remove all old versions of every datafile.."

    def handle(self, *args, **options):
        """Remove every previous version."""
        logger.info("Queueing task to remove all old versions of every datafile.")
        remove_all_old_versions.delay()
        logger.info(
            "Task to remove all old versions of every datafile has been queued. Please refer to the LogEntries "
            "in the DAC for more information."
        )
