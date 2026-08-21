"""Base contracts for code-owned ETL pipelines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Iterable

from django.db import transaction
from django.utils import timezone

from tdpservice.etl.exceptions import PipelineValidationError


@dataclass(frozen=True)
class NodeResult:
    """Structured result returned by a node handler."""

    input_row_count: int | None = None
    output_row_count: int | None = None
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class NodeContext:
    """Execution context passed to a pipeline node operation."""

    pipeline_run: Any
    artifacts: dict[str, Any]

    @property
    def parameters(self) -> dict:
        """Return run parameters."""
        return self.pipeline_run.parameters

    @property
    def output_scope(self) -> dict:
        """Return run output scope."""
        return self.pipeline_run.output_scope


class PipelineNode(ABC):
    """Execution boundary for one ETLNodeRun-backed pipeline node."""

    input_contracts: tuple[str, ...] = ()
    output_contracts: tuple[str, ...] = ()

    @abstractmethod
    def execute(self, context: NodeContext) -> NodeResult | None:
        """Run this node's business operation."""

    @property
    @abstractmethod
    def key(self) -> str:
        """Return this node's stable ETLNodeRun key."""

    def task(self, pipeline_run_id: int):
        """Return the Celery signature for this node."""
        from tdpservice.etl.tasks import run_pipeline_node

        return run_pipeline_node.si(pipeline_run_id, self.key)

    def run(self, pipeline_run) -> dict:
        """Execute this node and persist its ETLNodeRun state."""
        from tdpservice.etl.models import ETLNodeRun

        node_run = None

        try:
            with transaction.atomic():
                node_run = ETLNodeRun.objects.select_for_update().get(
                    pipeline_run=pipeline_run,
                    node_key=self.key,
                )
                start_result = self._start_node_run(pipeline_run, node_run)
                if start_result:
                    return start_result

            context = self._build_context(pipeline_run)
            result = self.execute(context)
            if result is None:
                result = NodeResult()

            self._mark_succeeded(node_run, result)
            return {"node_key": self.key, "status": node_run.status}
        except Exception as exc:
            self._mark_failed(pipeline_run, node_run, exc)
            raise

    def _start_node_run(self, pipeline_run, node_run) -> dict | None:
        """Claim a pending ETLNodeRun or return its existing terminal state."""
        from tdpservice.etl.models import ETLNodeRun, ETLPipelineRun

        if node_run.status in (
            ETLNodeRun.Status.RUNNING,
            ETLNodeRun.Status.SUCCEEDED,
        ):
            return {
                "node_key": self.key,
                "status": node_run.status,
                "already_started": True,
            }
        if node_run.status == ETLNodeRun.Status.FAILED:
            return {
                "node_key": self.key,
                "status": node_run.status,
                "already_completed": True,
            }

        now = timezone.now()
        if pipeline_run.status == ETLPipelineRun.Status.PENDING:
            pipeline_run.status = ETLPipelineRun.Status.RUNNING
            pipeline_run.started_at = now
            pipeline_run.save(update_fields=["status", "started_at", "updated_at"])

        node_run.status = ETLNodeRun.Status.RUNNING
        node_run.started_at = now
        node_run.error_message = None
        node_run.save(
            update_fields=[
                "status",
                "started_at",
                "error_message",
            ]
        )
        return None

    def _build_context(self, pipeline_run) -> NodeContext:
        """Build a validated node context from persisted upstream artifacts."""
        artifacts = {
            artifact.key: artifact
            for artifact in pipeline_run.artifacts.all().order_by("id")
        }
        available_contracts = set(artifacts)
        missing_contracts = set(self.input_contracts) - available_contracts
        if missing_contracts:
            raise PipelineValidationError(
                f"Missing input contracts for {self.key}: {sorted(missing_contracts)}"
            )

        return NodeContext(
            pipeline_run=pipeline_run,
            artifacts=artifacts,
        )

    def _mark_succeeded(
        self,
        node_run,
        result: NodeResult,
    ) -> None:
        """Persist a successful node result."""
        node_run.status = node_run.Status.SUCCEEDED
        node_run.finished_at = timezone.now()
        node_run.input_row_count = result.input_row_count
        node_run.output_row_count = result.output_row_count
        node_run.metadata = result.metadata
        node_run.save(
            update_fields=[
                "status",
                "finished_at",
                "input_row_count",
                "output_row_count",
                "metadata",
            ]
        )

    def _mark_failed(
        self,
        pipeline_run,
        node_run,
        exc: Exception,
    ) -> None:
        """Persist node and pipeline failure state."""
        from tdpservice.etl.models import ETLPipelineRun

        if node_run is not None:
            node_run.status = node_run.Status.FAILED
            node_run.finished_at = timezone.now()
            node_run.error_message = str(exc)
            node_run.save(update_fields=["status", "finished_at", "error_message"])

        pipeline_run.status = ETLPipelineRun.Status.FAILED
        pipeline_run.finished_at = timezone.now()
        pipeline_run.error_message = f"{self.key}: {exc}"
        pipeline_run.save(
            update_fields=["status", "finished_at", "error_message", "updated_at"]
        )


