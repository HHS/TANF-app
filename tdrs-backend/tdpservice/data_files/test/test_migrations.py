"""Migration tests for the data_files app."""

import importlib

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


MIGRATE_FROM = "0030_datafile_section_ref"
MIGRATE_TO = "0031_backfill_datafile_section_ref"
CONTRACT_MIGRATE_FROM = "0034_alter_shadowdatafile_classification_fields"
CONTRACT_MIGRATE_TO = "0035_replace_datafile_classification_fields"


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


def _create_contract_data_file(
    DataFile,
    Section,
    user,
    stt,
    *,
    slug,
    program_type,
    section,
    audit=False,
):
    """Create a DataFile in the final expand-phase schema."""
    if not Section.objects.filter(
        program__code=program_type,
        name=section,
    ).exists():
        migration = importlib.import_module(
            "tdpservice.data_files.migrations.0031_backfill_datafile_section_ref"
        )
        migration.ensure_canonical_sections(DataFile._meta.apps)
    section_ref = Section.objects.get(
        program__code=program_type,
        name=section,
    )
    return DataFile.objects.create(
        original_filename=f"{slug}.txt",
        slug=slug,
        extension="txt",
        quarter="Q1",
        year=2026,
        program_type=program_type,
        section=section,
        section_ref=section_ref,
        is_program_audit=audit,
        version=1,
        state="uploaded",
        user=user,
        stt=stt,
    )


@pytest.mark.django_db(transaction=True)
def test_data_file_contract_migration_replaces_legacy_classification_fields():
    """The contract migration preserves every supported file classification."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(executor, CONTRACT_MIGRATE_FROM)
    migrate_to = _migration_targets(executor, CONTRACT_MIGRATE_TO)

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        DataFile = old_apps.get_model("data_files", "DataFile")
        Section = old_apps.get_model("data_files", "Section")
        STT = old_apps.get_model("stts", "STT")
        User = old_apps.get_model("users", "User")

        stt = STT.objects.create(name="Contract migration STT")
        user = User.objects.create(username="contract-migration@example.com")
        expected_files = [
            ("tanf", "TAN", "Active Case Data", False),
            ("ssp", "SSP", "Closed Case Data", False),
            ("tribal", "TRIBAL", "Aggregate Data", False),
            ("fra", "FRA", "Work Outcomes of TANF Exiters", False),
            ("tanf-pia", "TAN", "Stratum Data", True),
            ("tribal-pia", "TRIBAL", "Closed Case Data", True),
        ]
        data_file_ids = []
        for slug, program_type, section_name, audit in expected_files:
            data_file = _create_contract_data_file(
                DataFile,
                Section,
                user,
                stt,
                slug=slug,
                program_type=program_type,
                section=section_name,
                audit=audit,
            )
            data_file_ids.append(data_file.id)

        executor = MigrationExecutor(connection)
        executor.migrate(migrate_to)
        new_apps = executor.loader.project_state(migrate_to).apps
        DataFile = new_apps.get_model("data_files", "DataFile")

        for data_file_id, (_, program_type, section_name, audit) in zip(
            data_file_ids, expected_files
        ):
            data_file = DataFile.objects.get(id=data_file_id)
            assert data_file.section.program.code == program_type
            assert data_file.section.name == section_name
            assert data_file.is_program_audit is audit

        assert DataFile._meta.get_field("section").null is False
        assert {field.name for field in DataFile._meta.fields}.isdisjoint(
            {"program_type", "section_ref"}
        )
    finally:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize("invalid_state", ["null", "mismatch"])
def test_data_file_contract_migration_rejects_invalid_canonical_sections(
    invalid_state,
):
    """The contract fails before removing columns when canonical data is invalid."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(executor, CONTRACT_MIGRATE_FROM)
    migrate_to = _migration_targets(executor, CONTRACT_MIGRATE_TO)
    invalid_data_file_id = None

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        DataFile = old_apps.get_model("data_files", "DataFile")
        Section = old_apps.get_model("data_files", "Section")
        STT = old_apps.get_model("stts", "STT")
        User = old_apps.get_model("users", "User")

        stt = STT.objects.create(name=f"Invalid contract {invalid_state} STT")
        user = User.objects.create(
            username=f"invalid-contract-{invalid_state}@example.com"
        )
        data_file = _create_contract_data_file(
            DataFile,
            Section,
            user,
            stt,
            slug=f"invalid-{invalid_state}",
            program_type="TAN",
            section="Active Case Data",
        )
        invalid_data_file_id = data_file.id
        if invalid_state == "null":
            DataFile.objects.filter(id=data_file.id).update(section_ref_id=None)
            error_match = "missing canonical sections"
        else:
            ssp_section = Section.objects.get(
                program__code="SSP",
                name="Active Case Data",
            )
            DataFile.objects.filter(id=data_file.id).update(section_ref=ssp_section)
            error_match = "conflict with legacy values"

        executor = MigrationExecutor(connection)
        with pytest.raises(RuntimeError, match=error_match):
            executor.migrate(migrate_to)

        table_columns = {
            column.name
            for column in connection.introspection.get_table_description(
                connection.cursor(), "data_files_datafile"
            )
        }
        assert {"program_type", "section", "section_ref_id"} <= table_columns
    finally:
        if invalid_data_file_id is not None:
            DataFile.objects.filter(id=invalid_data_file_id).delete()
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db
@pytest.mark.parametrize(
    "model_name,field_name,unknown_value,defaults",
    [
        (
            "Program",
            "code",
            "UNKNOWN",
            {"slug": "unknown", "name": "Unknown Program"},
        ),
        (
            "Section",
            "name",
            "Unknown Section",
            {},
        ),
    ],
)
def test_program_section_choices_migration_rejects_unknown_values(
    model_name,
    field_name,
    unknown_value,
    defaults,
):
    """The choices migration rejects records outside the static catalog."""
    migration = importlib.import_module(
        "tdpservice.data_files.migrations.0036_add_program_section_choices"
    )
    apps = migration_apps = MigrationExecutor(connection).loader.project_state(
        [("data_files", "0035_replace_datafile_classification_fields")]
    ).apps
    Program = migration_apps.get_model("data_files", "Program")
    Model = migration_apps.get_model("data_files", model_name)

    values = {field_name: unknown_value, **defaults}
    if model_name == "Section":
        values["program"] = Program.objects.get(code="TAN")
    record = Model.objects.create(**values)

    try:
        with pytest.raises(RuntimeError, match="unknown values"):
            migration.validate_program_and_section_values(apps, None)
    finally:
        record.delete()


