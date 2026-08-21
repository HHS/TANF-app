"""Tests for ETL scheduler helpers."""

from datetime import date

import pytest

from tdpservice.data_files.models import DataFile
from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.scheduler import (
    fiscal_year_for_date,
    is_first_workday,
    schedule_statistical_weights_run,
    schedule_statistical_weights_runs,
)


def test_fiscal_year_for_date_uses_federal_fiscal_year():
    """October starts the next federal fiscal year."""
    assert fiscal_year_for_date(date(2026, 9, 30)) == 2026
    assert fiscal_year_for_date(date(2026, 10, 1)) == 2027


def test_is_first_workday_skips_weekends_and_later_weekdays():
    """Only the first Monday-Friday date in a month is due."""
    assert is_first_workday(date(2026, 6, 1))
    assert not is_first_workday(date(2026, 6, 2))
    assert not is_first_workday(date(2026, 8, 1))
    assert is_first_workday(date(2026, 8, 3))


@pytest.mark.django_db
def test_schedule_statistical_weights_run_is_idempotent_for_month():
    """The scheduler creates at most one successful monthly run for a scope."""
    pipeline_run = schedule_statistical_weights_run(date(2026, 6, 1))

    assert pipeline_run is not None
    assert pipeline_run.pipeline_key == "statistical_weights"
    assert pipeline_run.trigger_source == ETLPipelineRun.TriggerSource.SCHEDULED
    assert pipeline_run.parameters == {
        "fiscal_year": 2026,
        "program": DataFile.ProgramType.TANF,
    }
    assert pipeline_run.node_runs.count() == 7

    assert schedule_statistical_weights_run(date(2026, 6, 1)) is None


@pytest.mark.django_db
def test_schedule_statistical_weights_runs_creates_one_run_per_program():
    """The monthly scheduler creates separate scoped runs for each program."""
    pipeline_runs = schedule_statistical_weights_runs(date(2026, 6, 1))

    assert [run.parameters["program"] for run in pipeline_runs] == [
        DataFile.ProgramType.TANF,
        DataFile.ProgramType.SSP,
        DataFile.ProgramType.TRIBAL,
    ]
    assert {run.output_scope["program"] for run in pipeline_runs} == {
        DataFile.ProgramType.TANF,
        DataFile.ProgramType.SSP,
        DataFile.ProgramType.TRIBAL,
    }

    assert schedule_statistical_weights_runs(date(2026, 6, 1)) == []
