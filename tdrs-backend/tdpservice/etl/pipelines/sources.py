"""Shared source-selection helpers for ETL pipelines."""

from dataclasses import dataclass

from django.db.models import F, OuterRef, Subquery

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile, ReparseFileMeta

SOURCE_DATAFILE_IDS_KEY = "source_datafile_ids"
ACTIVE_PIPELINE_RUN_STATUSES = ("PENDING", "RUNNING")


class ActiveDataFileOverlapError(ValueError):
    """Raised when active ETL and reparse work would use the same DataFile."""


class ActiveReparseDataFileOverlapError(ActiveDataFileOverlapError):
    """Raised when an ETL pipeline would use a DataFile being reparsed."""


class ActivePipelineDataFileOverlapError(ActiveDataFileOverlapError):
    """Raised when reparse would use a DataFile snapshotted by active ETL."""


@dataclass(frozen=True)
class DataFileSource:
    """A DataFile-backed source input declared by a pipeline."""

    key: str
    program_type: str
    section: str
    parser_state: str = SubmissionState.PARSE_COMPLETED
    is_program_audit: bool = False


class DataFileSourceSnapshot:
    """Snapshot latest accepted DataFile ids once for a pipeline run."""

    def __init__(self, metadata_key: str = SOURCE_DATAFILE_IDS_KEY):
        """Initialize the source snapshot with its run metadata key."""
        self.metadata_key = metadata_key

    def snapshot(
        self,
        pipeline_run,
        *,
        fiscal_year: int,
        sources: tuple[DataFileSource, ...],
    ) -> dict[str, list[int]]:
        """Return a run's source snapshot, creating it once when needed."""
        existing_snapshot = self.from_run(pipeline_run, sources=sources)
        if existing_snapshot is not None:
            validate_no_active_reparse_overlap(
                [
                    datafile_id
                    for datafile_ids in existing_snapshot.values()
                    for datafile_id in datafile_ids
                ]
            )
            return existing_snapshot

        source_ids = self.build_snapshot(fiscal_year=fiscal_year, sources=sources)
        metadata = dict(pipeline_run.metadata or {})
        metadata[self.metadata_key] = source_ids
        pipeline_run.metadata = metadata
        pipeline_run.save(update_fields=["metadata", "updated_at"])
        return source_ids

    def from_run(
        self,
        pipeline_run,
        *,
        sources: tuple[DataFileSource, ...],
    ) -> dict[str, list[int]] | None:
        """Return a run's existing source snapshot when present."""
        metadata = dict(pipeline_run.metadata or {})
        source_ids = metadata.get(self.metadata_key)
        if source_ids is None:
            return None
        return self._coerce_snapshot(source_ids, sources)

    def build_snapshot(
        self,
        *,
        fiscal_year: int,
        sources: tuple[DataFileSource, ...],
    ) -> dict[str, list[int]]:
        """Build a fresh latest-accepted DataFile id snapshot."""
        self._validate_sources(sources)
        source_ids = {
            source.key: self.latest_datafile_ids(fiscal_year, source)
            for source in sources
        }
        validate_no_active_reparse_overlap(
            [
                datafile_id
                for datafile_ids in source_ids.values()
                for datafile_id in datafile_ids
            ]
        )
        return source_ids

    def latest_datafile_ids(
        self,
        fiscal_year: int,
        source: DataFileSource,
    ) -> list[int]:
        """Return latest accepted DataFile ids by STT and quarter for a source."""
        accepted_files = DataFile.objects.filter(
            year=fiscal_year,
            program_type=source.program_type,
            section=source.section,
            is_program_audit=source.is_program_audit,
            state=source.parser_state,
        )

        latest_version = (
            DataFile.objects.filter(
                year=fiscal_year,
                program_type=source.program_type,
                section=source.section,
                is_program_audit=source.is_program_audit,
                state=source.parser_state,
                stt_id=OuterRef("stt_id"),
                quarter=OuterRef("quarter"),
            )
            .order_by("-version")
            .values("version")[:1]
        )

        return list(
            accepted_files.annotate(latest_version=Subquery(latest_version))
            .filter(version=F("latest_version"))
            .values_list("id", flat=True)
        )

    def _coerce_snapshot(
        self,
        source_ids: dict,
        sources: tuple[DataFileSource, ...],
    ) -> dict[str, list[int]]:
        """Return a snapshot with stable source keys and integer IDs."""
        self._validate_sources(sources)
        return {
            source.key: [int(value) for value in source_ids.get(source.key, [])]
            for source in sources
        }

    def _validate_sources(self, sources: tuple[DataFileSource, ...]) -> None:
        """Validate source keys are unique before snapshotting."""
        source_keys = [source.key for source in sources]
        if len(source_keys) != len(set(source_keys)):
            raise ValueError("DataFile source keys must be unique.")


def validate_no_active_reparse_overlap(datafile_ids) -> None:
    """Raise when ETL source DataFiles intersect active reparse work."""
    overlapping_ids = datafile_id_overlap(datafile_ids, active_reparse_datafile_ids())
    if overlapping_ids:
        raise ActiveReparseDataFileOverlapError(
            "DataFile ids are currently being reparsed and cannot be used by "
            f"an ETL pipeline: {overlapping_ids}."
        )


def validate_no_active_pipeline_source_overlap(datafile_ids) -> None:
    """Raise when reparse DataFiles intersect active ETL source snapshots."""
    overlapping_ids = datafile_id_overlap(
        datafile_ids,
        active_pipeline_source_datafile_ids(),
    )
    if overlapping_ids:
        raise ActivePipelineDataFileOverlapError(
            "DataFile ids are already snapshotted by active ETL pipeline runs "
            f"and cannot be reparsed: {overlapping_ids}."
        )


def datafile_id_overlap(candidate_ids, active_ids) -> set[int]:
    """Return DataFile IDs present in both flat ID sets."""
    return sorted(set(candidate_ids) & set(active_ids))


def active_reparse_datafile_ids() -> set[int]:
    """Return DataFile ids currently involved in active reparse work."""
    reparse_requested_files = DataFile.objects.filter(
        state=SubmissionState.REPARSE_REQUESTED
    )
    unfinished_reparse_files = ReparseFileMeta.objects.filter(finished=False)

    active_ids = set(reparse_requested_files.values_list("id", flat=True))
    active_ids.update(
        unfinished_reparse_files.values_list("data_file_id", flat=True).distinct()
    )
    return sorted(active_ids)


def active_pipeline_source_datafile_ids() -> set[int]:
    """Return DataFile ids snapshotted by active ETL runs."""
    from tdpservice.etl.models import ETLPipelineRun

    active_ids = set()
    active_runs = ETLPipelineRun.objects.filter(status__in=ACTIVE_PIPELINE_RUN_STATUSES)
    for metadata in active_runs.values_list("metadata", flat=True):
        source_ids_by_key = (metadata or {}).get(SOURCE_DATAFILE_IDS_KEY, {})
        for datafile_ids in source_ids_by_key.values():
            active_ids.update(int(datafile_id) for datafile_id in datafile_ids)
    return sorted(active_ids)
