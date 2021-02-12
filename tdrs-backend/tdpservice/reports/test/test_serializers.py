"""Test report serializers."""

import pytest
from ..serializers import ReportFileSerializer
from ..errors import ImmutabilityError

@pytest.mark.django_db
def test_serializer_with_valid_data(report):
    """If a serializer has valid data it will return a valid object."""
    get_serializer = ReportFileSerializer(report)
    create_serializer = ReportFileSerializer(data=get_serializer.data)
    assert create_serializer.is_valid() is True

@pytest.mark.django_db
def test_serializer_increment_create(report):
    """Test serializer produces reports with correct version."""
    get_serializer = ReportFileSerializer(report)
    serializer_1 = ReportFileSerializer(data=get_serializer.data)
    assert serializer_1.is_valid() is True
    report_1 = serializer_1.save()

    serializer_2 = ReportFileSerializer(data=get_serializer.data)
    assert serializer_2.is_valid() is True
    report_2 = serializer_2.save()

    assert report_2.version == report_1.version + 1

@pytest.mark.django_db
def test_immutability_of_report(report):
    """Test that report can only be created."""
    try:
        serializer = ReportFileSerializer(
            report, data={
                "original_filename": "BadGuy.js"
            },
            partial=True)

        serializer.is_valid()
        serializer.save()
        raise Exception("Should not be able to update reports.")
    except ImmutabilityError as err:
        expected = "Cannot update, reports are immutable. Create a new one instead."
        assert str(err) == expected
