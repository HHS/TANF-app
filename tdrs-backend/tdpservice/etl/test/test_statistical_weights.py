"""Tests for statistical weights ETL nodes."""

from decimal import Decimal
from unittest.mock import patch

from django.core import mail

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.etl.models import (
    ETLArtifact,
    ETLPipelineRun,
    ETLQAResult,
    StatisticalWeight,
    StatisticalWeightsCaseCount,
)
from tdpservice.etl.notifications import send_statistical_weights_notification
from tdpservice.etl.pipelines.base import NodeContext
from tdpservice.etl.pipelines.sources import SOURCE_DATAFILE_IDS_KEY
from tdpservice.etl.pipelines.statistical_weights import StatisticalWeightsPipeline
from tdpservice.etl.runner import PipelineRunFactory
from tdpservice.search_indexes.models.ssp import SSP_M1, SSP_M6, SSP_M7
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T6, TANF_T7
from tdpservice.search_indexes.models.tribal import (
    Tribal_TANF_T1,
    Tribal_TANF_T6,
    Tribal_TANF_T7,
)
from tdpservice.stts.models import STT

FISCAL_YEAR = 2026
REPORTING_MONTH = 202501
PIPELINE = StatisticalWeightsPipeline()
TANF_PROGRAM = DataFile.ProgramType.TANF


def _datafile(stt, user, section, version=1, program_type=TANF_PROGRAM):
    """Create a parse-completed DataFile in the weights fiscal year."""
    return DataFileFactory.create(
        stt=stt,
        user=user,
        section=section,
        program_type=program_type,
        quarter=DataFile.Quarter.Q1,
        year=FISCAL_YEAR,
        version=version,
        state=SubmissionState.PARSE_COMPLETED,
    )


def _node_context(pipeline_run):
    """Build a node context for direct handler execution."""
    return NodeContext(
        pipeline_run=pipeline_run,
        artifacts={artifact.key: artifact for artifact in pipeline_run.artifacts.all()},
    )


def _execute_node(pipeline_run, node_key):
    """Execute a statistical weights node directly for focused node tests."""
    return PIPELINE.nodes[node_key].execute(_node_context(pipeline_run))


def _snapshot_source_datafile_ids(fiscal_year, program):
    """Snapshot source DataFile IDs through the validation node."""
    return PIPELINE.nodes.validate_run_sources.snapshot_source_datafile_ids(
        fiscal_year,
        program,
    )


