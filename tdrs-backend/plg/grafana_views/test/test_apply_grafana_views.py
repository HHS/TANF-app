"""Regression tests for the deployment's Grafana SQL entry point."""

import logging
from pathlib import Path

from django.core.management import call_command
from django.db import ProgrammingError, connection

import pytest

from scripts import apply_grafana_views
from scripts.create_grafana_postgres_role import run as create_grafana_role
from tdpservice.data_files.models import DataFile, Program, Section
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.search_indexes.models.fra import TANF_Exiter1

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
    apply_grafana_views.run()
    directory = grafana_view_files / missing
    for path in directory.iterdir():
        path.unlink()
    caplog.set_level(logging.INFO)
    caplog.clear()
    with pytest.raises(FileNotFoundError):
        apply_grafana_views.run()
    assert "Grafana views applied successfully." not in caplog.text
    assert all(view_exists(Path(name).stem) for name in apply_grafana_views.CUSTOM_VIEW_FILES)


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


def test_recreation_replaces_incompatible_view_and_removes_unversioned_dependents(
    grafana_view_files: Path,
) -> None:
    """Repair deployed name drift without deleting retained submission records."""
    data_file = DataFileFactory.create(
        file=None, year=2026, program_type=Program.Code.FRA,
        section=Section.Name.FRA_WORK_OUTCOMES,
    )
    record = TANF_Exiter1.objects.create(
        datafile=data_file, SSN="123456789", EXIT_DATE=202601,
    )
    apply_grafana_views.run()
    with connection.cursor() as cursor:
        cursor.execute(
            "ALTER VIEW public.latest_tanf_exiters_view_prod "
            "RENAME COLUMN section TO section_id"
        )
        cursor.execute(
            "CREATE VIEW public.digit_unversioned_exiter AS "
            "SELECT section_id FROM public.latest_tanf_exiters_view_prod"
        )
        cursor.execute(
            "CREATE VIEW public.digit_independent_view AS "
            "SELECT id FROM public.data_files_datafile"
        )
    apply_grafana_views.run()
    assert not view_exists("digit_unversioned_exiter")
    assert view_exists("digit_independent_view")
    assert TANF_Exiter1.objects.filter(pk=record.pk, datafile=data_file).exists()
    assert DataFile.objects.filter(pk=data_file.pk).exists()
    with connection.cursor() as cursor:
        cursor.execute(
            'SELECT section, datafile_id, "EXIT_DATE" '
            "FROM public.latest_tanf_exiters_view_prod"
        )
        assert cursor.fetchall() == [(Section.Name.FRA_WORK_OUTCOMES, data_file.pk, 202601)]
        cursor.execute(
            "SELECT total_record_count FROM public.mr_record_counts_by_tableview "
            "WHERE program_type = 'FRA'"
        )
        assert cursor.fetchall() == [(1,)]


def test_recreation_failure_restores_existing_views_dependents_and_grants(
    grafana_view_files: Path,
) -> None:
    """A failed replacement restores dropped objects and their original privileges."""
    apply_grafana_views.run()
    role = "grafana_recreation_rollback_test"
    create_grafana_role(role, "latest_tanf_exiters_view_prod")
    with connection.cursor() as cursor:
        cursor.execute(
            "ALTER VIEW public.latest_tanf_exiters_view_prod "
            "RENAME COLUMN section TO section_id"
        )
        cursor.execute(
            "CREATE VIEW public.digit_unversioned_exiter AS "
            "SELECT section_id FROM public.latest_tanf_exiters_view_prod"
        )
        cursor.execute(
            "SELECT to_regclass('public.latest_tanf_exiters_view_prod')::oid"
        )
        original_oid = cursor.fetchone()[0]
    (grafana_view_files / "custom_views" / "stt_section_to_type_mapping.sql").write_text(
        "SELECT missing_grafana_column;"
    )
    with pytest.raises(ProgrammingError):
        apply_grafana_views.run()
    assert all(view_exists(Path(name).stem) for name in apply_grafana_views.CUSTOM_VIEW_FILES)
    assert view_exists("digit_unversioned_exiter")
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT to_regclass('public.latest_tanf_exiters_view_prod')::oid, "
            "has_table_privilege(%s, 'public.latest_tanf_exiters_view_prod', 'SELECT')",
            [role],
        )
        assert cursor.fetchone() == (original_oid, True)
        cursor.execute("SELECT section_id FROM public.latest_tanf_exiters_view_prod LIMIT 0")
