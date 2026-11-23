"""Keep Grafana SQL tests independent of external identity services."""

import pytest


@pytest.fixture(autouse=True)
def disable_keycloak_sync(settings) -> None:
    """Prevent database fixture creation from synchronizing real Keycloak users."""
    settings.KEYCLOAK_SYNC_ENABLED = False
