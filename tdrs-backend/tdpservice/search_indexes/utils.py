"""Utility functions for the reparse command."""
from django.core.management import call_command
from django.db.utils import DatabaseError
from tdpservice.parsers.models import DataFileSummary, ParserError
from tdpservice.search_indexes.util import MODELS, count_all_records
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.core.utils import log
from django.contrib.admin.models import ADDITION
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from tdpservice.data_files.models import DataFile
import logging

logger = logging.getLogger(__name__)


def backup(backup_file_name, log_context):
    """Execute Postgres DB backup."""
    try:
        logger.info("Beginning reparse DB Backup.")
        call_command("backup_db", "-b", "-f", f"{backup_file_name}")
        logger.info("Backup complete! Commencing clean and reparse.")

        log("Database backup complete.", logger_context=log_context, level="info")
    except Exception as e:
        log(
            "Database backup FAILED. Clean and reparse NOT executed. Database is CONSISTENT!",
            logger_context=log_context,
            level="error",
        )
        raise e


def get_log_context(system_user):
    """Return logger context."""
    context = {
        "user_id": system_user.id,
        "action_flag": ADDITION,
        "object_repr": "Clean and Reparse",
    }
    return context


def assert_sequential_execution(log_context):
    """Assert that no other reparse commands are still executing."""
    latest_meta_model = ReparseMeta.get_latest()
    now = timezone.now()
    is_not_none = latest_meta_model is not None
    if is_not_none and latest_meta_model.timeout_at is None:
        log(
            f"The latest ReparseMeta model's (ID: {latest_meta_model.pk}) timeout_at field is None. "
            "Cannot safely execute reparse, please fix manually.",
            logger_context=log_context,
            level="error",
        )
        return False
    if (
        is_not_none
        and not ReparseMeta.assert_all_files_done(latest_meta_model)
        and not now > latest_meta_model.timeout_at
    ):
        log(
            "A previous execution of the reparse command is RUNNING. Cannot execute in parallel, exiting.",
            logger_context=log_context,
            level="warn",
        )
        return False
    elif (
        is_not_none
        and latest_meta_model.timeout_at is not None
        and now > latest_meta_model.timeout_at
        and not ReparseMeta.assert_all_files_done(latest_meta_model)
    ):
        log(
            "Previous reparse has exceeded the timeout. Allowing execution of the command.",
            logger_context=log_context,
            level="warn",
        )
        return True
    return True


def should_exit(condition):
    """Exit on condition."""
    if condition:
        exit(1)


def count_total_num_records(log_context):
    """Count total number of records in the database for meta object."""
    try:
        return count_all_records()
    except DatabaseError as e:
        log(
            "Encountered a DatabaseError while counting records for meta model. The database "
            f"is consistent! Cancelling reparse to be safe. \n{e}",
            logger_context=log_context,
            level="error",
        )
        exit(1)
    except Exception as e:
        log(
            "Encountered generic exception while counting records for meta model. "
            f"The database is consistent! Cancelling reparse to be safe. \n{e}",
            logger_context=log_context,
            level="error",
        )
        exit(1)


def delete_summaries(file_ids, log_context):
    """Raw delete all DataFileSummary objects."""
    try:
        qset = DataFileSummary.objects.filter(datafile_id__in=file_ids)
        count = qset.count()
        logger.info(f"Deleting {count} datafile summary objects.")
        qset._raw_delete(qset.db)
        logger.info("Successfully deleted datafile summary objects.")
    except DatabaseError as e:
        log(
            "Encountered a DatabaseError while deleting DataFileSummary from Postgres. The database "
            "is INCONSISTENT! Restore the DB from the backup as soon as possible!",
            logger_context=log_context,
            level="critical",
        )
        raise e
    except Exception as e:
        log(
            "Caught generic exception while deleting DataFileSummary. The database is INCONSISTENT! "
            "Restore the DB from the backup as soon as possible!",
            logger_context=log_context,
            level="critical",
        )
        raise e


