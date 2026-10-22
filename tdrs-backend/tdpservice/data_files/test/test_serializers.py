"""Test data file serializers."""

from types import SimpleNamespace

from django.core.exceptions import ValidationError

import pytest
from rest_framework.exceptions import ValidationError as SerializerValidationError

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.errors import ImmutabilityError
from tdpservice.data_files.models import Section
from tdpservice.data_files.serializers import DataFileSerializer
from tdpservice.data_files.validators import (
    validate_file_extension,
    validate_file_infection,
)
from tdpservice.security.clients import ClamAVClient


@pytest.mark.parametrize(
    "section_name",
    [
        Section.Name.FRA_WORK_OUTCOMES,
        Section.Name.FRA_SECONDARY_SCHOOL_ATTAINMENT,
        Section.Name.FRA_SUPPLEMENTAL_WORK_OUTCOMES,
    ],
)
@pytest.mark.parametrize("extension", ["csv", "xlsx"])
def test_fra_section_validation_needs_no_database(
    section_name: str, extension: str
) -> None:
    """FRA permissions and extension rules apply without catalog queries."""
    user = SimpleNamespace(has_fra_access=True, is_ofa_sys_admin=False)
    serializer = DataFileSerializer(context={"user": user})
    data = {
        "section": section_name,
        "file": SimpleNamespace(name=f"submission.{extension}"),
    }

    assert serializer.validate_section(section_name) == section_name
    assert serializer.validate(data) == data
    with pytest.raises(ValidationError):
        serializer.validate(
            {"section": section_name, "file": SimpleNamespace(name="submission.txt")}
        )


@pytest.mark.parametrize(
    "section_name",
    [
        Section.Name.FRA_WORK_OUTCOMES,
        Section.Name.FRA_SECONDARY_SCHOOL_ATTAINMENT,
        Section.Name.FRA_SUPPLEMENTAL_WORK_OUTCOMES,
    ],
)
def test_fra_section_permissions_need_no_database(section_name: str) -> None:
    """FRA access remains required even without a database lookup."""
    user = SimpleNamespace(has_fra_access=False, is_ofa_sys_admin=False)
    serializer = DataFileSerializer(context={"user": user})

    with pytest.raises(SerializerValidationError, match="Section cannot be FRA"):
        serializer.validate_section(section_name)


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
    data_file_1 = serializer_1.save(user=user)

    serializer_2 = DataFileSerializer(context={"user": user}, data=other_data_file_data)
    assert serializer_2.is_valid() is True
    data_file_2 = serializer_2.save(user=user)

    assert data_file_2.version == data_file_1.version + 1
    assert data_file_1.program.code == "TAN"
    assert data_file_1.section.name == data_file_data["section"]
    assert data_file_2.section == data_file_1.section
    assert serializer_1.data["program_type"] == "TAN"
    assert serializer_1.data["section"] == data_file_data["section"]
    assert isinstance(serializer_1.data["program_type"], str)
    assert isinstance(serializer_1.data["section"], str)


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
    data_file = create_serializer.save(user=data_analyst)

    assert data_file.created_at


@pytest.mark.django_db
def test_user_is_read_only_on_create(data_file_data, data_analyst, user):
    """Test serializer input cannot select the user who owns a data file."""
    data_file_data["user"] = str(user.id)
    serializer = DataFileSerializer(context={"user": data_analyst}, data=data_file_data)

    serializer.is_valid(raise_exception=True)
    data_file = serializer.save(user=data_analyst)

    assert "user" not in serializer.validated_data
    assert data_file.user == data_analyst
    assert serializer.fields["user"].read_only is True


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
    data_file = serializer.save(user=data_analyst)

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
        "ADS.E2J.FTP4.TS06.txtcsv",
        "ADS.E2J.FTP4.TS06.txtzip",
    ],
)
def test_rejects_invalid_file_extensions(file_name):
    """Test invalid file names are rejected by serializer validation."""
    with pytest.raises(ValidationError):
        validate_file_extension(file_name)


@pytest.mark.parametrize(
    "file_name",
    [
        "fra.csvzip",
        "fra.xlsxabc",
        "fra.csv.exe",
    ],
)
def test_rejects_invalid_fra_file_extensions(file_name):
    """Test FRA file names are matched whole, not by prefix."""
    with pytest.raises(ValidationError):
        validate_file_extension(file_name, is_fra=True)


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
