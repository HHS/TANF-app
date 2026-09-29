# Submission State Machine for File Processing

## Purpose
Define and enforce a clear lifecycle for uploaded files so parsing and triage share a consistent contract. This is a precursor to the parser refactor to avoid churn and make status handling predictable.

## Current implementation

`data_files/submission_lifecycle.py` is the exclusive production state
controller. State-changing callers use intent methods, current-state age is
stored in `DataFile.state_changed_at`, and production parser writes are fenced
by the UUID in `DataFile.current_parse_token`. An hourly Celery beat task moves
active work older than one day to `stuck`; an unfinished reparse is also moved
to `stuck` when its `ReparseMeta.timeout_at` deadline expires, even if the
generic one-day window has not elapsed. The task is routed to a dedicated
`lifecycle` worker, keeping timeout control available even while the parser
worker is occupied. Non-production E2E runs may override the one-day timeout
and hourly cadence. A stuck file can be reparsed through
`stuck -> reparse_requested -> parse_started`.

## Why a state machine (and what it adds)
- **Guardrails for future changes:** Even though end users cannot alter parsing, developers can. An explicit transition map prevents drift when we add steps (AV scan, retries, change requests) or touch the parser/reparser code paths. Instead of silently landing in an inconsistent state, we fail fast on illegal transitions.
- **Durable, user-visible lifecycle:** `DataFileSummary` is per-parse and can be deleted/recreated during reparses. `DataFile.state` is a durable record of the submission lifecycle (upload -> scan -> parse) that survives reparses and exists even before a summary is created.
- **Better triage and alerts:** Granular states (for example `virus_scan_started` vs `parse_started`) make it obvious where a file stalled without scraping logs. They enable targeted alerts (for example, "stuck in `parse_started` > 15m") and safer retries.

## States
`uploaded` -> `virus_scan_started` -> (`virus_scan_failed` | `virus_scan_completed`) -> `parse_started` -> (`parse_failed` | `parsed_with_errors` | `parse_completed`) -> `completed`.

Any active state can transition to `canceled`. A file that exceeds time thresholds in an active state is marked `stuck` (and may later be escalated to `failed` by policy).

Note: parsing can write records in batches. This proposal does not model a separate ingest phase yet.

## Allowed transitions (code sketch)
```python
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable


class SubmissionState(str, Enum):
    UPLOADED = "uploaded"
    VIRUS_SCAN_STARTED = "virus_scan_started"
    VIRUS_SCAN_FAILED = "virus_scan_failed"
    VIRUS_SCAN_COMPLETED = "virus_scan_completed"
    PARSE_STARTED = "parse_started"
    PARSE_FAILED = "parse_failed"
    PARSED_WITH_ERRORS = "parsed_with_errors"
    PARSE_COMPLETED = "parse_completed"
    STUCK = "stuck"
    COMPLETED = "completed"
    CANCELED = "canceled"


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


class InvalidTransition(Exception):
    ...


@dataclass
class SubmissionLifecycle:
    state: SubmissionState
    history: list[str] = field(default_factory=list)

    def transition(self, next_state: SubmissionState, note: str = "") -> None:
        if next_state not in ALLOWED_TRANSITIONS[self.state]:
            raise InvalidTransition(f"{self.state} -> {next_state} not allowed")
        self.history.append(f"{self.state} -> {next_state}: {note}")
        self.state = next_state
