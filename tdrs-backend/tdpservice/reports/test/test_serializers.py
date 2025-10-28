"""Tests for ReportFileSerializer and ReportIngestSerializer."""

import pytest
from rest_framework.exceptions import ValidationError
from rest_framework.fields import ValidationError

from tdpservice.reports.serializers import (
    ReportFileSerializer,
    ReportIngestSerializer,
)


@pytest.mark.django_db
def test_report_file_serializer_valid(report_file_data, data_analyst):
    """Basic smoke test: ReportFileSerializer should validate incoming data."""
    ser = ReportFileSerializer(context={"user": data_analyst}, data=report_file_data)
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.pk is not None
    assert obj.original_filename == report_file_data["original_filename"]
    assert obj.section == "Active Case Data"

    assert str(obj.user_id) == data_analyst.id
    assert obj.stt_id == data_analyst.stt.id

    assert obj.extension == "zip"
    assert obj.file.name is not None

@pytest.mark.django_db
def test_report_file_serializer_invalid_file_type(bad_report_file_data, data_analyst):
    """Test report file serializer rejects non zip file types."""
    ser = ReportFileSerializer(context={"user": data_analyst}, data=bad_report_file_data)
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)

@pytest.mark.django_db
def test_report_ingest_serializer_valid(report_ingest_data, data_analyst):
    """Basic smoke test: ReportFileSerializer should validate incoming data."""
    ser = ReportIngestSerializer(context={"user": data_analyst}, data=report_ingest_data)
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.pk is not None
    assert obj.original_filename == report_ingest_data["original_filename"]

@pytest.mark.django_db
def test_report_ingest_serializer_invalid_file_type(bad_report_ingest_data, data_analyst):
    """Test report file serializer rejects non zip file types."""
    ser = ReportIngestSerializer(context={"user": data_analyst}, data=bad_report_ingest_data)
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)
