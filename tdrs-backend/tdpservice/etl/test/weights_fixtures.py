"""Small synthetic parsed inputs shared by node and live integration tests."""

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.etl.pipelines.sources import DataFileSource
from tdpservice.etl.pipelines.statistical_weights import StatisticalWeightsPipeline
from tdpservice.etl.pipelines.statistical_weights.adapters import adapter_for_program
from tdpservice.parsers.models import DataFileSummary
from tdpservice.parsers.test.factories import DataFileSummaryFactory
from tdpservice.stts.models import STT
from tdpservice.users.models import User

FISCAL_YEAR = 2026
REPORTING_MONTH = 202510
ALLOWED_STATUSES = (
    DataFileSummary.Status.ACCEPTED,
    DataFileSummary.Status.ACCEPTED_WITH_ERRORS,
    DataFileSummary.Status.PARTIALLY_ACCEPTED,
)


def create_weights_file(
    stt: STT,
    user: User,
    program: str,
    source: DataFileSource,
    *,
    version: int,
    status: str | None,
    state: str,
    selected: bool = False,
    quarter: str = DataFile.Quarter.Q1,
) -> DataFile:
    """Seed distinguishable persisted records even for excluded file versions."""
    datafile = DataFileFactory(
        stt=stt,
        user=user,
        program_type=program,
        section=source.section,
        year=FISCAL_YEAR,
        quarter=quarter,
        version=version,
        state=state,
    )
    if status is not None:
        DataFileSummaryFactory(datafile=datafile, status=status)
    adapter = adapter_for_program(program)
    month = REPORTING_MONTH if quarter == DataFile.Quarter.Q1 else 202601
    common = {"datafile": datafile, "RPT_MONTH_YEAR": month}
    if source.key == "active":
        for index, stratum in enumerate(("1", "1", "2") if selected else ("9",)):
            adapter.active_model.objects.create(
                **common, CASE_NUMBER=f"CASE{index:06}", STRATUM=stratum
            )
    elif source.key == "aggregate":
        adapter.aggregate_model.objects.create(
            **common, **{adapter.aggregate_case_count_field: 12 if selected else 999}
        )
    else:
        adapter.stratum_model.objects.create(
            **common,
            TDRS_SECTION_IND="1",
            STRATUM="1" if selected else "9",
            FAMILIES_MONTH=8 if selected else 999,
        )
    return datafile


def mixed_status_weights_data(
    stt: STT, user: User, program: str, status_shift: int = 0
) -> dict[str, list[int]]:
    """Mix newest eligible selection, rejected fallback, and all-ineligible groups."""
    selected_ids = {}
    node = StatisticalWeightsPipeline().nodes.validate_run_sources
    sources = node.datafile_sources(program)
    for index, source in enumerate(sources):
        status = ALLOWED_STATUSES[(index + status_shift) % len(ALLOWED_STATUSES)]
        versions = (
            (DataFileSummary.Status.REJECTED, SubmissionState.PARSED_WITH_ERRORS),
            (
                ALLOWED_STATUSES[(index + status_shift + 1) % len(ALLOWED_STATUSES)],
                SubmissionState.PARSED_WITH_ERRORS,
            ),
            (
                status,
                SubmissionState.PARSE_COMPLETED
                if status == DataFileSummary.Status.ACCEPTED
                else SubmissionState.PARSED_WITH_ERRORS,
            ),
            (DataFileSummary.Status.REJECTED, SubmissionState.PARSE_COMPLETED),
            (DataFileSummary.Status.PENDING, SubmissionState.PARSE_COMPLETED),
            (status, SubmissionState.PARSE_STARTED),
            (None, SubmissionState.PARSE_COMPLETED),
        )
        for version, (summary_status, state) in enumerate(versions, start=1):
            datafile = create_weights_file(
                stt,
                user,
                program,
                source,
                version=version,
                status=summary_status,
                state=state,
                selected=version == 3,
            )
            if version == 3:
                selected_ids[source.key] = [datafile.id]
        create_weights_file(
            stt,
            user,
            program,
            source,
            version=1,
            status=DataFileSummary.Status.REJECTED,
            state=SubmissionState.PARSED_WITH_ERRORS,
            quarter=DataFile.Quarter.Q2,
        )
    return selected_ids
