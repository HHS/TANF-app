"""Celery hook for parsing tasks."""
from __future__ import absolute_import
from celery import shared_task
import logging
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.parsers.preparser import preparse

logger = logging.getLogger(__name__)

@shared_task
def parse(data_file_id):
    """Send data file for processing."""
    # passing the data file FileField across redis was rendering non-serializable failures, doing the below lookup
    # to avoid those. I suppose good practice to not store/serializer large file contents in memory when stored in redis
    # for undetermined amount of time.
    data_file = DataFile.objects.get(id=data_file_id)
    logger.debug("Sending file '%s' of type '%s' and section '%s' to preparser.",
                 data_file.filename, "TANF", data_file.section)
    preparse(data_file, "TANF", data_file.section)  # data_file.type_ssp_something, data_file.section)
