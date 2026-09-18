"""Migration tests for the data_files app."""

import importlib

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


MIGRATE_FROM = "0030_datafile_section_ref"
MIGRATE_TO = "0031_backfill_datafile_section_ref"


def _migration_targets(executor, data_files_target):
    """Target DataFiles before the dependent STTs participation backfill."""
    target_overrides = {
        "data_files": data_files_target,
        "stts": "0013_program_section_sttprogramparticipation",
        "users": "0059_reconcile_role_permissions",
    }
    return [
        (app_label, target_overrides.get(app_label, migration))
        for app_label, migration in executor.loader.graph.leaf_nodes()
    ]


def _create_data_file(DataFile, user, stt, *, slug, program_type, section, audit=False):
    return DataFile.objects.create(
        original_filename=f"{slug}.txt",
        slug=slug,
        extension="txt",
        quarter="Q1",
        year=2020,
        program_type=program_type,
        section=section,
        is_program_audit=audit,
        version=1,
        state="uploaded",
        user=user,
        stt=stt,
    )


@pytest.mark.django_db(transaction=True)
def test_data_file_section_ref_backfill():
    """The backfill maps all legacy programs, sections, and PIA files."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(executor, MIGRATE_FROM)
    migrate_to = _migration_targets(executor, MIGRATE_TO)

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        DataFile = old_apps.get_model("data_files", "DataFile")
        Program = old_apps.get_model("data_files", "Program")
        STT = old_apps.get_model("stts", "STT")
        User = old_apps.get_model("users", "User")

        Program.objects.all().delete()

        stt = STT.objects.create(name="DataFile migration STT")
        user = User.objects.create(username="datafile-migration@example.com")
        expected_files = [
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="tanf-active",
                    program_type="TAN",
                    section="Active Case Data",
                ),
                "TAN",
                "Active Case Data",
                False,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="ssp-closed",
                    program_type="SSP",
                    section="Closed Case Data",
                ),
                "SSP",
                "Closed Case Data",
                False,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="tribal-aggregate",
                    program_type="TRIBAL",
                    section="Aggregate Data",
                ),
                "TRIBAL",
                "Aggregate Data",
                False,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="fra-outcomes",
                    program_type="FRA",
                    section="Work Outcomes of TANF Exiters",
                ),
                "FRA",
                "Work Outcomes of TANF Exiters",
                False,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="tanf-pia",
                    program_type="TAN",
                    section="Closed Case Data",
                    audit=True,
                ),
                "TAN",
                "Closed Case Data",
                True,
            ),
            (
                _create_data_file(
                    DataFile,
                    user,
                    stt,
                    slug="tribal-pia",
                    program_type="TRIBAL",
                    section="Active Case Data",
                    audit=True,
                ),
                "TRIBAL",
                "Active Case Data",
                True,
            ),
        ]

        executor = MigrationExecutor(connection)
        executor.migrate(migrate_to)
        new_apps = executor.loader.project_state(migrate_to).apps
        DataFile = new_apps.get_model("data_files", "DataFile")
        Program = new_apps.get_model("data_files", "Program")
        Section = new_apps.get_model("data_files", "Section")

        for old_data_file, program_code, section_name, audit in expected_files:
            data_file = DataFile.objects.get(id=old_data_file.id)
            assert data_file.section_ref.program.code == program_code
            assert data_file.section_ref.name == section_name
            assert data_file.is_program_audit is audit

        assert set(Program.objects.values_list("code", flat=True)) == {
            "TAN",
            "SSP",
            "TRIBAL",
            "FRA",
        }
        expected_sections = {
            "TAN": {
                "Active Case Data",
                "Closed Case Data",
                "Aggregate Data",
                "Stratum Data",
            },
            "SSP": {
                "Active Case Data",
                "Closed Case Data",
                "Aggregate Data",
                "Stratum Data",
            },
            "TRIBAL": {
                "Active Case Data",
                "Closed Case Data",
                "Aggregate Data",
                "Stratum Data",
            },
            "FRA": {
                "Work Outcomes of TANF Exiters",
                "Secondary School Attainment",
                "Supplemental Work Outcomes",
            },
        }
        for program_code, section_names in expected_sections.items():
            assert set(
                Section.objects.filter(program__code=program_code).values_list(
                    "name", flat=True
                )
            ) == section_names
        assert not Program.objects.filter(code="PIA").exists()

        migration = importlib.import_module(
            "tdpservice.data_files.migrations.0031_backfill_datafile_section_ref"
        )
        migration.backfill_datafile_section_ref(new_apps, None)
        assert DataFile.objects.filter(section_ref__isnull=True).count() == 0
    finally:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True)
def test_data_file_section_ref_backfill_rejects_unmapped_values():
    """The backfill fails rather than silently skipping unknown legacy values."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(executor, MIGRATE_FROM)
    migrate_to = _migration_targets(executor, MIGRATE_TO)
    invalid_data_file_id = None

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        DataFile = old_apps.get_model("data_files", "DataFile")
        STT = old_apps.get_model("stts", "STT")
        User = old_apps.get_model("users", "User")

        stt = STT.objects.create(name="Invalid DataFile migration STT")
        user = User.objects.create(username="invalid-datafile-migration@example.com")
        invalid_data_file = _create_data_file(
            DataFile,
            user,
            stt,
            slug="unknown-section",
            program_type="UNKNOWN",
            section="Unknown Section",
        )
        invalid_data_file_id = invalid_data_file.id

        executor = MigrationExecutor(connection)
        with pytest.raises(RuntimeError, match="UNKNOWN.*Unknown Section"):
            executor.migrate(migrate_to)
    finally:
        if invalid_data_file_id is not None:
            DataFile.objects.filter(id=invalid_data_file_id).delete()
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
