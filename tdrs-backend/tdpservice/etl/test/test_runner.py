"""Tests for ETL runner services."""

from collections.abc import Callable
from unittest.mock import patch

from django.db import IntegrityError, transaction

import pytest

from tdpservice.data_files.models import DataFile
from tdpservice.etl.exceptions import ActivePipelineRunError, PipelineValidationError
from tdpservice.etl.models import ETLArtifact, ETLNodeRun, ETLPipelineRun
from tdpservice.etl.pipelines.base import (
    NodeResult,
    PipelineDefinition,
    PipelineNode,
    PipelineNodeRegistry,
)
from tdpservice.etl.registry import get_pipeline_definition
from tdpservice.etl.runner import PipelineRunFactory, output_scope_key
from tdpservice.etl.tasks import run_pipeline_node


def _noop(context) -> None:
    """No-op node handler for graph tests."""
    return None


class DummyPipelineNode(PipelineNode):
    """Minimal concrete node for runner tests."""

    def __init__(
        self,
        key: str,
        operation: Callable[[object], NodeResult | None] | None = None,
        *,
        input_contracts: tuple[str, ...] = (),
        output_contracts: tuple[str, ...] = (),
    ):
        """Initialize a test node with configurable execution."""
        self._key = key
        self.operation = operation or _noop
        self.input_contracts = input_contracts
        self.output_contracts = output_contracts

    @property
    def key(self) -> str:
        """Return the stable test node key."""
        return self._key

    def execute(self, context) -> NodeResult | None:
        """Run the configured test operation."""
        return self.operation(context)


def _node(key: str, operation=None, **kwargs):
    """Build a concrete test node with a stable key."""
    return DummyPipelineNode(key, operation, **kwargs)


class ConcretePipelineDefinition(PipelineDefinition):
    """Minimal concrete pipeline definition for runner tests."""

    key = "test_pipeline"
    version = "1"
    display_name = "Test Pipeline"
    description = "Pipeline used by runner tests."
    allowed_parameters = {"fiscal_year": {"required": True}}

    def __init__(self, nodes, handlers=None):
        """Initialize a test pipeline with configurable nodes."""
        self.nodes = PipelineNodeRegistry(nodes)
        self.handlers = handlers or {}

    def extract(self, context):
        """Run a configurable extract handler."""
        return self.handlers.get("extract", _noop)(context)

    def consume(self, context):
        """Run a configurable consume handler."""
        return self.handlers["consume"](context)

    def validate_parameters(self, parameters: dict) -> dict:
        """Return test parameters unchanged."""
        return dict(parameters or {})

    def output_scope(self, parameters: dict) -> dict:
        """Return a simple fiscal-year output scope."""
        return {
            "pipeline": self.key,
            "fiscal_year": int(parameters["fiscal_year"]),
        }

    def _pipeline_nodes(self) -> PipelineNodeRegistry:
        """Return configured test node declarations."""
        return self.nodes

    def build_canvas(self, pipeline_run_id: int):
        """Test pipeline does not declare an executable Canvas."""
        raise PipelineValidationError(
            f"Pipeline {self.key} does not define an executable Celery Canvas."
        )


def _definition(nodes, handlers=None):
    """Build a minimal pipeline definition."""
    return ConcretePipelineDefinition(nodes, handlers)


