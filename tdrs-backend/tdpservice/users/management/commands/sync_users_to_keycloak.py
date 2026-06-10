"""Management command to sync all Django users to Keycloak."""

from django.core.management import BaseCommand


class Command(BaseCommand):
    """Bulk sync all active Django users to Keycloak."""

    help = "Sync all active Django users (attributes and groups) to Keycloak"

    def handle(self, *args, **options):
        """Execute the bulk sync."""
        from tdpservice.users.keycloak_client import KeycloakSyncClient

        self.stdout.write("Starting bulk sync of users to Keycloak...")

        client = KeycloakSyncClient.get_instance()
        stats = client.bulk_sync_all_users()

        self.stdout.write(
            self.style.SUCCESS(
                f"Sync complete: {stats['synced']} synced, "
                f"{stats['skipped']} skipped (not in Keycloak), "
                f"{stats['failed']} failed"
            )
        )
