"""Tests for shared ETL source snapshot helpers."""

from django.db import transaction

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile, Program, ReparseFileMeta, Section
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.pipelines.sources import (
    ActiveReparseDataFileOverlapError,
    DataFileSource,
    DataFileSourceSnapshot,
)
from tdpservice.etl.pipelines.statistical_weights import StatisticalWeightsPipeline
from tdpservice.etl.runner import PipelineRunFactory
from tdpservice.parsers.models import DataFileSummary
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.search_indexes.models.reparse_meta import ReparseMeta
from tdpservice.stts.models import STT
from tdpservice.stts.test.factories import STTFactory
from tdpservice.users.models import User

FISCAL_YEAR = 2026


def _datafile(stt, user, version):
    """Create a parse-completed TANF active DataFile."""
    return DataFileFactory.create(
        stt=stt,
        user=user,
        section=Section.Name.ACTIVE_CASE_DATA,
        program_type=Program.Code.TANF,
        quarter=DataFile.Quarter.Q1,
        year=FISCAL_YEAR,
        version=version,
        state=SubmissionState.PARSE_COMPLETED,
    )


def _pipeline_run():
    """Create a statistical weights pipeline run for snapshot tests."""
    return PipelineRunFactory.for_pipeline_key("statistical_weights").create(
        parameters={"fiscal_year": FISCAL_YEAR, "program": Program.Code.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


@pytest.mark.django_db
def test_datafile_source_snapshotter_reuses_existing_snapshot(stt, user):
    """A run keeps using its first DataFile snapshot even after newer files land."""
    _datafile(stt, user, version=1)
    current_file = _datafile(stt, user, version=2)
    pipeline_run = _pipeline_run()
    source = DataFileSource(
        key="active",
        program_type=Program.Code.TANF,
        section=Section.Name.ACTIVE_CASE_DATA,
    )
    snapshotter = DataFileSourceSnapshot()

    first_snapshot = snapshotter.snapshot(
        pipeline_run,
        fiscal_year=FISCAL_YEAR,
        sources=(source,),
    )
    _datafile(stt, user, version=3)
    second_snapshot = snapshotter.snapshot(
        pipeline_run,
        fiscal_year=FISCAL_YEAR,
        sources=(source,),
    )

    assert first_snapshot == {"active": [current_file.id]}
    assert second_snapshot == first_snapshot


@pytest.mark.django_db
def test_datafile_source_snapshotter_rejects_duplicate_source_keys(stt, user):
    """Source keys must be unique so downstream nodes receive stable contracts."""
    source = DataFileSource(
        key="active",
        program_type=Program.Code.TANF,
        section=Section.Name.ACTIVE_CASE_DATA,
    )
    snapshotter = DataFileSourceSnapshot()

    with pytest.raises(ValueError, match="source keys must be unique"):
        with transaction.atomic():
            snapshotter.snapshot(
                _pipeline_run(),
                fiscal_year=FISCAL_YEAR,
                sources=(source, source),
            )


@pytest.mark.django_db
def test_datafile_source_snapshotter_rejects_active_reparse_overlap(stt, user):
    """ETL source snapshots cannot include DataFiles being reparsed."""
    data_file = _datafile(stt, user, version=1)
    reparse = ReparseMeta.objects.create(db_backup_location="s3://backup")
    ReparseFileMeta.objects.create(data_file=data_file, reparse_meta=reparse)
    source = DataFileSource(
        key="active",
        program_type=Program.Code.TANF,
        section=Section.Name.ACTIVE_CASE_DATA,
    )
    snapshotter = DataFileSourceSnapshot()

    with pytest.raises(ActiveReparseDataFileOverlapError, match=str(data_file.id)):
        snapshotter.snapshot(
            _pipeline_run(),
            fiscal_year=FISCAL_YEAR,
            sources=(source,),
        )


ELIGIBLE_STATUSES = (
    DataFileSummary.Status.ACCEPTED,
    DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
    DataFileSummary.Status.PARTIALLY_ACCEPTED,
)
SECTIONS = (
    Section.Name.ACTIVE_CASE_DATA,
    Section.Name.AGGREGATE_DATA,
    Section.Name.STRATUM_DATA,
)
STABLE_STATES = (SubmissionState.PARSE_COMPLETED, SubmissionState.PARSED_WITH_ERRORS)


def _weights_source(program: str, section: str) -> DataFileSource:
    """Read the production declaration rather than duplicating its policy."""
    node = StatisticalWeightsPipeline().nodes.validate_run_sources
    return next(
        source
        for source in node.datafile_sources(program)
        if source.section == section
    )


def _summarized_file(
    stt: STT, user: User, source: DataFileSource, *, status: str | None, **overrides
) -> DataFile:
    """Create a candidate with an explicit summary or deliberately omit it."""
    datafile = DataFileFactory(
        **{
            "stt": stt,
            "user": user,
            "program_type": source.program_type,
            "section": source.section,
            "year": FISCAL_YEAR,
            "quarter": DataFile.Quarter.Q1,
            "version": 1,
            "state": SubmissionState.PARSE_COMPLETED,
            **overrides,
        }
    )
    if status is not None:
        DataFileSummaryFactory(datafile=datafile, status=status)
    return datafile


@pytest.mark.django_db
@pytest.mark.parametrize(
    "program", [Program.Code.TANF, Program.Code.SSP, Program.Code.TRIBAL]
)
@pytest.mark.parametrize("section", SECTIONS)
@pytest.mark.parametrize(
    "state,status,eligible",
    [
        (state, status, True)
        for state in STABLE_STATES
        for status in ELIGIBLE_STATUSES
    ]
    + [
        (state, status, False)
        for state in STABLE_STATES
        for status in (
            DataFileSummary.Status.REJECTED,
            DataFileSummary.Status.PENDING,
            None,
            "Unknown",
        )
    ]
    + [
        (state, DataFileSummary.Status.ACCEPTED, False)
        for state in SubmissionState
        if state not in STABLE_STATES
    ],
)
def test_weights_source_requires_stable_state_and_allowed_summary(
    stt, user, program, section, state, status, eligible
):
    """Every family/program intersects lifecycle and summary eligibility."""
    source = _weights_source(program, section)
    datafile = _summarized_file(stt, user, source, status=status, state=state)

    assert DataFileSourceSnapshot().latest_datafile_ids(FISCAL_YEAR, source) == (
        [datafile.id] if eligible else []
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "newest_status", ELIGIBLE_STATUSES + (DataFileSummary.Status.REJECTED,)
)
def test_weights_source_ranks_only_eligible_versions(stt, user, newest_status):
    """Newer eligible error outcomes win; newer rejection falls back."""
    source = _weights_source(Program.Code.TANF, SECTIONS[0])
    older = _summarized_file(stt, user, source, status=DataFileSummary.Status.ACCEPTED)
    newer = _summarized_file(
        stt,
        user,
        source,
        status=newest_status,
        version=2,
        state=SubmissionState.PARSED_WITH_ERRORS,
    )

    expected = newer if newest_status in ELIGIBLE_STATUSES else older
    assert DataFileSourceSnapshot().latest_datafile_ids(FISCAL_YEAR, source) == [
        expected.id
    ]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "state,status",
    [
        (SubmissionState.PARSE_COMPLETED, None),
        (SubmissionState.PARSE_COMPLETED, DataFileSummary.Status.PENDING),
        (SubmissionState.PARSE_FAILED, DataFileSummary.Status.ACCEPTED),
        (SubmissionState.REPARSE_REQUESTED, DataFileSummary.Status.ACCEPTED),
        (SubmissionState.PARSE_STARTED, DataFileSummary.Status.ACCEPTED),
    ],
)
def test_weights_source_falls_back_while_newer_version_is_ineligible(
    stt, user, state, status
):
    """An ineligible or reparsing upload does not hide an older eligible file."""
    source = _weights_source(Program.Code.TANF, SECTIONS[0])
    older = _summarized_file(stt, user, source, status=ELIGIBLE_STATUSES[1])
    newer = _summarized_file(stt, user, source, status=status, state=state, version=2)
    if state == SubmissionState.REPARSE_REQUESTED:
        ReparseFileMeta.objects.create(
            data_file=newer, reparse_meta=ReparseMeta.objects.create()
        )

    assert DataFileSourceSnapshot().build_snapshot(
        fiscal_year=FISCAL_YEAR, sources=(source,)
    ) == {source.key: [older.id]}


@pytest.mark.django_db
def test_weights_source_partitions_and_scope_isolation(stt, user):
    """Ranking is independent per STT/quarter and ignores out-of-scope versions."""
    source = _weights_source(Program.Code.TANF, SECTIONS[0])
    other_stt = STTFactory()
    expected = [
        _summarized_file(stt, user, source, status=ELIGIBLE_STATUSES[0]),
        _summarized_file(
            stt, user, source, status=ELIGIBLE_STATUSES[1],
            quarter=DataFile.Quarter.Q2, version=3,
        ),
        _summarized_file(
            other_stt, user, source, status=ELIGIBLE_STATUSES[2], version=2
        ),
    ]
    for overrides in (
        {"year": FISCAL_YEAR - 1},
        {"program_type": Program.Code.SSP},
        {"section": SECTIONS[1]},
        {"is_program_audit": True},
    ):
        _summarized_file(
            stt, user, source, status=ELIGIBLE_STATUSES[0], version=10, **overrides
        )
    _summarized_file(
        other_stt, user, source, status=DataFileSummary.Status.REJECTED,
        quarter=DataFile.Quarter.Q3,
    )

    assert set(DataFileSourceSnapshot().latest_datafile_ids(FISCAL_YEAR, source)) == {
        datafile.id for datafile in expected
    }


@pytest.mark.django_db
@pytest.mark.parametrize("status", ELIGIBLE_STATUSES[1:])
@pytest.mark.parametrize("after_snapshot", [False, True])
@pytest.mark.parametrize("guard", ["metadata", "state"])
def test_error_status_snapshot_reparse_guards(stt, user, status, after_snapshot, guard):
    """Both new and reused error-status snapshots enforce reparse exclusion."""
    source = _weights_source(Program.Code.TANF, SECTIONS[0])
    datafile = _summarized_file(
        stt, user, source, status=status, state=SubmissionState.PARSED_WITH_ERRORS
    )
    run = _pipeline_run()
    snapshotter = DataFileSourceSnapshot()
    if after_snapshot:
        assert snapshotter.snapshot(run, fiscal_year=FISCAL_YEAR, sources=(source,)) == {
            source.key: [datafile.id]
        }
    if guard == "metadata":
        ReparseFileMeta.objects.create(
            data_file=datafile, reparse_meta=ReparseMeta.objects.create()
        )
    else:
        datafile.state = SubmissionState.REPARSE_REQUESTED
        datafile.save(update_fields=["state"])

    if guard == "state" and not after_snapshot:
        assert snapshotter.snapshot(
            run, fiscal_year=FISCAL_YEAR, sources=(source,)
        ) == {source.key: []}
    else:
        with pytest.raises(ActiveReparseDataFileOverlapError, match=str(datafile.id)):
            snapshotter.snapshot(run, fiscal_year=FISCAL_YEAR, sources=(source,))


@pytest.mark.django_db
def test_default_source_keeps_lifecycle_only_semantics(stt, user):
    """Shared defaults impose no summary rule and do not broaden lifecycle scope."""
    source = DataFileSource(
        key="active", program_type=Program.Code.TANF, section=SECTIONS[0]
    )
    _summarized_file(stt, user, source, status=None)
    completed = _summarized_file(
        stt, user, source, status=DataFileSummary.Status.REJECTED, version=2
    )
    _summarized_file(
        stt,
        user,
        source,
        status=DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
        version=3,
        state=SubmissionState.PARSED_WITH_ERRORS,
    )

    assert DataFileSourceSnapshot().latest_datafile_ids(FISCAL_YEAR, source) == [
        completed.id
    ]