def delete_errors(file_ids, log_context):
    """Raw delete all ParserErrors for each file ID."""
    try:
        qset = ParserError.objects.filter(file_id__in=file_ids)
        count = qset.count()
        logger.info(f"Deleting {count} parser errors.")
        qset._raw_delete(qset.db)
        logger.info("Successfully deleted parser errors.")
    except DatabaseError as e:
        log(
            "Encountered a DatabaseError while deleting ParserErrors from Postgres. The database "
            "is INCONSISTENT! Restore the DB from the backup as soon as possible!",
            logger_context=log_context,
            level="critical",
        )
        raise e
    except Exception as e:
        log(
            "Caught generic exception while deleting ParserErrors. The database is INCONSISTENT! "
            "Restore the DB from the backup as soon as possible!",
            logger_context=log_context,
            level="critical",
        )
        raise e


def delete_records(file_ids, log_context):
    """Delete records, errors from Postgres."""
    total_deleted = 0
    for model in MODELS:
        try:
            qset = model.objects.filter(datafile_id__in=file_ids).order_by("id")
            count = qset.count()
            total_deleted += count
            logger.info(f"Deleting {count} records of type: {model}.")
            qset._raw_delete(qset.db)
        except DatabaseError as e:
            log(
                f"Encountered a DatabaseError while deleting records of type {model} from Postgres. The database "
                "is INCONSISTENT! Restore the DB from the backup as soon as possible!",
                logger_context=log_context,
                level="critical",
            )
            raise e
        except Exception as e:
            log(
                f"Caught generic exception while deleting records of type {model}. The database is "
                "INCONSISTENT! Restore the DB from the backup as soon as possible!",
                logger_context=log_context,
                level="critical",
            )
            raise e
    return total_deleted


def delete_associated_models(meta_model, file_ids, log_context):
    """Delete all models associated to the selected datafiles."""
    delete_summaries(file_ids, log_context)
    delete_errors(file_ids, log_context)
    num_deleted = delete_records(file_ids, log_context)
    meta_model.num_records_deleted = num_deleted


def get_files_to_reparse(fiscal_year, fiscal_quarter, selected_files, reparse_all):
    """Get the files to reparse."""
    backup_file_name = "/tmp/reparsing_backup"
    files = DataFile.objects.all()
    continue_msg = "You have selected to reparse datafiles for FY {fy} and {q}. The reparsed files "
    if selected_files:
        files = files.filter(id__in=selected_files)
        backup_file_name += "_selected_files"
        continue_msg = continue_msg.format(
            fy=f"selected files: {str(selected_files)}", q="Q1-4"
        )
    if reparse_all:
        backup_file_name += "_FY_All_Q1-4"
        continue_msg = continue_msg.format(fy="All", q="Q1-4")
    else:
        if not fiscal_year and not fiscal_quarter and not selected_files:
            print(
                "Options --fiscal_year and --fiscal_quarter not set. "
                "Provide either option to continue, or --all to wipe all submissions."
            )
            return
        if fiscal_year is not None and fiscal_quarter is not None:
            files = files.filter(year=fiscal_year, quarter=fiscal_quarter)
            backup_file_name += f"_FY_{fiscal_year}_{fiscal_quarter}"
            continue_msg = continue_msg.format(fy=fiscal_year, q=fiscal_quarter)
        elif fiscal_year is not None:
            files = files.filter(year=fiscal_year)
            backup_file_name += f"_FY_{fiscal_year}_Q1-4"
            continue_msg = continue_msg.format(fy=fiscal_year, q="Q1-4")
        elif fiscal_quarter is not None:
            files = files.filter(quarter=fiscal_quarter)
            backup_file_name += f"_FY_All_{fiscal_quarter}"
            continue_msg = continue_msg.format(fy="All", q=fiscal_quarter)
    return files, backup_file_name, continue_msg


def calculate_timeout(num_files, num_records):
    """Estimate a timeout parameter based on the number of files and the number of records."""
    # Increase by an order of magnitude to have the bases covered.
    line_parse_time = settings.MEDIAN_LINE_PARSE_TIME * 10
    time_to_queue_datafile = 10
    time_in_seconds = num_files * time_to_queue_datafile + num_records * line_parse_time
    delta = timedelta(seconds=time_in_seconds)
    logger.info(
        f"Setting timeout for the reparse event to be {delta} seconds from meta model creation date."
    )
    return delta

def get_number_of_records(files):
    """Get the number of records in the files."""
    total_number_of_records = 0
    for file in files:
        datafile_summary = DataFileSummary.objects.get(datafile=file)
        total_number_of_records += datafile_summary.total_number_of_records_in_file
    return total_number_of_records
