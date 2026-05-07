"""Reset Cypress profile-editing users."""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError


PROFILE_EDITING_USERNAMES = (
    "cypress-data-analyst-dana@teamraft.com",
    "cypress-fra-data-analyst-derek@teamraft.com",
    "cypress-data-analyst-donna@teamraft.com",
    "cypress-fra-data-analyst-david@teamraft.com",
    "cypress-fra-ofa-regional-staff-rachel@acf.hhs.gov",
    "cypress-fra-ofa-regional-staff-robert@acf.hhs.gov",
    "cypress-fra-ofa-regional-staff-rita@acf.hhs.gov",
    "cypress-fra-ofa-regional-staff-ryan@acf.hhs.gov",
)


class Command(BaseCommand):
    """Delete profile-editing Cypress users so fixtures reload clean state."""

    help = "Reset profile-editing Cypress users before loading e2e fixtures."

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--allow-non-debug",
            action="store_true",
            help=(
                "Allow this Cypress-only reset outside DEBUG. Use only from "
                "develop/dev deployment setup."
            ),
        )

    def handle(self, *args, **options):
        """Delete known Cypress profile-editing users."""
        if not settings.DEBUG and not options["allow_non_debug"]:
            raise CommandError(
                "Refusing to reset Cypress profile-editing users outside DEBUG "
                "without --allow-non-debug."
            )

        User = get_user_model()
        deleted_count, _ = User.objects.filter(
            username__in=PROFILE_EDITING_USERNAMES
        ).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Reset {deleted_count} Cypress profile-editing records."
            )
        )
