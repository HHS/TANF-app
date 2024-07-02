"""Command to facilitate backup of the Postgres DB."""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from tdpservice.scheduling.db_backup import main, get_system_values
from tdpservice.users.models import User
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Command class."""

    help = "Backup the Postgres DB to a file locally or to S3 if in cloud.gov."

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument("-b", "--backup", required=True, action='store_true',
                            help="Backup the databse to the file.")
        parser.add_argument("-f", "--file", required=True, type=str, action='store',
                            help="The FQP of the file.")

    def handle(self, *args, **options):
        """Backup the Postgres DB."""
        file = options["file"]
        if not settings.USE_LOCALSTACK:
            system_user, created = User.objects.get_or_create(username='system')
            if created:
                logger.debug('Created reserved system user.')
            try:
                main(['-b', '-f', f'{file}'], sys_values=get_system_values(), system_user=system_user)
            except Exception as e:
                logger.error(f"Exception occured while executing backup/restore: {e}")
                raise e
            logger.info("Cloud backup/restore job complete.")
        else:
            db_host = settings.DATABASES['default']['HOST']
            db_port = settings.DATABASES['default']['PORT']
            db_name = settings.DATABASES['default']['NAME']
            db_user = settings.DATABASES['default']['USER']

            export_password = f"export PGPASSWORD={settings.DATABASES['default']['PASSWORD']}"
            try:
                cmd = (f"{export_password} && pg_dump -h {db_host} -p {db_port} -d {db_name} -U {db_user} -F c "
                       f"--no-password --no-acl --no-owner -f {file}")
                os.system(cmd)
                logger.info(f"Local backup saved to: {file}.")
                logger.info("Local backup job complete.")
            except Exception as e:
                raise e
