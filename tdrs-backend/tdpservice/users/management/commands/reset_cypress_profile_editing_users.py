"""Reset Cypress profile-editing users."""

import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError


PROFILE_EDITING_USERS_FIXTURE = Path(
    settings.BASE_DIR, "fixtures", "cypress", "profile_editing_users.json"
)


def get_profile_editing_usernames():
    """Return profile-editing Cypress usernames from the fixture."""
    try:
        with PROFILE_EDITING_USERS_FIXTURE.open(encoding="utf-8") as fixture_file:
            fixture_data = json.load(fixture_file)
    except FileNotFoundError as exc:
        raise CommandError(
            f"Profile-editing fixture not found: {PROFILE_EDITING_USERS_FIXTURE}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise CommandError(
            f"Profile-editing fixture contains invalid JSON: {exc}"
        ) from exc

    usernames = tuple(
        entry.get("fields", {}).get("username")
        for entry in fixture_data
        if entry.get("model") == "users.user"
        and entry.get("fields", {}).get("username")
    )

    if not usernames:
        raise CommandError(
            f"No profile-editing users found in fixture: {PROFILE_EDITING_USERS_FIXTURE}"
        )

    return usernames


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

        usernames = get_profile_editing_usernames()
        User = get_user_model()
        deleted_count, _ = User.objects.filter(username__in=usernames).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Reset {deleted_count} Cypress profile-editing records."
            )
        )
