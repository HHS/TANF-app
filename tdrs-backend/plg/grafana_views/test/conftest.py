"""Keep Grafana SQL tests independent of external identity services."""

from pathlib import Path

import pytest

from plg.grafana_views import generate_views
from scripts import apply_grafana_views


@pytest.fixture(autouse=True)
def disable_keycloak_sync(settings) -> None:
    """Prevent database fixture creation from synchronizing real Keycloak users."""
    settings.KEYCLOAK_SYNC_ENABLED = False


@pytest.fixture
def grafana_view_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Generate the real deployment SQL in a test-owned directory."""
    source = Path(__file__).resolve().parents[1]
    for name in ("schema_fields.json", "helper_functions.sql"):
        (tmp_path / name).write_bytes((source / name).read_bytes())
    monkeypatch.setattr(generate_views, "CWD", str(tmp_path))
    generate_views.main(False)
    generate_views.main(True)
    custom = tmp_path / "custom_views"
    custom.mkdir()
    for path in (source / "custom_views").glob("*.sql"):
        (custom / path.name).write_bytes(path.read_bytes())
    monkeypatch.setattr(apply_grafana_views, "VIEWS_PATH", str(tmp_path))
    return tmp_path
