"""Tests for ReportFileSerializer and ReportSourceSerializer."""

import pytest
from rest_framework.exceptions import ValidationError

from tdpservice.reports.serializers import (
    ReportFileSerializer,
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
    ser = ReportFileSerializer(context={"user": data_analyst}, data=bad_report_file_data)
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)

@pytest.mark.django_db
def test_report_source_serializer_valid(report_source_data, data_analyst):
    """Basic smoke test: ReportSourceSerializer should validate incoming data."""
    ser = ReportSourceSerializer(context={"user": data_analyst}, data=report_source_data)
    assert ser.is_valid(), ser.errors
    obj = ser.save()

    assert obj.pk is not None
    assert obj.original_filename == report_source_data["original_filename"]

@pytest.mark.django_db
def test_report_source_serializer_invalid_file_type(bad_report_source_data, data_analyst):
    """Test report source serializer rejects non zip file types."""
    ser = ReportSourceSerializer(context={"user": data_analyst}, data=bad_report_source_data)
    with pytest.raises(ValidationError):
        ser.is_valid(raise_exception=True)
