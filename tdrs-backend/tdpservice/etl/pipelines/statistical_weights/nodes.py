"""Pipeline nodes and artifact persistence for statistical weights."""

from dataclasses import dataclass

from django.db import transaction
from django.db.models import Count, Sum

from tdpservice.data_files.models import DataFile
from tdpservice.etl.artifacts import upsert_table_dataset_artifact
from tdpservice.etl.models import StatisticalWeightsCaseCount
from tdpservice.etl.notifications import send_statistical_weights_notification
from tdpservice.etl.pipelines.base import NodeContext, NodeResult, PipelineNode
from tdpservice.etl.pipelines.sources import (
    SOURCE_DATAFILE_IDS_KEY,
    DataFileSource,
    DataFileSourceSnapshot,
)
from tdpservice.etl.pipelines.statistical_weights.adapters import adapter_for_program
from tdpservice.etl.pipelines.statistical_weights.candidates import (
    WeightCandidate,
    WeightCandidateBuilder,
)
from tdpservice.etl.pipelines.statistical_weights.publishing import (
    StatisticalWeightsPublisher,
)
from tdpservice.etl.pipelines.statistical_weights.qa import StatisticalWeightsQA


@dataclass(frozen=True)
class StatisticalWeightsNodeResources:
    """Shared dependencies for statistical weights pipeline nodes."""

    source_keys: dict[str, str]
    section: str
    datafile_snapshot: DataFileSourceSnapshot
    candidates: WeightCandidateBuilder
    qa: StatisticalWeightsQA
    publisher: StatisticalWeightsPublisher
    artifacts: "StatisticalWeightsArtifactStore"


class StatisticalWeightsNode(PipelineNode):
    """Base class for statistical weights pipeline nodes."""

    def __init__(
        self,
        resources: StatisticalWeightsNodeResources,
        *,
        input_contracts: tuple[str, ...] = (),
        output_contracts: tuple[str, ...] = (),
    ):
        """Initialize a statistical weights node with shared resources."""
        self.resources = resources
        self.input_contracts = input_contracts
        self.output_contracts = output_contracts

    def datafile_sources(self, program: str) -> tuple[DataFileSource, ...]:
        """Return this pipeline's DataFile source declarations."""
        adapter = adapter_for_program(program)
        return (
            DataFileSource(
                key=self.resources.source_keys["active"],
                program_type=adapter.program_type,
                section=DataFile.Section.ACTIVE_CASE_DATA,
            ),
            DataFileSource(
                key=self.resources.source_keys["aggregate"],
                program_type=adapter.program_type,
                section=DataFile.Section.AGGREGATE_DATA,
            ),
            DataFileSource(
                key=self.resources.source_keys["stratum"],
                program_type=adapter.program_type,
                section=DataFile.Section.STRATUM_DATA,
            ),
        )

    def snapshot_source_datafile_ids(
        self,
        fiscal_year: int,
        program_type: str,
    ) -> dict[str, list[int]]:
        """Return a fresh source DataFile snapshot for one weights run."""
        return self.resources.datafile_snapshot.build_snapshot(
            fiscal_year=fiscal_year,
            sources=self.datafile_sources(program_type),
        )

    def source_datafile_ids(self, context: NodeContext) -> dict[str, list[int]]:
        """Return a run's source DataFile snapshot, creating it once when needed."""
        return self.resources.datafile_snapshot.snapshot(
            context.pipeline_run,
            fiscal_year=int(context.parameters["fiscal_year"]),
            sources=self.datafile_sources(context.parameters["program"]),
        )

    def build_candidates(
        self,
        context: NodeContext,
        *,
        s1_rows: list[dict] | None = None,
        s3_rows: list[dict] | None = None,
        s4_rows: list[dict] | None = None,
    ) -> list[WeightCandidate]:
        """Build candidate statistical weight rows from persisted aggregates."""
        if s1_rows is None:
            s1_rows = self.resources.artifacts.active_family_count_rows(context)
        if s3_rows is None:
            s3_rows = self.resources.artifacts.aggregate_case_count_rows(context)
        if s4_rows is None:
            s4_rows = self.resources.artifacts.stratum_case_count_rows(context)
        return self.resources.candidates.build(
            self.fiscal_year(context),
            s1_rows,
            s3_rows,
            s4_rows,
            self.program(context),
        )

    def fiscal_year(self, context: NodeContext) -> int:
        """Return the fiscal year parameter."""
        return int(context.parameters["fiscal_year"])

    def program(self, context: NodeContext) -> str:
        """Return the exact DataFile program type parameter for this run."""
        return context.parameters["program"]


