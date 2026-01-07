"""Celery hook for datafile version cleanup task."""

from __future__ import absolute_import

import itertools
import logging
from datetime import datetime

from celery import shared_task

from tdpservice.core.utils import log
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.utils import delete_records, get_log_context
from tdpservice.stts.models import STT
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
    stts = STT.objects.all()
    min_year = 2019  # TDP didn't exist before this
    max_year = datetime.now().year
    years = [year for year in range(min_year, max_year + 1)]
    quarters = DataFile.Quarter
    program_types = DataFile.ProgramType
    sections = DataFile.Section
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

    for year, quarter, program_type, section, stt in itertools.product(
        years, quarters, program_types, sections, stts
    ):
        try:
            files = DataFile.objects.filter(
                year=year,
                quarter=quarter,
                program_type=program_type,
                section=section,
                stt=stt,
            )
            if files.count() == 0:
                continue
            newest_file = files.latest("version")
            ids = files.exclude(id=newest_file.id).values_list("id", flat=True)
            delete_records(ids, log_context)
        except Exception as e:
            log(
                f"Failed to delete old versions of file for: Year:{year}, Quarter:{quarter}, "
                f"Program Type:{program_type}, Section:{section}, STT:{stt.name}",
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
