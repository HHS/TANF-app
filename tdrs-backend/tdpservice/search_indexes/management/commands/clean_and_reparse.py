"""
Delete and reparse a set of datafiles
"""

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
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
        parser.add_argument("-q", "--fiscal_quarter", type=str)
        parser.add_argument("-y", "--fiscal_year", type=str)
        parser.add_argument("-a", "--all", action='store_true')
        parser.add_argument("-n", "--new-indices", action='store_true')
        parser.add_argument("-d", "--delete-old-indices", action='store_true')

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
        delete_old_indices = options.get('delete_old_indices', False)

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
            pattern = "%d-%m-%Y_%H:%M:%S"
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
                if not delete_old_indices:
                    call_command('tdp_search_index', '--create', '-f', '--use-alias', '--use-alias-keep-index')
                else:
                    call_command('tdp_search_index', '--create', '-f', '--use-alias')
            except Exception as e:
                log(f"Elastic index creation FAILED. Clean and re-parse NOT executed. "
                    "Database is CONSISTENT, Elastic is INCONSISTENT!",
                    logger_context=log_context,
                    level='error')
                raise e

        file_ids = files.values_list('id', flat=True).distinct()

        model_types = [
            tanf.TANF_T1, tanf.TANF_T2, tanf.TANF_T3, tanf.TANF_T4, tanf.TANF_T5, tanf.TANF_T6, tanf.TANF_T7,
            ssp.SSP_M1, ssp.SSP_M2, ssp.SSP_M3, ssp.SSP_M4, ssp.SSP_M5, ssp.SSP_M6, ssp.SSP_M7,
            tribal.Tribal_TANF_T1, tribal.Tribal_TANF_T2, tribal.Tribal_TANF_T3, tribal.Tribal_TANF_T4, tribal.Tribal_TANF_T5, tribal.Tribal_TANF_T6, tribal.Tribal_TANF_T7
        ]

        log("DB backup and Index creation complete. Beginning database cleanse.",
            logger_context=log_context,
            level='info')

        for m in model_types:
            objs = m.objects.all().filter(datafile_id__in=file_ids)
            logger.info(f'Deleting {objs.count()}, {m} objects')

            # atomic delete?
            try:
                objs._raw_delete(objs.db)
            except Exception as e:
                log(f'_raw_delete failed for model {m}. Database and Elastic are INCONSISTENT! Restore the DB from '
                    'the backup as soon as possible!',
                    logger_context=log_context,
                    level='critical')
                raise e

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