class PipelineNodeRegistry:
    """Node collection addressable by node key or attribute name."""

    def __init__(self, nodes: Iterable[PipelineNode]):
        """Initialize a registry from pipeline-owned nodes."""
        self._nodes = tuple(nodes)
        self._node_map = {node.key: node for node in self._nodes}

    def __iter__(self):
        """Iterate over registered nodes in declaration order."""
        return iter(self._nodes)

    def __getitem__(self, key: str) -> PipelineNode:
        """Return a node by ETLNodeRun node_key."""
        try:
            return self._node_map[key]
        except KeyError as exc:
            raise PipelineValidationError(f"Unknown pipeline node: {key}") from exc

    def __getattr__(self, key: str) -> PipelineNode:
        """Return a node by attribute when the key is a valid Python name."""
        try:
            return self[key]
        except PipelineValidationError as exc:
            raise AttributeError(key) from exc


class PipelineDefinition(ABC):
    """Base interface for one approved ETL pipeline."""

    key: str
    version: str
    display_name: str
    description: str
    allowed_parameters: dict
    nodes: PipelineNodeRegistry
    schedule: dict | None = None
    required_groups: tuple[str, ...] = ("OFA System Admin",)

    @abstractmethod
    def validate_parameters(self, parameters: dict) -> dict:
        """Validate and normalize run parameters for this pipeline."""

    @abstractmethod
    def output_scope(self, parameters: dict) -> dict:
        """Build the idempotency/output scope for this pipeline."""

    @abstractmethod
    def build_canvas(self, pipeline_run_id: int) -> Any:
        """Build the code-owned Celery Canvas for this pipeline run."""

    @abstractmethod
    def _pipeline_nodes(self) -> PipelineNodeRegistry:
        """Build the pipeline registry for canvas execution."""

    def validate(self) -> None:
        """Validate node metadata for this pipeline."""
        node_keys = [node.key for node in self.nodes]
        if any(not node_key for node_key in node_keys):
            raise PipelineValidationError("Pipeline node keys cannot be empty.")
        if len(node_keys) != len(set(node_keys)):
            raise PipelineValidationError("Pipeline node keys must be unique.")

    def serialize(self) -> dict:
        """Return API-safe pipeline definition metadata."""
        return {
            "key": self.key,
            "version": self.version,
            "display_name": self.display_name,
            "description": self.description,
            "allowed_parameters": self.allowed_parameters,
            "schedule": self.schedule,
            "nodes": [
                {
                    "key": node.key,
                    "input_contracts": list(node.input_contracts),
                    "output_contracts": list(node.output_contracts),
                }
                for node in self.nodes
            ],
        }