@pytest.mark.django_db(transaction=True)
def test_shadow_section_migration_preserves_classifications_and_reverses() -> None:
    """Canonical conversion and rollback preserve shadow rows and audit flags."""
    executor = MigrationExecutor(connection)
    before = _migration_targets(
        executor, "0037_merge_program_section_choices_and_parser_mode"
    )
    after = _migration_targets(executor, "0038_shadowdatafile_canonical_section")
    try:
        executor.migrate(before)
        apps = executor.loader.project_state(before).apps
        ShadowDataFile = apps.get_model("data_files", "ShadowDataFile")
        Program = apps.get_model("data_files", "Program")
        Section = apps.get_model("data_files", "Section")
        user = apps.get_model("users", "User").objects.create(
            username="shadow-migration"
        )
        stt = apps.get_model("stts", "STT").objects.create(name="Shadow migration STT")
        expected = [
            ("TAN", "Active Case Data", False),
            ("SSP", "Active Case Data", False),
            ("TRIBAL", "Aggregate Data", False),
            ("FRA", "Work Outcomes of TANF Exiters", False),
            ("TAN", "Active Case Data", True),
            ("TRIBAL", "Closed Case Data", True),
        ]
        rows = []
        for index, (code, name, audit) in enumerate(expected):
            program, _ = Program.objects.get_or_create(
                code=code, defaults={"slug": code.lower(), "name": code}
            )
            section, _ = Section.objects.get_or_create(program=program, name=name)
            datafile = _create_data_file(
                ShadowDataFile,
                user,
                stt,
                slug=f"shadow-{index}",
                program_type=code,
                section=name,
                audit=audit,
            )
            rows.append((datafile.pk, section.pk))

        executor = MigrationExecutor(connection)
        executor.migrate(after)
        ShadowDataFile = executor.loader.project_state(after).apps.get_model(
            "data_files", "ShadowDataFile"
        )
        for (file_id, section_id), (_, _, audit) in zip(rows, expected):
            datafile = ShadowDataFile.objects.get(pk=file_id)
            assert datafile.section_id == section_id
            assert datafile.is_program_audit is audit
        assert ShadowDataFile._meta.get_field("section").null is False
        assert "program_type" not in {
            field.name for field in ShadowDataFile._meta.fields
        }

        executor = MigrationExecutor(connection)
        executor.migrate(before)
        ShadowDataFile = executor.loader.project_state(before).apps.get_model(
            "data_files", "ShadowDataFile"
        )
        for (file_id, _), (code, name, audit) in zip(rows, expected):
            datafile = ShadowDataFile.objects.get(pk=file_id)
            assert (datafile.program_type, datafile.section) == (code, name)
            assert datafile.is_program_audit is audit
    finally:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())


@pytest.mark.django_db(transaction=True)
@pytest.mark.parametrize(
    "code,name",
    [
        ("UNKNOWN", "Active Case Data"),
        ("TAN", "Unknown Section"),
        ("FRA", "Active Case Data"),
    ],
)
def test_shadow_section_migration_rejects_unmapped_classifications(
    code: str, name: str
) -> None:
    """Unmapped classifications fail without discarding the legacy columns."""
    executor = MigrationExecutor(connection)
    before = _migration_targets(
        executor, "0037_merge_program_section_choices_and_parser_mode"
    )
    after = _migration_targets(executor, "0038_shadowdatafile_canonical_section")
    invalid_id = None
    try:
        executor.migrate(before)
        apps = executor.loader.project_state(before).apps
        ShadowDataFile = apps.get_model("data_files", "ShadowDataFile")
        user = apps.get_model("users", "User").objects.create(username="invalid-shadow")
        stt = apps.get_model("stts", "STT").objects.create(name="Invalid shadow STT")
        catalog_migration = importlib.import_module(
            "tdpservice.data_files.migrations.0031_backfill_datafile_section_ref"
        )
        catalog_migration.ensure_canonical_sections(apps)
        datafile = _create_data_file(
            ShadowDataFile,
            user,
            stt,
            slug="invalid-shadow",
            program_type=code,
            section=name,
        )
        invalid_id = datafile.pk
        executor = MigrationExecutor(connection)
        with pytest.raises(RuntimeError, match="unmapped classifications"):
            executor.migrate(after)
        datafile.refresh_from_db()
        assert (datafile.program_type, datafile.section) == (code, name)
    finally:
        if invalid_id is not None:
            ShadowDataFile.objects.filter(pk=invalid_id).delete()
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
