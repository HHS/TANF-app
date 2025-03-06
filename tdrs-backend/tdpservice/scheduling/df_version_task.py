"""Celery hook for datafile version cleanup task."""

from __future__ import absolute_import
from celery import shared_task
import logging
from tdpservice.data_files.models import DataFile


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=None)
def delete_old_versions(self, data_file_id=None):
    """Delete old versions of the file."""
    if data_file_id is None:
        logger.error("Null data_file_id provided to delete_old_versions task.")
        return

    try:
        data_file = DataFile.objects.get(id=data_file_id)
        logger.info(f"Deleting previous versions of file: {repr(data_file)}")

        prev_versions = DataFile.objects.filter(year=data_file.year,
                                                quarter=data_file.quarter,
                                                section=data_file.section,
                                                stt=data_file.stt).exclude(version=data_file.version)

        logger.info(f"Preparing to delete {prev_versions.count()} old versions of file: {repr(data_file)}")
        for prev_version in prev_versions:
            prev_version.delete()
            logger.info(f"Succesfully deleted old version: {repr(prev_version)}")
    except Exception as e:
        if self.request.retries == data_file.version:
            logger.exception(f"Failed to delete old versions of file: {repr(data_file)}.")
            raise e
        logger.exception("Encountered exception while deleting old versions of file: "
                         f"{repr(data_file)}. Retrying in 30 seconds.")
        self.retry(countdown=30, exc=e)