def _create_pipeline_run(program=TANF_PROGRAM):
    """Create a statistical weights pipeline run."""
    return PipelineRunFactory.for_pipeline_key(StatisticalWeightsPipeline.key).create(
        parameters={"fiscal_year": FISCAL_YEAR, "program": program},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


@pytest.fixture
def parsed_weights_data(stt, user):
    """Create parsed T1/T6/T7 rows for statistical weights tests."""
    stt.sample = True
    stt.save()

    old_active_file = _datafile(
        stt,
        user,
        DataFile.Section.ACTIVE_CASE_DATA,
        version=1,
    )
    current_active_file = _datafile(
        stt,
        user,
        DataFile.Section.ACTIVE_CASE_DATA,
        version=2,
    )
    aggregate_file = _datafile(stt, user, DataFile.Section.AGGREGATE_DATA)
    stratum_file = _datafile(stt, user, DataFile.Section.STRATUM_DATA)

    TANF_T1.objects.create(
        datafile=old_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="OLD0000001",
        STRATUM="9",
    )
    TANF_T1.objects.create(
        datafile=current_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000001",
        STRATUM="1",
    )
    TANF_T1.objects.create(
        datafile=current_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000002",
        STRATUM="1",
    )
    TANF_T1.objects.create(
        datafile=current_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000002",
        STRATUM="1",
    )
    TANF_T1.objects.create(
        datafile=current_active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000003",
        STRATUM="2",
    )

    TANF_T6.objects.create(
        datafile=aggregate_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        NUM_FAMILIES=10,
    )
    TANF_T7.objects.create(
        datafile=stratum_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        TDRS_SECTION_IND="1",
        STRATUM="1",
        FAMILIES_MONTH=8,
    )

    return stt


@pytest.mark.django_db
def test_validate_run_sources_rejects_missing_source_datafiles():
    """Runs fail early when there are no accepted source files to snapshot."""
    pipeline_run = _create_pipeline_run()

    with pytest.raises(ValueError, match="active, aggregate, stratum"):
        _execute_node(pipeline_run, "validate_run_sources")

    pipeline_run.refresh_from_db()
    assert pipeline_run.metadata[SOURCE_DATAFILE_IDS_KEY] == {
        "active": [],
        "aggregate": [],
        "stratum": [],
    }


@pytest.mark.django_db
def test_build_candidates_uses_latest_files_and_stratum_fallback(parsed_weights_data):
    """Weights use latest accepted files and prefer T7 stratum counts over T6."""
    source_ids = _snapshot_source_datafile_ids(
        FISCAL_YEAR,
        TANF_PROGRAM,
    )
    candidates = PIPELINE.candidates.build(
        FISCAL_YEAR,
        PIPELINE.nodes.extract_active_family_counts.extract_rows(
            source_ids[PIPELINE.source_keys["active"]],
            TANF_PROGRAM,
        ),
        PIPELINE.nodes.extract_aggregate_case_counts.extract_rows(
            source_ids[PIPELINE.source_keys["aggregate"]],
            TANF_PROGRAM,
        ),
        PIPELINE.nodes.extract_stratum_case_counts.extract_rows(
            source_ids[PIPELINE.source_keys["stratum"]],
            TANF_PROGRAM,
        ),
        TANF_PROGRAM,
    )

    assert len(candidates) == 2
    assert {candidate.stratum for candidate in candidates} == {"1", "2"}

    stratum_one = next(
        candidate for candidate in candidates if candidate.stratum == "1"
    )
    assert stratum_one.case_count == 2
    assert stratum_one.cases == 8
    assert stratum_one.weight == Decimal("4.0000")

    stratum_two = next(
        candidate for candidate in candidates if candidate.stratum == "2"
    )
    assert stratum_two.case_count == 1
    assert stratum_two.cases == 10
    assert stratum_two.weight == Decimal("10.0000")


@pytest.mark.django_db
@pytest.mark.parametrize(
    (
        "program",
        "program_type",
        "active_model",
        "aggregate_model",
        "stratum_model",
        "aggregate_field",
    ),
    [
        (
            DataFile.ProgramType.SSP,
            DataFile.ProgramType.SSP,
            SSP_M1,
            SSP_M6,
            SSP_M7,
            "SSPMOE_FAMILIES",
        ),
        (
            DataFile.ProgramType.TRIBAL,
            DataFile.ProgramType.TRIBAL,
            Tribal_TANF_T1,
            Tribal_TANF_T6,
            Tribal_TANF_T7,
            "NUM_FAMILIES",
        ),
    ],
)
def test_program_adapters_build_non_tanf_candidates(
    stt,
    user,
    program,
    program_type,
    active_model,
    aggregate_model,
    stratum_model,
    aggregate_field,
):
    """SSP and Tribal runs use program-specific parsed models and fields."""
    active_file = _datafile(
        stt,
        user,
        DataFile.Section.ACTIVE_CASE_DATA,
        program_type=program_type,
    )
    aggregate_file = _datafile(
        stt,
        user,
        DataFile.Section.AGGREGATE_DATA,
        program_type=program_type,
    )
    stratum_file = _datafile(
        stt,
        user,
        DataFile.Section.STRATUM_DATA,
        program_type=program_type,
    )

    active_model.objects.create(
        datafile=active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000001",
        STRATUM="1",
    )
    active_model.objects.create(
        datafile=active_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="CASE000002",
        STRATUM="1",
    )
    aggregate_model.objects.create(
        datafile=aggregate_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        **{aggregate_field: 12},
    )
    stratum_model.objects.create(
        datafile=stratum_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        TDRS_SECTION_IND="1",
        STRATUM="1",
        FAMILIES_MONTH=6,
    )

    source_ids = _snapshot_source_datafile_ids(
        FISCAL_YEAR,
        program,
    )
    candidates = PIPELINE.candidates.build(
        FISCAL_YEAR,
        PIPELINE.nodes.extract_active_family_counts.extract_rows(
            source_ids[PIPELINE.source_keys["active"]],
            program,
        ),
        PIPELINE.nodes.extract_aggregate_case_counts.extract_rows(
            source_ids[PIPELINE.source_keys["aggregate"]],
            program,
        ),
        PIPELINE.nodes.extract_stratum_case_counts.extract_rows(
            source_ids[PIPELINE.source_keys["stratum"]],
            program,
        ),
        program,
    )

    assert len(candidates) == 1
    assert candidates[0].program == program
    assert candidates[0].case_count == 2
    assert candidates[0].cases == 6
    assert candidates[0].weight == Decimal("3.0000")


@pytest.mark.django_db
def test_validate_run_sources_snapshots_source_files(parsed_weights_data, user):
    """A run continues to use the DataFile snapshot captured during validation."""
    pipeline_run = _create_pipeline_run()
    _execute_node(pipeline_run, "validate_run_sources")

    newer_file = _datafile(
        parsed_weights_data,
        user,
        DataFile.Section.ACTIVE_CASE_DATA,
        version=3,
    )
    TANF_T1.objects.create(
        datafile=newer_file,
        RPT_MONTH_YEAR=REPORTING_MONTH,
        CASE_NUMBER="NEW0000001",
        STRATUM="8",
    )

    result = _execute_node(pipeline_run, "extract_active_family_counts")
    artifact = pipeline_run.artifacts.get(key=PIPELINE.intermediate_keys["s1"])
    rows = StatisticalWeightsCaseCount.objects.filter(
        pipeline_run=pipeline_run,
        count_kind=StatisticalWeightsCaseCount.CountKind.ACTIVE_FAMILY,
    )

    assert result.output_row_count == 2
    assert artifact.row_count == 2
    assert {row.stratum for row in rows} == {"1", "2"}


@pytest.mark.django_db
def test_extract_nodes_write_artifacts(parsed_weights_data):
    """Extract nodes persist their declared run-scoped artifact contracts."""
    pipeline_run = _create_pipeline_run()
    _execute_node(pipeline_run, "validate_run_sources")

    _execute_node(pipeline_run, "extract_active_family_counts")
    _execute_node(pipeline_run, "extract_aggregate_case_counts")
    _execute_node(pipeline_run, "extract_stratum_case_counts")
    _execute_node(pipeline_run, "extract_active_family_counts")

    artifacts = {
        artifact.key: artifact
        for artifact in ETLArtifact.objects.filter(pipeline_run=pipeline_run)
    }
    assert artifacts[PIPELINE.intermediate_keys["s1"]].row_count == 2
    assert artifacts[PIPELINE.intermediate_keys["s1"]].storage_kind == (
        ETLArtifact.StorageKind.POSTGRES_TABLE
    )
    assert artifacts[PIPELINE.intermediate_keys["s1"]].reference == (
        StatisticalWeightsCaseCount._meta.db_table
    )
    assert artifacts[PIPELINE.intermediate_keys["s3"]].row_count == 1
    assert artifacts[PIPELINE.intermediate_keys["s4"]].row_count == 1
    assert (
        StatisticalWeightsCaseCount.objects.filter(
            pipeline_run=pipeline_run,
            count_kind=StatisticalWeightsCaseCount.CountKind.ACTIVE_FAMILY,
        ).count()
        == 2
    )
    assert (
        StatisticalWeightsCaseCount.objects.filter(
            pipeline_run=pipeline_run,
            count_kind=StatisticalWeightsCaseCount.CountKind.AGGREGATE_CASE,
        ).count()
        == 1
    )
    assert (
        StatisticalWeightsCaseCount.objects.filter(
            pipeline_run=pipeline_run,
            count_kind=StatisticalWeightsCaseCount.CountKind.STRATUM_CASE,
        ).count()
        == 1
    )


@pytest.mark.django_db
def test_qa_and_publish_use_persisted_aggregate_artifacts(parsed_weights_data):
    """QA and publication consume persisted aggregates, not live source queries."""
    pipeline_run = _create_pipeline_run()
    _execute_node(pipeline_run, "validate_run_sources")
    _execute_node(pipeline_run, "extract_active_family_counts")
    _execute_node(pipeline_run, "extract_aggregate_case_counts")
    _execute_node(pipeline_run, "extract_stratum_case_counts")

    TANF_T1.objects.all().delete()
    TANF_T6.objects.all().delete()
    TANF_T7.objects.all().delete()

    qa_result = _execute_node(pipeline_run, "run_weights_qa")
    publish_result = _execute_node(pipeline_run, "publish_weights")

    assert qa_result.output_row_count == 4
    assert publish_result.metadata == {
        "program": TANF_PROGRAM,
        "version": 1,
        "row_count": 2,
    }
    pipeline_run.refresh_from_db()
    assert (
        pipeline_run.final_output_id
        == pipeline_run.artifacts.get(key=PIPELINE.output_key).id
    )
    assert StatisticalWeight.objects.filter(pipeline_run=pipeline_run).count() == 2


@pytest.mark.django_db
def test_missing_stt_qa_uses_stt_reference_data(parsed_weights_data, region):
    """Required T1/T6 STTs come from state and territory STT records."""
    STT.objects.create(
        name="Guam",
        region=region,
        stt_code="66",
        type=STT.EntityType.TERRITORY,
    )
    STT.objects.create(
        name="Example Tribe",
        region=region,
        stt_code="001",
        type=STT.EntityType.TRIBE,
    )
    pipeline_run = _create_pipeline_run()
    _execute_node(pipeline_run, "validate_run_sources")
    _execute_node(pipeline_run, "extract_active_family_counts")
    _execute_node(pipeline_run, "extract_aggregate_case_counts")
    _execute_node(pipeline_run, "extract_stratum_case_counts")

    _execute_node(pipeline_run, "run_weights_qa")

    qa_result = ETLQAResult.objects.get(
        pipeline_run=pipeline_run,
        check_key="weights_missing_stts",
    )
    assert qa_result.result_payload["s1_missing"] == [66]
    assert qa_result.result_payload["s3_missing"] == [66]
    assert qa_result.result_payload["s4_missing"] == []


@pytest.mark.django_db
def test_publish_weights_rejects_empty_candidates():
    """Empty in-memory candidates cannot become successful output versions."""
    pipeline_run = _create_pipeline_run()
    PIPELINE.artifacts.write_active_family_counts(pipeline_run, [])
    PIPELINE.artifacts.write_aggregate_case_counts(pipeline_run, [])
    PIPELINE.artifacts.write_stratum_case_counts(pipeline_run, [])

    with pytest.raises(ValueError, match="No statistical weight candidates"):
        _execute_node(pipeline_run, "publish_weights")

    assert not StatisticalWeight.objects.filter(pipeline_run=pipeline_run).exists()
    assert not ETLArtifact.objects.filter(
        pipeline_run=pipeline_run,
        key=PIPELINE.output_key,
        artifact_role=ETLArtifact.ArtifactRole.FINAL,
    ).exists()


@pytest.mark.django_db
def test_publish_weights_versions_outputs(parsed_weights_data):
    """Reruns publish a new version and retain the prior version until purge."""
    first_run = _create_pipeline_run()
    _execute_node(first_run, "validate_run_sources")
    _execute_node(first_run, "extract_active_family_counts")
    _execute_node(first_run, "extract_aggregate_case_counts")
    _execute_node(first_run, "extract_stratum_case_counts")
    first_result = _execute_node(first_run, "publish_weights")
    first_run.status = ETLPipelineRun.Status.SUCCEEDED
    first_run.save(update_fields=["status", "updated_at"])

    assert first_result.metadata == {
        "program": TANF_PROGRAM,
        "version": 1,
        "row_count": 2,
    }
    assert StatisticalWeight.objects.filter(version=1).count() == 2

    second_run = _create_pipeline_run()
    _execute_node(second_run, "validate_run_sources")
    _execute_node(second_run, "extract_active_family_counts")
    _execute_node(second_run, "extract_aggregate_case_counts")
    _execute_node(second_run, "extract_stratum_case_counts")
    second_result = _execute_node(second_run, "publish_weights")

    assert second_result.metadata == {
        "program": TANF_PROGRAM,
        "version": 2,
        "row_count": 2,
    }
    assert StatisticalWeight.objects.filter(version=2).count() == 2
    assert (
        StatisticalWeight.objects.filter(
            version=1,
            retention_expires_at__isnull=False,
        ).count()
        == 2
    )
    assert (
        StatisticalWeight.objects.filter(
            version=2,
            retention_expires_at__isnull=True,
        ).count()
        == 2
    )

    output = second_run.artifacts.get(key=PIPELINE.output_key)
    second_run.refresh_from_db()
    assert second_run.final_output_id == output.id
    assert output.artifact_role == ETLArtifact.ArtifactRole.FINAL
    assert output.version == 2
    assert output.row_count == 2
    assert output.published


@pytest.mark.django_db
def test_notify_weights_run_includes_operational_summary(
    ofa_system_admin,
    digit_team,
):
    """Statistical weights notification includes status, row count, QA, and run URL."""
    pipeline_run = _create_pipeline_run()
    pipeline_run.status = ETLPipelineRun.Status.RUNNING
    pipeline_run.save(update_fields=["status", "updated_at"])
    output = ETLArtifact.objects.create(
        pipeline_run=pipeline_run,
        key=PIPELINE.output_key,
        artifact_role=ETLArtifact.ArtifactRole.FINAL,
        artifact_kind=ETLArtifact.ArtifactKind.DATASET,
        storage_kind=ETLArtifact.StorageKind.POSTGRES_TABLE,
        reference=StatisticalWeight._meta.db_table,
        schema_key="statistical_weights",
        version=3,
        row_count=2,
        published=True,
        metadata=pipeline_run.output_scope,
    )
    pipeline_run.final_output = output
    pipeline_run.save(update_fields=["final_output", "updated_at"])
    ETLQAResult.objects.create(
        pipeline_run=pipeline_run,
        check_key="weights_row_counts",
        status=ETLQAResult.Status.PASSED,
        summary="Captured statistical weights row counts.",
        result_payload={"candidate_output": 2},
    )
    ETLQAResult.objects.create(
        pipeline_run=pipeline_run,
        check_key="weights_active_stratum_mismatch",
        status=ETLQAResult.Status.WARNING,
        summary="Found 12 T1/T7 stratum mismatches.",
        result_payload={"mismatches": []},
    )

    result = _execute_node(pipeline_run, "notify_weights_run")

    assert result.metadata["notification"] == "sent"
    assert len(mail.outbox) == 1
    text_message = mail.outbox[0].body
    html_message = mail.outbox[0].alternatives[0][0]
    assert "Pipeline: TANF Statistical Weights" in text_message
    assert f"Run ID: {pipeline_run.id}" in text_message
    assert "Status: SUCCEEDED" in text_message
    assert "Trigger Source: ADMIN" in text_message
    assert "Row Count: 2" in text_message
    assert "weights_row_counts: PASSED" in text_message
    assert (
        "weights_active_stratum_mismatch: WARNING - Found 12 T1/T7 stratum mismatches."
        in text_message
    )
    assert f"/admin/etl/etlpipelinerun/{pipeline_run.id}/change" in text_message
    assert "View ETL Run" in html_message
    assert "Node ID" in html_message
    assert "Status" in html_message
    assert "Error/Warning Message" in html_message
    assert "weights_row_counts" in html_message
    assert "weights_active_stratum_mismatch" in html_message
    assert "Found 12 T1/T7 stratum mismatches." in html_message
    assert f"/admin/etl/etlpipelinerun/{pipeline_run.id}/change" in html_message


@pytest.mark.django_db
def test_statistical_weights_notification_routes_through_email_helper(
    ofa_system_admin,
    digit_team,
):
    """ETL notifications use the shared email helper/template path."""
    pipeline_run = _create_pipeline_run()

    with patch(
        "tdpservice.etl.notifications.send_statistical_weights_run_email"
    ) as send_email:
        result = send_statistical_weights_notification(pipeline_run)

    send_email.assert_called_once()
    called_run, recipients = send_email.call_args.args
    assert called_run == pipeline_run
    assert set(recipients) == {ofa_system_admin.email, digit_team.email}
    assert result["notification"] == "sent"
