"""Exclusive controller for production DataFile submission state."""

import logging
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Iterator
from uuid import UUID

from django.db import transaction
from django.utils import timezone

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


class StaleParseOwnership(RuntimeError):
    """Raised when a parser no longer owns the current DataFile parse."""


REPARSE_REQUESTABLE_STATES = {
    SubmissionState.VIRUS_SCAN_COMPLETED,
    SubmissionState.PARSE_FAILED,
    SubmissionState.PARSED_WITH_ERRORS,
    SubmissionState.PARSE_COMPLETED,
    SubmissionState.STUCK,
}

PARSE_QUEUEABLE_STATES = {
    SubmissionState.VIRUS_SCAN_COMPLETED,
    SubmissionState.REPARSE_REQUESTED,
    # A failed initial parse can be retried without destructive reparse cleanup.
    SubmissionState.PARSE_FAILED,
}

STALE_ELIGIBLE_STATES = {
    SubmissionState.UPLOADED,
    SubmissionState.VIRUS_SCAN_STARTED,
    SubmissionState.VIRUS_SCAN_COMPLETED,
    SubmissionState.REPARSE_REQUESTED,
    SubmissionState.PARSE_STARTED,
}


ALLOWED_TRANSITIONS: Dict[SubmissionState, Iterable[SubmissionState]] = {
    SubmissionState.UPLOADED: {
        SubmissionState.VIRUS_SCAN_STARTED,
        SubmissionState.STUCK,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_STARTED: {
        SubmissionState.VIRUS_SCAN_COMPLETED,
        SubmissionState.VIRUS_SCAN_FAILED,
        SubmissionState.STUCK,
        SubmissionState.CANCELED,
    },
    SubmissionState.VIRUS_SCAN_FAILED: {SubmissionState.CANCELED},
    SubmissionState.VIRUS_SCAN_COMPLETED: {
        SubmissionState.REPARSE_REQUESTED,
        SubmissionState.PARSE_STARTED,
        SubmissionState.PARSE_FAILED,
        SubmissionState.STUCK,
        SubmissionState.CANCELED,
    },
    SubmissionState.REPARSE_REQUESTED: {
        SubmissionState.PARSE_STARTED,
        SubmissionState.PARSE_FAILED,
        SubmissionState.STUCK,
        SubmissionState.CANCELED,
    },
    SubmissionState.PARSE_STARTED: {
        SubmissionState.PARSE_FAILED,
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_COMPLETED,
        SubmissionState.STUCK,
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
        SubmissionState.REPARSE_REQUESTED,
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
    return set(ALLOWED_TRANSITIONS[coerce_submission_state(current_state)])


def validate_transition(current_state, next_state) -> TransitionRecord:
    """Validate a transition request and return a transition record."""
    normalized_current_state = coerce_submission_state(current_state)
    normalized_next_state = coerce_submission_state(next_state)
    if normalized_next_state not in allowed_next_states(normalized_current_state):
        raise InvalidTransition(
            f"Cannot transition submission from {normalized_current_state.value} "
            f"to {normalized_next_state.value}."
        )
    return TransitionRecord(normalized_current_state, normalized_next_state)


def _coerce_parse_token(parse_token) -> UUID:
    """Normalize a parser ownership token."""
    if isinstance(parse_token, UUID):
        return parse_token
    return UUID(str(parse_token))


def _locked_data_file(data_file):
    """Return the current persisted DataFile with a row lock."""
    from tdpservice.data_files.models import DataFile

    return DataFile.objects.select_for_update().get(pk=data_file.pk)


def _emit_transition_log(
    transition: TransitionRecord,
    data_file_id: int,
    logger_hook: Callable | None,
    log_fields: dict | None,
    level: str = "info",
) -> None:
    """Emit a structured lifecycle transition log."""
    payload = {
        "data_file_id": data_file_id,
        "previous_state": transition.previous_state.value,
        "next_state": transition.next_state.value,
        "note": transition.note,
    }
    payload.update(transition.metadata or {})
    if log_fields:
        payload.update(log_fields)
    if logger_hook is not None:
        logger_hook(payload)
    elif level == "warning":
        logger.warning("DataFile submission state transition", extra=payload)
    else:
        logger.info("DataFile submission state transition", extra=payload)


def _apply_transition_locked(
    data_file, next_state, *, note: str = "", **audit_context
) -> TransitionRecord:
    """Persist a validated state and audit row under the caller's DataFile lock."""
    validate_transition(data_file.state, next_state)
    transition = _transition_from_values(
        data_file=data_file,
        previous_state=data_file.state,
        next_state=next_state,
        note=note,
        **audit_context,
    )
    _save_transition_locked(data_file, transition)
    return transition


def _force_reparse_revert_locked(
    data_file,
    target_state: SubmissionState,
    note: str,
    **audit_context,
) -> TransitionRecord:
    """Apply the controller's explicit pre-destructive reparse rollback."""
    transition = _transition_from_values(
        data_file=data_file,
        previous_state=data_file.state,
        next_state=target_state,
        note=note,
        **audit_context,
    )
    _save_transition_locked(data_file, transition)
    return transition


def start_datafile_av_scan(
    data_file,
    note: str = "virus scan started",
    logger_hook: Callable | None = None,
    *,
    actor=None,
    source: str | None = None,
    event_id: UUID | str | None = None,
    log_fields: dict | None = None,
):
    """Record that the upload controller started AV scanning."""
    with transaction.atomic():
        locked = _locked_data_file(data_file)
        transition = _apply_transition_locked(
            locked,
            SubmissionState.VIRUS_SCAN_STARTED,
            note=note,
            actor=actor,
            source=source,
            event_id=event_id,
            log_fields=log_fields,
        )
    data_file.state = transition.next_state
    data_file.state_changed_at = locked.state_changed_at
    _emit_transition_log(transition, data_file.id, logger_hook, None)
    return data_file


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


def _emit_av_completion_log(logger_hook, payload, level="info") -> None:
    """Emit AV completion logging through the optional hook or module logger."""
    if logger_hook is not None:
        logger_hook(payload)
        return
    log_method = logger.warning if level == "warning" else logger.info
    log_method("DataFile AV scan completion", extra=payload)


def complete_datafile_av_scan(
    data_file,
    scan_result,
    note: str = "",
    logger_hook: Callable | None = None,
    strict: bool = False,
    *,
    actor=None,
    source: str | None = None,
    event_id: UUID | str | None = None,
    log_fields: dict | None = None,
):
    """Apply an idempotent AV result through the lifecycle controller."""
    target_state = _next_state_for_scan_result(scan_result)
    normalized_scan_result = _normalize_scan_result(scan_result)
    with transaction.atomic():
        locked = _locked_data_file(data_file)
        previous_state = coerce_submission_state(locked.state)
        if previous_state == target_state:
            transition = None
        elif previous_state != SubmissionState.VIRUS_SCAN_STARTED:
            if strict:
                raise InvalidTransition(
                    "Cannot apply AV scan completion while DataFile is in "
                    f"{previous_state.value}."
                )
            transition = None
        else:
            transition = _apply_transition_locked(
                locked,
                target_state,
                note=note or "Applied AV scan completion result.",
                actor=actor,
                source=source,
                event_id=event_id,
                log_fields={**(log_fields or {}), "scan_result": normalized_scan_result},
            )

    data_file.state = locked.state
    data_file.state_changed_at = locked.state_changed_at
    if transition is not None:
        _emit_transition_log(
            transition,
            data_file.id,
            logger_hook,
            {"scan_result": normalized_scan_result},
        )
        return data_file, True

    duplicate = previous_state == target_state
    payload = {
        "data_file_id": data_file.id,
        "previous_state": previous_state.value,
        "next_state": target_state.value,
        "scan_result": normalized_scan_result,
        "note": note
        or (
            "Duplicate AV completion result; no-op."
            if duplicate
            else "Ignoring out-of-order AV completion result for DataFile."
        ),
    }
    _emit_av_completion_log(logger_hook, payload, level="info" if duplicate else "warning")
    return data_file, False


def prepare_datafile_for_reparse(
    data_file,
    note: str = "admin reparse requested",
    logger_hook: Callable | None = None,
    *,
    actor=None,
    source: str | None = None,
    event_id: UUID | str | None = None,
    log_fields: dict | None = None,
):
    """Request a safe reparse without allowing the caller to select state."""
    from tdpservice.etl.pipelines.sources import (
        ActivePipelineDataFileOverlapError,
        validate_no_active_pipeline_source_overlap,
    )

    try:
        validate_no_active_pipeline_source_overlap([data_file.id])
    except ActivePipelineDataFileOverlapError as exc:
        raise ReparsePreparationError(str(exc)) from exc

    with transaction.atomic():
        locked = _locked_data_file(data_file)
        current_state = coerce_submission_state(locked.state)
        if current_state == SubmissionState.REPARSE_REQUESTED:
            data_file.state = locked.state
            return data_file, False
        if current_state not in REPARSE_REQUESTABLE_STATES:
            raise ReparsePreparationError(
                f"Cannot reparse DataFile {data_file.id} in state {current_state.value}."
            )
        if not locked.file:
            raise ReparsePreparationError(
                f"Cannot reparse DataFile {data_file.id} because it has no stored file."
            )
        transition = _apply_transition_locked(
            locked,
            SubmissionState.REPARSE_REQUESTED,
            note=note,
            actor=actor,
            source=source,
            event_id=event_id or uuid.uuid4(),
            log_fields=log_fields,
        )

    data_file.state = transition.next_state
    data_file.state_changed_at = locked.state_changed_at
    _emit_transition_log(transition, data_file.id, logger_hook, None)
    return data_file, True


def revert_reparse_request(
    data_file,
    original_state,
    note: str = "",
    *,
    actor=None,
    source: str | None = None,
    event_id: UUID | str | None = None,
) -> bool:
    """Conditionally revert a failed pre-destructive reparse request."""
    target_state = coerce_submission_state(original_state)
    if target_state not in REPARSE_REQUESTABLE_STATES:
        raise ReparsePreparationError(
            f"Cannot revert DataFile {data_file.id} to {target_state.value}."
        )

    with transaction.atomic():
        locked = _locked_data_file(data_file)
        current_state = coerce_submission_state(locked.state)
        if current_state != SubmissionState.REPARSE_REQUESTED:
            data_file.state = locked.state
            logger.info(
                "Skipping reparse revert; DataFile is no longer in REPARSE_REQUESTED.",
                extra={
                    "data_file_id": data_file.id,
                    "current_state": current_state.value,
                },
            )
            return False
        transition = _force_reparse_revert_locked(
            locked,
            target_state,
            note,
            actor=actor,
            source=source,
            event_id=event_id or get_reparse_event_id(locked),
        )

    data_file.state = transition.next_state
    data_file.state_changed_at = locked.state_changed_at
    _emit_transition_log(transition, data_file.id, None, None, level="warning")
    return True


def claim_parse(data_file, reparse_file_meta=None, actor: str = "parser_queue") -> UUID:
    """Assign a token to the only parser currently allowed to write a DataFile."""
    with transaction.atomic():
        locked = _locked_data_file(data_file)
        current_state = coerce_submission_state(locked.state)
        if current_state not in PARSE_QUEUEABLE_STATES:
            raise InvalidTransition(
                f"Cannot queue parsing while DataFile is in {current_state.value}."
            )
        if reparse_file_meta is not None and reparse_file_meta.data_file_id != locked.id:
            raise InvalidTransition(
                f"Reparse metadata {reparse_file_meta.id} does not belong to "
                f"DataFile {locked.id}."
            )
        if locked.current_parse_token is not None:
            raise StaleParseOwnership(
                f"DataFile {data_file.id} already has an active parser owner."
            )
        parse_token = uuid.uuid4()
        locked.current_parse_token = parse_token
        locked.save(update_fields=["current_parse_token"])

    data_file.current_parse_token = parse_token
    logger.info(
        "DataFile parse claimed",
        extra={
            "data_file_id": data_file.id,
            "parse_token": str(parse_token),
            "actor": actor,
        },
    )
    return parse_token


def _owns_parse(locked, parse_token: UUID) -> bool:
    """Return whether the token currently owns the locked DataFile."""
    return locked.current_parse_token == parse_token


def begin_parse(
    data_file,
    parse_token,
    reparse_file_meta=None,
    actor: str = "python_parser",
    event_id: UUID | str | None = None,
):
    """Start the current claimed parse and transition to PARSE_STARTED."""
    normalized_token = _coerce_parse_token(parse_token)
    with transaction.atomic():
        locked = _locked_data_file(data_file)
        if not _owns_parse(locked, normalized_token):
            raise StaleParseOwnership(
                f"Parser token {normalized_token} no longer owns DataFile {data_file.id}."
            )
        transition = _apply_transition_locked(
            locked,
            SubmissionState.PARSE_STARTED,
            note="parsing started",
            source=actor,
            event_id=event_id,
            reparse_meta_id=(reparse_file_meta.reparse_meta_id if reparse_file_meta else None),
            log_fields={"parse_token": str(normalized_token)},
        )
        if reparse_file_meta is not None:
            if reparse_file_meta.data_file_id != locked.id:
                raise InvalidTransition(
                    f"Reparse metadata {reparse_file_meta.id} does not belong to "
                    f"DataFile {locked.id}."
                )
            type(reparse_file_meta).objects.filter(
                pk=reparse_file_meta.pk,
                finished=False,
            ).update(started_at=timezone.now())

    data_file.state = transition.next_state
    data_file.state_changed_at = locked.state_changed_at
    data_file.current_parse_token = normalized_token
    _emit_transition_log(
        transition,
        data_file.id,
        None,
        {"parse_token": str(normalized_token), "actor": actor},
    )
    return normalized_token


def _clear_parse_token_locked(locked) -> None:
    """Release parser ownership while the DataFile row is locked."""
    locked.current_parse_token = None
    locked.save(update_fields=["current_parse_token"])


def _finish_reparse_locked(reparse_file_meta, success: bool, **metrics) -> bool:
    """Close the specific unfinished reparse metadata row."""
    if reparse_file_meta is None:
        return False
    updates = {
        "finished": True,
        "success": success,
        "finished_at": timezone.now(),
        **metrics,
    }
    return (
        type(reparse_file_meta)
        .objects.filter(pk=reparse_file_meta.pk, finished=False)
        .update(**updates)
        == 1
    )


def record_parse_dispatch_failure(
    data_file,
    parse_token,
    reparse_file_meta=None,
    note: str = "parser task dispatch failed",
    event_id: UUID | str | None = None,
) -> bool:
    """Release a claimed parse when the broker rejects dispatch."""
    normalized_token = _coerce_parse_token(parse_token)
    with transaction.atomic():
        locked = _locked_data_file(data_file)
        if not _owns_parse(locked, normalized_token):
            return False
        transition = None
        if locked.state != SubmissionState.PARSE_FAILED:
            transition = _apply_transition_locked(
                locked,
                SubmissionState.PARSE_FAILED,
                note=note,
                source="parser_queue",
                event_id=event_id,
                reparse_meta_id=(reparse_file_meta.reparse_meta_id if reparse_file_meta else None),
                log_fields={"parse_token": str(normalized_token)},
            )
        _clear_parse_token_locked(locked)
        _finish_reparse_locked(reparse_file_meta, success=False)

    data_file.state = locked.state
    data_file.state_changed_at = locked.state_changed_at
    data_file.current_parse_token = None
    if transition is not None:
        _emit_transition_log(transition, data_file.id, None, None, level="warning")
    return True


def _target_state_for_summary_status(summary_status) -> SubmissionState:
    """Map parser summary status to the durable submission outcome."""
    value = getattr(summary_status, "value", summary_status)
    if str(value) == "Accepted":
        return SubmissionState.PARSE_COMPLETED
    if str(value) in {
        "Accepted with Errors",
        "Partially Accepted with Errors",
        "Rejected",
    }:
        return SubmissionState.PARSED_WITH_ERRORS
    raise ValueError(f"Unsupported parse summary status: {summary_status}")


def record_parse_outcome(
    data_file,
    parse_token,
    summary_status,
    *,
    actor: str = "python_parser",
    log_fields: dict | None = None,
    event_id: UUID | str | None = None,
    reparse_meta_id: int | None = None,
    task_name: str | None = None,
):
    """Record a successful technical parse and release parser ownership."""
    target_state = _target_state_for_summary_status(summary_status)
    normalized_token = _coerce_parse_token(parse_token)
    fields = {"parse_token": str(normalized_token), **(log_fields or {})}
    with transaction.atomic():
        locked = _locked_data_file(data_file)
        if not _owns_parse(locked, normalized_token):
            raise StaleParseOwnership(
                f"Parser token {normalized_token} no longer owns DataFile {data_file.id}."
            )
        transition = _apply_transition_locked(
            locked,
            target_state,
            source=actor,
            event_id=event_id,
            reparse_meta_id=reparse_meta_id,
            task_name=task_name,
            log_fields=fields,
            note=(
                "parsing completed successfully"
                if target_state == SubmissionState.PARSE_COMPLETED
                else "parsing completed with errors"
            ),
        )
        _clear_parse_token_locked(locked)

    data_file.state = transition.next_state
    data_file.state_changed_at = locked.state_changed_at
    data_file.current_parse_token = None
    fields = {"parse_token": str(normalized_token), "actor": actor}
    fields.update(log_fields or {})
    _emit_transition_log(transition, data_file.id, None, fields)
    return data_file


def record_parse_failure(
    data_file,
    parse_token,
    note: str,
    *,
    reparse_file_meta=None,
    actor: str = "python_parser",
    log_fields: dict | None = None,
    event_id: UUID | str | None = None,
    reparse_meta_id: int | None = None,
    task_name: str | None = None,
) -> bool:
    """Record a technical failure only for the current parser owner."""
    normalized_token = _coerce_parse_token(parse_token)
    fields = {"parse_token": str(normalized_token), **(log_fields or {})}
    with transaction.atomic():
        locked = _locked_data_file(data_file)
        if not _owns_parse(locked, normalized_token):
            return False
        transition = _apply_transition_locked(
            locked,
            SubmissionState.PARSE_FAILED,
            source=actor,
            event_id=event_id,
            reparse_meta_id=reparse_meta_id,
            task_name=task_name,
            log_fields=fields,
            note=note,
        )
        _clear_parse_token_locked(locked)
        _finish_reparse_locked(reparse_file_meta, success=False)

    data_file.state = transition.next_state
    data_file.state_changed_at = locked.state_changed_at
    data_file.current_parse_token = None
    fields = {"parse_token": str(normalized_token), "actor": actor}
    fields.update(log_fields or {})
    _emit_transition_log(transition, data_file.id, None, fields, level="warning")
    return True


def finish_reparse(
    data_file,
    reparse_file_meta,
    *,
    success: bool,
    num_records_created: int,
    cat_4_errors_generated: int,
) -> bool:
    """Finalize the specific reparse metadata row once."""
    if reparse_file_meta is None or reparse_file_meta.data_file_id != data_file.id:
        return False
    with transaction.atomic():
        _locked_data_file(data_file)
        return _finish_reparse_locked(
            reparse_file_meta,
            success,
            num_records_created=num_records_created,
            cat_4_errors_generated=cat_4_errors_generated,
        )


def mark_stuck(
    data_file,
    note: str = "submission exceeded the stale threshold",
    logger_hook: Callable | None = None,
):
    """Atomically mark a still-active submission STUCK and revoke its parser."""
    from tdpservice.data_files.models import ReparseFileMeta

    with transaction.atomic():
        locked = _locked_data_file(data_file)
        current_state = coerce_submission_state(locked.state)
        if current_state not in STALE_ELIGIBLE_STATES:
            data_file.state = locked.state
            return data_file, False

        revoked_token = locked.current_parse_token
        log_fields = (
            {"revoked_parse_token": str(revoked_token)} if revoked_token else None
        )
        transition = _apply_transition_locked(
            locked,
            SubmissionState.STUCK,
            note=note,
            log_fields=log_fields,
        )
        _clear_parse_token_locked(locked)
        ReparseFileMeta.objects.filter(
            data_file=locked,
            finished=False,
        ).update(finished=True, success=False, finished_at=timezone.now())

    data_file.state = transition.next_state
    data_file.state_changed_at = locked.state_changed_at
    data_file.current_parse_token = None
    log_fields = (
        {"revoked_parse_token": str(revoked_token)} if revoked_token else None
    )
    _emit_transition_log(
        transition,
        data_file.id,
        logger_hook,
        log_fields,
        level="warning",
    )
    return data_file, True


@contextmanager
def parse_write_scope(data_file_id: int, parse_token) -> Iterator[None]:
    """Fence one production parser write with the DataFile ownership lock."""
    from tdpservice.data_files.models import DataFile

    normalized_token = _coerce_parse_token(parse_token)
    with transaction.atomic():
        data_file = DataFile.objects.select_for_update().get(pk=data_file_id)
        if (
            data_file.current_parse_token != normalized_token
            or data_file.state != SubmissionState.PARSE_STARTED
        ):
            raise StaleParseOwnership(
                f"Parser token {normalized_token} may no longer write "
                f"DataFile {data_file_id}."
            )
        yield


def assert_parse_owner(data_file_id: int, parse_token) -> None:
    """Fail fast when a parser task has lost ownership between writes."""
    from tdpservice.data_files.models import DataFile

    normalized_token = _coerce_parse_token(parse_token)
    if not DataFile.objects.filter(
        pk=data_file_id,
        current_parse_token=normalized_token,
        state=SubmissionState.PARSE_STARTED,
    ).exists():
        raise StaleParseOwnership(
            f"Parser token {normalized_token} no longer owns DataFile {data_file_id}."
        )


def record_shadow_parse_state(
    data_file,
    next_state,
    note: str = "",
    *,
    source: str | None = None,
    event_id: UUID | str | None = None,
    reparse_meta_id: int | None = None,
    task_name: str | None = None,
    log_fields: dict | None = None,
):
    """Persist non-authoritative shadow state and its separate audit history."""
    from tdpservice.data_files.models import ShadowDataFile

    if not isinstance(data_file, ShadowDataFile):
        raise ValueError("Shadow state transitions require a ShadowDataFile.")
    with transaction.atomic():
        locked = ShadowDataFile.objects.select_for_update().get(pk=data_file.pk)
        if locked.state == next_state:
            data_file.state = locked.state
            data_file.state_changed_at = locked.state_changed_at
            return data_file
        transition = _apply_transition_locked(
            locked,
            next_state,
            note=note,
            source=source,
            event_id=event_id,
            reparse_meta_id=reparse_meta_id,
            task_name=task_name,
            log_fields=log_fields,
        )
    data_file.state = locked.state
    data_file.state_changed_at = locked.state_changed_at
    _emit_transition_log(transition, data_file.id, None, None)
    return data_file


def record_synthetic_import_completed(data_file) -> bool:
    """Record the explicit lifecycle bypass used by statistical test-data imports."""
    with transaction.atomic():
        locked = _locked_data_file(data_file)
        previous_state = coerce_submission_state(locked.state)
        if previous_state == SubmissionState.PARSE_COMPLETED:
            return False
        transition = _transition_from_values(
            data_file=locked,
            previous_state=previous_state,
            next_state=SubmissionState.PARSE_COMPLETED,
            note="Synthetic statistical test-data import completed",
            source="management_command",
        )
        _save_transition_locked(locked, transition)
    data_file.state = SubmissionState.PARSE_COMPLETED
    data_file.state_changed_at = locked.state_changed_at
    logger.info(
        "Synthetic DataFile import completed",
        extra={
            "data_file_id": data_file.id,
            "previous_state": previous_state.value,
            "next_state": SubmissionState.PARSE_COMPLETED.value,
        },
    )
    return True


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


def _save_transition_locked(data_file, transition: TransitionRecord) -> None:
    """Save the state timestamp and history in the caller's transaction."""
    data_file.state = transition.next_state
    data_file.state_changed_at = timezone.now()
    data_file.save(update_fields=["state", "state_changed_at"])
    persist_datafile_state_transition(data_file, transition)
