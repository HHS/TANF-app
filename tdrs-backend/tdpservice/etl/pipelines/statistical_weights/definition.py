"""Pipeline definition for statistical weights."""

from typing import Any

from celery import chain, chord

from tdpservice.data_files.models import DataFile
from tdpservice.etl.exceptions import PipelineValidationError
from tdpservice.etl.pipelines.base import PipelineDefinition, PipelineNodeRegistry
from tdpservice.etl.pipelines.sources import DataFileSourceSnapshot
from tdpservice.etl.pipelines.statistical_weights.candidates import (
    WeightCandidateBuilder,
)
from tdpservice.etl.pipelines.statistical_weights.nodes import (
    ExtractActiveFamilyCountsNode,
    ExtractAggregateCaseCountsNode,
    ExtractStratumCaseCountsNode,
    NotifyWeightsRunNode,
    PublishWeightsNode,
    RunWeightsQANode,
    StatisticalWeightsArtifactStore,
    StatisticalWeightsNodeResources,
    ValidateRunSourcesNode,
)
from tdpservice.etl.pipelines.statistical_weights.publishing import (
    StatisticalWeightsPublisher,
)
from tdpservice.etl.pipelines.statistical_weights.qa import StatisticalWeightsQA


class StatisticalWeightsPipeline(PipelineDefinition):
    """Pipeline definition for Section 1 statistical weights."""

    key = "statistical_weights"
    version = "1"
    display_name = "Statistical Weights"
    description = (
        "Generate Section 1 statistical weights for a fiscal year and program."
    )
    schedule = {"first_workday_monthly": True}

    # TODO: Alex indicated this pipeline executes for section 1 and 2. But I don't see the scripts for it. Hard coded
    # to section 1 for now.
    section = "1"
    source_keys = {
        "active": "active",
        "aggregate": "aggregate",
        "stratum": "stratum",
    }
    intermediate_keys = {
        "s1": "weights.s1",
        "s3": "weights.s3",
        "s4": "weights.s4",
    }
    output_key = "statistical_weights"
    supported_program_types = (
        DataFile.ProgramType.TANF,
        DataFile.ProgramType.SSP,
        DataFile.ProgramType.TRIBAL,
    )
    allowed_parameters = {
        "fiscal_year": {
            "type": "integer",
            "required": True,
            "description": "Fiscal year to generate weights for.",
        },
        "program": {
            "type": "string",
            "required": True,
            "description": "DataFile program type to generate weights for.",
            "choices": list(supported_program_types),
        },
    }

    def __init__(self):
        """Initialize this pipeline's executable node declarations."""
        self.datafile_snapshot = DataFileSourceSnapshot()
        self.candidates = WeightCandidateBuilder(section=self.section)
        self.qa = StatisticalWeightsQA()
        self.publisher = StatisticalWeightsPublisher(
            section=self.section,
            output_key=self.output_key,
        )
        self.artifacts = StatisticalWeightsArtifactStore(
            intermediate_keys=self.intermediate_keys,
        )
        self.node_resources = StatisticalWeightsNodeResources(
            source_keys=self.source_keys,
            section=self.section,
            datafile_snapshot=self.datafile_snapshot,
            candidates=self.candidates,
            qa=self.qa,
            publisher=self.publisher,
            artifacts=self.artifacts,
        )
        self.nodes = self._pipeline_nodes()

    def validate_parameters(self, parameters: dict) -> dict:
        """Validate statistical weights run parameters."""
        validated = dict(parameters or {})
        unexpected = set(validated) - set(self.allowed_parameters)
        if unexpected:
            raise PipelineValidationError(
                f"Unexpected parameters: {sorted(unexpected)}"
            )

        for name, metadata in self.allowed_parameters.items():
            if metadata.get("required") and name not in validated:
                raise PipelineValidationError(f"Missing required parameter: {name}")

        validated["fiscal_year"] = self._normalize_fiscal_year(validated["fiscal_year"])
        validated["program"] = self._validate_program_type(validated["program"])
        return validated

    def output_scope(self, parameters: dict) -> dict:
        """Build the idempotency/output scope for statistical weights."""
        return {
            "pipeline": self.key,
            "fiscal_year": int(parameters["fiscal_year"]),
            "program": self._validate_program_type(parameters["program"]),
            "section": self.section,
        }

    def build_canvas(self, pipeline_run_id: int) -> Any:
        """Build the Celery Canvas for the statistical weights DAG."""
        from tdpservice.etl.tasks import finalize_pipeline_run

        nodes = self.nodes
        run_weights_qa_signature = nodes.run_weights_qa.task(pipeline_run_id)
        finalize = chain(
            nodes.publish_weights.task(pipeline_run_id),
            nodes.notify_weights_run.task(pipeline_run_id),
            finalize_pipeline_run.si(pipeline_run_id),
        )
        finalize.set(immutable=True)
        run_weights_qa_signature.link(finalize)

        return chain(
            nodes.validate_run_sources.task(pipeline_run_id),
            chord(
                [
                    nodes.extract_active_family_counts.task(pipeline_run_id),
                    nodes.extract_aggregate_case_counts.task(pipeline_run_id),
                    nodes.extract_stratum_case_counts.task(pipeline_run_id),
                ],
                run_weights_qa_signature,
            ),
        )

    def _pipeline_nodes(self) -> PipelineNodeRegistry:
        """Return ETLNodeRun-backed node declarations for this pipeline."""
        resources = self.node_resources
        return PipelineNodeRegistry(
            (
                ValidateRunSourcesNode(resources),
                ExtractActiveFamilyCountsNode(
                    resources,
                    output_contracts=(self.intermediate_keys["s1"],),
                ),
                ExtractAggregateCaseCountsNode(
                    resources,
                    output_contracts=(self.intermediate_keys["s3"],),
                ),
                ExtractStratumCaseCountsNode(
                    resources,
                    output_contracts=(self.intermediate_keys["s4"],),
                ),
                RunWeightsQANode(
                    resources,
                    input_contracts=(
                        self.intermediate_keys["s1"],
                        self.intermediate_keys["s3"],
                        self.intermediate_keys["s4"],
                    ),
                ),
                PublishWeightsNode(
                    resources,
                    input_contracts=(
                        self.intermediate_keys["s1"],
                        self.intermediate_keys["s3"],
                        self.intermediate_keys["s4"],
                    ),
                    output_contracts=(self.output_key,),
                ),
                NotifyWeightsRunNode(
                    resources,
                    input_contracts=(self.output_key,),
                ),
            )
        )

    @staticmethod
    def _normalize_fiscal_year(value) -> int:
        """Normalize and validate fiscal year."""
        try:
            fiscal_year = int(value)
        except (TypeError, ValueError) as exc:
            raise PipelineValidationError("fiscal_year must be an integer.") from exc

        if fiscal_year < 2000:
            raise PipelineValidationError("fiscal_year must be 2000 or later.")
        return fiscal_year

    @classmethod
    def _validate_program_type(cls, value) -> str:
        """Validate that program is an exact DataFile.ProgramType value."""
        if value not in cls.supported_program_types:
            choices = ", ".join(cls.supported_program_types)
            raise PipelineValidationError(f"program must be one of: {choices}.")
        return value
