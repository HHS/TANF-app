"""Tests for loading de-identified statistical weights CSV fixtures."""

import gzip
import lzma
import shutil
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import CommandError

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile, Program, Section
from tdpservice.data_files.test.factories import DataFileFactory
from tdpservice.etl.pipelines.statistical_weights import StatisticalWeightsPipeline
from tdpservice.parsers.models import DataFileSummary
from tdpservice.search_indexes.models.tanf import TANF_T1, TANF_T6, TANF_T7

PIPELINE = StatisticalWeightsPipeline()


def _write_weights_csvs(data_dir: Path, reporting_months=None):
    """Create small TANF T1/T6/T7 CSVs shaped like the DataSurge extracts."""
    if reporting_months is None:
        reporting_months = ["202310", "202401"]

    t1_rows = [
        f"55,{reporting_months[0]},CASE000001,01,100.0",
        f"55,{reporting_months[1]},CASE000002,02,200.0",
    ]
    (data_dir / "TANF_T1_fixture.csv").write_text(
        "FIPS_CODE,RPT_MONTH_YEAR,CASE_NUMBER,STRATUM,CASH_AMOUNT\n"
        + "\n".join(t1_rows)
        + "\n"
    )
    (data_dir / "TANF_T6_fixture.csv").write_text(
        "FIPS_CODE,RPT_MONTH_YEAR,NUM_FAMILIES\n55,202310,9\n"
    )
    (data_dir / "TANF_T7_fixture.csv").write_text(
        "FIPS_CODE,RPT_MONTH_YEAR,TDRS_SECTION_IND,STRATUM,FAMILIES_MONTH\n"
        "55,202310,1,01,7\n"
    )


def _compress_csvs(data_dir: Path, extension: str):
    """Compress fixture CSVs with a stdlib-supported format."""
    openers = {".gz": gzip.open, ".xz": lzma.open}
    for csv_path in data_dir.glob("TANF_T*_fixture.csv"):
        compressed_path = csv_path.with_suffix(f"{csv_path.suffix}{extension}")
        with csv_path.open("rb") as source:
            with openers[extension](compressed_path, "wb") as target:
                shutil.copyfileobj(source, target)
        csv_path.unlink()


@pytest.mark.django_db
def test_load_statistical_weights_test_data_creates_datafiles_and_rows(tmp_path, stt):
    """The importer creates synthetic DataFiles and parsed rows for the ETL."""
    _write_weights_csvs(tmp_path)

    call_command(
        "load_statistical_weights_test_data",
        data_dir=str(tmp_path),
        fiscal_year=2024,
        datafile_version=9001,
        batch_size=1,
    )

    datafiles = DataFile.objects.filter(
        original_filename__startswith="etl-test-statistical-weights",
        year=2024,
        version=9001,
    )
    assert datafiles.count() == 4
    assert set(datafiles.values_list("state", flat=True)) == {
        SubmissionState.PARSE_COMPLETED
    }
    assert not datafiles.filter(section__isnull=True).exists()
    assert set(datafiles.values_list(
        "summary__status", "summary__total_number_of_records_in_file",
        "summary__total_number_of_records_created",
    )) == {(DataFileSummary.Status.ACCEPTED, 1, 1)}
    assert set(datafiles.values_list("section__program__code", flat=True)) == {
        Program.Code.TANF
    }

    t1_rows = list(TANF_T1.objects.order_by("RPT_MONTH_YEAR"))
    assert len(t1_rows) == 2
    assert t1_rows[0].line_number == 2
    assert t1_rows[0].CASH_AMOUNT == 100
    assert t1_rows[0].datafile.quarter == DataFile.Quarter.Q1
    assert t1_rows[1].datafile.quarter == DataFile.Quarter.Q2

    source_ids = PIPELINE.nodes.validate_run_sources.snapshot_source_datafile_ids(
        2024,
        Program.Code.TANF,
    )
    assert set(source_ids[PIPELINE.source_keys["active"]]) == set(
        DataFile.objects.filter(
            section__name=Section.Name.ACTIVE_CASE_DATA
        ).values_list(
            "id", flat=True
        )
    )
    assert PIPELINE.nodes.extract_active_family_counts.extract_rows(
        source_ids[PIPELINE.source_keys["active"]],
        Program.Code.TANF,
    ) == [
        {
            "stt_code": "55",
            "reporting_month": 202310,
            "stratum": "1",
            "case_count": 1,
        },
        {
            "stt_code": "55",
            "reporting_month": 202401,
            "stratum": "2",
            "case_count": 1,
        },
    ]
    assert TANF_T6.objects.count() == 1
    assert TANF_T7.objects.count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("extension", [".gz", ".xz"])
