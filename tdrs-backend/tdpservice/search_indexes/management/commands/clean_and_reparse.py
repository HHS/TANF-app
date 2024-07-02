"""
Delete and reparse a set of datafiles
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from elasticsearch.helpers.errors import BulkIndexError
from tdpservice.data_files.models import DataFile
from tdpservice.scheduling import parser_task
from tdpservice.search_indexes.documents import tanf, ssp, tribal
from tdpservice.core.utils import log
from django.contrib.admin.models import ADDITION
from tdpservice.users.models import User
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command class."""

    help = "Delete and reparse a set of datafiles. All reparsed data will be moved into a new set of Elastic indexes."

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument("-q", "--fiscal_quarter", type=str, help="Reparse all files in the fiscal quarter, "
                            "e.g. Q1.")
        parser.add_argument("-y", "--fiscal_year", type=str, help="Reparse all files in the fiscal year, e.g. 2021.")
        parser.add_argument("-a", "--all", action='store_true', help="Clean and reparse all datafiles. If selected, "
                            "fiscal_year/quarter aren't necessary.")
        parser.add_argument("-n", "--new_indices", action='store_true', help="Move reparsed data to new Elastic "
                            "indices.")
        parser.add_argument("-d", "--delete_indices", action='store_true', help="Requires new_indices. Delete the "
                            "current indices.")

    def __get_log_context(self, system_user):
        context = {'user_id': system_user.id,
                   'action_flag': ADDITION,
                   'object_repr': "Clean and Reparse"
                   }
        return context

    def handle(self, *args, **options):
        """Delete datafiles matching a query."""
        fiscal_year = options.get('fiscal_year', None)
        fiscal_quarter = options.get('fiscal_quarter', None)
        delete_all = options.get('all', False)
        new_indices = options.get('new_indices', False)
        delete_indices = options.get('delete_indices', False)

        backup_file_name = f"/tmp/reparsing_backup"
        files = None
        if delete_all:
            files = DataFile.objects.all()
            print(
                f'This will delete ALL ({files.count()}) '
                'data files for ALL submission periods.'
            )
            backup_file_name += "_FY_all_Q1-4"
        else:
            if not fiscal_year and not fiscal_quarter:
                print(
                    'Options --fiscal_year and --fiscal_quarter not set. '
                    'Provide either option to continue, or --all to wipe all submissions.'
                )
                return
            files = DataFile.objects.all()
            if (fiscal_year and fiscal_quarter):
                files = files.filter(year=fiscal_year, quarter=fiscal_quarter)
                backup_file_name += f"_FY_{fiscal_year}_Q{fiscal_quarter}"
            elif fiscal_year:
                files = files.filter(year=fiscal_year)
                backup_file_name += f"_FY_{fiscal_year}_Q1-4"
            elif fiscal_quarter:
                files = files.filter(quarter=fiscal_quarter)
                backup_file_name += f"_FY_all_Q{fiscal_quarter}"
            print(
                f'This will delete {files.count()} datafiles, '
                'create new elasticsearch indices, '
                'and re-parse each of the datafiles.'
            )

        c = str(input('Continue [y/n]? ')).lower()
        if c not in ['y', 'yes']:
            print('Cancelled.')
            return

        system_user, created = User.objects.get_or_create(username='system')
        if created:
            logger.debug('Created reserved system user.')
        log_context = self.__get_log_context(system_user)

        all_fy = "all"
        all_q = "1-4"
        log(f"Beginning Clean and reparse for FY {fiscal_year if fiscal_year else all_fy} and "
            f"Q{fiscal_quarter if fiscal_quarter else all_q}",
            logger_context=log_context,
            level='info')

        if files.count() == 0:
            log(f"No files available for the selected Fiscal Year: {fiscal_year if fiscal_year else all_fy} and "
                f"Quarter: {fiscal_quarter if fiscal_quarter else all_q}. Nothing to do.",
                logger_context=log_context,
                level='warn')
            return

        try:
            logger.info("Beginning reparse DB Backup.")
            pattern = "%Y-%m-%d_%H.%M.%S"
            backup_file_name += f"_{datetime.now().strftime(pattern)}.pg"
            call_command('backup_restore_db', '-b', '-f', f'{backup_file_name}')
            if os.path.getsize(backup_file_name) == 0:
                raise Exception("DB backup failed! Backup file size is 0 bytes!")
            logger.info("Backup complete! Commencing clean and reparse.")
        except Exception as e:
            log(f"Database backup FAILED. Clean and re-parse NOT executed. Database and Elastic are CONSISTENT!",
                logger_context=log_context,
                level='error')
            raise e

        if new_indices:
            try:
                if not delete_indices:
                    call_command('tdp_search_index', '--create', '-f', '--use-alias', '--use-alias-keep-index')
                else:
                    call_command('tdp_search_index', '--create', '-f', '--use-alias')
            except Exception as e:
                log(f"Elastic index creation FAILED. Clean and re-parse NOT executed. "
                    "Database is CONSISTENT, Elastic is INCONSISTENT!",
                    logger_context=log_context,
                    level='error')
                raise e
            # TODO: Need to ask Alex if we can run some queries in prod to deduce the average number of records per DF.

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

        log("DB backup and Index creation complete. Beginning database cleanse.",
            logger_context=log_context,
            level='info')

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
            except BulkIndexError as e:
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
        logger.info(f"Deleted a total of {total_deleted} records accross {files.count()} files.")

        logger.info(f'Deleting and reparsing {files.count()} files')
        for f in files:
            try:
                f.delete()
            except Exception as e:
                log(f'DataFile.delete failed for id: {f.pk}. Database and Elastic are INCONSISTENT! Restore the '
                    'DB from the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e

            try:
                f.save()
            except Exception as e:
                log(f'DataFile.save failed for id: {f.pk}. Database and Elastic are INCONSISTENT! Restore the '
                    'DB from the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e

            # latest version only? -> possible new ticket
            parser_task.parse.delay(f.pk, should_send_submission_email=False)

        log("Database cleansing complete and all files have been rescheduling for parsing and validation.",
            logger_context=log_context,
            level='info')
        log(f"Clean and reparse completed for FY {fiscal_year if fiscal_year else all_fy} and "
            f"Q{fiscal_quarter if fiscal_quarter else all_q}",
            logger_context=log_context,
            level='info')
        logger.info('Done. All tasks have been queued to re-parse the selected datafiles.')
