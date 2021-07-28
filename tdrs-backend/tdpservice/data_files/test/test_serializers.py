"""Test data file serializers."""
from django.core.exceptions import ValidationError
import pytest

from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.serializers import DataFileSerializer
from tdpservice.data_files.validators import validate_file_extension


@pytest.mark.django_db
def test_serializer_with_valid_data(data_file_data):
    """If a serializer has valid data it will return a valid object."""
    create_serializer = DataFileSerializer(data=data_file_data)
    create_serializer.is_valid(raise_exception=True)
    assert create_serializer.is_valid() is True


@pytest.mark.django_db
def test_serializer_increment_create(data_file_data, other_data_file_data):
    """Test serializer produces data_files with correct version."""
    serializer_1 = DataFileSerializer(data=data_file_data)
    assert serializer_1.is_valid() is True
    data_file_1 = serializer_1.save()

    serializer_2 = DataFileSerializer(data=other_data_file_data)
    assert serializer_2.is_valid() is True
    data_file_2 = serializer_2.save()

    assert data_file_2.version == data_file_1.version + 1


@pytest.mark.django_db
def test_immutability_of_data_file(data_file):
    """Test that data file can only be created."""
    with pytest.raises(ImmutabilityError):
        serializer = DataFileSerializer(
            data_file, data={
                "original_filename": "BadGuy.js"
            },
            partial=True
        )

        serializer.is_valid()
        serializer.save()


@pytest.mark.django_db
def test_created_at(data_file_data):
    """If a serializer has valid data it will return a valid object."""
    create_serializer = DataFileSerializer(data=data_file_data)
    assert create_serializer.is_valid() is True
    data_file = create_serializer.save()

    assert data_file.created_at


@pytest.mark.parametrize("file_name", [
    'sample.txt',
    'Sample',
    'ADS.E2J.FTP4.TS06.txt',
    'ADS.E2J.FTP4.TS06',
    'ADS.E2J.FTP2.MS18',
    'ADS.E2J.FTP1.TS278'
])
def test_accepts_valid_file_extensions(file_name):
    """Test valid file names are accepted by serializer validation."""
    try:
        validate_file_extension(file_name)
    except ValidationError as err:
        pytest.fail(f'Received unexpected error: {err}')


@pytest.mark.parametrize("file_name", [
    'java.jar',
    'mysql.bin',
    'malicious.exe',
    'exec.py',
    'hax.pdf',
    'types.ts',
    'notepad.txt.exe',
    'ADS.E2J.FTP1.TS273894',
    'ADS.E2J.FTP1.TS38WRONG',
    'ADS.E2J.FTP1.MS38483',
    'ADS.E2J.FTP1.MS38WRONG'
])
def test_rejects_invalid_file_extensions(file_name):
    """Test invalid file names are rejected by serializer validation."""
    with pytest.raises(ValidationError):
        validate_file_extension(file_name)
