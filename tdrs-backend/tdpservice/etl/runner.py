"""ETL pipeline run creation and execution services."""

import hashlib
import json

from django.db import IntegrityError, transaction
from django.utils import timezone

from tdpservice.etl.exceptions import ActivePipelineRunError
from tdpservice.etl.models import ETLNodeRun, ETLPipelineRun
from tdpservice.etl.pipelines.base import PipelineDefinition
from tdpservice.etl.registry import get_pipeline_definition

ACTIVE_RUN_STATUSES = (
    ETLPipelineRun.Status.PENDING,
    ETLPipelineRun.Status.RUNNING,
)


class PipelineRunFactory:
    """Create pipeline run records from a code-owned pipeline definition."""

    def __init__(self, definition: PipelineDefinition):
        """Initialize a run creator for one pipeline definition."""
        self.definition = definition

    @classmethod
    def for_pipeline_key(cls, pipeline_key: str) -> "PipelineRunFactory":
        """Build a creator for an approved pipeline key."""
        return cls(get_pipeline_definition(pipeline_key))

    def create(
        self,
        *,
        parameters: dict,
        trigger_source: str,
        triggered_by=None,
        retry_of: ETLPipelineRun | None = None,
    ) -> ETLPipelineRun:
        """Create a pipeline run and initial ETLNodeRun records."""
        self.definition.validate()
        normalized_parameters = self.definition.validate_parameters(parameters)
        output_scope = self.definition.output_scope(normalized_parameters)
        scope_key = output_scope_key(output_scope)

        try:
            with transaction.atomic():
                active_run = (
                    ETLPipelineRun.objects.select_for_update()
                    .filter(
                        pipeline_key=self.definition.key,
                        output_scope_key=scope_key,
                        status__in=ACTIVE_RUN_STATUSES,
                    )
                    .first()
                )
                if active_run:
                    raise ActivePipelineRunError(
                        f"Run {active_run.id} is already active for this output scope."
                    )

                pipeline_run = ETLPipelineRun.objects.create(
                    pipeline_key=self.definition.key,
                    pipeline_version=self.definition.version,
                    status=ETLPipelineRun.Status.PENDING,
                    parameters=normalized_parameters,
                    output_scope=output_scope,
                    output_scope_key=scope_key,
                    trigger_source=trigger_source,
                    triggered_by=triggered_by,
                    retry_of=retry_of,
                )
                ETLNodeRun.objects.bulk_create(
                    [
                        ETLNodeRun(pipeline_run=pipeline_run, node_key=node.key)
                        for node in self.definition.nodes
                    ]
                )
        except IntegrityError as exc:
            active_run = (
                ETLPipelineRun.objects.filter(
                    pipeline_key=self.definition.key,
                    output_scope_key=scope_key,
                    status__in=ACTIVE_RUN_STATUSES,
                )
                .order_by("id")
                .first()
            )
            if active_run:
                raise ActivePipelineRunError(
                    f"Run {active_run.id} is already active for this output scope."
                ) from exc
            raise

        return pipeline_run


class PipelineRunLauncher:
    """Launch and finalize a persisted pipeline run."""

    def __init__(
        self,
        *,
        pipeline_run: ETLPipelineRun,
        definition: PipelineDefinition,
    ):
        """Initialize a launcher for one persisted pipeline run."""
        self.pipeline_run = pipeline_run
        self.definition = definition

    @classmethod
    def for_run_id(cls, pipeline_run_id: int) -> "PipelineRunLauncher":
        """Build a launcher for a persisted pipeline run."""
        pipeline_run = ETLPipelineRun.objects.get(id=pipeline_run_id)
        definition = get_pipeline_definition(pipeline_run.pipeline_key)
        definition.validate()
        return cls(pipeline_run=pipeline_run, definition=definition)

    def launch(self):
        """Queue the pipeline-owned Canvas for a pipeline run."""
        if self.pipeline_run.status == ETLPipelineRun.Status.PENDING:
            self.pipeline_run.status = ETLPipelineRun.Status.RUNNING
            self.pipeline_run.started_at = timezone.now()
            self.pipeline_run.save(update_fields=["status", "started_at", "updated_at"])

        pipeline_canvas = self.definition.build_canvas(self.pipeline_run.id)
        return pipeline_canvas.apply_async()

    def finalize(self) -> dict:
        """Finalize a pipeline run after its Celery Canvas completes."""
        node_runs = self.pipeline_run.node_runs.all()

        if node_runs.filter(status=ETLNodeRun.Status.FAILED).exists():
            self.pipeline_run.status = ETLPipelineRun.Status.FAILED
        elif node_runs.exclude(status=ETLNodeRun.Status.SUCCEEDED).exists():
            self.pipeline_run.status = ETLPipelineRun.Status.FAILED
            self.pipeline_run.error_message = (
                "One or more ETLNodeRun records did not complete."
            )
        else:
            self.pipeline_run.status = ETLPipelineRun.Status.SUCCEEDED

        self.pipeline_run.finished_at = timezone.now()
        self.pipeline_run.save(
            update_fields=["status", "finished_at", "error_message", "updated_at"]
        )
        return {
            "pipeline_run_id": self.pipeline_run.id,
            "status": self.pipeline_run.status,
        }


def output_scope_key(output_scope: dict) -> str:
    """Return a stable hash key for an output scope."""
    canonical_scope = json.dumps(
        output_scope,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical_scope.encode("utf-8")).hexdigest()
