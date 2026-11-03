# Submission state machine for file processing

## Purpose

Uploaded files have a durable lifecycle independent of their per-parse summary.
This makes scan failures, parser failures, and stalled work distinguishable,
including before a summary exists and while a reparse replaces old results.

## Current implementation

[`submission_lifecycle.py`](../../../tdrs-backend/tdpservice/data_files/submission_lifecycle.py)
is the exclusive, function-based production state controller. Callers express
intent; they do not select or save a target state. Its `ALLOWED_TRANSITIONS`
map is authoritative. The old class/code sketch and `transition_datafile()`
API are superseded.

The ordinary flow is `UPLOADED → VIRUS_SCAN_STARTED → VIRUS_SCAN_COMPLETED →
PARSE_STARTED`. Scan failure ends at `VIRUS_SCAN_FAILED`; parsing ends at
`PARSE_COMPLETED`, `PARSED_WITH_ERRORS`, or `PARSE_FAILED`.
Reparse preparation enters `REPARSE_REQUESTED` before parsing begins.
Summary status is not submission state: record rejection after a completed
parse differs from a technical parser failure.

The controller locks and revalidates rows, then saves state, its
`state_changed_at` timestamp, and a `DataFileStateTransition` audit record
atomically. Audit rows survive reparse cleanup and are visible read-only in
Django admin. Structured transition logs share their event ID and context with
the persisted audit. Production parser writes are separately fenced by
`DataFile.current_parse_token`; Go reports production outcomes to Django
instead of writing production state.

An hourly Celery beat task moves active work older than one day to `STUCK`.
An unfinished reparse also becomes stuck at its `ReparseMeta.timeout_at`
deadline if that is earlier. The dedicated `lifecycle` queue keeps timeout
control available while a parser is occupied. Non-production E2E settings may
shorten the timeout and cadence. Stuck work can re-enter through
`STUCK → REPARSE_REQUESTED → PARSE_STARTED`.

## Explicit exceptions and operational guidance

Pre-destructive reparse rollback and legacy-state repair bypass the ordinary
forward map through narrowly scoped controller intents. They still use the
shared atomic audit path. Rollback must not restore a success state after
destructive cleanup. Legacy repairs record inferred evidence rather than
claiming that a scan or parse just ran.

See the [lifecycle controller guide](../datafile-lifecycle-orchestrator.md)
for the current intent APIs, production/shadow ownership, recovery metadata,
source-guard limitations, and dry-run/explicit-apply backfill procedure.
