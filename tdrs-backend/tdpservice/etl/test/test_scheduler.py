"""Tests for ETL scheduler helpers."""

from datetime import date, datetime, time
from datetime import timezone as datetime_timezone

from django.utils import timezone

import pytest

from tdpservice.data_files.models import Program
from tdpservice.etl.models import ETLPipelineRun
from tdpservice.etl.runner import PipelineRunFactory
from tdpservice.etl.scheduler import (
    is_first_workday,
    reporting_fiscal_year_for_date,
    schedule_statistical_weights_run,
    schedule_statistical_weights_runs,
)
from tdpservice.etl.tasks import schedule_statistical_weights


@pytest.fixture
def scheduler_clock(monkeypatch):
    """Align auto-created run timestamps with the scheduler's simulated date."""
    def set_date(value: date) -> None:
        now = datetime.combine(value, time(13), tzinfo=datetime_timezone.utc)
        monkeypatch.setattr(timezone, "now", lambda: now)

    with timezone.override("UTC"):
        yield set_date


@pytest.mark.parametrize(
    "today,expected_year",
    [
        (date(2026, 9, 30), 2026),
        (date(2026, 10, 1), 2026),
        (date(2026, 12, 31), 2026),
        (date(2027, 1, 1), 2026),
        (date(2027, 1, 31), 2026),
        (date(2027, 2, 1), 2027),
        (date(2027, 2, 2), 2027),
        (date(2025, 1, 31), 2024),
        (date(2025, 2, 1), 2025),
        (date(2025, 2, 2), 2025),
        (date(2025, 2, 3), 2025),
    ],
)
def test_reporting_fiscal_year_for_date_uses_february_cutoff(today, expected_year):
    """Reporting eligibility advances February 1, including weekend cutoffs."""
    assert reporting_fiscal_year_for_date(today) == expected_year


def test_is_first_workday_skips_weekends_and_later_weekdays():
    """Only the first Monday-Friday date in a month is due."""
    assert is_first_workday(date(2026, 6, 1))
    assert not is_first_workday(date(2026, 6, 2))
    assert not is_first_workday(date(2026, 8, 1))
    assert is_first_workday(date(2026, 8, 3))


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status",
    [
        ETLPipelineRun.Status.PENDING,
        ETLPipelineRun.Status.RUNNING,
        ETLPipelineRun.Status.SUCCEEDED,
    ],
)
def test_schedule_statistical_weights_run_is_idempotent_for_month(scheduler_clock, status):
    """Active and successful scheduled runs suppress repeat checks this month."""
    today = date(2026, 6, 1)
    scheduler_clock(today)
    pipeline_run = schedule_statistical_weights_run(today)

    assert pipeline_run is not None
    assert pipeline_run.pipeline_key == "statistical_weights"
    assert pipeline_run.trigger_source == ETLPipelineRun.TriggerSource.SCHEDULED
    assert pipeline_run.parameters == {
        "fiscal_year": 2026,
        "program": Program.Code.TANF,
    }
    assert pipeline_run.node_runs.count() == 7
    assert pipeline_run.created_at.date() == today
    pipeline_run.status = status
    pipeline_run.save(update_fields=["status"])

    assert schedule_statistical_weights_run(today) is None
    assert ETLPipelineRun.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize(
    "today,expected_year",
    [
        (date(2026, 9, 1), 2026),
        (date(2026, 10, 1), 2026),
        (date(2027, 1, 1), 2026),
        (date(2027, 2, 1), 2027),
        (date(2025, 2, 3), 2025),
    ],
)
def test_schedule_statistical_weights_runs_creates_one_run_per_program(
    scheduler_clock, today, expected_year
):
    """The monthly scheduler creates separate scoped runs for each program."""
    scheduler_clock(today)
    pipeline_runs = schedule_statistical_weights_runs(today)

    assert [run.parameters["program"] for run in pipeline_runs] == [
        Program.Code.TANF,
        Program.Code.SSP,
        Program.Code.TRIBAL,
    ]
    assert {run.output_scope["program"] for run in pipeline_runs} == {
        Program.Code.TANF,
        Program.Code.SSP,
        Program.Code.TRIBAL,
    }

    for run in pipeline_runs:
        assert run.parameters == {
            "fiscal_year": expected_year,
            "program": run.output_scope["program"],
        }
        assert run.output_scope == {
            "pipeline": "statistical_weights",
            "fiscal_year": expected_year,
            "program": run.parameters["program"],
            "section": "1",
        }
        assert run.trigger_source == ETLPipelineRun.TriggerSource.SCHEDULED
        assert run.created_at.date() == today

    assert schedule_statistical_weights_runs(today) == []
    assert ETLPipelineRun.objects.count() == 3


