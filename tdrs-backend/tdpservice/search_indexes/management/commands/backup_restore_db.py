import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from tdpservice.data_files.models import DataFile
from tdpservice.scheduling import parser_task
from tdpservice.search_indexes.documents import tanf, ssp, tribal
from tdpservice.scheduling.db_backup import main, get_system_values
from tdpservice.users.models import User
from tdpservice.core.utils import log
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Command class."""

    help = "Backup the Postgres DB to a file or restore the Postgres DB from a file."

    def add_arguments(self, parser):
        """Add arguments to the management command."""
        parser.add_argument("-b", "--backup", action='store_true', help="Backup the databse to the file.")
        parser.add_argument("-r", "--restore", action='store_true', help="Restore the database from the file.")
        parser.add_argument("-f", "--file", required=True, type=str, action='store', help="The FQP of the file.")

    def handle(self, *args, **options):
        if (not options['backup'] and not options['restore']) or (options['backup'] and options['restore']):
            print("\nYou must specify -b or -r but not both.\n")
            return
        switch = '-b' if options['backup'] else '-r'
        file = options["file"]
        if not settings.USE_LOCALSTACK:
            system_user, created = User.objects.get_or_create(username='system')
            if created:
                logger.debug('Created reserved system user.')
            main([f'{switch}', '-f', f'{file}'], sys_values=get_system_values(), system_user=system_user)
            logger.info("Cloud backup/restore job complete.")
        else:
            os.system(f"export PGPASSWORD={settings.DATABASES['default']['PASSWORD']}")

            db_host = settings.DATABASES['default']['HOST']
            db_port = settings.DATABASES['default']['PORT']
            db_name = settings.DATABASES['default']['NAME']
            db_user = settings.DATABASES['default']['USER']

            if options['backup']:
                cmd = (f"pg_dump -h {db_host} -p {db_port} -d {db_name} -U {db_user} -F c --no-password --no-acl "
                       f"--no-owner -f {file} -v")
                os.system(cmd)
                logger.info(f"Local backup saved to: {file}.")
            elif options['restore']:
                cmd = (f"createdb -U {db_user} -h {db_host} -T template0 {db_name}")
                logger.info(f"Creating DB with command: {cmd}")
                os.system(cmd)
                logger.info(f"Successfully created DB: {db_name}.")

                cmd = (f"pg_restore -p {db_port} -h {db_host} -U {db_user} -d {db_name} {file}")
                logger.info(f"Restoring DB with command: {cmd}")
                os.system(cmd)
                logger.info(f"Successfully restored DB: {db_name} from file: {file}.")
            logger.info("Local backup/restore job complete.")
