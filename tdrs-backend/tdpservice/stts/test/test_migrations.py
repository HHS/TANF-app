"""Migration tests for the stts app."""

import importlib

import pytest
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


def _migration_targets(executor, stts_target):
    """Keep other apps at their leaves while targeting an STTs migration."""
    target_overrides = {
        "stts": stts_target,
        "users": "0059_reconcile_role_permissions",
    }
    return [
        (app_label, target_overrides.get(app_label, migration))
        for app_label, migration in executor.loader.graph.leaf_nodes()
    ]


@pytest.mark.django_db(transaction=True)
def test_general_program_participation_data_migration():
    """The generalized backfill creates exact primary and SSP participation data."""
    executor = MigrationExecutor(connection)
    migrate_from = _migration_targets(
        executor, "0013_program_section_sttprogramparticipation"
    )
    migrate_to = _migration_targets(executor, "0014_populate_program_participations")

    try:
        executor.migrate(migrate_from)
        old_apps = executor.loader.project_state(migrate_from).apps
        Program = old_apps.get_model("data_files", "Program")
        Region = old_apps.get_model("stts", "Region")
        STT = old_apps.get_model("stts", "STT")
        SttProgramParticipation = old_apps.get_model(
            "stts", "SttProgramParticipation"
        )
        data_file_migration = importlib.import_module(
            "tdpservice.data_files.migrations.0031_backfill_datafile_section_ref"
        )
        data_file_migration.ensure_canonical_sections(old_apps)

        region = Region.objects.create(id=9998)
        core_sections = {
            "Active Case Data": "active.txt",
            "Closed Case Data": "closed.txt",
            "Aggregate Data": "aggregate.txt",
        }
        state = STT.objects.create(
            name="Three Section State",
            region=region,
            type="state",
            filenames=core_sections,
            ssp=False,
        )
        null_ssp_state = STT.objects.create(
            name="Null SSP State",
            region=region,
            type="state",
            filenames=core_sections,
            ssp=None,
        )
        territory = STT.objects.create(
            name="Four Section Territory",
            region=region,
            type="territory",
            filenames={**core_sections, "Stratum Data": "stratum.txt"},
            ssp=False,
        )
        tribe = STT.objects.create(
            name="Three Section Tribe",
            region=region,
            type="tribe",
            filenames={
                "Tribal Active Case Data": "active.txt",
                "Tribal Closed Case Data": "closed.txt",
                "Tribal Aggregate Data": "aggregate.txt",
            },
            ssp=False,
        )
        ssp_state = STT.objects.create(
            name="Active SSP State",
            region=region,
            type="state",
            filenames={
                **core_sections,
                "Stratum Data": "stratum.txt",
                "SSP Active Case Data": "ssp-active.txt",
                "SSP Closed Case Data": "ssp-closed.txt",
                "SSP Aggregate Data": "ssp-aggregate.txt",
            },
            ssp=True,
        )
        former_ssp_state = STT.objects.create(
            name="Former SSP State",
            region=region,
            type="state",
            filenames={
                **core_sections,
                "SSP Active Case Data": "ssp-active.txt",
                "SSP Closed Case Data": "ssp-closed.txt",
                "SSP Aggregate Data": "ssp-aggregate.txt",
            },
            ssp=False,
        )
        former_participation = SttProgramParticipation.objects.create(
            stt=former_ssp_state,
            program=Program.objects.get(code="SSP"),
            status="FORMER",
        )

        executor = MigrationExecutor(connection)
        executor.migrate(migrate_to)
        new_apps = executor.loader.project_state(migrate_to).apps
        Program = new_apps.get_model("data_files", "Program")
        Section = new_apps.get_model("data_files", "Section")
        SttProgramParticipation = new_apps.get_model(
            "stts", "SttProgramParticipation"
        )

        expected_participations = {
            state.id: {"TAN": {"Active Case Data", "Closed Case Data", "Aggregate Data"}},
            null_ssp_state.id: {
                "TAN": {"Active Case Data", "Closed Case Data", "Aggregate Data"}
            },
            territory.id: {
                "TAN": {
                    "Active Case Data",
                    "Closed Case Data",
                    "Aggregate Data",
                    "Stratum Data",
                }
            },
            tribe.id: {
                "TRIBAL": {
                    "Active Case Data",
                    "Closed Case Data",
                    "Aggregate Data",
                }
            },
            ssp_state.id: {
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
                },
            },
            former_ssp_state.id: {
                "TAN": {"Active Case Data", "Closed Case Data", "Aggregate Data"},
                "SSP": {"Active Case Data", "Closed Case Data", "Aggregate Data"},
            },
        }

        participation_ids = {}
        for stt_id, expected_programs in expected_participations.items():
            participations = SttProgramParticipation.objects.filter(stt_id=stt_id)
            assert set(participations.values_list("program__code", flat=True)) == set(
                expected_programs
            )
            for participation in participations:
                participation_ids[(stt_id, participation.program.code)] = participation.id
                assert participation.status == (
                    "FORMER"
                    if participation.id == former_participation.id
                    else "ACTIVE"
                )
                assert set(participation.sections.values_list("name", flat=True)) == (
                    expected_programs[participation.program.code]
                )

        assert not SttProgramParticipation.objects.filter(program__code="FRA").exists()

        ssp_participation = SttProgramParticipation.objects.get(
            stt_id=ssp_state.id,
            program__code="SSP",
        )
        ssp_participation.sections.set(
            [Section.objects.get(program__code="TAN", name="Active Case Data")]
        )
        migration = importlib.import_module(
            "tdpservice.stts.migrations.0014_populate_program_participations"
        )
        migration.populate_program_participations(new_apps, None)

        assert {
            (participation.stt_id, participation.program.code): participation.id
            for participation in SttProgramParticipation.objects.filter(
                stt_id__in=expected_participations
            )
        } == participation_ids
        assert set(
            SttProgramParticipation.objects.get(
                stt_id=ssp_state.id,
                program__code="SSP",
            ).sections.values_list("name", flat=True)
        ) == expected_participations[ssp_state.id]["SSP"]
        assert set(Program.objects.values_list("code", flat=True)) == {
            "TAN",
            "SSP",
            "TRIBAL",
            "FRA",
        }
    finally:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
