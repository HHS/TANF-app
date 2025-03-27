"""Celery hook for datafile version cleanup task."""

from __future__ import absolute_import
from celery import shared_task
from datetime import datetime
import logging
from tdpservice.core.utils import log
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.utils import delete_records, get_log_context
from tdpservice.stts.models import STT
from tdpservice.users.models import User


logger = logging.getLogger(__name__)


RETRY_DELAY = 30


@shared_task(bind=True, max_retries=None)
def remove_old_versions(self, data_file_id=None, data_file_version=None):
    """Delete old versions of the file's records."""
    if data_file_id is None or data_file_version is None:
        logger.error("Null data_file_id or data_file_version provided to delete_old_versions task.")
        return

    try:
        data_file = DataFile.objects.get(id=data_file_id)

        # Strictly look at versions less than our version. If submitted very rapidly and we have multiple
        # celery workers, this task could execute in parallel and introduce race conditions if the query deletes all
        # other versions instead of versions strictly less than itself.
        prev_versions = DataFile.objects.filter(version__lt=data_file_version,
                                                year=data_file.year,
                                                quarter=data_file.quarter,
                                                section=data_file.section,
                                                stt=data_file.stt,)

        num_prev_versions = prev_versions.count()
        logger.info(f"Preparing to delete {num_prev_versions} old versions of file: {repr(data_file)}")
        ids = prev_versions.values_list('id', flat=True)
        if len(ids) > 0:
            system_user, created = User.objects.get_or_create(username='system')
            log_context = get_log_context(system_user)
            delete_records(ids, True, log_context)
            logger.info(f"Successfully deleted {num_prev_versions} old version(s) of file: {repr(data_file)}")
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
    min_year = 2019  # TDP didn't exist before this
    max_year = datetime.now().year
    sections = DataFile.Section
    quarters = DataFile.Quarter
    num_exceptions = 0

    num_out_of_range = DataFile.objects.exclude(year__range=(min_year, max_year)).count()
    if num_out_of_range > 0:
        log(f"Found {num_out_of_range} files with years outside of the range {min_year} to "
            f"{max_year}. These will need manual cleanup!", level='warning')

    system_user, created = User.objects.get_or_create(username='system')
    log_context = get_log_context(system_user)
    for year in range(min_year, max_year + 1):
        for stt in stts:
            for section in sections:
                for quarter in quarters:
                    try:
                        files = DataFile.objects.filter(year=year, quarter=quarter, section=section, stt=stt)
                        if files.count() == 0:
                            continue
                        newest_file = files.latest('version')
                        ids = files.exclude(id=newest_file.id).values_list('id', flat=True)
                        delete_records(ids, True, log_context)
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
