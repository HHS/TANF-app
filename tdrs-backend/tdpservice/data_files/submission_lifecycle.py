"""Helpers for DataFile submission state transitions."""

import logging
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable

from django.db import transaction

from celery import current_task

from tdpservice.data_files.enums import SubmissionState

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TransitionRecord:
    """In-memory record of a single submission state transition."""

    previous_state: SubmissionState
    next_state: SubmissionState
    event_id: Any | None = None
    note: str = ""
    metadata: dict | None = None
    actor: Any | None = None
    source: str | None = None
    task_name: str | None = None
    celery_task_id: str | None = None
    reparse_meta_id: int | None = None


class InvalidTransition(ValueError):
    """Raised when an invalid submission state transition is attempted."""


class InvalidScanResult(ValueError):
    """Raised when an AV scan result cannot be mapped to a submission state."""


class ReparsePreparationError(ValueError):
    """Raised when a DataFile cannot be safely prepared for reparse."""


REPARSE_REQUESTABLE_STATES = {
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
        SubmissionState.VIRUS_SCAN_COMPLETED,
        SubmissionState.VIRUS_SCAN_FAILED,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_FAILED: {
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_COMPLETED: {
        SubmissionState.REPARSE_REQUESTED,
        SubmissionState.PARSE_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.REPARSE_REQUESTED: {
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
        SubmissionState.REPARSE_REQUESTED,
        SubmissionState.PARSE_STARTED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSED_WITH_ERRORS: {
        SubmissionState.REPARSE_REQUESTED,
        SubmissionState.PARSE_STARTED,
        SubmissionState.COMPLETED,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_COMPLETED: {
        SubmissionState.REPARSE_REQUESTED,
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
    actor=None,
    logger_hook: Callable | None = None,
    log_fields: dict | None = None,
    source: str | None = None,
    task_name: str | None = None,
    celery_task_id: str | None = None,
    reparse_meta_id: int | None = None,
    event_id: Any | None = None,
):
    """Safely transition a DataFile.state value and persist the new state."""
    with transaction.atomic():
        locked_data_file = _locked_data_file_for_transition(data_file)
        validated_transition = validate_transition(locked_data_file.state, next_state)
        transition = _transition_from_values(
            data_file=locked_data_file,
            previous_state=validated_transition.previous_state,
            next_state=validated_transition.next_state,
            note=note,
            actor=actor,
            log_fields=log_fields,
            source=source,
            task_name=task_name,
            celery_task_id=celery_task_id,
            reparse_meta_id=reparse_meta_id,
            event_id=event_id,
        )
        _save_locked_data_file_transition(locked_data_file, transition)
        _sync_transitioned_data_file(data_file, locked_data_file)

    if logger_hook is not None:
        logger_hook(transition.metadata)
    else:
        logger.info("DataFile submission state transition", extra=transition.metadata)

    return data_file


def force_transition_datafile(
    data_file,
    next_state,
    note="",
    actor=None,
    logger_hook: Callable | None = None,
    log_fields: dict | None = None,
    source: str | None = None,
    task_name: str | None = None,
    celery_task_id: str | None = None,
    reparse_meta_id: int | None = None,
    event_id: Any | None = None,
):
    """Transition a DataFile while intentionally bypassing validation."""
    with transaction.atomic():
        locked_data_file = _locked_data_file_for_transition(data_file)
        transition = _transition_from_values(
            data_file=locked_data_file,
            previous_state=locked_data_file.state,
            next_state=next_state,
            note=note,
            actor=actor,
            log_fields=log_fields,
            source=source,
            task_name=task_name,
            celery_task_id=celery_task_id,
            reparse_meta_id=reparse_meta_id,
            event_id=event_id,
        )
        _save_locked_data_file_transition(locked_data_file, transition)
        _sync_transitioned_data_file(data_file, locked_data_file)

    if logger_hook is not None:
        logger_hook(transition.metadata)
    else:
        logger.info("DataFile submission state transition", extra=transition.metadata)

    return data_file


def _locked_data_file_for_transition(data_file):
    """Return the current DataFile row locked for a state transition."""
    if data_file.pk is None:
        raise ValueError("Cannot transition an unsaved DataFile.")
    return (
        data_file.__class__._default_manager.select_for_update().get(pk=data_file.pk)
    )


def _save_locked_data_file_transition(data_file, transition):
    """Persist a state update and matching audit row for a locked DataFile."""
    data_file.state = transition.next_state
    data_file.save(update_fields=["state"])
    persist_datafile_state_transition(data_file, transition)


def _sync_transitioned_data_file(data_file, persisted_data_file):
    """Keep caller-held DataFile instances aligned with the committed row."""
    data_file.state = persisted_data_file.state
    if hasattr(data_file, "section_ref_id"):
        data_file.section_ref_id = persisted_data_file.section_ref_id
    return data_file


def _active_celery_task_context():
    """Return task-correlation values for the current Celery task, if present."""
    try:
        request = getattr(current_task, "request", None)
        task_name = getattr(current_task, "name", None)
    except Exception:
        return None, None
    celery_task_id = getattr(request, "id", None) if request is not None else None
    return task_name, celery_task_id


def _resolve_task_context(task_name, celery_task_id):
    """Use explicit task context or fall back to the active Celery task."""
    inferred_task_name, inferred_celery_task_id = _active_celery_task_context()
    return task_name or inferred_task_name, celery_task_id or inferred_celery_task_id


def _build_transition_payload(
    *,
    data_file,
    previous_state,
    next_state,
    note,
    log_fields,
    source,
    task_name,
    celery_task_id,
    reparse_meta_id,
    event_id,
):
    """Build the structured lifecycle payload shared by logs and persistence."""
    log_payload = {
        "data_file_id": data_file.id,
        "previous_state": previous_state.value,
        "next_state": next_state.value,
        "note": note,
    }
    if log_fields:
        log_payload.update(log_fields)
    if source:
        log_payload["source"] = source
    if task_name:
        log_payload["task_name"] = task_name
    if celery_task_id:
        log_payload["celery_task_id"] = celery_task_id
    if reparse_meta_id is not None:
        log_payload["reparse_meta_id"] = reparse_meta_id
    if event_id is not None:
        log_payload["event_id"] = str(event_id)

    return log_payload


def _transition_from_values(
    *,
    data_file,
    previous_state,
    next_state,
    note="",
    actor=None,
    log_fields=None,
    source=None,
    task_name=None,
    celery_task_id=None,
    reparse_meta_id=None,
    event_id=None,
):
    """Create an in-memory transition from explicit state values."""
    previous_state = coerce_submission_state(previous_state)
    next_state = coerce_submission_state(next_state)
    task_name, celery_task_id = _resolve_task_context(task_name, celery_task_id)
    metadata = _build_transition_payload(
        data_file=data_file,
        previous_state=previous_state,
        next_state=next_state,
        note=note,
        log_fields=log_fields,
        source=source,
        task_name=task_name,
        celery_task_id=celery_task_id,
        reparse_meta_id=reparse_meta_id,
        event_id=event_id,
    )
    return TransitionRecord(
        previous_state=previous_state,
        next_state=next_state,
        event_id=event_id,
        note=note,
        metadata=metadata,
        actor=actor,
        source=source,
        task_name=task_name,
        celery_task_id=celery_task_id,
        reparse_meta_id=reparse_meta_id,
    )


def persist_datafile_state_transition(data_file, transition):
    """Persist a DataFile state transition audit record."""
    from tdpservice.data_files.models import DataFileStateTransition

    actor = transition.actor
    if actor is not None and not getattr(actor, "is_authenticated", True):
        actor = None

    transition_fields = {
        "previous_state": transition.previous_state.value,
        "next_state": transition.next_state.value,
        "event_type": DataFileStateTransition.EVENT_TYPE,
        "note": transition.note,
        "metadata": transition.metadata or {},
        "actor": actor,
        "source": transition.source,
        "task_name": transition.task_name,
        "celery_task_id": transition.celery_task_id,
        "reparse_meta_id": transition.reparse_meta_id,
    }
    if transition.event_id is not None:
        transition_fields["event_id"] = transition.event_id

    DataFileStateTransition.objects.create_for_object(data_file, **transition_fields)


def _normalize_scan_result(scan_result) -> str:
    """Normalize a scan result value into an upper-case token."""
    value = getattr(scan_result, "value", scan_result)
    return str(value).strip().upper()


def _next_state_for_scan_result(scan_result) -> SubmissionState:
    """Map an AV scan result token to a submission lifecycle state."""
    normalized = _normalize_scan_result(scan_result)

    if normalized in {"CLEAN", "PASS", "PASSED", "OK"}:
        return SubmissionState.VIRUS_SCAN_COMPLETED

    if normalized in {"INFECTED", "FAIL", "FAILED", "FLAGGED", "ERROR"}:
        return SubmissionState.VIRUS_SCAN_FAILED

    raise InvalidScanResult(f"Unsupported AV scan result: {scan_result}")


def _emit_av_completion_log(logger_hook, payload, level="info"):
    """Emit AV completion logging through the optional hook or module logger."""
    if logger_hook is not None:
        logger_hook(payload)
        return

    log_method = logger.warning if level == "warning" else logger.info
    log_method("DataFile AV scan completion", extra=payload)


def complete_datafile_av_scan(
    data_file,
    scan_result,
    note="",
    actor=None,
    logger_hook: Callable | None = None,
    strict=False,
    source: str | None = None,
    event_id: Any | None = None,
):
    """Apply an AV scan completion result to DataFile state.

    Expected transitions:
    - virus_scan_started -> virus_scan_completed for clean results
    - virus_scan_started -> virus_scan_failed for infected, flagged, or error results

    By default this function is idempotent and logs a no-op for duplicate or
    out-of-order results. Set strict=True to raise InvalidTransition for
    out-of-order states.
    """
    target_state = _next_state_for_scan_result(scan_result)
    normalized_scan_result = _normalize_scan_result(scan_result)

    with transaction.atomic():
        locked_data_file = _locked_data_file_for_transition(data_file)
        previous_state = coerce_submission_state(locked_data_file.state)

        if previous_state == target_state:
            payload = {
                "data_file_id": locked_data_file.id,
                "previous_state": previous_state.value,
                "next_state": target_state.value,
                "scan_result": normalized_scan_result,
                "note": note or "Duplicate AV completion result; no-op.",
            }
            log_level = "info"
            transition_occurred = False
        elif previous_state != SubmissionState.VIRUS_SCAN_STARTED:
            if strict:
                raise InvalidTransition(
                    f"Cannot apply AV scan completion while DataFile is in "
                    f"{previous_state.value}."
                )

            payload = {
                "data_file_id": locked_data_file.id,
                "previous_state": previous_state.value,
                "next_state": target_state.value,
                "scan_result": normalized_scan_result,
                "note": note
                or "Ignoring out-of-order AV completion result for DataFile.",
            }
            log_level = "warning"
            transition_occurred = False
        else:
            transition = _transition_from_values(
                data_file=locked_data_file,
                previous_state=previous_state,
                next_state=target_state,
                note=note or "Applied AV scan completion result.",
                actor=actor,
                log_fields={"scan_result": normalized_scan_result},
                source=source,
                event_id=event_id,
            )
            _save_locked_data_file_transition(locked_data_file, transition)
            payload = transition.metadata
            log_level = "info"
            transition_occurred = True

        _sync_transitioned_data_file(data_file, locked_data_file)

        if event_id is not None:
            payload.setdefault("event_id", str(event_id))

    _emit_av_completion_log(logger_hook, payload, level=log_level)
    return data_file, transition_occurred


def prepare_datafile_for_reparse(
    data_file,
    note="admin reparse requested",
    actor=None,
    logger_hook: Callable | None = None,
    source: str | None = None,
    event_id: Any | None = None,
):
    """Transition a safe DataFile into the requested reparse state."""
    from tdpservice.etl.pipelines.sources import (
        ActivePipelineDataFileOverlapError,
        validate_no_active_pipeline_source_overlap,
    )

    try:
        validate_no_active_pipeline_source_overlap([data_file.id])
    except ActivePipelineDataFileOverlapError as exc:
        raise ReparsePreparationError(str(exc)) from exc

    with transaction.atomic():
        locked_data_file = _locked_data_file_for_transition(data_file)
        current_state = coerce_submission_state(locked_data_file.state)

        if current_state == SubmissionState.REPARSE_REQUESTED:
            _sync_transitioned_data_file(data_file, locked_data_file)
            return data_file, False

        if current_state not in REPARSE_REQUESTABLE_STATES:
            raise ReparsePreparationError(
                f"Cannot reparse DataFile {data_file.id} in state {current_state.value}."
            )

        transition = _transition_from_values(
            data_file=locked_data_file,
            previous_state=current_state,
            next_state=SubmissionState.REPARSE_REQUESTED,
            note=note,
            actor=actor,
            source=source,
            event_id=event_id or uuid.uuid4(),
        )
        _save_locked_data_file_transition(locked_data_file, transition)
        _sync_transitioned_data_file(data_file, locked_data_file)

    if logger_hook is not None:
        logger_hook(transition.metadata)
    else:
        logger.info("DataFile submission state transition", extra=transition.metadata)

    return data_file, True


def get_reparse_event_id(data_file):
    """Return the current reparse attempt ID, creating one when none is logged."""
    from tdpservice.data_files.models import DataFileStateTransition

    if coerce_submission_state(data_file.state) == SubmissionState.REPARSE_REQUESTED:
        transition = (
            DataFileStateTransition.objects.for_object(data_file)
            .filter(next_state=SubmissionState.REPARSE_REQUESTED)
            .first()
        )
        if transition is not None:
            return transition.event_id

    return uuid.uuid4()


def revert_reparse_request(
    data_file,
    original_state,
    note="",
    actor=None,
    source=None,
    event_id=None,
):
    """Revert a DataFile out of REPARSE_REQUESTED back to its prior state.

    Recovery helper for the case where a reparse was queued but the worker
    setup (sequential check, backup, etc.) failed before parser tasks were
    actually scheduled. The normal state machine does not allow stepping
    backwards from REPARSE_REQUESTED, so this bypasses ``transition_datafile``
    intentionally. Returns True if a revert occurred, False otherwise (e.g.,
    the file has already progressed past REPARSE_REQUESTED).
    """
    target_state = coerce_submission_state(original_state)
    with transaction.atomic():
        locked_data_file = _locked_data_file_for_transition(data_file)
        current_state = coerce_submission_state(locked_data_file.state)
        if current_state != SubmissionState.REPARSE_REQUESTED:
            _sync_transitioned_data_file(data_file, locked_data_file)
            logger.info(
                "Skipping reparse revert; DataFile is no longer in REPARSE_REQUESTED.",
                extra={
                    "data_file_id": data_file.id,
                    "current_state": current_state.value,
                },
            )
            return False

        transition = _transition_from_values(
            data_file=locked_data_file,
            previous_state=current_state,
            next_state=target_state,
            note=note,
            actor=actor,
            source=source,
            event_id=event_id or get_reparse_event_id(locked_data_file),
        )
        _save_locked_data_file_transition(locked_data_file, transition)
        _sync_transitioned_data_file(data_file, locked_data_file)

    logger.warning(
        "DataFile reparse request reverted after worker setup failure.",
        extra=transition.metadata,
    )
    return True
