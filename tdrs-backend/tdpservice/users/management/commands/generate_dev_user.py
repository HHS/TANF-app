"""generate_dev_user command."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import BaseCommand

User = get_user_model()

email = "dev@test.com"
pswd = "pass"
first = "Jon"
last = "Tester"

class Command(BaseCommand):
    """Command class."""

    def handle(self, *args, **options):
        """Generate dev user if they don't exist."""
        try:
            user = User.objects.get(username=email)
            print(f"Found {vars(user)}")
        except User.DoesNotExist:
            group = Group.objects.get(name="Developer")
            user = User.objects.create(username=email,
                                       email=email,
                                       password=pswd,
                                       is_superuser=True,
                                       is_staff=True,
                                       first_name=first,
                                       last_name=last,
                                       stt_id=31,
                                       account_approval_status="Approved")
            user.groups.add(group)
            print(f"Created {vars(user)}")
