"""Helpers for DataFile submission state transitions."""

import logging
from dataclasses import dataclass
from typing import Callable, Dict, Iterable

from tdpservice.data_files.enums import SubmissionState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TransitionRecord:
    """In-memory record of a single submission state transition."""

    previous_state: SubmissionState
    next_state: SubmissionState
    note: str = ""


class InvalidTransition(ValueError):
    """Raised when an invalid submission state transition is attempted."""


class ReparsePreparationError(ValueError):
    """Raised when a DataFile cannot be safely prepared for reparse."""


REPARSE_READY_STATES = {
    SubmissionState.VIRUS_SCAN_COMPLETED,
    SubmissionState.PARSE_FAILED,
    SubmissionState.PARSED_WITH_ERRORS,
    SubmissionState.PARSE_COMPLETED,
}


ALLOWED_TRANSITIONS: Dict[SubmissionState, Iterable[SubmissionState]] = {
    SubmissionState.UPLOADED: {
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_STARTED: {
        SubmissionState.VIRUS_SCAN_FAILED,
        SubmissionState.VIRUS_SCAN_COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_FAILED: {
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_COMPLETED: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_STARTED: {
        SubmissionState.PARSE_FAILED,
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_FAILED: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSED_WITH_ERRORS: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_COMPLETED: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.STUCK: {
        SubmissionState.CANCELED,
    },
    SubmissionState.COMPLETED: set(),
    SubmissionState.CANCELED: set(),
}


def coerce_submission_state(state) -> SubmissionState:
    """Normalize a state value into a SubmissionState enum."""
    if isinstance(state, SubmissionState):
        return state
    return SubmissionState(state)


def allowed_next_states(current_state) -> set[SubmissionState]:
    """Return the allowed next states for the given current state."""
    normalized_current_state = coerce_submission_state(current_state)
    return set(ALLOWED_TRANSITIONS[normalized_current_state])


def validate_transition(current_state, next_state) -> TransitionRecord:
    """Validate a transition request and return a transition record."""
    normalized_current_state = coerce_submission_state(current_state)
    normalized_next_state = coerce_submission_state(next_state)

    if normalized_next_state not in allowed_next_states(normalized_current_state):
        raise InvalidTransition(
            f"Cannot transition submission from {normalized_current_state.value} "
            + f"to {normalized_next_state.value}."
        )

    return TransitionRecord(
        previous_state=normalized_current_state,
        next_state=normalized_next_state,
    )


def transition_datafile(
    data_file,
    next_state,
    note="",
    logger_hook: Callable | None = None,
):
    """Safely transition a DataFile.state value and persist the new state."""
    transition = validate_transition(data_file.state, next_state)
    transition = TransitionRecord(
        previous_state=transition.previous_state,
        next_state=transition.next_state,
        note=note,
    )

    data_file.state = transition.next_state
    data_file.save(update_fields=["state"])

    log_payload = {
        "data_file_id": data_file.id,
        "previous_state": transition.previous_state.value,
        "next_state": transition.next_state.value,
        "note": note,
    }

    if logger_hook is not None:
        logger_hook(log_payload)
    else:
        logger.info("DataFile submission state transition", extra=log_payload)

    return data_file


def prepare_datafile_for_reparse(
    data_file,
    note="manual admin legacy reparse preparation",
    logger_hook: Callable | None = None,
):
    """Ensure a DataFile is in a state that can be queued for reparse.

    Legacy submitted files may still be in the initial uploaded state. If the
    stored file exists, advance them through the AV lifecycle so the parser can
    move them to parse_started using the normal transition rules.
    """
    current_state = coerce_submission_state(data_file.state)

    if current_state in REPARSE_READY_STATES:
        return data_file, False

    if current_state != SubmissionState.UPLOADED:
        raise ReparsePreparationError(
            f"Cannot reparse DataFile {data_file.id} in state {current_state.value}."
        )

    if not data_file.file or not data_file.file.name:
        raise ReparsePreparationError(
            f"Cannot reparse DataFile {data_file.id}: no stored file is attached."
        )

    if not data_file.file.storage.exists(data_file.file.name):
        raise ReparsePreparationError(
            f"Cannot reparse DataFile {data_file.id}: stored file was not found."
        )

    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_STARTED,
        note=note,
        logger_hook=logger_hook,
    )
    transition_datafile(
        data_file,
        SubmissionState.VIRUS_SCAN_COMPLETED,
        note=note,
        logger_hook=logger_hook,
    )

    return data_file, True