class ValidateRunSourcesNode(StatisticalWeightsNode):
    """Validate statistical weights run sources."""

    key = "validate_run_sources"

    def execute(self, context: NodeContext) -> NodeResult:
        """Validate statistical-weights parameters and snapshot source files."""
        fiscal_year = self.fiscal_year(context)
        program = self.program(context)
        if fiscal_year < 2000:
            raise ValueError("fiscal_year must be 2000 or later.")

        source_ids = self.source_datafile_ids(context)
        missing_sources = [
            source_key
            for source_key, datafile_ids in source_ids.items()
            if not datafile_ids
        ]
        if missing_sources:
            missing_list = ", ".join(sorted(missing_sources))
            raise ValueError(
                "No accepted DataFiles found for required statistical weights "
                f"sources: {missing_list}."
            )

        return NodeResult(
            metadata={
                "fiscal_year": fiscal_year,
                "program": program,
                SOURCE_DATAFILE_IDS_KEY: source_ids,
            }
        )


class ExtractActiveFamilyCountsNode(StatisticalWeightsNode):
    """Build and persist active-family case count rows."""

    key = "extract_active_family_counts"

    def execute(self, context: NodeContext) -> NodeResult:
        """Build and persist s1 rows."""
        program = self.program(context)
        adapter = adapter_for_program(program)
        datafile_ids = self.source_datafile_ids(context)[
            self.resources.source_keys["active"]
        ]
        source_count = adapter.active_queryset(datafile_ids).count()
        rows = self.extract_rows(datafile_ids, program)
        metadata = {
            "dataset": "s1",
            "program": program,
            "source_datafile_ids": datafile_ids,
        }
        self.resources.artifacts.write_active_family_counts(
            context.pipeline_run,
            rows,
            metadata=metadata,
        )
        return NodeResult(
            input_row_count=source_count,
            output_row_count=len(rows),
            metadata=metadata,
        )

    def extract_rows(
        self,
        datafile_ids: list[int],
        program: str,
    ) -> list[dict]:
        """Build s1: unique families by STT, reporting month, and stratum."""
        adapter = adapter_for_program(program)
        rows = (
            adapter.active_queryset(datafile_ids)
            .values("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
            .annotate(case_count=Count("CASE_NUMBER", distinct=True))
            .order_by("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
        )
        return [
            {
                "stt_code": adapter.normalize_code(row["datafile__stt__stt_code"]),
                "reporting_month": row["RPT_MONTH_YEAR"],
                "stratum": adapter.normalize_code(row["STRATUM"]),
                "case_count": int(row["case_count"] or 0),
            }
            for row in rows
        ]


class ExtractAggregateCaseCountsNode(StatisticalWeightsNode):
    """Build and persist aggregate case count rows."""

    key = "extract_aggregate_case_counts"

    def execute(self, context: NodeContext) -> NodeResult:
        """Build and persist s3 rows."""
        program = self.program(context)
        adapter = adapter_for_program(program)
        datafile_ids = self.source_datafile_ids(context)[
            self.resources.source_keys["aggregate"]
        ]
        source_count = adapter.aggregate_queryset(datafile_ids).count()
        rows = self.extract_rows(datafile_ids, program)
        metadata = {
            "dataset": "s3",
            "program": program,
            "source_datafile_ids": datafile_ids,
        }
        self.resources.artifacts.write_aggregate_case_counts(
            context.pipeline_run,
            rows,
            metadata=metadata,
        )
        return NodeResult(
            input_row_count=source_count,
            output_row_count=len(rows),
            metadata=metadata,
        )

    def extract_rows(
        self,
        datafile_ids: list[int],
        program: str,
    ) -> list[dict]:
        """Build s3: aggregate cases by STT and reporting month."""
        adapter = adapter_for_program(program)
        rows = (
            adapter.aggregate_queryset(datafile_ids)
            .values("datafile__stt__stt_code", "RPT_MONTH_YEAR")
            .annotate(case_count=Sum(adapter.aggregate_case_count_field))
            .order_by("datafile__stt__stt_code", "RPT_MONTH_YEAR")
        )
        return [
            {
                "stt_code": adapter.normalize_code(row["datafile__stt__stt_code"]),
                "reporting_month": row["RPT_MONTH_YEAR"],
                "case_count": int(row["case_count"] or 0),
            }
            for row in rows
        ]


class ExtractStratumCaseCountsNode(StatisticalWeightsNode):
    """Build and persist stratum case count rows."""

    key = "extract_stratum_case_counts"

    def execute(self, context: NodeContext) -> NodeResult:
        """Build and persist s4 rows."""
        program = self.program(context)
        adapter = adapter_for_program(program)
        datafile_ids = self.source_datafile_ids(context)[
            self.resources.source_keys["stratum"]
        ]
        source_count = adapter.stratum_queryset(datafile_ids).count()
        rows = self.extract_rows(datafile_ids, program)
        metadata = {
            "dataset": "s4",
            "program": program,
            "source_datafile_ids": datafile_ids,
        }
        self.resources.artifacts.write_stratum_case_counts(
            context.pipeline_run,
            rows,
            metadata=metadata,
        )
        return NodeResult(
            input_row_count=source_count,
            output_row_count=len(rows),
            metadata=metadata,
        )

    def extract_rows(
        self,
        datafile_ids: list[int],
        program: str,
    ) -> list[dict]:
        """Build s4: stratum cases by STT, reporting month, and stratum."""
        adapter = adapter_for_program(program)
        rows = (
            adapter.stratum_queryset(datafile_ids)
            .filter(TDRS_SECTION_IND=self.resources.section, FAMILIES_MONTH__gt=0)
            .values("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
            .annotate(cases=Sum("FAMILIES_MONTH"))
            .order_by("datafile__stt__stt_code", "RPT_MONTH_YEAR", "STRATUM")
        )
        return [
            {
                "stt_code": adapter.normalize_code(row["datafile__stt__stt_code"]),
                "reporting_month": row["RPT_MONTH_YEAR"],
                "stratum": adapter.normalize_code(row["STRATUM"]),
                "cases": int(row["cases"] or 0),
            }
            for row in rows
        ]


class RunWeightsQANode(StatisticalWeightsNode):
    """Run statistical weights QA checks."""

    key = "run_weights_qa"

    def execute(self, context: NodeContext) -> NodeResult:
        """Run and persist statistical weights QA checks."""
        s1_rows = self.resources.artifacts.active_family_count_rows(context)
        s3_rows = self.resources.artifacts.aggregate_case_count_rows(context)
        s4_rows = self.resources.artifacts.stratum_case_count_rows(context)
        candidates = self.build_candidates(
            context,
            s1_rows=s1_rows,
            s3_rows=s3_rows,
            s4_rows=s4_rows,
        )
        return self.resources.qa.run(
            pipeline_run=context.pipeline_run,
            program=self.program(context),
            s1_rows=s1_rows,
            s3_rows=s3_rows,
            s4_rows=s4_rows,
            candidates=candidates,
        )


class PublishWeightsNode(StatisticalWeightsNode):
    """Publish immutable statistical weights output rows."""

    key = "publish_weights"

    def execute(self, context: NodeContext) -> NodeResult:
        """Publish a new immutable statistical weights version."""
        return self.resources.publisher.publish(
            pipeline_run=context.pipeline_run,
            output_scope=context.output_scope,
            fiscal_year=self.fiscal_year(context),
            program=self.program(context),
            candidates=self.build_candidates(context),
        )


class NotifyWeightsRunNode(StatisticalWeightsNode):
    """Notify operational users that a statistical weights run completed."""

    key = "notify_weights_run"

    def execute(self, context: NodeContext) -> NodeResult:
        """Notify operational users that a statistical weights run completed."""
        return NodeResult(
            metadata=send_statistical_weights_notification(context.pipeline_run)
        )


class StatisticalWeightsArtifactStore:
    """Persist and read run-scoped statistical weights artifacts."""

    schema_keys = {
        "s1": "statistical_weights.s1",
        "s3": "statistical_weights.s3",
        "s4": "statistical_weights.s4",
    }
    count_kinds = {
        "s1": StatisticalWeightsCaseCount.CountKind.ACTIVE_FAMILY,
        "s3": StatisticalWeightsCaseCount.CountKind.AGGREGATE_CASE,
        "s4": StatisticalWeightsCaseCount.CountKind.STRATUM_CASE,
    }

    def __init__(self, *, intermediate_keys: dict[str, str]):
        """Initialize the store with pipeline artifact keys."""
        self.intermediate_keys = intermediate_keys

    def write_active_family_counts(
        self,
        pipeline_run,
        rows: list[dict],
        metadata: dict | None = None,
    ):
        """Replace and manifest s1 active-family count rows."""
        objects = [
            StatisticalWeightsCaseCount(
                pipeline_run=pipeline_run,
                count_kind=self.count_kinds["s1"],
                stt_code=row["stt_code"],
                reporting_month=row["reporting_month"],
                stratum=row["stratum"],
                count=row["case_count"],
            )
            for row in rows
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="s1",
            objects=objects,
            metadata=metadata,
        )

    def write_aggregate_case_counts(
        self,
        pipeline_run,
        rows: list[dict],
        metadata: dict | None = None,
    ):
        """Replace and manifest s3 aggregate case count rows."""
        objects = [
            StatisticalWeightsCaseCount(
                pipeline_run=pipeline_run,
                count_kind=self.count_kinds["s3"],
                stt_code=row["stt_code"],
                reporting_month=row["reporting_month"],
                count=row["case_count"],
            )
            for row in rows
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="s3",
            objects=objects,
            metadata=metadata,
        )

    def write_stratum_case_counts(
        self,
        pipeline_run,
        rows: list[dict],
        metadata: dict | None = None,
    ):
        """Replace and manifest s4 stratum case count rows."""
        objects = [
            StatisticalWeightsCaseCount(
                pipeline_run=pipeline_run,
                count_kind=self.count_kinds["s4"],
                stt_code=row["stt_code"],
                reporting_month=row["reporting_month"],
                stratum=row["stratum"],
                count=row["cases"],
            )
            for row in rows
        ]
        return self._replace_rows(
            pipeline_run=pipeline_run,
            key_name="s4",
            objects=objects,
            metadata=metadata,
        )

    def active_family_count_rows(self, context) -> list[dict]:
        """Return s1 rows from the table-backed artifact."""
        self._artifact(context, "s1")
        return [
            {
                "stt_code": row.stt_code,
                "reporting_month": row.reporting_month,
                "stratum": row.stratum,
                "case_count": row.count,
            }
            for row in (
                StatisticalWeightsCaseCount.objects.filter(
                    pipeline_run=context.pipeline_run,
                    count_kind=self.count_kinds["s1"],
                ).order_by("stt_code", "reporting_month", "stratum")
            )
        ]

    def aggregate_case_count_rows(self, context) -> list[dict]:
        """Return s3 rows from the table-backed artifact."""
        self._artifact(context, "s3")
        return [
            {
                "stt_code": row.stt_code,
                "reporting_month": row.reporting_month,
                "case_count": row.count,
            }
            for row in (
                StatisticalWeightsCaseCount.objects.filter(
                    pipeline_run=context.pipeline_run,
                    count_kind=self.count_kinds["s3"],
                ).order_by("stt_code", "reporting_month")
            )
        ]

    def stratum_case_count_rows(self, context) -> list[dict]:
        """Return s4 rows from the table-backed artifact."""
        self._artifact(context, "s4")
        return [
            {
                "stt_code": row.stt_code,
                "reporting_month": row.reporting_month,
                "stratum": row.stratum,
                "cases": row.count,
            }
            for row in (
                StatisticalWeightsCaseCount.objects.filter(
                    pipeline_run=context.pipeline_run,
                    count_kind=self.count_kinds["s4"],
                ).order_by("stt_code", "reporting_month", "stratum")
            )
        ]

    def _replace_rows(
        self,
        *,
        pipeline_run,
        key_name: str,
        objects: list,
        metadata: dict | None,
    ):
        """Replace table rows and upsert the matching artifact manifest."""
        count_kind = self.count_kinds[key_name]
        artifact_metadata = {"count_kind": count_kind.value, **(metadata or {})}
        with transaction.atomic():
            StatisticalWeightsCaseCount.objects.filter(
                pipeline_run=pipeline_run,
                count_kind=count_kind,
            ).delete()
            StatisticalWeightsCaseCount.objects.bulk_create(objects)
            return upsert_table_dataset_artifact(
                pipeline_run=pipeline_run,
                key=self.intermediate_keys[key_name],
                model=StatisticalWeightsCaseCount,
                schema_key=self.schema_keys[key_name],
                row_count=len(objects),
                metadata=artifact_metadata,
            )

    def _artifact(self, context, key_name: str):
        """Return a declared artifact from node context."""
        return context.artifacts[self.intermediate_keys[key_name]]
