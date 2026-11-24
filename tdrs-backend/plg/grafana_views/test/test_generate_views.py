"""Behavior tests for generated Grafana data views."""

import pytest
from django.db import connection

from plg.grafana_views import generate_views
from plg.grafana_views.generate_views import render_query
from scripts.create_grafana_postgres_role import run as create_grafana_role
from tdpservice.data_files.models import Program, Section
from tdpservice.data_files.test.factories import DataFileFactory


@pytest.mark.django_db
@pytest.mark.parametrize("is_admin", [False, True])
@pytest.mark.parametrize(
    "program_code,section_name,is_program_audit",
    [
        (Program.Code.TANF, Section.Name.ACTIVE_CASE_DATA, False),
        (Program.Code.SSP, Section.Name.CLOSED_CASE_DATA, False),
        (Program.Code.TRIBAL, Section.Name.AGGREGATE_DATA, False),
        (Program.Code.FRA, Section.Name.FRA_WORK_OUTCOMES, False),
        (Program.Code.TANF, Section.Name.ACTIVE_CASE_DATA, True),
        (Program.Code.TRIBAL, Section.Name.CLOSED_CASE_DATA, True),
    ],
)
def test_generated_datafile_view_exposes_canonical_history_to_readonly_role(
    tmp_path,
    monkeypatch,
    is_admin: bool,
    program_code: str,
    section_name: str,
    is_program_audit: bool,
) -> None:
    """Grafana can read canonical labels and every submission version."""
    old_file = DataFileFactory.create(
        program_type=program_code,
        section=section_name,
        is_program_audit=is_program_audit,
        file=None,
        version=1,
    )
    latest_file = DataFileFactory.create(
        section=old_file.section,
        is_program_audit=is_program_audit,
        stt=old_file.stt,
        user=old_file.user,
        year=old_file.year,
        quarter=old_file.quarter,
        file=None,
        version=2,
    )
    (tmp_path / "schema_fields.json").write_text('{"schemas": {}}')
    (tmp_path / "helper_functions.sql").write_text("")
    monkeypatch.setattr(generate_views, "CWD", str(tmp_path))
    generate_views.main(is_admin)
    output_dir = "admin_views" if is_admin else "user_views"
    sql = (tmp_path / output_dir / "data_files_datafile_view.sql").read_text()

    with connection.cursor() as cursor:
        cursor.execute(sql)
        cursor.execute(sql)
    create_grafana_role("grafana_datafile_view_test", "data_files_datafile_view")
    with connection.cursor() as cursor:
        cursor.execute("SET LOCAL ROLE grafana_datafile_view_test")
        try:
            cursor.execute(
                """
                SELECT id, section_id, section, program_type, is_program_audit, version
                FROM data_files_datafile_view
                WHERE id IN (%s, %s)
                ORDER BY version
                """,
                [old_file.pk, latest_file.pk],
            )
            rows = cursor.fetchall()
        finally:
            cursor.execute("RESET ROLE")

    assert rows == [
        (
            old_file.pk,
            old_file.section_id,
            section_name,
            program_code,
            is_program_audit,
            1,
        ),
        (
            latest_file.pk,
            old_file.section_id,
            section_name,
            program_code,
            is_program_audit,
            2,
        ),
    ]


@pytest.mark.django_db
def test_generated_query_uses_canonical_values_for_latest_data_file():
    """Generated views expose canonical strings from only the latest file."""
    old_data_file = DataFileFactory.create(
        year=2026,
        version=1,
        program_type="SSP",
        section="Closed Case Data",
    )
    latest_data_file = DataFileFactory.create(
        year=old_data_file.year,
        quarter=old_data_file.quarter,
        stt=old_data_file.stt,
        user=old_data_file.user,
        version=2,
        program_type=Program.Code.SSP,
        section=Section.Name.CLOSED_CASE_DATA,
    )

    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TEMP TABLE grafana_test_records (
                datafile_id integer NOT NULL,
                record_value text NOT NULL
            ) ON COMMIT DROP
            """
        )
        cursor.execute(
            """
            INSERT INTO grafana_test_records (datafile_id, record_value)
            VALUES (%s, 'old'), (%s, 'latest')
            """,
            [old_data_file.pk, latest_data_file.pk],
        )
        cursor.execute(
            render_query(
                '"record_value",',
                "grafana_test_records",
                "test_record",
            )
        )
        columns = [column.name for column in cursor.description]
        rows = cursor.fetchall()

    assert columns == [
        "record_value",
        "section",
        "version",
        "year",
        "quarter",
        "STT",
        "STT_CODE",
        "REGION",
        "program_type",
    ]
    assert len(rows) == 1
    row = dict(zip(columns, rows[0]))
    assert row["record_value"] == "latest"
    assert row["section"] == "Closed Case Data"
    assert row["program_type"] == "SSP"
    assert row["version"] == 2
