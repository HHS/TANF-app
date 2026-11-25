"""Integration tests for the statistical weights ETL pipeline.

Eager Canvas tasks share Django's connection, so per-test rollback isolates
synthetic inputs while preserving migrated reference rows in the task-owned DB.
"""

import csv
import lzma
from datetime import datetime
from datetime import timezone as datetime_timezone
from decimal import Decimal
from pathlib import Path

from django.utils import timezone

import pytest

from tdpservice.data_files.models import Program
from tdpservice.etl.models import ETLPipelineRun, StatisticalWeight
from tdpservice.etl.pipelines.sources import SOURCE_DATAFILE_IDS_KEY
from tdpservice.etl.tasks import schedule_statistical_weights
from tdpservice.etl.test.weights_fixtures import mixed_status_weights_data

FISCAL_YEAR = 2024
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
EXPECTED_OUTPUT = DATA_DIR / "expected_outputs" / "sorted_weights_2024.csv.xz"
WEIGHT_QUANTIZER = Decimal("0.0001")


@pytest.mark.etl_integration
@pytest.mark.django_db
def test_tanf_statistical_weights_pipeline_matches_expected_output(
    api_client,
    ofa_system_admin,
):
    """Load fixture inputs, run TANF FY2024 weights, and verify table output."""
    from django.core.management import call_command

    call_command(
        "load_statistical_weights_test_data",
        data_dir=str(DATA_DIR),
        fiscal_year=FISCAL_YEAR,
        replace=True,
        populate_stts=True,
        verbosity=0,
    )

    api_client.force_authenticate(user=ofa_system_admin)
    response = api_client.post(
        "/v1/etl/runs/",
        {
            "pipeline_key": "statistical_weights",
            "parameters": {
                "fiscal_year": FISCAL_YEAR,
                "program": Program.Code.TANF,
            },
        },
        format="json",
    )

    assert response.status_code == 201
    pipeline_run = ETLPipelineRun.objects.get(id=response.data["id"])
    assert pipeline_run.status == ETLPipelineRun.Status.SUCCEEDED
    assert pipeline_run.final_output is not None
    assert pipeline_run.final_output.key == "statistical_weights"
    assert pipeline_run.final_output.published

    expected_rows = _expected_weight_rows()
    actual_rows = _published_weight_rows(pipeline_run)

    assert pipeline_run.final_output.row_count == len(expected_rows)
    assert actual_rows == expected_rows


@pytest.mark.etl_integration
@pytest.mark.django_db
@pytest.mark.parametrize(
    "program", [Program.Code.TANF, Program.Code.SSP, Program.Code.TRIBAL]
)
def test_statistical_weights_mixed_status_publication(
    api_client, ofa_system_admin, stt, program
):
    """The API publishes only newest eligible rows across every source family."""
    expected_ids = mixed_status_weights_data(stt, ofa_system_admin, program)
    api_client.force_authenticate(user=ofa_system_admin)
    response = api_client.post(
        "/v1/etl/runs/",
        {
            "pipeline_key": "statistical_weights",
            "parameters": {"fiscal_year": 2026, "program": program},
        },
        format="json",
    )

    assert response.status_code == 201
    pipeline_run = ETLPipelineRun.objects.get(id=response.data["id"])
    assert pipeline_run.status == ETLPipelineRun.Status.SUCCEEDED
    assert pipeline_run.metadata[SOURCE_DATAFILE_IDS_KEY] == expected_ids
    assert pipeline_run.final_output.published
    assert pipeline_run.final_output.row_count == 2
    assert _published_weight_rows(pipeline_run) == [
        ("55", 202510, "1", 2, 8, Decimal("4.0000")),
        ("55", 202510, "2", 1, 12, Decimal("12.0000")),
    ]
    assert set(
        StatisticalWeight.objects.filter(pipeline_run=pipeline_run).values_list(
            "program", flat=True
        )
    ) == {program}


@pytest.mark.etl_integration
@pytest.mark.django_db
@pytest.mark.parametrize(
    "today",
    [
        datetime(2026, 10, 1, 13, tzinfo=datetime_timezone.utc),
        datetime(2027, 1, 1, 13, tzinfo=datetime_timezone.utc),
    ],
)
def test_statistical_weights_scheduled_reporting_year_mixed_status(
    stt, ofa_system_admin, monkeypatch, today
):
    """Scheduled reporting-year runs publish eligible rows and suppress repeats."""
    programs = (Program.Code.TANF, Program.Code.SSP, Program.Code.TRIBAL)
    expected_ids = {
        program: mixed_status_weights_data(stt, ofa_system_admin, program)
        for program in programs
    }
    monkeypatch.setattr(timezone, "now", lambda: today)

    with timezone.override("UTC"):
        result = schedule_statistical_weights()
        assert result["created"] is True
        assert len(result["pipeline_run_ids"]) == 3
        runs = ETLPipelineRun.objects.filter(id__in=result["pipeline_run_ids"])
        assert {run.parameters["program"] for run in runs} == set(programs)
        for run in runs:
            program = run.parameters["program"]
            assert run.status == ETLPipelineRun.Status.SUCCEEDED
            assert run.parameters["fiscal_year"] == 2026
            assert run.output_scope["fiscal_year"] == 2026
            assert run.trigger_source == ETLPipelineRun.TriggerSource.SCHEDULED
            assert run.created_at == today
            assert run.metadata[SOURCE_DATAFILE_IDS_KEY] == expected_ids[program]
            assert run.final_output.published
            assert run.final_output.row_count == 2
            assert _published_weight_rows(run) == [
                ("55", 202510, "1", 2, 8, Decimal("4.0000")),
                ("55", 202510, "2", 1, 12, Decimal("12.0000")),
            ]

        assert schedule_statistical_weights() == {"created": False}
        assert ETLPipelineRun.objects.count() == 3
        assert StatisticalWeight.objects.count() == 6


def _expected_weight_rows() -> list[tuple]:
    """Return normalized rows from the compressed expected output CSV."""
    with lzma.open(EXPECTED_OUTPUT, mode="rt", newline="", encoding="utf-8") as file:
        return sorted(_expected_weight_row(row) for row in csv.reader(file))


def _expected_weight_row(row: list[str]) -> tuple:
    """Return one normalized expected statistical weight row."""
    stt_code, reporting_month, stratum, case_count, cases, weight = row
    return (
        stt_code,
        int(reporting_month),
        stratum,
        int(case_count),
        int(cases),
        Decimal(weight).quantize(WEIGHT_QUANTIZER),
    )


def _published_weight_rows(pipeline_run: ETLPipelineRun) -> list[tuple]:
    """Return normalized published table rows for one pipeline run."""
    rows = StatisticalWeight.objects.filter(pipeline_run=pipeline_run).values_list(
        "stt_code",
        "reporting_month",
        "stratum",
        "case_count",
        "cases",
        "weight",
    )
    return sorted(
        (
            stt_code,
            reporting_month,
            stratum,
            case_count,
            cases,
            weight.quantize(WEIGHT_QUANTIZER),
        )
        for stt_code, reporting_month, stratum, case_count, cases, weight in rows
    )
