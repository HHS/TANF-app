"""Reparsing command for selected files."""
# should include all the steps in the management command
import datetime
from django.core.management import call_command
from elasticsearch.exceptions import ElasticsearchException
from tdpservice.data_files.models import DataFile
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.core.utils import log
from tdpservice.users.models import User
from tdpservice.scheduling import parser_task
from django.db.utils import DatabaseError
from tdpservice.search_indexes.utils import (
    backup,
    get_log_context,
    assert_sequential_execution,
    delete_associated_models,
    count_total_num_records,
    calculate_timeout,
    get_number_of_records
)
import logging

logger = logging.getLogger(__name__)

def handle_datafiles(files, meta_model, log_context):
    """Delete, re-save, and reparse selected datafiles."""
    for file in files:
        try:
            file.reparses.add(meta_model)
            file.save()
            parser_task.parse.delay(file.pk, reparse_id=meta_model.pk)
        except DatabaseError as e:
            log(
                "Encountered a DatabaseError while re-creating datafiles. The database "
                "and Elastic are INCONSISTENT! Restore the DB from the backup as soon as possible!",
                logger_context=log_context,
                level="critical",
            )
            raise e
        except Exception as e:
            log(
                "Caught generic exception in _handle_datafiles. Database and Elastic are INCONSISTENT! "
                "Restore the DB from the backup as soon as possible!",
                logger_context=log_context,
                level="critical",
            )
            raise e

def handle_elastic(new_indices, log_context):
    """Create new Elastic indices and delete old ones."""
    if new_indices:
        try:
            logger.info("Creating new elastic indexes.")
            call_command("tdp_search_index", "--create", "-f", "--use-alias")
            log("Index creation complete.", logger_context=log_context, level="info")
        except ElasticsearchException as e:
            log(
                "Elastic index creation FAILED. Clean and reparse NOT executed. "
                "Database is CONSISTENT, Elastic is INCONSISTENT!",
                logger_context=log_context,
                level="error",
            )
            raise e
        except Exception as e:
            log(
                "Caught generic exception in _handle_elastic. Clean and reparse NOT executed. "
                "Database is CONSISTENT, Elastic is INCONSISTENT!",
                logger_context=log_context,
                level="error",
            )
            raise e

def clean_reparse(selected_file_ids):
    """Reparse selected files."""
    selected_files = [int(file_id) for file_id in selected_file_ids[0].split(",")]

    files = DataFile.objects.filter(id__in=selected_files)
    num_files = files.count()

    fiscal_quarter = None
    fiscal_year = None
    all_reparse = False
    new_indices = False

    if num_files == 1:
        log(
            f"Reparsing {num_files} file: {files.first()}",
            level="info",
        )
        fiscal_quarter = files.first().quarter
        fiscal_year = files.first().year

    meta_model = ReparseMeta(
        fiscal_quarter=fiscal_quarter,
        fiscal_year=fiscal_year,
        all=all_reparse,
        new_indices=new_indices,
        delete_old_indices=new_indices,
    )
    total_number_of_records = get_number_of_records(files)
    calculated_timeout_at = calculate_timeout(
        total_number_of_records, meta_model.num_records_deleted
    )
    backup_file_name = "/tmp/reparsing_backup"
    continue_msg = "You have selected to reparse datafiles for FY {fy} and {q}. The reparsed files "
    continue_msg = continue_msg.format(
        fy=f"selected files: {str(selected_files)}", q="Q1-4"
    )

    # add fmt_str

    system_user, created = User.objects.get_or_create(username="system")
    if created:
        logger.info("Created system user")
    log_context = get_log_context(system_user)

    all_fy = "All"
    all_q = "Q1-4"

    log(
        f"Starting clean_and_reparse for {num_files} files",
        logger_context=log_context,
        level=logging.INFO,
    )

    is_sequential = assert_sequential_execution(log_context)
    if not is_sequential:
        raise Exception(f"Sequential execution required for selected file ids: {selected_file_ids}")
    meta_model.save()
    # Backup the Postgres DB
    backup_file_name += f"_rpv{meta_model.pk}_{datetime.datetime.now().strftime('%d-%m-%Y-%H-%M-%S')}.pg"
    backup(backup_file_name, log_context)

    meta_model.db_backup_location = backup_file_name
    meta_model.save()

    # Create and delete Elastic indices if necessary
    handle_elastic(new_indices, log_context)

    file_ids = files.values_list("id", flat=True).distinct()
    meta_model.total_num_records_initial = count_total_num_records(log_context)
    meta_model.save()

    delete_associated_models(meta_model, file_ids, new_indices, log_context)

    meta_model.timeout_at = meta_model.created_at + calculated_timeout_at
    meta_model.save()
    logger.info(
        f"Deleted a total of {meta_model.num_records_deleted} records across {num_files} files."
    )

    # Delete and re-save datafiles to handle cascading dependencies
    logger.info(f"Deleting and re-parsing {num_files} files")
    handle_datafiles(files, meta_model, log_context)

    log(
        "Database cleansing complete and all files have been re-scheduling for parsing and validation.",
        logger_context=log_context,
        level="info",
    )
    log(
        f"Clean and reparse command completed. All files for FY {fiscal_year if fiscal_year else all_fy} and "
        f"{fiscal_quarter if fiscal_quarter else all_q} have been queued for parsing.",
        logger_context=log_context,
        level="info",
    )
    logger.info("Done. All tasks have been queued to parse the selected datafiles.")
