"""Celery hook for parsing tasks."""
from __future__ import absolute_import
from celery import shared_task
import logging
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.parse import parse_datafile

logger = logging.getLogger(__name__)


@shared_task
def parse(data_file_id):
    """Send data file for processing."""
    # passing the data file FileField across redis was rendering non-serializable failures, doing the below lookup
    # to avoid those. I suppose good practice to not store/serializer large file contents in memory when stored in redis
    # for undetermined amount of time.
    data_file = DataFile.objects.get(id=data_file_id)

    logger.info(f"DataFile parsing started for file {data_file.filename}")
    errors = parse_datafile(data_file)
    logger.info(f"DataFile parsing finished with {len(errors)} errors: {errors}")
