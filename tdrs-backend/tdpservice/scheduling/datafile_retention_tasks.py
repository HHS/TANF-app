"""Celery hook for datafile version cleanup task."""

from __future__ import absolute_import

import logging
from datetime import datetime

from celery import shared_task

from tdpservice.core.utils import log
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.utils import delete_records, get_log_context
from tdpservice.users.models import User

logger = logging.getLogger(__name__)


@shared_task
def remove_all_old_versions():
    """Delete old versions for every file in the database."""
    system_user, created = User.objects.get_or_create(username="system")
    log_context = get_log_context(system_user)
    log_context["object_repr"] = "Datafile Version Cleanup"

    log(
        "Beginning deletion of old datafile versions.",
        level="info",
        logger_context=log_context,
    )
    min_year = 2019  # TDP didn't exist before this
    max_year = datetime.now().year
    num_exceptions = 0

    num_out_of_range = DataFile.objects.exclude(
        year__range=(min_year, max_year)
    ).count()
    if num_out_of_range > 0:
        log(
            f"Found {num_out_of_range} files with years outside of the range {min_year} to "
            f"{max_year}. These will need manual cleanup!",
            level="warning",
            logger_context=log_context,
        )

    # Query only the distinct file groupings that actually exist in the database,
    # instead of iterating over the full Cartesian product of all possible combinations.
    existing_groupings = (
        DataFile.objects.filter(year__range=(min_year, max_year))
        .values_list("year", "quarter", "program_type", "section", "stt")
        .distinct()
    )

    # Collect all old-version file IDs across all groupings, then delete in one batch.
    all_old_file_ids = []
    for year, quarter, program_type, section, stt_id in existing_groupings:
        files = DataFile.objects.filter(
            year=year,
            quarter=quarter,
            program_type=program_type,
            section=section,
            stt_id=stt_id,
        )
        if files.count() <= 1:
            continue
        newest_file = files.latest("version")
        old_ids = list(files.exclude(id=newest_file.id).values_list("id", flat=True))
        all_old_file_ids.extend(old_ids)

    if all_old_file_ids:
        try:
            delete_records(all_old_file_ids, log_context)
        except Exception as e:
            log(
                f"Failed to delete old versions of {len(all_old_file_ids)} files.",
                level="error",
                logger_context=log_context,
            )
            logger.exception(e)
            num_exceptions += 1

    if num_exceptions == 0:
        log(
            "Successfully deleted all old versions of files.",
            level="info",
            logger_context=log_context,
        )
    else:
        log(
            f"Failed to delete all old versions of files. Encountered {num_exceptions} exceptions while trying.",
            level="error",
            logger_context=log_context,
        )
