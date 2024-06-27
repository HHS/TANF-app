"""
Delete and reparse a set of datafiles
"""

import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from tdpservice.data_files.models import DataFile
from tdpservice.scheduling import parser_task
from tdpservice.search_indexes.documents import tanf, ssp, tribal
from tdpservice.scheduling.db_backup import backup_database, upload_file, get_system_values
from tdpservice.users.models import User
from tdpservice.core.utils import log


class Command(BaseCommand):
    """Command class."""

    help = "Delete and reparse a set of datafiles"

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument("--fiscal_quarter", type=str)
        parser.add_argument("--fiscal_year", type=str)
        parser.add_argument("--all", action='store_true')

    def backup_postgres_db(self):
        sys_values = {
            'SPACE': '',
            'POSTGRES_CLIENT_DIR': 'postgres',
            'POSTGRES_CLIENT': 'postgres',
            'S3_ENV_VARS': '',
            'S3_CREDENTIALS': '',
            'S3_URI': '',
            'S3_ACCESS_KEY_ID': settings.AWS_S3_DATAFILES_ACCESS_KEY,
            'S3_SECRET_ACCESS_KEY': settings.AWS_S3_DATAFILES_SECRET_KEY,
            'S3_BUCKET': settings.AWS_S3_DATAFILES_BUCKET_NAME,
            'S3_REGION': settings.AWS_S3_DATAFILES_REGION_NAME,
            'DATABASE_URI': 'localhost',
            'AWS_ACCESS_KEY_ID': settings.AWS_S3_DATAFILES_ACCESS_KEY,
            'AWS_SECRET_ACCESS_KEY': settings.AWS_S3_DATAFILES_SECRET_KEY,
            'DATABASE_PORT': settings.DATABASES['default']['PORT'],
            'DATABASE_PASSWORD': settings.DATABASES['default']['PASSWORD'],
            'DATABASE_DB_NAME': settings.DATABASES['default']['NAME'],
            'DATABASE_HOST': settings.DATABASES['default']['HOST'],
            'DATABASE_USERNAME': settings.DATABASES['default']['USER'],
            'PGPASSFILE': '',
        }
        if settings.USE_LOCALSTACK is False:
            sys_values = get_system_values()
        else:  # fix me :)
            return

        arg_file = "/tmp/backup.pg"
        arg_database = sys_values['DATABASE_URI']
        system_user, created = User.objects.get_or_create(username='system')
        # logger_context = {}

        # log(
        #     user_id=system_user.pk,
        #     content_type_id=content_type.pk,
        #     object_id=None,
        #     object_repr="Begining Database Backup",
        #     action_flag=ADDITION,
        #     change_message="Begining database backup."
        # )
        # back up database
        backup_database(
            file_name=arg_file,
            postgres_client=sys_values['POSTGRES_CLIENT_DIR'],
            database_uri=arg_database,
            system_user=system_user
        )

        # upload backup file
        upload_file(
            file_name=arg_file,
            bucket=sys_values['S3_BUCKET'],
            sys_values=sys_values,
            system_user=system_user,
            region=sys_values['S3_REGION'],
            object_name="backup"+arg_file,
        )

        # log(
        #     user_id=system_user.pk,
        #     content_type_id=content_type.pk,
        #     object_id=None,
        #     object_repr="Finished Database Backup",
        #     action_flag=ADDITION,
        #     change_message="Finished database backup."
        # )

        # logger.info(f"Deleting {arg_file} from local storage.")
        os.system('rm ' + arg_file)

    def handle(self, *args, **options):
        """Delete datafiles matching a query."""
        # try
        try:
            self.backup_postgres_db()
        except Exception as e:
            print('Database backup failed with exception')
            raise e

        fiscal_year = options.get('fiscal_year', None)
        fiscal_quarter = options.get('fiscal_quarter', None)
        delete_all = options.get('all', False)

        files = None
        if delete_all:
            files = DataFile.objects.all()
            print(
                f'This will delete ALL ({files.count()}) '
                'data files for ALL submission periods.'
            )
        else:
            if not fiscal_year and not fiscal_quarter:
                print(
                    'Options --fiscal_year and --fiscal_quarter not set. '
                    'Provide either option to continue, or --all to wipe all submissions.'
                )
                return
            files = DataFile.objects.all()
            files = files.filter(year=fiscal_year) if fiscal_year else files
            files = files.filter(quarter=fiscal_quarter) if fiscal_quarter else files
            print(
                f'This will delete {files.count()} datafiles, '
                'create new elasticsearch indices, '
                'and re-parse each of the datafiles.'
            )

        c = str(input('Continue [y/n]? ')).lower()
        if c not in ['y', 'yes']:
            print('Cancelled.')
            return

        call_command('tdp_search_index', '--create', '-f')

        file_ids = files.values_list('id', flat=True).distinct()

        model_types = [
            tanf.TANF_T1, tanf.TANF_T2, tanf.TANF_T3, tanf.TANF_T4, tanf.TANF_T5, tanf.TANF_T6, tanf.TANF_T7,
            ssp.SSP_M1, ssp.SSP_M2, ssp.SSP_M3, ssp.SSP_M4, ssp.SSP_M5, ssp.SSP_M6, ssp.SSP_M7,
            tribal.Tribal_TANF_T1, tribal.Tribal_TANF_T2, tribal.Tribal_TANF_T3, tribal.Tribal_TANF_T4, tribal.Tribal_TANF_T5, tribal.Tribal_TANF_T6, tribal.Tribal_TANF_T7
        ]

        for m in model_types:
            objs = m.objects.all().filter(datafile_id__in=file_ids)
            print(f'deleting {objs.count()}, {m} objects')

            # atomic delete?
            try:
                objs._raw_delete(objs.db)
            except Exception as e:
                print(f'_raw_delete failed for model {m}')
                raise e

        print(f'Deleting and reparsing {files.count()} files')
        for f in files:

            try:
                f.delete()
            except Exception as e:
                print(f'DataFile.delete failed for id: {f.pk}')
                raise e

            try:
                f.save()
            except Exception as e:
                print(f'DataFile.save failed for id: {f.pk}')
                raise e

            # latest version only? -> possible new ticket
            parser_task.parse.delay(f.pk, should_send_submission_email=False)
        print('Done.')
