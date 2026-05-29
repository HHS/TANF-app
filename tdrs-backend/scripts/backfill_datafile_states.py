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


def run(*args):
    """Backfill legacy DataFile submission states based on summary status."""
    # Dry-run:  ./manage.py runscript backfill_datafile_states
    # Apply:    ./manage.py runscript backfill_datafile_states --script-args apply=true
    apply = _parse_apply(args)
    print(f"Running in {'APPLY' if apply else 'DRY-RUN'} mode")

    qs = DataFile.objects.select_related("summary").order_by("id")
    if ONLY_UPLOADED:
        qs = qs.filter(state=SubmissionState.UPLOADED)

    counts = {
        "would_update": 0,
        "updated": 0,
        "skipped": 0,
    }

    for df in qs.iterator():
        target_state = None
        reason = ""

        summary = getattr(df, "summary", None)

        if summary:
            if summary.status == DataFileSummary.Status.PENDING:
                counts["skipped"] += 1
                print(f"SKIP {df.id}: summary is Pending")
                continue

            target_state = STATUS_TO_STATE.get(summary.status)
            reason = f"summary status is {summary.status}"

        else:
            if not df.file or not df.file.name:
                counts["skipped"] += 1
                print(f"SKIP {df.id}: no summary and no stored file attached")
                continue

            if not df.file.storage.exists(df.file.name):
                counts["skipped"] += 1
                print(f"SKIP {df.id}: no summary and stored file not found: {df.file.name}")
                continue

            target_state = SubmissionState.VIRUS_SCAN_COMPLETED
            reason = "no summary, stored file exists"

        if target_state is None:
            counts["skipped"] += 1
            print(f"SKIP {df.id}: no target state for {reason}")
            continue

        print(f"{'UPDATE' if apply else 'WOULD UPDATE'} {df.id}: {df.state} -> {target_state.value} ({reason})")

        if not apply:
            counts["would_update"] += 1
            continue

        with transaction.atomic():
            locked = DataFile.objects.select_for_update().get(id=df.id)

            if locked.state != SubmissionState.UPLOADED:
                counts["skipped"] += 1
                print(f"SKIP {locked.id}: state changed to {locked.state}")
                continue

            if target_state in {
                SubmissionState.PARSE_COMPLETED,
                SubmissionState.PARSED_WITH_ERRORS,
                SubmissionState.PARSE_FAILED,
            }:
                transition_datafile(
                    locked,
                    SubmissionState.VIRUS_SCAN_STARTED,
                    note="one-time legacy state backfill",
                )
                transition_datafile(
                    locked,
                    SubmissionState.VIRUS_SCAN_COMPLETED,
                    note="one-time legacy state backfill",
                )
                transition_datafile(
                    locked,
                    SubmissionState.PARSE_STARTED,
                    note="one-time legacy state backfill",
                )

            elif target_state == SubmissionState.VIRUS_SCAN_COMPLETED:
                transition_datafile(
                    locked,
                    SubmissionState.VIRUS_SCAN_STARTED,
                    note="one-time legacy state backfill",
                )

            transition_datafile(
                locked,
                target_state,
                note="one-time legacy state backfill",
            )
            counts["updated"] += 1

    print(counts)
