"""Test data file serializers."""
from django.core.exceptions import ValidationError
import pytest

from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.serializers import DataFileSerializer
from tdpservice.data_files.validators import (
    validate_file_extension,
    validate_file_infection
)
from tdpservice.security.clients import ClamAVClient


@pytest.mark.django_db
def test_serializer_with_valid_data(data_file_data, user):
    """If a serializer has valid data it will return a valid object."""
    create_serializer = DataFileSerializer(
        context={'user': user},
        data=data_file_data
    )
    create_serializer.is_valid(raise_exception=True)
    assert create_serializer.is_valid() is True


@pytest.mark.django_db
def test_serializer_increment_create(
    data_file_data,
    other_data_file_data,
    user
):
    """Test serializer produces data_files with correct version."""
    serializer_1 = DataFileSerializer(
        context={'user': user},
        data=data_file_data
    )
    assert serializer_1.is_valid() is True
    data_file_1 = serializer_1.save()

    serializer_2 = DataFileSerializer(
        context={'user': user},
        data=other_data_file_data
    )
    assert serializer_2.is_valid() is True
    data_file_2 = serializer_2.save()

    assert data_file_2.version == data_file_1.version + 1


@pytest.mark.django_db
def test_immutability_of_data_file(data_file_instance):
    """Test that data file can only be created."""
    with pytest.raises(ImmutabilityError):
        serializer = DataFileSerializer(
            data_file_instance, data={
                "original_filename": "BadGuy.js"
            },
            partial=True
        )

        serializer.is_valid()
        serializer.save()


@pytest.mark.django_db
def test_created_at(data_file_data, user):
    """If a serializer has valid data it will return a valid object."""
    create_serializer = DataFileSerializer(
        context={'user': user},
        data=data_file_data
    )
    assert create_serializer.is_valid() is True
    data_file = create_serializer.save()

    assert data_file.created_at
    assert data_file.av_scans.exists()


@pytest.mark.django_db
def test_data_file_still_created_if_av_scan_fails_to_create(
    data_file_data,
    mocker,
    user
):
    """Test valid DataFile is still created if ClamAV scan isn't recorded.

    In this scenario all validation would have already passed but in the event
    the ClamAVFileScan isn't found in the database due to an error or race
    condition we should still store the DataFile.
    """
    mocker.patch(
        'tdpservice.security.models.ClamAVFileScanManager.record_scan',
        return_value=None
    )
    create_serializer = DataFileSerializer(
        context={'user': user},
        data=data_file_data
    )
    assert create_serializer.is_valid() is True
    data_file = create_serializer.save()

    assert data_file is not None
    assert data_file.av_scans.count() == 0


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


@pytest.mark.django_db
def test_rejects_infected_file(infected_file, fake_file_name, user):
    """Test infected files are rejected by serializer validation."""
    with pytest.raises(ValidationError):
        validate_file_infection(infected_file, fake_file_name, user)


@pytest.mark.django_db
def test_rejects_uploads_on_clamav_connection_error(
    fake_file,
    fake_file_name,
    mocker,
    user
):
    """Test that DataFiles cannot pass validation if ClamAV is down."""
    mocker.patch(
        'tdpservice.security.clients.ClamAVClient.scan_file',
        side_effect=ClamAVClient.ServiceUnavailable()
    )
    with pytest.raises(ValidationError):
        validate_file_infection(fake_file, fake_file_name, user)
