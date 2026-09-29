"""Test data file serializers."""

from django.core.exceptions import ValidationError

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.serializers import DataFileSerializer
from tdpservice.data_files.validators import (
    validate_file_extension,
    validate_file_infection,
)
from tdpservice.security.clients import ClamAVClient


@pytest.mark.django_db
def test_serializer_with_valid_data(data_file_data, data_analyst):
    """If a serializer has valid data it will return a valid object."""
    create_serializer = DataFileSerializer(
        context={"user": data_analyst}, data=data_file_data
    )
    create_serializer.is_valid(raise_exception=True)
    assert create_serializer.is_valid() is True


@pytest.mark.django_db
def test_serializer_increment_create(data_file_data, other_data_file_data, user):
    """Test serializer produces data_files with correct version."""
    serializer_1 = DataFileSerializer(context={"user": user}, data=data_file_data)
    assert serializer_1.is_valid() is True
    data_file_1 = serializer_1.save()

    serializer_2 = DataFileSerializer(context={"user": user}, data=other_data_file_data)
    assert serializer_2.is_valid() is True
    data_file_2 = serializer_2.save()

    assert data_file_2.version == data_file_1.version + 1
    assert data_file_1.section_ref.program.code == data_file_1.program_type
    assert data_file_1.section_ref.name == data_file_1.section
    assert data_file_2.section_ref == data_file_1.section_ref


@pytest.mark.django_db
def test_immutability_of_data_file(data_file_instance):
    """Test that data file can only be created."""
    with pytest.raises(ImmutabilityError):
        serializer = DataFileSerializer(
            data_file_instance,
            data={
                "original_filename": "BadGuy.js",
            },
            partial=True,
        )

        serializer.is_valid()
        serializer.save()


@pytest.mark.django_db
def test_created_at(data_file_data, data_analyst):
    """Test that serializer creates a DataFile with a created_at timestamp."""
    create_serializer = DataFileSerializer(
        context={"user": data_analyst}, data=data_file_data
    )
    assert create_serializer.is_valid() is True
    data_file = create_serializer.save()

    assert data_file.created_at


@pytest.mark.django_db
def test_lifecycle_state_fields_are_serialized(data_file_instance):
    """Test lifecycle state, label, and valid transitions are exposed."""
    data_file_instance.state = SubmissionState.PARSED_WITH_ERRORS
    serialized = DataFileSerializer(data_file_instance).data

    assert serialized["state"] == SubmissionState.PARSED_WITH_ERRORS
    assert serialized["state_display"] == "Parsed with errors"
    assert serialized["allowed_next_states"] == [
        SubmissionState.REPARSE_REQUESTED,
        SubmissionState.PARSE_STARTED,
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    ]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "terminal_state",
    [SubmissionState.COMPLETED, SubmissionState.CANCELED],
)
def test_terminal_lifecycle_states_have_no_allowed_transitions(
    data_file_instance, terminal_state
):
    """Test terminal lifecycle states do not advertise follow-up actions."""
    data_file_instance.state = terminal_state

    serialized = DataFileSerializer(data_file_instance).data

    assert serialized["allowed_next_states"] == []


@pytest.mark.django_db
def test_unknown_lifecycle_state_serializes_safely(data_file_instance):
    """Test an unexpected database value does not break API serialization."""
    data_file_instance.state = "future_state"

    serialized = DataFileSerializer(data_file_instance).data

    assert serialized["state"] == "future_state"
    assert serialized["state_display"] == "future_state"
    assert serialized["allowed_next_states"] == []


@pytest.mark.django_db
def test_lifecycle_state_is_read_only_on_create(data_file_data, data_analyst):
    """Test API input cannot override the initial lifecycle state."""
    data_file_data["state"] = SubmissionState.PARSE_FAILED
    serializer = DataFileSerializer(context={"user": data_analyst}, data=data_file_data)

    serializer.is_valid(raise_exception=True)
    data_file = serializer.save()

    assert "state" not in serializer.validated_data
    assert data_file.state == SubmissionState.UPLOADED
    assert serializer.fields["state"].read_only is True
    assert serializer.fields["state_display"].read_only is True
    assert serializer.fields["allowed_next_states"].read_only is True


@pytest.mark.parametrize(
    "file_name",
    [
        "sample.txt",
        "Sample",
        "ADS.E2J.FTP4.TS06.txt",
        "ADS.E2J.FTP4.TS06",
        "ADS.E2J.FTP2.MS18",
        "ADS.E2J.FTP1.TS278",
    ],
)
def test_accepts_valid_file_extensions(file_name):
    """Test valid file names are accepted by serializer validation."""
    try:
        validate_file_extension(file_name)
    except ValidationError as err:
        pytest.fail(f"Received unexpected error: {err}")


@pytest.mark.parametrize(
    "file_name",
    [
        "java.jar",
        "mysql.bin",
        "malicious.exe",
        "exec.py",
        "hax.pdf",
        "types.ts",
        "notepad.txt.exe",
        "ADS.E2J.FTP1.TS273894",
        "ADS.E2J.FTP1.TS38WRONG",
        "ADS.E2J.FTP1.MS38483",
        "ADS.E2J.FTP1.MS38WRONG",
    ],
)
def test_rejects_invalid_file_extensions(file_name):
    """Test invalid file names are rejected by serializer validation."""
    with pytest.raises(ValidationError):
        validate_file_extension(file_name)


@pytest.mark.django_db
def test_rejects_infected_file(infected_file, fake_file_name, user, settings):
    """Test infected files are rejected by the AV validator helper."""
    settings.CLAMAV_NEEDED = True
    with pytest.raises(ValidationError):
        validate_file_infection(infected_file, fake_file_name, user)


@pytest.mark.django_db
def test_rejects_uploads_on_clamav_connection_error(
    fake_file, fake_file_name, mocker, user, settings
):
    """Test that the AV validator helper rejects if ClamAV is down."""
    settings.CLAMAV_NEEDED = True
    mocker.patch(
        "tdpservice.security.clients.ClamAVClient.scan_file",
        side_effect=ClamAVClient.ServiceUnavailable(),
    )
    with pytest.raises(ValidationError):
        validate_file_infection(fake_file, fake_file_name, user)
