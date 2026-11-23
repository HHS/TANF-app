"""Regression tests for the deployment's Grafana SQL entry point."""

import logging
from pathlib import Path

from django.core.management import call_command
from django.db import ProgrammingError, connection

import pytest

from scripts import apply_grafana_views

pytestmark = pytest.mark.django_db


def view_exists(name: str) -> bool:
    """Inspect relations without querying a potentially missing view."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT to_regclass(%s) IS NOT NULL", [f"public.{name}"])
        return cursor.fetchone()[0]


def test_loader_applies_real_sql_in_order_and_recreates_views(
    grafana_view_files: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Both generated groups precede dependents; repeated and recovery runs work."""
    (grafana_view_files / "user_views" / "README.md").write_text("Not SQL")
    (grafana_view_files / "admin_views" / "directory.sql").mkdir()
    applied = []
    original = apply_grafana_views.apply_view

    def record_application(path: Path) -> None:
        original(path)
        applied.append(path)

    monkeypatch.setattr(apply_grafana_views, "apply_view", record_application)
    monkeypatch.chdir(grafana_view_files / "custom_views")
    call_command("runscript", "apply_grafana_views", verbosity=0)
    expected = [
        path
        for group in ("user_views", "admin_views")
        for path in sorted((grafana_view_files / group).iterdir())
        if path.is_file() and path.suffix == ".sql"
    ] + [
        grafana_view_files / "custom_views" / name
        for name in apply_grafana_views.CUSTOM_VIEW_FILES
    ]
    assert applied == expected
    apply_grafana_views.run()
    with connection.cursor() as cursor:
        for filename in reversed(apply_grafana_views.CUSTOM_VIEW_FILES):
            name = Path(filename).stem
            cursor.execute(f'DROP VIEW public."{name}"')
    apply_grafana_views.run()
    assert all(view_exists(Path(name).stem) for name in apply_grafana_views.CUSTOM_VIEW_FILES)


@pytest.mark.parametrize("missing", ["user_views", "admin_views", "custom_views"])
def test_loader_rejects_missing_required_sql(
    grafana_view_files: Path, missing: str, caplog
) -> None:
    """Absent generated or custom definitions cannot produce a success message."""
    directory = grafana_view_files / missing
    for path in directory.iterdir():
        path.unlink()
    caplog.set_level(logging.INFO)
    with pytest.raises(FileNotFoundError):
        apply_grafana_views.run()
    assert "Grafana views applied successfully." not in caplog.text


def test_loader_rolls_back_custom_batch_and_stops_on_sql_error(
    grafana_view_files: Path, caplog
) -> None:
    """A broken dependent definition rolls back custom DDL but not prerequisites."""
    (grafana_view_files / "custom_views" / "stt_section_to_type_mapping.sql").write_text(
        "SELECT missing_grafana_column;"
    )
    caplog.set_level(logging.INFO)
    with pytest.raises(ProgrammingError):
        apply_grafana_views.run()
    assert view_exists("data_files_datafile_view")
    assert not view_exists("latest_tanf_exiters_view_prod")
    assert not view_exists("mr_record_counts_by_tableview")
    assert "Failed to apply SQL file: stt_section_to_type_mapping.sql" in caplog.text
    assert "Applying SQL file: mr_record_counts_by_tableview.sql" not in caplog.text
    assert "Grafana views applied successfully." not in caplog.text


def test_runscript_propagates_custom_sql_failure(grafana_view_files: Path) -> None:
    """The actual management-command handler must reject a broken SQL batch."""
    (grafana_view_files / "custom_views" / "latest_tanf_exiters_view_prod.sql").write_text(
        "SELECT missing_grafana_column;"
    )
    with pytest.raises(ProgrammingError):
        call_command("runscript", "apply_grafana_views", verbosity=0)
