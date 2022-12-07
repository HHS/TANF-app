"""generate_cypress_users command."""

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.conf import settings


import factory

User = get_user_model()


def get_or_create_user(username):
    user = None

    try:
        user = User.objects.get(username=username)
        print(f'found {username}')
    except User.DoesNotExist:
        user = User.objects.create(username=username)
        print(f'created {username}')

    return user


class Command(BaseCommand):
    """Command class."""

    help = "Generate a test user for each role."

    def handle(self, *args, **options):
        """Generate a test user for each role."""

        if settings.DEBUG:
            cypress_new_user = get_or_create_user('new-cypress@goraft.tech')
        else:
            raise Exception('Cannot create cypress users in non-dev environments.')
