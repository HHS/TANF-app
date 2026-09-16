"""Tests for ReportFileSerializer and ReportSourceSerializer."""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from django.utils.dateparse import parse_datetime

import pytest
from rest_framework.exceptions import ValidationError

from tdpservice.reports.models import ReportType
from tdpservice.reports.serializers import (
    ReportFileSerializer,
    ReportSourceDownloadStatisticsSerializer,
    ReportSourceSerializer,
)


@pytest.mark.django_db
def test_report_file_serializer_valid(report_file_data, data_analyst):
    """Basic smoke test: ReportFileSerializer should validate incoming data."""
    ser = ReportFileSerializer(context={"user": data_analyst}, data=report_file_data)
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.pk is not None
    assert obj.original_filename == report_file_data["original_filename"]

    assert str(obj.user_id) == data_analyst.id
    assert obj.stt_id == data_analyst.stt.id

    assert obj.extension == "zip"
    assert obj.file.name is not None


@pytest.mark.django_db
def test_report_file_serializer_invalid_file_type(bad_report_file_data, data_analyst):
    """Test report file serializer rejects non zip file types."""
    ser = ReportFileSerializer(
        context={"user": data_analyst}, data=bad_report_file_data
    )
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_report_source_serializer_valid(report_source_data, data_analyst):
    """Basic smoke test: ReportSourceSerializer should validate incoming data."""
    ser = ReportSourceSerializer(
        context={"user": data_analyst}, data=report_source_data
    )
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.pk is not None
    assert obj.original_filename == report_source_data["original_filename"]


@pytest.mark.django_db
def test_report_source_serializer_invalid_file_type(
    bad_report_source_data, data_analyst
):
    """Test report source serializer rejects non zip file types."""
    ser = ReportSourceSerializer(
        context={"user": data_analyst}, data=bad_report_source_data
    )
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)


@pytest.mark.django_db
def test_report_file_serializer_includes_report_type(report_file_data, data_analyst):
    """report_type should appear in serialized output and default to TANF_SSP."""
    ser = ReportFileSerializer(context={"user": data_analyst}, data=report_file_data)
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.report_type == ReportType.TANF_SSP

    # Verify it's in the serialized representation
    output = ReportFileSerializer(obj).data
    assert "report_type" in output
    assert output["report_type"] == "TANF_SSP"


@pytest.mark.django_db
def test_report_file_serializer_includes_downloaded_at(report_file_instance):
    """Report file responses include the first download timestamp."""
    downloaded_at = timezone.now().replace(microsecond=0)
    report_file_instance.downloaded_at = downloaded_at
    report_file_instance.save(update_fields=["downloaded_at"])

    output = ReportFileSerializer(report_file_instance).data

    assert parse_datetime(output["downloaded_at"]) == downloaded_at


@pytest.mark.django_db
def test_report_file_serializer_with_fra_report_type(report_file_data, data_analyst):
    """Test ReportFileSerializer accepts FRA report_type."""
    report_file_data["report_type"] = "FRA"
    ser = ReportFileSerializer(context={"user": data_analyst}, data=report_file_data)
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.report_type == ReportType.FRA


@pytest.mark.django_db
def test_report_file_serializer_with_tribal_tanf_report_type(
    report_file_data, data_analyst
):
    """Test ReportFileSerializer accepts TRIBAL_TANF report_type."""
    report_file_data["report_type"] = "TRIBAL_TANF"
    ser = ReportFileSerializer(context={"user": data_analyst}, data=report_file_data)
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.report_type == ReportType.TRIBAL_TANF


@pytest.mark.django_db
def test_report_source_serializer_includes_report_type(
    report_source_data, data_analyst
):
    """report_type should appear in serialized output and default to TANF_SSP."""
    ser = ReportSourceSerializer(
        context={"user": data_analyst}, data=report_source_data
    )
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.report_type == ReportType.TANF_SSP


@pytest.mark.django_db
def test_report_source_serializer_with_fra_report_type(
    report_source_data, data_analyst
):
    """Test ReportSourceSerializer accepts FRA report_type."""
    report_source_data["report_type"] = "FRA"
    ser = ReportSourceSerializer(
        context={"user": data_analyst}, data=report_source_data
    )
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.report_type == ReportType.FRA


@pytest.mark.django_db
def test_report_source_serializer_with_tribal_tanf_report_type(
    report_source_data, data_analyst
):
    """Test ReportSourceSerializer accepts TRIBAL_TANF report_type."""
    report_source_data["report_type"] = "TRIBAL_TANF"
    ser = ReportSourceSerializer(
        context={"user": data_analyst}, data=report_source_data
    )
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.report_type == ReportType.TRIBAL_TANF


@pytest.mark.django_db
def test_report_source_serializer_includes_annotated_download_counts(
    report_source_statistics,
):
    """Summary counts are serialized without additional database queries."""
    source = report_source_statistics["source"]
    source.downloaded_count = 2
    source.total_count = 4

    with CaptureQueriesContext(connection) as captured_queries:
        output = ReportSourceSerializer(source).data

    assert output["downloaded_count"] == 2
    assert output["total_count"] == 4
    assert len(captured_queries) == 0


def test_report_source_download_statistics_serializer_contract():
    """The detail contract contains only source, counts, and grouped STTs."""
    data = {
        "report_source_id": 12,
        "downloaded_count": 1,
        "total_count": 2,
        "regions": [
            {
                "id": 4,
                "stts": [
                    {"id": 1, "name": "Alabama", "downloaded_at": None},
                ],
            }
        ],
    }

    output = ReportSourceDownloadStatisticsSerializer(data).data

    assert output == data
    assert "file" not in output
