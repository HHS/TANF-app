"""Code-owned ETL pipeline registry."""
from tdpservice.etl.pipelines.base import PipelineDefinition
from tdpservice.etl.pipelines.statistical_weights import StatisticalWeightsPipeline

PIPELINE_REGISTRY = {
    "statistical_weights": StatisticalWeightsPipeline,
}


def list_pipeline_definitions() -> list[PipelineDefinition]:
    """Return all approved pipeline definitions."""
    return [factory() for factory in PIPELINE_REGISTRY.values()]


def get_pipeline_definition(pipeline_key: str) -> PipelineDefinition:
    """Return one approved pipeline definition."""
    try:
        return PIPELINE_REGISTRY[pipeline_key]()
    except KeyError as exc:
        raise KeyError(f"Unknown ETL pipeline: {pipeline_key}") from exc
