"""Delete and reparse a set of datafiles."""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.core.paginator import Paginator
from django.db.utils import DatabaseError
from elasticsearch.exceptions import ElasticsearchException
from tdpservice.data_files.models import DataFile
from tdpservice.parsers.models import DataFileSummary, ParserError
from tdpservice.scheduling import parser_task
from tdpservice.search_indexes.util import DOCUMENTS, count_all_records
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.core.utils import log
from django.contrib.admin.models import ADDITION
from tdpservice.users.models import User
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command class."""

    help = "Delete and reparse a set of datafiles.."

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument("-q", "--fiscal_quarter", type=str, choices=["Q1", "Q2", "Q3", "Q4"],
                            help="Reparse all files in the fiscal quarter, e.g. Q1.")
        parser.add_argument("-y", "--fiscal_year", type=int, help="Reparse all files in the fiscal year, e.g. 2021.")
        parser.add_argument("-a", "--all", action='store_true', help="Clean and reparse all datafiles. If selected, "
                            "fiscal_year/quarter aren't necessary.")
        parser.add_argument("-f", "--files", nargs='+', type=str, help="Re-parse specific datafiles by datafile id")

    def _get_log_context(self, system_user):
        """Return logger context."""
        context = {'user_id': system_user.id,
                   'action_flag': ADDITION,
                   'object_repr': "Clean and Reparse"
                   }
        return context

    def _backup(self, backup_file_name, log_context):
        """Execute Postgres DB backup."""
        try:
            logger.info("Beginning reparse DB Backup.")
            call_command('backup_db', '-b', '-f', f'{backup_file_name}')
            logger.info("Backup complete! Commencing clean and reparse.")

            log("Database backup complete.",
                logger_context=log_context,
                level='info')
        except Exception as e:
            log("Database backup FAILED. Clean and reparse NOT executed. Database and Elastic are CONSISTENT!",
                logger_context=log_context,
                level='error')
            raise e

    def _handle_elastic(self, new_indices, log_context):
        """Create new Elastic indices and delete old ones."""
        if new_indices:
            try:
                logger.info("Creating new elastic indexes.")
                call_command('tdp_search_index', '--create', '-f', '--use-alias')
                log("Index creation complete.",
                    logger_context=log_context,
                    level='info')
            except ElasticsearchException as e:
                log("Elastic index creation FAILED. Clean and reparse NOT executed. "
                    "Database is CONSISTENT, Elastic is INCONSISTENT!",
                    logger_context=log_context,
                    level='error')
                raise e
            except Exception as e:
                log("Caught generic exception in _handle_elastic. Clean and reparse NOT executed. "
                    "Database is CONSISTENT, Elastic is INCONSISTENT!",
                    logger_context=log_context,
                    level='error')
                raise e

    def _delete_summaries(self, file_ids, log_context):
        """Raw delete all DataFileSummary objects."""
        try:
            qset = DataFileSummary.objects.filter(datafile_id__in=file_ids)
            count = qset.count()
            logger.info(f"Deleting {count} datafile summary objects.")
            qset._raw_delete(qset.db)
            logger.info("Successfully deleted datafile summary objects.")
        except DatabaseError as e:
            log('Encountered a DatabaseError while deleting DataFileSummary from Postgres. The database '
                'and Elastic are INCONSISTENT! Restore the DB from the backup as soon as possible!',
                logger_context=log_context,
                level='critical')
            raise e
        except Exception as e:
            log('Caught generic exception while deleting DataFileSummary. The database and Elastic are INCONSISTENT! '
                'Restore the DB from the backup as soon as possible!',
                logger_context=log_context,
                level='critical')
            raise e

    def __handle_elastic_doc_delete(self, doc, qset, model, elastic_exceptions, new_indices):
        """Delete documents from Elastic and handle exceptions."""
        if not new_indices:
            # If we aren't creating new indices, then we don't want duplicate data in the existing indices.
            # We alos use a Paginator here because it allows us to slice querysets based on a batch size. This
            # prevents a very large queryset from being brought into main memory when `doc().update(...)`
            # evaluates it by iterating over the queryset and deleting the models from ES.
            paginator = Paginator(qset, settings.BULK_CREATE_BATCH_SIZE)
            for page in paginator:
                try:
                    doc().update(page.object_list, refresh=True, action='delete')
                except ElasticsearchException:
                    elastic_exceptions[model] = elastic_exceptions.get(model, 0) + 1
                    continue

    def _delete_records(self, file_ids, new_indices, log_context):
        """Delete records, errors, and documents from Postgres and Elastic."""
        total_deleted = 0
        elastic_exceptions = dict()
        for doc in DOCUMENTS:
            try:
                model = doc.Django.model
                qset = model.objects.filter(datafile_id__in=file_ids).order_by('id')
                count = qset.count()
                total_deleted += count
                logger.info(f"Deleting {count} records of type: {model}.")
                self.__handle_elastic_doc_delete(doc, qset, model, elastic_exceptions, new_indices)
                qset._raw_delete(qset.db)
            except DatabaseError as e:
                log(f'Encountered a DatabaseError while deleting records of type {model} from Postgres. The database '
                    'and Elastic are INCONSISTENT! Restore the DB from the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e
            except Exception as e:
                log(f'Caught generic exception while deleting records of type {model}. The database and Elastic are '
                    'INCONSISTENT! Restore the DB from the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e

        if elastic_exceptions != {}:
            msg = ("Warning: Elastic is inconsistent and the database is consistent. "
                   "Models which generated the Elastic exception(s) are below:\n")
            for key, val in elastic_exceptions.items():
                msg += f"Model: {key} generated {val} Elastic Exception(s) while being deleted.\n"
            log(msg, logger_context=log_context, level='warn')
        return total_deleted

    def _delete_errors(self, file_ids, log_context):
        """Raw delete all ParserErrors for each file ID."""
        try:
            qset = ParserError.objects.filter(file_id__in=file_ids)
            count = qset.count()
            logger.info(f"Deleting {count} parser errors.")
            qset._raw_delete(qset.db)
            logger.info("Successfully deleted parser errors.")
        except DatabaseError as e:
            log('Encountered a DatabaseError while deleting ParserErrors from Postgres. The database '
                'and Elastic are INCONSISTENT! Restore the DB from the backup as soon as possible!',
                logger_context=log_context,
                level='critical')
            raise e
        except Exception as e:
            log('Caught generic exception while deleting ParserErrors. The database and Elastic are INCONSISTENT! '
                'Restore the DB from the backup as soon as possible!',
                logger_context=log_context,
                level='critical')
            raise e

    def _delete_associated_models(self, meta_model, file_ids, new_indices, log_context):
        """Delete all models associated to the selected datafiles."""
        self._delete_summaries(file_ids, log_context)
        self._delete_errors(file_ids, log_context)
        num_deleted = self._delete_records(file_ids, new_indices, log_context)
        meta_model.num_records_deleted = num_deleted

    def _handle_datafiles(self, files, meta_model, log_context):
        """Delete, re-save, and reparse selected datafiles."""
        for file in files:
            try:
                file.reparses.add(meta_model)
                file.save()
                parser_task.parse.delay(file.pk, reparse_id=meta_model.pk)
            except DatabaseError as e:
                log('Encountered a DatabaseError while re-creating datafiles. The database '
                    'and Elastic are INCONSISTENT! Restore the DB from the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e
            except Exception as e:
                log('Caught generic exception in _handle_datafiles. Database and Elastic are INCONSISTENT! '
                    'Restore the DB from the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e

    def _count_total_num_records(self, log_context):
        """Count total number of records in the database for meta object."""
        try:
            return count_all_records()
        except DatabaseError as e:
            log('Encountered a DatabaseError while counting records for meta model. The database '
                f'and Elastic are consistent! Cancelling reparse to be safe. \n{e}',
                logger_context=log_context,
                level='error')
            exit(1)
        except Exception as e:
            log('Encountered generic exception while counting records for meta model. '
                f'The database and Elastic are consistent! Cancelling reparse to be safe. \n{e}',
                logger_context=log_context,
                level='error')
            exit(1)

    def _assert_sequential_execution(self, log_context):
        """Assert that no other reparse commands are still executing."""
        latest_meta_model = ReparseMeta.get_latest()
        now = timezone.now()
        is_not_none = latest_meta_model is not None
        if (is_not_none and latest_meta_model.timeout_at is None):
            log(f"The latest ReparseMeta model's (ID: {latest_meta_model.pk}) timeout_at field is None. "
                "Cannot safely execute reparse, please fix manually.",
                logger_context=log_context,
                level='error')
            return False
        if (is_not_none and not ReparseMeta.assert_all_files_done(latest_meta_model) and
                not now > latest_meta_model.timeout_at):
            log('A previous execution of the reparse command is RUNNING. Cannot execute in parallel, exiting.',
                logger_context=log_context,
                level='warn')
            return False
        elif (is_not_none and latest_meta_model.timeout_at is not None and now > latest_meta_model.timeout_at and not
              ReparseMeta.assert_all_files_done(latest_meta_model)):
            log("Previous reparse has exceeded the timeout. Allowing execution of the command.",
                logger_context=log_context,
                level='warn')
            return True
        return True

    def _should_exit(self, condition):
        """Exit on condition."""
        if condition:
            exit(1)

    def _calculate_timeout(self, num_files, num_records):
        """Estimate a timeout parameter based on the number of files and the number of records."""
        # Increase by an order of magnitude to have the bases covered.
        line_parse_time = settings.MEDIAN_LINE_PARSE_TIME * 10
        time_to_queue_datafile = 10
        time_in_seconds = num_files * time_to_queue_datafile + num_records * line_parse_time
        delta = timedelta(seconds=time_in_seconds)
        logger.info(f"Setting timeout for the reparse event to be {delta} seconds from meta model creation date.")
        return delta

    def _handle_input(self, testing, continue_msg):
        """Handle user input."""
        if not testing:
            c = str(input(f'\n{continue_msg}\nContinue [y/n]? ')).lower()
            if c not in ['y', 'yes']:
                print('Cancelled.')
                exit(0)

    def get_files_to_reparse(case, fiscal_year, fiscal_quarter, selected_files, reparse_all):
        """Get the files to reparse."""
        backup_file_name = "/tmp/reparsing_backup"
        files = DataFile.objects.all()
        continue_msg = "You have selected to reparse datafiles for FY {fy} and {q}. The reparsed files "
        if selected_files:
            files = files.filter(id__in=selected_files)
            backup_file_name += "_selected_files"
            continue_msg = continue_msg.format(fy=f"selected files: {str(selected_files)}", q="Q1-4")
        if reparse_all:
            backup_file_name += "_FY_All_Q1-4"
            continue_msg = continue_msg.format(fy="All", q="Q1-4")
        else:
            if not fiscal_year and not fiscal_quarter and not selected_files:
                print(
                    'Options --fiscal_year and --fiscal_quarter not set. '
                    'Provide either option to continue, or --all to wipe all submissions.'
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

    def handle(self, *args, **options):
        """Delete and reparse datafiles matching a query."""
        fiscal_year = options.get('fiscal_year', None)
        fiscal_quarter = options.get('fiscal_quarter', None)
        reparse_all = options.get('all', False)
        print(f'************** reparse all {reparse_all}')
        selected_files = options.get('files', None)
        selected_files = [int(file) for file in selected_files[0].split(',')] if selected_files else None
        print(f'************** selected files {selected_files}')
        new_indices = reparse_all is True

        # Option that can only be specified by calling `handle` directly and passing it.
        testing = options.get('testing', False)
        ##

        args_passed = fiscal_year is not None or fiscal_quarter is not None or reparse_all or selected_files

        if not args_passed:
            logger.warning("No arguments supplied.")
            self.print_help("manage.py", "clean_and_parse")
            return

        # Set up the backup file name and continue message
        files, backup_file_name, continue_msg = self.get_files_to_reparse(
            fiscal_year,
            fiscal_quarter,
            selected_files,
            reparse_all)

        # end of the if statement

        fmt_str = "be" if new_indices else "NOT be"
        continue_msg += "will {new_index} stored in new indices and the old indices ".format(new_index=fmt_str)

        num_files = files.count()
        fmt_str = f"ALL ({num_files})" if reparse_all else f"({num_files})"
        continue_msg += "\nThese options will delete and reparse {0} datafiles.".format(fmt_str)

        if not selected_files:
            self._handle_input(testing, continue_msg)

        system_user, created = User.objects.get_or_create(username='system')
        if created:
            logger.debug('Created reserved system user.')
        log_context = self._get_log_context(system_user)

        all_fy = "All"
        all_q = "Q1-4"

        if not selected_files:
            log(f"Starting clean and reparse command for FY {fiscal_year if fiscal_year else all_fy} and "
                f"{fiscal_quarter if fiscal_quarter else all_q}",
                logger_context=log_context,
                level='info')
        else:
            log(f"Starting clean and reparse action for files: {str(selected_files)}",
                logger_context=log_context,
                level='info')

        if num_files == 0:
            log(f"No files available for the selected Fiscal Year: {fiscal_year if fiscal_year else all_fy} and "
                f"Quarter: {fiscal_quarter if fiscal_quarter else all_q}. Nothing to do.",
                logger_context=log_context,
                level='warn')
            return

        is_sequential = self._assert_sequential_execution(log_context)
        self._should_exit(not is_sequential)
        meta_model = ReparseMeta.objects.create(fiscal_quarter=fiscal_quarter,
                                                fiscal_year=fiscal_year,
                                                all=reparse_all,
                                                new_indices=new_indices,
                                                delete_old_indices=new_indices)

        # Backup the Postgres DB
        backup_file_name += f"_rpv{meta_model.pk}.pg"
        self._backup(backup_file_name, log_context)

        meta_model.db_backup_location = backup_file_name
        meta_model.save()

        # Create and delete Elastic indices if necessary
        self._handle_elastic(new_indices, log_context)

        # Delete records from Postgres and Elastic if necessary
        file_ids = files.values_list('id', flat=True).distinct()
        meta_model.total_num_records_initial = self._count_total_num_records(log_context)
        meta_model.save()

        self._delete_associated_models(meta_model, file_ids, new_indices, log_context)

        meta_model.timeout_at = meta_model.created_at + self._calculate_timeout(num_files,
                                                                                meta_model.num_records_deleted)
        meta_model.save()
        logger.info(f"Deleted a total of {meta_model.num_records_deleted} records accross {num_files} files.")

        # Delete and re-save datafiles to handle cascading dependencies
        logger.info(f'Deleting and re-parsing {num_files} files')
        self._handle_datafiles(files, meta_model, log_context)

        log("Database cleansing complete and all files have been re-scheduling for parsing and validation.",
            logger_context=log_context,
            level='info')
        log(f"Clean and reparse command completed. All files for FY {fiscal_year if fiscal_year else all_fy} and "
            f"{fiscal_quarter if fiscal_quarter else all_q} have been queued for parsing.",
            logger_context=log_context,
            level='info')
        logger.info('Done. All tasks have been queued to parse the selected datafiles.')
