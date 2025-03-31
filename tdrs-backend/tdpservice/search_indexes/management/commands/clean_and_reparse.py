"""Delete and reparse a set of datafiles."""

from django.core.management.base import BaseCommand
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.core.utils import log
from tdpservice.users.models import User
import logging
from tdpservice.search_indexes.utils import (
    backup,
    get_log_context,
    assert_sequential_execution,
    should_exit,
    delete_associated_models,
    count_total_num_records,
    calculate_timeout,
    get_files_to_reparse,
)
from tdpservice.search_indexes.reparse import handle_datafiles

logger = logging.getLogger(__name__)
class Command(BaseCommand):
    """Command class."""

    help = "Delete and reparse a set of datafiles.."

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument(
            "-q",
            "--fiscal_quarter",
            type=str,
            choices=["Q1", "Q2", "Q3", "Q4"],
            help="Reparse all files in the fiscal quarter, e.g. Q1.",
        )
        parser.add_argument(
            "-y",
            "--fiscal_year",
            type=int,
            help="Reparse all files in the fiscal year, e.g. 2021.",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="Clean and reparse all datafiles. If selected, "
            "fiscal_year/quarter aren't necessary.",
        )
        parser.add_argument(
            "-f",
            "--files",
            nargs="+",
            type=str,
            help="Re-parse specific datafiles by datafile id",
        )

    def _handle_input(self, testing, continue_msg):
        """Handle user input."""
        if not testing:
            c = str(input(f"\n{continue_msg}\nContinue [y/n]? ")).lower()
            if c not in ["y", "yes"]:
                print("Cancelled.")
                exit(0)

    def handle(self, *args, **options):
        """Delete and reparse datafiles matching a query."""
        fiscal_year = options.get("fiscal_year", None)
        fiscal_quarter = options.get("fiscal_quarter", None)
        reparse_all = options.get("all", False)
        selected_files = options.get("files", None)
        selected_files = (
            [int(file) for file in selected_files[0].split(",")]
            if selected_files
            else None
        )
        new_indices = reparse_all is True

        # Option that can only be specified by calling `handle` directly and passing it.
        testing = options.get("testing", False)
        ##

        args_passed = (
            fiscal_year is not None
            or fiscal_quarter is not None
            or reparse_all
            or selected_files
        )

        if not args_passed:
            logger.warning("No arguments supplied.")
            self.print_help("manage.py", "clean_and_parse")
            return

        # Set up the backup file name and continue message
        files, backup_file_name, continue_msg = get_files_to_reparse(
            fiscal_year, fiscal_quarter, selected_files, reparse_all
        )

        # end of the if statement

        fmt_str = "be" if new_indices else "NOT be"
        continue_msg += (
            "will {new_index} stored in new indices and the old indices ".format(
                new_index=fmt_str
            )
        )

        num_files = files.count()
        fmt_str = f"ALL ({num_files})" if reparse_all else f"({num_files})"
        continue_msg += "\nThese options will delete and reparse {0} datafiles.".format(
            fmt_str
        )

        if not selected_files:
            self._handle_input(testing, continue_msg)

        system_user, created = User.objects.get_or_create(username="system")
        if created:
            logger.debug("Created reserved system user.")
        log_context = get_log_context(system_user)

        all_fy = "All"
        all_q = "Q1-4"

        if not selected_files:
            log(
                f"Starting clean and reparse command for FY {fiscal_year if fiscal_year else all_fy} and "
                f"{fiscal_quarter if fiscal_quarter else all_q}",
                logger_context=log_context,
                level="info",
            )
        else:
            log(
                f"Starting clean and reparse action for files: {str(selected_files)}",
                logger_context=log_context,
                level="info",
            )

        if num_files == 0:
            log(
                f"No files available for the selected Fiscal Year: {fiscal_year if fiscal_year else all_fy} and "
                f"Quarter: {fiscal_quarter if fiscal_quarter else all_q}. Nothing to do.",
                logger_context=log_context,
                level="warn",
            )
            return

        is_sequential = assert_sequential_execution(log_context)
        should_exit(not is_sequential)
        meta_model = ReparseMeta.objects.create(
            fiscal_quarter=fiscal_quarter,
            fiscal_year=fiscal_year,
            all=reparse_all,
            new_indices=new_indices,
            delete_old_indices=new_indices,
        )

        # Backup the Postgres DB
        backup_file_name += f"_rpv{meta_model.pk}.pg"
        backup(backup_file_name, log_context)

        meta_model.db_backup_location = backup_file_name
        meta_model.save()

        # Delete records from Postgres if necessary
        file_ids = files.values_list("id", flat=True).distinct()
        meta_model.total_num_records_initial = count_total_num_records(log_context)
        meta_model.save()

        delete_associated_models(meta_model, file_ids, log_context)

        meta_model.timeout_at = meta_model.created_at + calculate_timeout(
            num_files, meta_model.num_records_deleted
        )
        meta_model.save()
        logger.info(
            f"Deleted a total of {meta_model.num_records_deleted} records accross {num_files} files."
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
