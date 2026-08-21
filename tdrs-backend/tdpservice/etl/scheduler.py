"""Scheduling helpers for ETL pipelines."""

from datetime import date

from django.utils import timezone

from tdpservice.data_files.models import DataFile
from tdpservice.etl.exceptions import ActivePipelineRunError
from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.pipelines.statistical_weights import StatisticalWeightsPipeline
from tdpservice.etl.runner import PipelineRunFactory


def fiscal_year_for_date(value: date) -> int:
    """Return the federal fiscal year for a date."""
    return value.year + 1 if value.month >= 10 else value.year


def is_first_workday(value: date) -> bool:
    """Return whether a date is the first Monday-Friday workday of its month."""
    if value.weekday() >= 5:
        return False

    prior_day = 1
    while prior_day < value.day:
        if date(value.year, value.month, prior_day).weekday() < 5:
            return False
        prior_day += 1

    return True


def schedule_statistical_weights_run(
    today: date | None = None,
    program: str = DataFile.ProgramType.TANF,
) -> ETLPipelineRun | None:
    """Create a scheduled statistical weights run when due."""
    today = today or timezone.localdate()
    if not is_first_workday(today):
        return None

    fiscal_year = fiscal_year_for_date(today)
    definition = StatisticalWeightsPipeline()
    parameters = definition.validate_parameters(
        {"fiscal_year": fiscal_year, "program": program}
    )
    output_scope = definition.output_scope(parameters)
    already_scheduled = ETLPipelineRun.objects.filter(
        pipeline_key=definition.key,
        output_scope=output_scope,
        trigger_source=ETLPipelineRun.TriggerSource.SCHEDULED,
        status__in=[
            ETLPipelineRun.Status.PENDING,
            ETLPipelineRun.Status.RUNNING,
            ETLPipelineRun.Status.SUCCEEDED,
        ],
        created_at__year=today.year,
        created_at__month=today.month,
    ).exists()
    if already_scheduled:
        return None

    try:
        return PipelineRunFactory.for_pipeline_key(definition.key).create(
            parameters=parameters,
            trigger_source=ETLPipelineRun.TriggerSource.SCHEDULED,
        )
    except ActivePipelineRunError:
        return None


def schedule_statistical_weights_runs(
    today: date | None = None,
) -> list[ETLPipelineRun]:
    """Create scheduled statistical weights runs for all supported programs."""
    scheduled_runs = []
    for program in StatisticalWeightsPipeline.supported_program_types:
        pipeline_run = schedule_statistical_weights_run(today, program)
        if pipeline_run:
            scheduled_runs.append(pipeline_run)
    return scheduled_runs