@pytest.mark.django_db
def test_schedule_statistical_weights_run_allows_failed_retry(scheduler_clock):
    """A failed scheduled run does not consume the monthly successful-run slot."""
    today = date(2026, 10, 1)
    scheduler_clock(today)
    failed_run = schedule_statistical_weights_run(today)
    failed_run.status = ETLPipelineRun.Status.FAILED
    failed_run.save(update_fields=["status"])

    retry = schedule_statistical_weights_run(today)

    assert retry is not None
    assert retry.id != failed_run.id
    assert retry.output_scope == failed_run.output_scope
    assert ETLPipelineRun.objects.count() == 2


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status", [ETLPipelineRun.Status.PENDING, ETLPipelineRun.Status.RUNNING]
)
@pytest.mark.parametrize(
    "trigger", [ETLPipelineRun.TriggerSource.ADMIN, ETLPipelineRun.TriggerSource.SCHEDULED]
)
def test_schedule_statistical_weights_run_skips_active_scope_from_prior_month(
    scheduler_clock, status, trigger
):
    """Active scope conflicts still prevent runs outside monthly suppression."""
    scheduler_clock(date(2026, 9, 1))
    active_run = PipelineRunFactory.for_pipeline_key("statistical_weights").create(
        parameters={"fiscal_year": 2026, "program": Program.Code.TANF},
        trigger_source=trigger,
    )
    active_run.status = status
    active_run.save(update_fields=["status"])
    scheduler_clock(date(2026, 10, 1))

    assert schedule_statistical_weights_run(date(2026, 10, 1)) is None
    assert ETLPipelineRun.objects.count() == 1


@pytest.mark.django_db
def test_schedule_statistical_weights_runs_are_independent_across_months(scheduler_clock):
    """Successful prior-month runs do not suppress the same reporting-year scope."""
    scheduler_clock(date(2026, 9, 1))
    september_runs = schedule_statistical_weights_runs(date(2026, 9, 1))
    ETLPipelineRun.objects.update(status=ETLPipelineRun.Status.SUCCEEDED)
    scheduler_clock(date(2026, 10, 1))

    october_runs = schedule_statistical_weights_runs(date(2026, 10, 1))

    assert len(october_runs) == 3
    assert [run.output_scope for run in october_runs] == [
        run.output_scope for run in september_runs
    ]
    assert ETLPipelineRun.objects.count() == 6


@pytest.mark.django_db
def test_completed_manual_run_does_not_suppress_scheduled_run(scheduler_clock):
    """Monthly suppression is limited to SCHEDULED runs, not manual history."""
    today = date(2026, 10, 1)
    scheduler_clock(today)
    manual_run = PipelineRunFactory.for_pipeline_key("statistical_weights").create(
        parameters={"fiscal_year": 2026, "program": Program.Code.TANF},
        trigger_source=ETLPipelineRun.TriggerSource.ADMIN,
    )
    manual_run.status = ETLPipelineRun.Status.SUCCEEDED
    manual_run.save(update_fields=["status"])

    scheduled_run = schedule_statistical_weights_run(today)

    assert scheduled_run is not None
    assert scheduled_run.output_scope == manual_run.output_scope
    assert ETLPipelineRun.objects.count() == 2


@pytest.mark.django_db
@pytest.mark.parametrize(
    "today",
    [date(2026, 6, 2), date(2026, 8, 1), date(2026, 8, 2), date(2025, 2, 1), date(2025, 2, 2)],
)
def test_scheduler_does_not_create_runs_on_non_first_workdays(scheduler_clock, today):
    """Neither a weekend cutoff nor a later weekday adds a scheduled run."""
    scheduler_clock(today)

    assert schedule_statistical_weights_runs(today) == []
    assert not ETLPipelineRun.objects.exists()


@pytest.mark.django_db
@pytest.mark.parametrize("utc_hour,expected_count", [(0, 0), (13, 3)])
def test_scheduler_defaults_to_current_local_date(monkeypatch, utc_hour, expected_count):
    """Default dates use the active timezone, not the UTC calendar date."""
    now = datetime(2027, 2, 1, utc_hour, 30, tzinfo=datetime_timezone.utc)
    monkeypatch.setattr(timezone, "now", lambda: now)
    with timezone.override("America/New_York"):
        runs = schedule_statistical_weights_runs()

    assert len(runs) == expected_count
    assert all(run.parameters["fiscal_year"] == 2027 for run in runs)
    assert ETLPipelineRun.objects.count() == expected_count


@pytest.mark.django_db
def test_scheduled_task_dispatches_reporting_year_runs(scheduler_clock, mocker):
    """The daily Celery task launches each program's reporting-year run once."""
    scheduler_clock(date(2026, 10, 1))
    launch = mocker.patch("tdpservice.etl.tasks.launch_pipeline_run.delay")

    result = schedule_statistical_weights()

    runs = list(ETLPipelineRun.objects.order_by("id"))
    assert result == {"created": True, "pipeline_run_ids": [run.id for run in runs]}
    assert [run.parameters for run in runs] == [
        {"fiscal_year": 2026, "program": program}
        for program in (Program.Code.TANF, Program.Code.SSP, Program.Code.TRIBAL)
    ]
    assert launch.call_args_list == [mocker.call(run.id) for run in runs]
    assert schedule_statistical_weights() == {"created": False}
    assert launch.call_count == 3
