"""One-time backfill of legacy DataFile submission states.

Usage
-----
Dry-run (default, prints what would change without writing)::

    ./manage.py runscript backfill_datafile_states

Apply changes::

    ./manage.py runscript backfill_datafile_states --script-args apply=true

The ``apply`` flag accepts: true/false, yes/no, 1/0, or the bare word
``apply``. It may be passed positionally (``--script-args true``) or as a
key=value pair (``--script-args apply=true``). Anything else is treated as
dry-run.

Behavior
--------
Scans ``DataFile`` rows currently in the ``UPLOADED`` state and, based on
the related ``DataFileSummary.status`` (or the presence of a stored file
when no summary exists), transitions each row forward through the
submission lifecycle to its correct terminal state. Pending summaries and
rows with no recoverable evidence are skipped. A final counts dict is
printed at the end.
"""

from django.db import transaction

from tdpservice.data_files.enums import SubmissionState
from tdpservice.data_files.models import DataFile
from tdpservice.data_files.submission_lifecycle import transition_datafile
from tdpservice.parsers.models import DataFileSummary

ONLY_UPLOADED = True

STATUS_TO_STATE = {
    DataFileSummary.Status.ACCEPTED: SubmissionState.PARSE_COMPLETED,
    DataFileSummary.Status.ACCEPTED_WITH_ERRORS: SubmissionState.PARSED_WITH_ERRORS,
    DataFileSummary.Status.PARTIALLY_ACCEPTED: SubmissionState.PARSED_WITH_ERRORS,
    DataFileSummary.Status.REJECTED: SubmissionState.PARSE_FAILED,
}

TRUTHY = {"1", "true", "t", "yes", "y", "apply"}


def _parse_apply(args):
    """Parse the APPLY flag from runscript --script-args.

    Accepts either a positional value (e.g. ``true``) or ``apply=true``.
    Defaults to False (dry-run) when not provided.
    """
    for arg in args:
        if arg is None:
            continue
        value = arg.split("=", 1)[1] if "=" in arg else arg
        return value.strip().lower() in TRUTHY
    return False


def _resolve_target_state(df):
    """Return ``(target_state, reason, skip_message)`` for a DataFile.

    ``target_state`` is None when the row should be skipped; ``skip_message``
    explains why (or is empty when the row is actionable).
    """
    summary = getattr(df, "summary", None)

    if summary:
        if summary.status == DataFileSummary.Status.PENDING:
            return None, "", f"SKIP {df.id}: summary is Pending"

        target_state = STATUS_TO_STATE.get(summary.status)
        reason = f"summary status is {summary.status}"
        if target_state is None:
            return None, reason, f"SKIP {df.id}: no target state for {reason}"
        return target_state, reason, ""

    if not df.file or not df.file.name:
        return None, "", f"SKIP {df.id}: no summary and no stored file attached"

    if not df.file.storage.exists(df.file.name):
        return (
            None,
            "",
            f"SKIP {df.id}: no summary and stored file not found: {df.file.name}",
        )

    return SubmissionState.VIRUS_SCAN_COMPLETED, "no summary, stored file exists", ""


def _walk_to_target_state(locked, target_state):
    """Walk ``locked`` through legal lifecycle transitions to ``target_state``."""
    note = "one-time legacy state backfill"
    if target_state in {
        SubmissionState.PARSE_COMPLETED,
        SubmissionState.PARSED_WITH_ERRORS,
        SubmissionState.PARSE_FAILED,
    }:
        transition_datafile(locked, SubmissionState.VIRUS_SCAN_STARTED, note=note)
        transition_datafile(locked, SubmissionState.VIRUS_SCAN_COMPLETED, note=note)
        transition_datafile(locked, SubmissionState.PARSE_STARTED, note=note)
    elif target_state == SubmissionState.VIRUS_SCAN_COMPLETED:
        transition_datafile(locked, SubmissionState.VIRUS_SCAN_STARTED, note=note)

    transition_datafile(locked, target_state, note=note)


def _apply_target_state(df_id, target_state, counts):
    """Re-lock ``df_id`` and transition it to ``target_state`` if still safe."""
    with transaction.atomic():
        locked = DataFile.objects.select_for_update().get(id=df_id)

        if locked.state != SubmissionState.UPLOADED:
            counts["skipped"] += 1
            print(f"SKIP {locked.id}: state changed to {locked.state}")
            return

        _walk_to_target_state(locked, target_state)
        counts["updated"] += 1


def run(*args):
    """Backfill legacy DataFile submission states based on summary status."""
    # Dry-run:  ./manage.py runscript backfill_datafile_states
    # Apply:    ./manage.py runscript backfill_datafile_states --script-args apply=true
    apply = _parse_apply(args)
    print(f"Running in {'APPLY' if apply else 'DRY-RUN'} mode")

    qs = DataFile.objects.select_related("summary").order_by("id")
    if ONLY_UPLOADED:
        qs = qs.filter(state=SubmissionState.UPLOADED)

    counts = {"would_update": 0, "updated": 0, "skipped": 0}

    for df in qs.iterator():
        target_state, reason, skip_message = _resolve_target_state(df)
        if target_state is None:
            counts["skipped"] += 1
            print(skip_message)
            continue

        print(
            f"{'UPDATE' if apply else 'WOULD UPDATE'} {df.id}: "
            f"{df.state} -> {target_state.value} ({reason})"
        )

        if not apply:
            counts["would_update"] += 1
            continue

        _apply_target_state(df.id, target_state, counts)

    print(counts)
