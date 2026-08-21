"""Celery tasks for ETL pipelines."""

from celery import shared_task

from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.registry import get_pipeline_definition
from tdpservice.etl.runner import PipelineRunLauncher
from tdpservice.etl.scheduler import schedule_statistical_weights_runs


@shared_task(name="tdpservice.etl.tasks.launch_pipeline_run")
def launch_pipeline_run(pipeline_run_id: int):
    """Launch a pipeline run by queueing its execution graph."""
    result = PipelineRunLauncher.for_run_id(pipeline_run_id).launch()
    return {"pipeline_run_id": pipeline_run_id, "task_id": result.id}


@shared_task(name="tdpservice.etl.tasks.run_pipeline_node")
def run_pipeline_node(pipeline_run_id: int, node_key: str):
    """Run one ETLNodeRun-backed pipeline node."""
    pipeline_run = ETLPipelineRun.objects.get(id=pipeline_run_id)
    definition = get_pipeline_definition(pipeline_run.pipeline_key)
    definition.validate()
    return definition.nodes[node_key].run(pipeline_run)


@shared_task(name="tdpservice.etl.tasks.finalize_pipeline_run")
def finalize_pipeline_run(pipeline_run_id: int):
    """Finalize a pipeline run."""
    return PipelineRunLauncher.for_run_id(pipeline_run_id).finalize()


@shared_task(name="tdpservice.etl.tasks.schedule_statistical_weights")
def schedule_statistical_weights():
    """Run the daily scheduler check for statistical weights."""
    pipeline_runs = schedule_statistical_weights_runs()
    if not pipeline_runs:
        return {"created": False}

    for pipeline_run in pipeline_runs:
        launch_pipeline_run.delay(pipeline_run.id)

    return {
        "created": True,
        "pipeline_run_ids": [pipeline_run.id for pipeline_run in pipeline_runs],
    }


def enqueue_pipeline_run(pipeline_run: ETLPipelineRun):
    """Queue a pipeline run launcher task."""
    return launch_pipeline_run.delay(pipeline_run.id)