def test_load_statistical_weights_test_data_reads_compressed_csvs(
    tmp_path, stt, extension
):
    """The importer reads stdlib-compressed CSV fixtures."""
    _write_weights_csvs(tmp_path)
    _compress_csvs(tmp_path, extension)

    call_command(
        "load_statistical_weights_test_data",
        data_dir=str(tmp_path),
        fiscal_year=2024,
        datafile_version=9001,
    )

    assert TANF_T1.objects.count() == 2
    assert TANF_T6.objects.count() == 1
    assert TANF_T7.objects.count() == 1


@pytest.mark.django_db
def test_load_statistical_weights_test_data_requires_replace(tmp_path, stt):
    """The importer refuses to append duplicate synthetic fixture rows."""
    _write_weights_csvs(tmp_path)

    call_command(
        "load_statistical_weights_test_data",
        data_dir=str(tmp_path),
        fiscal_year=2024,
        datafile_version=9001,
    )

    with pytest.raises(CommandError, match="already exists"):
        call_command(
            "load_statistical_weights_test_data",
            data_dir=str(tmp_path),
            fiscal_year=2024,
            datafile_version=9001,
        )

    old_ids = set(DataFile.objects.values_list("id", flat=True))
    DataFileSummary.objects.update(status=DataFileSummary.Status.REJECTED)

    call_command(
        "load_statistical_weights_test_data",
        data_dir=str(tmp_path),
        fiscal_year=2024,
        datafile_version=9001,
        replace=True,
    )

    assert TANF_T1.objects.count() == 2
    assert TANF_T6.objects.count() == 1
    assert TANF_T7.objects.count() == 1
    assert not DataFile.objects.filter(id__in=old_ids).exists()
    assert DataFileSummary.objects.count() == 4
    assert set(DataFileSummary.objects.values_list(
        "status", "total_number_of_records_in_file", "total_number_of_records_created",
    )) == {(DataFileSummary.Status.ACCEPTED, 1, 1)}


@pytest.mark.django_db
def test_load_statistical_weights_test_data_rejects_wrong_fiscal_year(tmp_path, stt):
    """CSV rows must belong to the requested federal fiscal year."""
    _write_weights_csvs(tmp_path, reporting_months=["202410", "202411"])

    with pytest.raises(CommandError, match="belongs to FY2025"):
        call_command(
            "load_statistical_weights_test_data",
            data_dir=str(tmp_path),
            fiscal_year=2024,
            datafile_version=9001,
        )


@pytest.mark.django_db
@pytest.mark.parametrize("limit,expected_count", [(None, 2), (1, 1)])
def test_synthetic_summaries_count_only_imported_rows(tmp_path, stt, limit, expected_count):
    """Summary totals count per-file imported rows, not all CSV rows or real files."""
    _write_weights_csvs(tmp_path, reporting_months=["202310", "202311"])
    real_file = DataFileFactory(
        stt=stt, year=2024, state=SubmissionState.PARSE_COMPLETED
    )
    call_command(
        "load_statistical_weights_test_data",
        data_dir=str(tmp_path),
        fiscal_year=2024,
        limit_per_file=limit,
        batch_size=1,
    )

    summary = DataFileSummary.objects.get(
        datafile__version=9001,
        datafile__section__name=Section.Name.ACTIVE_CASE_DATA,
    )
    assert summary.status == DataFileSummary.Status.ACCEPTED
    assert summary.total_number_of_records_in_file == expected_count
    assert summary.total_number_of_records_created == expected_count
    assert TANF_T1.objects.filter(datafile=summary.datafile).count() == expected_count
    assert not DataFileSummary.objects.filter(datafile=real_file).exists()
