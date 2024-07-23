"""Celery hook for parsing tasks."""
from __future__ import absolute_import
from celery import shared_task
import logging
from django.contrib.auth.models import Group
from django.db.utils import DatabaseError
from tdpservice.users.models import AccountApprovalStatusChoices, User
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.parse import parse_datafile
from tdpservice.parsers.models import DataFileSummary, ParserErrorCategoryChoices
from tdpservice.parsers.aggregates import case_aggregates_by_month, total_errors_by_month
from tdpservice.parsers.util import log_parser_exception, make_generate_parser_error
from tdpservice.email.helpers.data_file import send_data_submitted_email


logger = logging.getLogger(__name__)


@shared_task
def parse(data_file_id, should_send_submission_email=True):
    """Send data file for processing."""
    # passing the data file FileField across redis was rendering non-serializable failures, doing the below lookup
    # to avoid those. I suppose good practice to not store/serializer large file contents in memory when stored in redis
    # for undetermined amount of time.
    try:
        data_file = DataFile.objects.get(id=data_file_id)
        logger.info(f"DataFile parsing started for file {data_file.filename}")

        dfs = DataFileSummary.objects.create(datafile=data_file, status=DataFileSummary.Status.PENDING)
        errors = parse_datafile(data_file, dfs)
        dfs.status = dfs.get_status()

        if "Case Data" in data_file.section:
            dfs.case_aggregates = case_aggregates_by_month(data_file, dfs.status)
        else:
            dfs.case_aggregates = total_errors_by_month(data_file, dfs.status)

        dfs.save()

        logger.info(f"Parsing finished for file -> {repr(data_file)} with status {dfs.status} and {len(errors)} errors.")

        if should_send_submission_email is True:
            recipients = User.objects.filter(
                stt=data_file.stt,
                account_approval_status=AccountApprovalStatusChoices.APPROVED,
                groups=Group.objects.get(name='Data Analyst')
            ).values_list('username', flat=True).distinct()

            send_data_submitted_email(dfs, recipients)
    except DatabaseError as e:
        log_parser_exception(data_file,
                             f"Encountered Database exception in parser_task.py: \n{e}",
                             "error"
                             )
    except Exception as e:
        generate_error = make_generate_parser_error(data_file, None)
        error = generate_error(schema=None,
                               error_category=ParserErrorCategoryChoices.PRE_CHECK,
                               error_message=("We're sorry, an unexpected error has occurred and the file has been "
                                              "rejected. Please contact the TDP support team at TANFData@acf.hhs.gov "
                                              "for further assistance."),
                               record=None,
                               field=None
                               )
        error.save()
        dfs.set_status(DataFileSummary.Status.REJECTED)
        dfs.save()
        log_parser_exception(data_file,
                             (f"Uncaught exception while parsing datafile: {data_file.pk}! Please review the logs to "
                              f"see if manual intervention is required. Exception: \n{e}"),
                             "critical")
