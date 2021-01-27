"""Test report serializers."""

import pytest
from ..serializers import ReportFileSerializer

def test_serializer_with_valid_date(report_data):
    """If a serializer has valid data it will return a valid object."""
    serializer = ReportFileSerializer(data=report_data)
    assert serializer.is_valid() is True

def test_serializer_increment_create(report_data):
    """Test serializer produces reports with correct version"""
    serializer_1 = ReportFileSerializer(data=report_data)
    assert serializer_1.is_valid() is True
    report_1 = serializer_1.save()

    serializer_2 = ReportFileSerializer(data=report_data)
    assert serializer_2.is_valid() is True
    report_2 = serializer_2.save()

    assert report_2.version == report_1.version + 1

