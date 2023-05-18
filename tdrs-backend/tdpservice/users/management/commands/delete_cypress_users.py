"""delete_cypress_user command."""

import logging

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.conf import settings

User = get_user_model()
logger = logging.getLogger(__name__)

def delete_cypress_user(username):
    """Delete the user if it exists."""
    try:
        user = User.objects.get(username=username)
        user.delete()
        logger.debug(f'Deleting {username}')
    except User.DoesNotExist:
        logger.debug(f'{username} does not exist')


class Command(BaseCommand):
    """Command class."""

    help = "Delete test users if they exist."

    def add_arguments(self, parser):
        """Add custom argument(s) for command."""
        parser.add_argument("-usernames", nargs="+", type=str)

    def handle(self, *args, **options):
        """Delete test users if they exist."""
        if settings.DEBUG:
            for username in options['usernames']:
                delete_cypress_user(username)
        else:
            raise Exception('Cannot delete cypress users in non-dev environments.')
