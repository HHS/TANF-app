"""generate_test_users command."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from django.db import IntegrityError, transaction

import factory

User = get_user_model()


class Command(BaseCommand):
    """Command class."""

    help = "Generate a test user for each role."

    def handle(self, *args, **options):
        """Generate a test user for each role."""
        first_name = factory.Faker("first_name")
        last_name = factory.Faker("last_name")
        password = "test_password"  # Static password so we can login.
        user_count = 0
        try:
            user = User.objects.create_user(
                username="test__unassigned",
                email="test+unassigned@example.com",
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
            superuser = User.objects.create_superuser(
                username="test__superuser",
                email="test+superuser@example.com",
                password=password,
                first_name=first_name,
                last_name=last_name,
            )
        except IntegrityError:  # pragma: nocover
            # User already exists.
            pass
        else:
            user_count += 2
            self.stdout.write(f"Username: {user.username}")
            self.stdout.write(f"Password: {password}")
            self.stdout.write()
            self.stdout.write(f"Username: {superuser.username}")
            self.stdout.write(f"Password: {password}")
        for group in Group.objects.all():
            username = f"test__{group.name.replace(' ', '_').lower()}"
            email = f"test_{group.name.replace(' ', '_').lower()}" + "@example.com"

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    user.groups.add(group)
            except IntegrityError:  # pragma: nocover
                # User already exists.
                pass
            else:
                user_count += 1
                self.stdout.write(f"Username: {user.username}")
                self.stdout.write(f"Password: {password}")
                self.stdout.write()

        self.stdout.write(f"Created {user_count} users.")
