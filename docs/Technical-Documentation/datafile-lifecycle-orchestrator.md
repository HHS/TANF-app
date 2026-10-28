# DataFile lifecycle controller

**Status:** Implemented; updated 2026-10-01 for #5971

**Related issues:** #5735, #5756, #5946, #5987

This document describes the current implementation. It supersedes the original
class-based orchestrator proposal; there is no `DataFileOrchestrator` class or
public `transition_datafile()` API.

## Ownership and entry points

[`submission_lifecycle.py`](../../tdrs-backend/tdpservice/data_files/submission_lifecycle.py)
is the exclusive production state controller. Callers express an intent rather
than selecting and persisting a target state. API and admin state fields are
read-only. The model supplies the initial `UPLOADED` default.

| Intent | Controller entry points |
| --- | --- |
| Virus scan | `start_datafile_av_scan`, `complete_datafile_av_scan` |
| Prepare a reparse | `prepare_datafile_for_reparse` |
| Claim and begin parsing | `claim_parse`, `begin_parse` |
| Record parser result or failure | `record_parse_outcome`, `record_parse_failure`, `record_parse_dispatch_failure` |
| Recover stalled work | `mark_stuck` |
| Recover a failed pre-destructive reparse request | `revert_reparse_request` |
| Repair legacy state from existing evidence | `backfill_legacy_datafile_state` |

The controller's `ALLOWED_TRANSITIONS` is the authoritative transition map.
The ordinary submission path is upload, scan, then parsing. A completed parse
has state `PARSE_COMPLETED` or `PARSED_WITH_ERRORS`; technical parser failure
has state `PARSE_FAILED`. Summary status and submission state are distinct:
a normally completed parser may reject records and still finish as
`PARSED_WITH_ERRORS`.

Every parse dispatch receives an ephemeral UUID stored in
`DataFile.current_parse_token`. Production summary, error, and record writes
are fenced against that token and `PARSE_STARTED`. `parse_write_scope`
provides the Python write boundary; Go checks the same ownership before writing.
A parse token is not the audit event ID.

## Python and Go responsibilities

Django owns production state in Python-only, Go-shadow, and Go-only modes.
The Go worker returns its outcome to Django's `post_parse` task, including
the table mode, parse token, and event ID. It does not update production
`DataFile.state`. Django owns lifecycle finalization and application-side
post-parse work.

Shadow state is separate and non-authoritative. Go's
`UpdateShadowDataFileState` rejects production tables and writes shadow state
and its audit row atomically. Django also finalizes shadow outcomes.
Shadow history uses a different content type, so a matching numeric file ID
does not merge shadow and production history.

## Atomic persistence and audit contract

State-changing operations lock and revalidate the database row. The controller
persists `state`, `state_changed_at`, and a `DataFileStateTransition` in the
same transaction. Audit persistence failure rolls back the state update.
Unchanged or stale operations do not create duplicate transitions.
These are durable audit records, not only application logs.

The shared transition payload includes:

- DataFile ID, section, and program type.
- Previous state, next state, and note/reason.
- Event ID, generated when none is supplied, shared by the log and audit row.
- Source, actor, reparse metadata ID, task name, and Celery task ID when available.
  Actor is stored on the audit row; the other correlation values are included
  in structured metadata. Task context falls back to the active Celery task.

History is exposed read-only in the production and shadow file admin pages.
Use content type, file ID, source, and event ID to correlate an attempt.
A recovery before batch metadata exists legitimately has no reparse metadata ID.

## Recovery boundaries

`revert_reparse_request` is a narrow exception to the forward transition map.
It locks the row, requires the current state to remain `REPARSE_REQUESTED`,
and permits only an original reparse-requestable state. If another operation
has advanced the file, it does nothing. It uses the same atomic persistence
and metadata builder as ordinary transitions, with
`recovery=pre_destructive_reparse_revert`. Missing source and reason default
to explicit reparse-recovery values. Available task/reparse IDs can be supplied.

