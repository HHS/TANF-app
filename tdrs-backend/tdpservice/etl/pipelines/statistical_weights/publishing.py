"""Publication service for statistical weights outputs."""

from datetime import timedelta

from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from tdpservice.etl.artifacts import upsert_table_dataset_artifact
from tdpservice.etl.models import ETLArtifact, ETLQAResult, StatisticalWeight
from tdpservice.etl.pipelines.base import NodeResult
from tdpservice.etl.pipelines.statistical_weights.adapters import adapter_for_program
from tdpservice.etl.pipelines.statistical_weights.candidates import WeightCandidate


class StatisticalWeightsPublisher:
    """Publish immutable statistical weights table versions."""

    def __init__(self, *, section: str, output_key: str):
        """Initialize publication for one output contract."""
        self.section = section
        self.output_key = output_key

    def publish(
        self,
        *,
        pipeline_run,
        output_scope: dict,
        fiscal_year: int,
        program: str,
        candidates: list[WeightCandidate],
    ) -> NodeResult:
        """Publish a new immutable statistical weights version."""
        adapter_for_program(program)
        blocking_failure_exists = ETLQAResult.objects.filter(
            pipeline_run=pipeline_run,
            blocking=True,
            status=ETLQAResult.Status.FAILED,
        ).exists()
        if blocking_failure_exists:
            raise ValueError(
                "Blocking QA failure prevents statistical weights publication."
            )
        if not candidates:
            raise ValueError("No statistical weight candidates to publish.")

        now = timezone.now()
        retention_expires_at = now + timedelta(days=365)

        with transaction.atomic():
            existing_rows = StatisticalWeight.objects.select_for_update().filter(
                **self.scope_filter(fiscal_year, program)
            )
            current_version = (
                existing_rows.aggregate(latest=Max("version"))["latest"] or 0
            )
            next_version = current_version + 1

            if current_version:
                existing_rows.filter(
                    version=current_version, retention_expires_at__isnull=True
                ).update(retention_expires_at=retention_expires_at)

            StatisticalWeight.objects.bulk_create(
                [
                    StatisticalWeight(
                        fiscal_year=candidate.fiscal_year,
                        reporting_month=candidate.reporting_month,
                        program=candidate.program,
                        section=candidate.section,
                        stt_code=candidate.stt_code,
                        stratum=candidate.stratum,
                        version=next_version,
                        case_count=candidate.case_count,
                        cases=candidate.cases,
                        weight=candidate.weight,
                        pipeline_run=pipeline_run,
                        published_at=now,
                    )
                    for candidate in candidates
                ]
            )
            final_output = upsert_table_dataset_artifact(
                pipeline_run=pipeline_run,
                key=self.output_key,
                model=StatisticalWeight,
                schema_key="statistical_weights",
                artifact_role=ETLArtifact.ArtifactRole.FINAL,
                version=next_version,
                row_count=len(candidates),
                published=True,
                metadata=output_scope,
            )
            pipeline_run.final_output = final_output
            pipeline_run.save(update_fields=["final_output", "updated_at"])

        return NodeResult(
            output_row_count=len(candidates),
            metadata={
                "program": program,
                "version": next_version,
                "row_count": len(candidates),
            },
        )

    def scope_filter(self, fiscal_year: int, program: str) -> dict:
        """Return the StatisticalWeight filter for a fiscal-year output scope."""
        adapter_for_program(program)
        return {
            "fiscal_year": fiscal_year,
            "program": program,
            "section": self.section,
        }