def _create_pipeline_run():
    """Create a statistical weights pipeline run for runner tests."""
    return PipelineRunFactory.for_pipeline_key("statistical_weights").create(
        parameters={"fiscal_year": 2026, "program": DataFile.ProgramType.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


def test_pipeline_canvas_uses_chord_for_extract_fan_in():
    """The pipeline-owned Canvas expresses the DAG without a layer compiler."""
    definition = get_pipeline_definition("statistical_weights")

    canvas_graph = definition.build_canvas(pipeline_run_id=1)
    chord_task = canvas_graph.tasks[1]

    canvas_repr = repr(canvas_graph)
    assert chord_task.name == "celery.chord"
    assert [task.args[1] for task in chord_task.tasks] == [
        "extract_active_family_counts",
        "extract_aggregate_case_counts",
        "extract_stratum_case_counts",
    ]
    assert chord_task.body.immutable
    assert chord_task.body.args[1] == "run_weights_qa"
    downstream_chain = chord_task.body.options["link"][0]
    assert downstream_chain.immutable
    assert [task.args[1] for task in downstream_chain.tasks[:2]] == [
        "publish_weights",
        "notify_weights_run",
    ]
    assert (
        downstream_chain.tasks[2].name == "tdpservice.etl.tasks.finalize_pipeline_run"
    )
    assert all(task.immutable for task in downstream_chain.tasks)
    assert "validate_run_sources" in canvas_repr
    assert "extract_active_family_counts" in canvas_repr
    assert "extract_aggregate_case_counts" in canvas_repr
    assert "extract_stratum_case_counts" in canvas_repr
    assert "build_weight_candidates" not in canvas_repr
    assert "advance_pipeline_run" not in canvas_repr


def test_pipeline_nodes_create_registered_task_signatures():
    """Pipeline nodes expose their Celery task signatures directly."""
    definition = get_pipeline_definition("statistical_weights")

    node = definition.nodes["publish_weights"]
    signature = definition.nodes.publish_weights.task(pipeline_run_id=123)

    assert definition.nodes.publish_weights is node
    assert signature.name == "tdpservice.etl.tasks.run_pipeline_node"
    assert signature.args == (123, "publish_weights")


def test_pipeline_validation_rejects_duplicate_node_keys():
    """Pipeline node keys must be unique for ETLNodeRun lookup."""
    definition = _definition(
        [
            _node("extract"),
            _node("extract"),
        ]
    )

    with pytest.raises(PipelineValidationError):
        definition.validate()


def test_pipeline_node_exposes_configured_key():
    """Pipeline nodes expose their configured ETLNodeRun key."""
    node = _node("extract")

    assert node.key == "extract"


def test_pipeline_definition_requires_canvas_builder_implementation():
    """Pipeline definitions must implement executable Canvas declaration."""

    class MissingCanvasPipeline(PipelineDefinition):
        key = "missing_canvas"
        version = "1"
        display_name = "Missing Canvas"
        description = "Pipeline missing a Canvas implementation."
        allowed_parameters = {}
        nodes = PipelineNodeRegistry(())

        def validate_parameters(self, parameters: dict) -> dict:
            return {}

        def output_scope(self, parameters: dict) -> dict:
            return {}

    with pytest.raises(TypeError):
        MissingCanvasPipeline()


def test_statistical_weights_parameters_normalize_fiscal_year():
    """Fiscal year input is normalized for output-scope idempotency."""
    definition = get_pipeline_definition("statistical_weights")

    assert definition.validate_parameters(
        {"fiscal_year": "2026", "program": DataFile.ProgramType.TANF}
    ) == {
        "fiscal_year": 2026,
        "program": DataFile.ProgramType.TANF,
    }


def test_validate_statistical_weights_parameters_rejects_program_alias():
    """Program input must use exact DataFile.ProgramType values."""
    definition = get_pipeline_definition("statistical_weights")

    with pytest.raises(PipelineValidationError):
        definition.validate_parameters({"fiscal_year": "2026", "program": "TANF"})


def test_validate_statistical_weights_parameters_rejects_unknown_program():
    """Only supported statistical weights programs are accepted."""
    definition = get_pipeline_definition("statistical_weights")

    with pytest.raises(PipelineValidationError):
        definition.validate_parameters({"fiscal_year": 2026, "program": "WPR"})


def test_validate_run_parameters_rejects_unknown_parameters():
    """Only code-defined pipeline parameters are accepted."""
    definition = get_pipeline_definition("statistical_weights")

    with pytest.raises(PipelineValidationError):
        definition.validate_parameters(
            {
                "fiscal_year": 2026,
                "program": DataFile.ProgramType.TANF,
                "raw_sql": "select 1",
            }
        )


@pytest.mark.django_db
def test_active_run_scope_key_constraint_allows_completed_reruns():
    """The database rejects duplicate active scopes and allows completed reruns."""
    definition = get_pipeline_definition("statistical_weights")
    parameters = {"fiscal_year": 2026, "program": DataFile.ProgramType.TANF}
    scope = definition.output_scope(parameters)
    scope_key = output_scope_key(scope)

    ETLPipelineRun.objects.create(
        pipeline_key=definition.key,
        pipeline_version=definition.version,
        status=ETLPipelineRun.Status.PENDING,
        parameters=parameters,
        output_scope=scope,
        output_scope_key=scope_key,
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ETLPipelineRun.objects.create(
                pipeline_key=definition.key,
                pipeline_version=definition.version,
                status=ETLPipelineRun.Status.RUNNING,
                parameters=parameters,
                output_scope=scope,
                output_scope_key=scope_key,
                trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
            )

    ETLPipelineRun.objects.create(
        pipeline_key=definition.key,
        pipeline_version=definition.version,
        status=ETLPipelineRun.Status.SUCCEEDED,
        parameters=parameters,
        output_scope=scope,
        output_scope_key=scope_key,
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )


@pytest.mark.django_db
def test_create_pipeline_run_reports_active_scope():
    """Run creation converts active-scope conflicts into a domain error."""
    creator = PipelineRunFactory.for_pipeline_key("statistical_weights")
    first_run = creator.create(
        parameters={"fiscal_year": 2026, "program": DataFile.ProgramType.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    with pytest.raises(ActivePipelineRunError):
        creator.create(
            parameters={"fiscal_year": 2026, "program": DataFile.ProgramType.TANF},
            trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
        )

    first_run.status = ETLPipelineRun.Status.SUCCEEDED
    first_run.save(update_fields=["status", "updated_at"])
    second_run = creator.create(
        parameters={"fiscal_year": 2026, "program": DataFile.ProgramType.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    assert second_run.output_scope_key == first_run.output_scope_key


@pytest.mark.django_db
def test_create_pipeline_run_scopes_active_runs_by_program():
    """Different programs can run concurrently for the same fiscal year."""
    creator = PipelineRunFactory.for_pipeline_key("statistical_weights")

    tanf_run = creator.create(
        parameters={"fiscal_year": 2026, "program": DataFile.ProgramType.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    ssp_run = creator.create(
        parameters={"fiscal_year": 2026, "program": DataFile.ProgramType.SSP},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )

    assert tanf_run.output_scope_key != ssp_run.output_scope_key
    assert tanf_run.output_scope["program"] == DataFile.ProgramType.TANF
    assert ssp_run.output_scope["program"] == DataFile.ProgramType.SSP


@pytest.mark.django_db
def test_run_pipeline_node_task_resolves_registered_node():
    """The Celery task resolves a node and delegates execution to the node."""
    calls = []

    def handler(context):
        calls.append(context.parameters["fiscal_year"])
        return NodeResult(output_row_count=1)

    definition = _definition([_node("extract", handler)])
    parameters = {"fiscal_year": 2026}
    scope = definition.output_scope(parameters)
    pipeline_run = ETLPipelineRun.objects.create(
        pipeline_key=definition.key,
        pipeline_version=definition.version,
        status=ETLPipelineRun.Status.RUNNING,
        parameters=parameters,
        output_scope=scope,
        output_scope_key=output_scope_key(scope),
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    ETLNodeRun.objects.create(pipeline_run=pipeline_run, node_key="extract")

    with patch("tdpservice.etl.tasks.get_pipeline_definition", return_value=definition):
        result = run_pipeline_node(pipeline_run.id, "extract")

    assert result == {
        "node_key": "extract",
        "status": ETLNodeRun.Status.SUCCEEDED,
    }
    assert calls == [2026]


@pytest.mark.django_db
def test_run_pipeline_node_ignores_already_succeeded_node():
    """Duplicate task delivery does not run a node handler twice."""
    calls = []

    def handler(context):
        calls.append(context.parameters["fiscal_year"])
        return NodeResult(output_row_count=1)

    definition = _definition([_node("extract", handler)])
    parameters = {"fiscal_year": 2026}
    scope = definition.output_scope(parameters)
    pipeline_run = ETLPipelineRun.objects.create(
        pipeline_key=definition.key,
        pipeline_version=definition.version,
        status=ETLPipelineRun.Status.RUNNING,
        parameters=parameters,
        output_scope=scope,
        output_scope_key=output_scope_key(scope),
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    ETLNodeRun.objects.create(pipeline_run=pipeline_run, node_key="extract")

    first_result = definition.nodes["extract"].run(pipeline_run)
    second_result = definition.nodes["extract"].run(pipeline_run)

    assert first_result == {
        "node_key": "extract",
        "status": ETLNodeRun.Status.SUCCEEDED,
    }
    assert second_result == {
        "node_key": "extract",
        "status": ETLNodeRun.Status.SUCCEEDED,
        "already_started": True,
    }
    assert calls == [2026]


@pytest.mark.django_db
def test_run_pipeline_node_fails_missing_input_contracts():
    """Nodes fail before their handlers when declared artifact inputs are missing."""
    pipeline_run = _create_pipeline_run()
    pipeline_run.node_runs.filter(
        node_key__in=[
            "validate_run_sources",
            "extract_active_family_counts",
            "extract_aggregate_case_counts",
            "extract_stratum_case_counts",
        ]
    ).update(status=ETLNodeRun.Status.SUCCEEDED)

    with pytest.raises(PipelineValidationError):
        get_pipeline_definition("statistical_weights").nodes.run_weights_qa.run(
            pipeline_run
        )

    node_run = pipeline_run.node_runs.get(node_key="run_weights_qa")
    pipeline_run.refresh_from_db()
    assert node_run.status == ETLNodeRun.Status.FAILED
    assert "Missing input contracts" in node_run.error_message
    assert pipeline_run.status == ETLPipelineRun.Status.FAILED


@pytest.mark.django_db
def test_run_pipeline_node_accepts_present_artifact_contract():
    """A declared artifact manifest satisfies a node input contract."""
    calls = []

    def handler(context):
        calls.append(sorted(context.artifacts))
        return NodeResult(output_row_count=1)

    definition = _definition(
        [_node("consume", handler, input_contracts=("artifact.input",))],
    )
    parameters = {"fiscal_year": 2026}
    scope = definition.output_scope(parameters)
    pipeline_run = ETLPipelineRun.objects.create(
        pipeline_key=definition.key,
        pipeline_version=definition.version,
        status=ETLPipelineRun.Status.RUNNING,
        parameters=parameters,
        output_scope=scope,
        output_scope_key=output_scope_key(scope),
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    ETLNodeRun.objects.create(pipeline_run=pipeline_run, node_key="consume")
    ETLArtifact.objects.create(
        pipeline_run=pipeline_run,
        key="artifact.input",
        artifact_kind=ETLArtifact.ArtifactKind.DATASET,
        storage_kind=ETLArtifact.StorageKind.POSTGRES_TABLE,
        reference="example_table",
        schema_key="example.input",
        row_count=1,
    )

    result = definition.nodes["consume"].run(pipeline_run)

    assert result == {
        "node_key": "consume",
        "status": ETLNodeRun.Status.SUCCEEDED,
    }
    assert calls == [["artifact.input"]]
