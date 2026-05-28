"""Tests for submission lifecycle helpers."""

import pytest

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.submission_lifecycle import (
    InvalidTransition,
    allowed_next_states,
    transition_datafile,
    validate_transition,
)
from tdpservice.data_files.test.factories import DataFileFactory


def test_valid_transitions_succeed():
    """Test allowed state transitions validate successfully."""
    first = validate_transition(
        SubmissionState.UPLOADED, SubmissionState.VIRUS_SCAN_STARTED
    )
    second = validate_transition(
        SubmissionState.VIRUS_SCAN_STARTED, SubmissionState.VIRUS_SCAN_COMPLETED
    )

    assert first.previous_state == SubmissionState.UPLOADED
    assert first.next_state == SubmissionState.VIRUS_SCAN_STARTED
    assert second.previous_state == SubmissionState.VIRUS_SCAN_STARTED
    assert second.next_state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert allowed_next_states(SubmissionState.UPLOADED) == {
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.CANCELED,
    }


def test_invalid_transition_raises():
    """Test invalid transitions raise InvalidTransition."""
    with pytest.raises(InvalidTransition, match="uploaded to parse_completed"):
        validate_transition(SubmissionState.UPLOADED, SubmissionState.PARSE_COMPLETED)


@pytest.mark.parametrize(
    "state",
    [
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    ],
)
def test_terminal_states_cannot_transition(state):
    """Test terminal states reject further transitions."""
    with pytest.raises(InvalidTransition, match=f"{state.value} to uploaded"):
        validate_transition(state, SubmissionState.UPLOADED)


@pytest.mark.django_db
def test_transition_datafile_updates_state():
    """Test transition_datafile persists the expected state."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_STARTED,
        note="Picked up by AV scan worker",
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.VIRUS_SCAN_STARTED


@pytest.mark.django_db
def test_transition_datafile_calls_logger_hook():
    """Test transition_datafile emits structured payloads to a logger hook."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)
    payloads = []

    transition_datafile(
        data_file,
        SubmissionState.PARSE_COMPLETED,
        note="Parser completed successfully",
        logger_hook=payloads.append,
    )

    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.PARSE_STARTED.value,
            "next_state": SubmissionState.PARSE_COMPLETED.value,
            "note": "Parser completed successfully",
        }
    ]


@pytest.mark.django_db
def test_transition_datafile_integration_persists_sequential_state_changes():
    """Test sequential persisted transitions on a real DataFile instance."""
    data_file = DataFileFactory(state=SubmissionState.UPLOADED)
    payloads = []

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_STARTED,
        note="Virus scan worker picked up the file",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.VIRUS_SCAN_STARTED

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_COMPLETED,
        note="Virus scan passed",
        logger_hook=payloads.append,
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.VIRUS_SCAN_COMPLETED
    assert payloads == [
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.UPLOADED.value,
            "next_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "note": "Virus scan worker picked up the file",
        },
        {
            "data_file_id": data_file.id,
            "previous_state": SubmissionState.VIRUS_SCAN_STARTED.value,
            "next_state": SubmissionState.VIRUS_SCAN_COMPLETED.value,
            "note": "Virus scan passed",
        },
    ]


@pytest.mark.django_db
def test_transition_datafile_supports_parse_failed_state():
    """Test transition_datafile persists parse failures caused by exceptions."""
    data_file = DataFileFactory(state=SubmissionState.PARSE_STARTED)

    transition_datafile(
        data_file,
        SubmissionState.PARSE_FAILED,
        note="Parser raised an unexpected exception",
    )
    data_file.refresh_from_db()

    assert data_file.state == SubmissionState.PARSE_FAILED


@pytest.mark.parametrize(
    "state",
    [
        SubmissionState.PARSE_FAILED,
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_COMPLETED,
    ],
)
def test_parse_outcome_states_can_reparse(state):
    """Test parsed files can transition back to parse_started for reparse."""
    transition = validate_transition(state, SubmissionState.PARSE_STARTED)

    assert transition.previous_state == state
    assert transition.next_state == SubmissionState.PARSE_STARTED
