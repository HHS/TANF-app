"""Delete and re-parse a set of datafiles."""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from elasticsearch.exceptions import ElasticsearchException
from tdpservice.data_files.models import DataFile
from tdpservice.scheduling import parser_task
from tdpservice.search_indexes.documents import tanf, ssp, tribal
from tdpservice.core.utils import log
from django.contrib.admin.models import ADDITION
from tdpservice.users.models import User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command class."""

    help = "Delete and re-parse a set of datafiles. All re-parsed data will be moved into a new set of Elastic indexes."

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument("-q", "--fiscal_quarter", type=str, choices=["Q1", "Q2", "Q3", "Q4"],
                            help="Re-parse all files in the fiscal quarter, e.g. Q1.")
        parser.add_argument("-y", "--fiscal_year", type=int, help="Re-parse all files in the fiscal year, e.g. 2021.")
        parser.add_argument("-a", "--all", action='store_true', help="Clean and re-parse all datafiles. If selected, "
                            "fiscal_year/quarter aren't necessary.")
        parser.add_argument("-n", "--new_indices", action='store_true', help="Move re-parsed data to new Elastic "
                            "indices.")
        parser.add_argument("-d", "--delete_indices", action='store_true', help="Requires new_indices. Delete the "
                            "current Elastic indices.")

    def __get_log_context(self, system_user):
        """Return logger context."""
        context = {'user_id': system_user.id,
                   'action_flag': ADDITION,
                   'object_repr': "Clean and Re-parse"
                   }
        return context

    def __backup(self, backup_file_name, log_context):
        """Execute Postgres DB backup."""
        try:
            logger.info("Beginning re-parse DB Backup.")
            call_command('backup_db', '-b', '-f', f'{backup_file_name}')
            logger.info("Backup complete! Commencing clean and re-parse.")

            log("Database backup complete.",
                logger_context=log_context,
                level='info')
        except Exception as e:
            log("Database backup FAILED. Clean and re-parse NOT executed. Database and Elastic are CONSISTENT!",
                logger_context=log_context,
                level='error')
            raise e

    def __handle_elastic(self, new_indices, delete_indices, log_context):
        """Create new Elastic indices and delete old ones."""
        if new_indices:
            try:
                if not delete_indices:
                    call_command('tdp_search_index', '--create', '-f', '--use-alias', '--use-alias-keep-index')
                else:
                    call_command('tdp_search_index', '--create', '-f', '--use-alias')
                log("Index creation complete.",
                    logger_context=log_context,
                    level='info')
            except Exception as e:
                log("Elastic index creation FAILED. Clean and re-parse NOT executed. "
                    "Database is CONSISTENT, Elastic is INCONSISTENT!",
                    logger_context=log_context,
                    level='error')
                raise e
            # TODO: Need to ask Alex if we can run some queries in prod to deduce the average number of records per DF.

    def __delete_records(self, docs, file_ids, new_indices, log_context):
        """Delete records and documents from Postgres and Elastic respectively."""
        total_deleted = 0
        for doc in docs:
            # atomic delete?
            try:
                model = doc.Django.model
                qset = model.objects.all().filter(datafile_id__in=file_ids)
                total_deleted += qset.count()
                if not new_indices:
                    # If we aren't creating new indices, then we don't want duplicate data in the existing indices.
                    doc().update(qset, refresh=True, action='delete')
                qset._raw_delete(qset.db)
            except ElasticsearchException as e:
                log(f'Elastic document delete failed for model {model}. Database and Elastic are INCONSISTENT! Restore '
                    'the DB from the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e
            except Exception as e:
                log(f'_raw_delete failed for model {model}. Database and Elastic are INCONSISTENT! Restore the DB from '
                    'the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e
        return total_deleted

    def __handle_datafiles(self, files, log_context):
        """Delete, re-save, and re-parse selected datafiles."""
        for f in files:
            try:
                f.delete()
                f.save()
            except Exception as e:
                log(f'DataFile.delete or DataFile.save failed for id: {f.pk}. Database and Elastic are INCONSISTENT! '
                    'Restore the DB from the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e

            # latest version only? -> possible new ticket
            parser_task.parse.delay(f.pk, should_send_submission_email=False)

    def handle(self, *args, **options):
        """Delete and re-parse datafiles matching a query."""
        fiscal_year = options.get('fiscal_year', None)
        fiscal_quarter = options.get('fiscal_quarter', None)
        delete_all = options.get('all', False)
        new_indices = options.get('new_indices', False)
        delete_indices = options.get('delete_indices', False)

        args_passed = fiscal_quarter is not None or fiscal_quarter is not None or delete_all

        if not args_passed:
            logger.warn("No arguments supplied.")
            self.print_help("manage.py", "clean_and_parse")
            return

        backup_file_name = "/tmp/reparsing_backup"
        files = DataFile.objects.all()
        continue_msg = "You have selected to re-parse datafiles for FY {fy} and {q}. The re-parsed files "
        if delete_all:
            backup_file_name += "_FY_All_Q1-4"
            continue_msg = continue_msg.format(fy="All", q="Q1-4")
        else:
            if not fiscal_year and not fiscal_quarter:
                print(
                    'Options --fiscal_year and --fiscal_quarter not set. '
                    'Provide either option to continue, or --all to wipe all submissions.'
                )
                return
            if fiscal_year is not None and fiscal_quarter is not None:
                files = files.filter(year=fiscal_year, quarter=fiscal_quarter)
                backup_file_name += f"_FY_{fiscal_year}_Q{fiscal_quarter}"
                continue_msg = continue_msg.format(fy=fiscal_year, q=fiscal_quarter)
            elif fiscal_year is not None:
                files = files.filter(year=fiscal_year)
                backup_file_name += f"_FY_{fiscal_year}_Q1-4"
                continue_msg = continue_msg.format(fy=fiscal_year, q="Q1-4")
            elif fiscal_quarter is not None:
                files = files.filter(quarter=fiscal_quarter)
                backup_file_name += f"_FY_All_Q{fiscal_quarter}"
                continue_msg = continue_msg.format(fy="All", q=fiscal_quarter)

        fmt_str = "be" if new_indices else "NOT be"
        continue_msg += "will {new_index} stored in new indices and the old indices ".format(new_index=fmt_str)

        fmt_str = "be" if delete_indices else "NOT be"
        continue_msg += "will {old_index} deleted.".format(old_index=fmt_str)

        fmt_str = f"ALL ({files.count()})" if delete_all else f"({files.count()})"
        continue_msg += "\nThese options will delete and re-parse {0} datafiles.".format(fmt_str)

        c = str(input(f'\n{continue_msg}\nContinue [y/n]? ')).lower()
        if c not in ['y', 'yes']:
            print('Cancelled.')
            return

        system_user, created = User.objects.get_or_create(username='system')
        if created:
            logger.debug('Created reserved system user.')
        log_context = self.__get_log_context(system_user)

        all_fy = "All"
        all_q = "1-4"
        log(f"Beginning Clean and re-parse for FY {fiscal_year if fiscal_year else all_fy} and "
            f"Q{fiscal_quarter if fiscal_quarter else all_q}",
            logger_context=log_context,
            level='info')

        if files.count() == 0:
            log(f"No files available for the selected Fiscal Year: {fiscal_year if fiscal_year else all_fy} and "
                f"Quarter: {fiscal_quarter if fiscal_quarter else all_q}. Nothing to do.",
                logger_context=log_context,
                level='warn')
            return

        # Backup the Postgres DB
        pattern = "%Y-%m-%d_%H.%M.%S"
        backup_file_name += f"_{datetime.now().strftime(pattern)}.pg"
        self.__backup(backup_file_name, log_context)

        # Create and delete Elastic indices if necessary
        self.__handle_elastic(new_indices, delete_indices, log_context)

        # Delete records from Postgres and Elastic if necessary
        file_ids = files.values_list('id', flat=True).distinct()
        docs = [
                tanf.TANF_T1DataSubmissionDocument, tanf.TANF_T2DataSubmissionDocument,
                tanf.TANF_T3DataSubmissionDocument, tanf.TANF_T4DataSubmissionDocument,
                tanf.TANF_T5DataSubmissionDocument, tanf.TANF_T6DataSubmissionDocument,
                tanf.TANF_T7DataSubmissionDocument,

                ssp.SSP_M1DataSubmissionDocument, ssp.SSP_M2DataSubmissionDocument, ssp.SSP_M3DataSubmissionDocument,
                ssp.SSP_M4DataSubmissionDocument, ssp.SSP_M5DataSubmissionDocument, ssp.SSP_M6DataSubmissionDocument,
                ssp.SSP_M7DataSubmissionDocument,

                tribal.Tribal_TANF_T1DataSubmissionDocument, tribal.Tribal_TANF_T2DataSubmissionDocument,
                tribal.Tribal_TANF_T3DataSubmissionDocument, tribal.Tribal_TANF_T4DataSubmissionDocument,
                tribal.Tribal_TANF_T5DataSubmissionDocument, tribal.Tribal_TANF_T6DataSubmissionDocument,
                tribal.Tribal_TANF_T7DataSubmissionDocument
            ]
        total_deleted = self.__delete_records(docs, file_ids, new_indices, log_context)
        logger.info(f"Deleted a total of {total_deleted} records accross {files.count()} files.")

        # Delete and re-save datafiles to handle cascading dependencies
        logger.info(f'Deleting and reparsing {files.count()} files')
        self.__handle_datafiles(files, log_context)

        log("Database cleansing complete and all files have been re-scheduling for parsing and validation.",
            logger_context=log_context,
            level='info')
        log(f"Clean and re-parse completed for FY {fiscal_year if fiscal_year else all_fy} and "
            f"Q{fiscal_quarter if fiscal_quarter else all_q}",
            logger_context=log_context,
            level='info')
        logger.info('Done. All tasks have been queued to re-parse the selected datafiles.')
