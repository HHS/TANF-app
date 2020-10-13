"""generate_test_users command."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import BaseCommand
from django.db import IntegrityError, transaction
from django.apps import apps

import factory

User = get_user_model()

group_names = ["admin", "data prepper", "OFA analyst"]


class Command(BaseCommand):
    """Command class."""

    help = "Generate a test user for each role."

    def handle(self, *args, **options):
        groups = [Group(name=group_name) for group_name in group_names]
        Group.objects.bulk_create(groups, ignore_conflicts=True)
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
        except IntegrityError as ie:  # pragma: nocover
            print("Integrity Error: ", ie)
            # User already exists.
            pass
        else:
            user_count += 1
            self.stdout.write(f"Username: {user.username}")
            self.stdout.write(f"Password: {password}")
            self.stdout.write()
        for group in Group.objects.all():
            username = f"test__{group.name.replace(' ', '_').lower()}"
            email = f"test_{group.name.replace(' ', '_').lower()}"+ "@example.com"

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
                    user.groups
            except IntegrityError:  # pragma: nocover
                # User already exists.
                pass
            else:
                user_count += 1
                self.stdout.write(f"Username: {user.username}")
                self.stdout.write(f"Password: {password}")
                self.stdout.write(f"email: {email}")
                self.stdout.write()

        self.stdout.write(f"Created {user_count} users.")