This rollback is only for failure before destructive cleanup, such as a failed
backup or enqueue. After destructive cleanup begins, the worker must not
pretend the old parse data is intact by reverting to its former success state.
It leaves the request for failure handling and re-raises the error. Existing
backup/recovery procedures remain in force.

Celery beat checks active submissions hourly by default. Work older than one
day, or an unfinished reparse past `ReparseMeta.timeout_at`, becomes `STUCK`.
The earlier applicable deadline wins. The checker runs on the dedicated
`lifecycle` queue, locks and revalidates each candidate, revokes parser ownership,
and fails unfinished reparse metadata. A completion that wins the lock first
is not overwritten. Non-production E2E settings may shorten the timeout/cadence.
A stuck file can re-enter through `REPARSE_REQUESTED`.

## Legacy backfill procedure

The supported entry point is
[`scripts/backfill_datafile_states.py`](../../tdrs-backend/scripts/backfill_datafile_states.py).
Run from the backend environment with the intended database/storage settings:

```sh
# Read-only preview; review candidate IDs, inferred outcomes, and skip reasons.
python manage.py runscript backfill_datafile_states

# Explicitly apply reviewed repairs.
python manage.py runscript backfill_datafile_states --script-args apply=true
```

Use the normal operational change/backup process before applying to production.
This is an explicit administrative operation, not a data migration or deployment
side effect. Each candidate is rechecked under a row lock in both preview and
apply mode; only `UPLOADED` rows without a parser claim are eligible.

| Existing evidence | Inferred state |
| --- | --- |
| Accepted summary | `PARSE_COMPLETED` |
| Accepted-with-errors or partially accepted summary | `PARSED_WITH_ERRORS` |
| Rejected summary | `PARSE_FAILED` |
| No summary, attached file exists in storage | `VIRUS_SCAN_COMPLETED` |
| Pending/unknown summary, no attached file, or missing storage object | Skip |

The rejected-summary mapping preserves this legacy repair's historical policy;
it is not the normal parser-outcome policy described above. Storage presence is
historical evidence, not proof of a fresh virus scan.

Apply mode records one inferred repair from the actual old state to the inferred
state, with source `legacy_state_backfill`, a reason, and
`inferred=true` / `recovery=legacy_state_backfill`. It does not invent intermediate
scan/parse events, run a scan/parser, or modify summaries. State, timestamp, and
audit history commit together. Repeating the command skips repaired rows.

## Regression checks

The Python source guard scans application modules and operational scripts.
It checks attribute assignments (including variable-valued assignments),
`setattr`, common ORM updates and create/default forms, and bulk/update-fields
writes. The controller, test code, and migrations are excluded. The only
application attribute exception is `stt.state` in `populate_stts.py`, which is a
geographic relationship, not submission state. Synthetic imports use the
model's initial default and the controller's explicit synthetic-import intent.

The Go guard parses source string literals and checks production state updates,
including reordered SET columns and quoted/schema-qualified tables, as well as
the removed production writer function. Shadow writes remain allowed.

These are best-effort regression checks, not semantic proofs: dynamically
constructed SQL, new ORM APIs, aliases, and runtime field construction still
require review. Behavioral tests cover controller ownership, recovery boundaries,
audit rollback/correlation, and backfill dry-run/apply/idempotency.

```sh
# From tdrs-backend, in the backend test environment:
pytest tdpservice/data_files/test/test_submission_lifecycle.py \
  tdpservice/data_files/test/test_submission_state_controller_integration.py \
  tdpservice/data_files/test/test_backfill_datafile_states.py \
  tdpservice/data_files/test/test_reparse_files_task.py

# From tdrs-services/parser:
go test ./internal/db ./internal/server/celery
```

Go database integration tests additionally require a disposable
`TEST_DATABASE_URL`; see the [parser README](../../tdrs-services/parser/README.md).
