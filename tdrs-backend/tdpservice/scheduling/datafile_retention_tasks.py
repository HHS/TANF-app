"""Celery hook for datafile version cleanup task."""

from __future__ import absolute_import
from celery import shared_task
from django.db.models import Min, Max
import logging
from tdpservice.core.utils import log
from tdpservice.data_files.models import DataFile
from tdpservice.stts.models import STT


logger = logging.getLogger(__name__)


RETRY_DELAY = 30


@shared_task(bind=True, max_retries=None)
def remove_old_versions(self, data_file_id=None, data_file_version=None):
    """Delete old versions of the file."""
    if data_file_id is None or data_file_version is None:
        logger.error("Null data_file_id or data_file_version provided to delete_old_versions task.")
        return

    try:
        data_file = DataFile.objects.get(id=data_file_id)

        # Strictly look at versions less than our version. If a files we subbmitted very rapidly and we have multiple
        # celery workers, this task could execute in parallel and introduce race conditions if the query deletes all
        # other versions instead of versions strictly less than itself.
        prev_versions = DataFile.objects.filter(version__lt=data_file_version,
                                                year=data_file.year,
                                                quarter=data_file.quarter,
                                                section=data_file.section,
                                                stt=data_file.stt,)

        num_prev_versions = prev_versions.count()
        logger.info(f"Preparing to delete {num_prev_versions} old versions of file: {repr(data_file)}")
        for prev_version in prev_versions:
            prev_version.delete()
            logger.info(f"Succesfully deleted old version: {repr(prev_version)}")
        logger.info(f"Successfully deleted {num_prev_versions} old versions of file: {repr(data_file)}")
    except Exception as e:
        if self.request.retries == data_file_version:
            logger.exception(f"Failed to delete old versions of file: {data_file_id}.")
            raise e
        logger.exception("Encountered exception while deleting old versions of file: "
                         f"{data_file_id}. Retrying in {RETRY_DELAY} seconds.")
        self.retry(countdown=RETRY_DELAY, exc=e)


@shared_task
def remove_all_old_versions():
    """Delete old versions for every file in the database."""
    stts = STT.objects.all()
    min_year = DataFile.objects.aggregate(min_year=Min('year'))['min_year']
    max_year = DataFile.objects.aggregate(max_year=Max('year'))['max_year']
    sections = DataFile.Section
    quarters = DataFile.Quarter
    num_exceptions = 0
    for year in range(min_year, max_year + 1):
        for stt in stts:
            for section in sections:
                for quarter in quarters:
                    try:
                        files = DataFile.objects.filter(year=year, quarter=quarter, section=section, stt=stt)
                        if files.count() == 0:
                            continue
                        newest_file = files.latest('version')
                        files.exclude(id=newest_file.id).delete()
                    except Exception as e:
                        log(f"Failed to delete old versions of file for: Year:{year}, Quarter:{quarter}, "
                            f"Section:{section}, STT:{stt.name}", level='error')
                        logger.exception(e)
                        num_exceptions += 1

    if num_exceptions == 0:
        log("Successfully deleted all old versions of files.", level='info')
    else:
        log(f"Failed to delete all old versions of files. Encountered {num_exceptions} exceptions while trying.",
            level='error')
