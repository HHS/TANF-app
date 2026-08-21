"""Integration tests for the statistical weights ETL pipeline."""

import csv
import lzma
from decimal import Decimal
from pathlib import Path

import pytest

from tdpservice.data_files.models import DataFile
from tdpservice.etl.models import ETLPipelineRun, StatisticalWeight

FISCAL_YEAR = 2024
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
EXPECTED_OUTPUT = DATA_DIR / "expected_outputs" / "sorted_weights_2024.csv.xz"
WEIGHT_QUANTIZER = Decimal("0.0001")


@pytest.mark.etl_integration
@pytest.mark.django_db(transaction=True)
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
                "program": DataFile.ProgramType.TANF,
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
