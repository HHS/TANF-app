# Technical Memo: Refactoring Parsing and Reparsing in TANF Data Portal Backend

## 1. Purpose

This memo proposes a refactor of the **parsing** and **reparsing** pipelines in the TANF Data Portal backend (`tdrs-backend`). The goal is to:

- Reduce duplicated orchestration logic between initial parsing and reparsing
- Make parsing behavior easier to reason about, test, and extend
- Improve performance and observability for large-scale reparsing operations
- Clearly separate “what to parse” (selection) from “how to parse” (pipeline)
- Establish a stable contract (service + state machine) so new file types and policy changes do not require touching Celery tasks or ad hoc utilities.

### Why this refactor is beneficial
- **Single source of truth for parsing logic:** Today, behavior is split across parser classes, the Celery task, and reparse utilities. Moving to a ParsingService collapses side effects (status updates, summaries, error reports) into one place, reducing drift and regression risk.
- **Testability:** A service with clear inputs/outputs can be unit-tested without Celery, making it easier to cover both happy paths and failure modes. Reparsing can reuse the same entry point with explicit context.
- **Extensibility:** A factory-driven, class-based parser plus decoder abstraction makes it straightforward to add file types (for example, new CSV/XLSX variants) or program types without rewriting orchestration. SchemaManager and decoders become the main extension points.
- **Operational clarity:** With the submission state machine and centralized transitions, operators and users see consistent states (for example, uploaded, virus_scan_started, parse_started, parsed_with_errors, parsed_completed, completed) instead of implicit flags scattered across models.
- **Safer reparsing:** Consolidating reparse behavior (backups, deletions, status updates) through a dedicated reparse service and shared state transitions improves idempotency, makes resume/rollback safer, and keeps ReparseMeta/ReparseFileMeta in sync.
- **Observability:** Centralized logging and optional metrics around a single service boundary make it easier to trace a file journey, correlate errors, and measure performance (parse durations, error counts).
The recommendations are based on the current implementation in:

- `tdpservice/parsers/…`
- `tdpservice/scheduling/parser_task.py`
- `tdpservice/search_indexes/reparse.py`
- `tdpservice/search_indexes/utils.py`
- `tdpservice/search_indexes/models/reparse_meta.py`
- `tdpservice/data_files/models.py` (especially `DataFile` and `ReparseFileMeta`)


## 2. Current Architecture (High-Level)

### 2.1 Initial parsing flow

**Entry point:** a TANF/SSP/TRIBAL/FRA data file is uploaded (`DataFile` instance created).

**Core components:**

- **Celery task:** `tdpservice/scheduling/parser_task.parse_data_file`
  - Looks up the `DataFile`
  - Uses `ParserFactory` to get the correct parser class for the file’s program type
  - Calls parser methods (e.g., `parse_and_validate()`)
  - Updates `DataFileSummary` / status flags
  - Generates error reports via `ErrorReportFactory`
  - Sends notification emails (`send_data_submitted_email`)
  - If the parse is part of a reparse run, it also updates `ReparseFileMeta`

- **Parser infrastructure:**
  - `tdpservice/parsers/factory.ParserFactory`
  - `tdpservice/parsers/parser_classes/base_parser.BaseParser`
  - Concrete parsers:
    - `TanfDataReportParser`
    - `FRAParser`
    - `ProgramAuditParser`
  - `SchemaManager` (`schema_manager.py`) to manage program- and section-specific schema
  - `ErrorGeneratorFactory` and `ParserError` to generate and persist row-level errors
  - `DataFileSummary` to track high-level outcomes (record counts, error counts)

**Characteristics:**
- “Initial parse” logic is **implicitly defined** by the behavior inside `parse_data_file` and the individual parser classes.
- The Celery task contains non-trivial orchestration logic: logging, error handling, and special cases for reparse runs.


### 2.2 Reparsing flow

Reparsing is used to “clean and reprocess” existing data files, usually when schemas or validation logic change.

**Core components:**

- **Reparse orchestration:** `tdpservice/search_indexes/reparse.py`
  - User / admin triggers some “clean and reparse” behavior (fiscal year, quarter, optional filters)
  - Uses helpers from `tdpservice/search_indexes/utils.py` and `tdpservice/search_indexes/util.py`:
    - `backup(...)` → creates a DB backup
    - `delete_associated_models(...)` → deletes records associated with the selected files (ParserError, DataFileSummary, index rows, etc.)
    - `calculate_timeout(...)` / `assert_sequential_execution(...)` → safety checks for long-running reparses
    - `count_total_num_records(...)` / `count_all_records(...)` → record-count snapshots

- **Meta tracking models:**
  - `ReparseMeta` (`tdpservice/search_indexes/models/reparse_meta.py`)
    - Represents a single “reparse run” (with fields like `timeout_at`, `finished`, `success`, `total_num_records_initial`, `total_num_records_after`, etc.)
    - Aggregates related `ReparseFileMeta` records
  - `ReparseFileMeta` (`tdpservice/data_files/models.py`)
    - Represents the parse status of a single `DataFile` within a reparse run (finished, success, record counts, error counts)

- **Scheduling reparses:**
  - Once backup and deletion are done, `reparse.py` calls into `parser_task` for each `DataFile` to schedule Celery tasks for reparsing.
  - The same `parse_data_file` task is used, but with additional `reparse_id` context that ties the parse to a `ReparseMeta` / `ReparseFileMeta` pair.

**Characteristics:**
- Reparsing logic is spread across:
  - `search_indexes/reparse.py`
  - `search_indexes/utils.py`
  - `parser_task.parse_data_file`
  - The parsers and error-reporting logic
- `ReparseMeta` / `ReparseFileMeta` add an extra dimension of lifecycle and state, but much of the behavior to maintain them lives in the Celery task.


## 3. Pain Points & Risks

From a maintainability and performance perspective, several issues stand out:

### 3.1 Duplicated orchestration between “parse” and “reparse”

- The **initial parsing path** and the **reparsing path** both:
  - Determine which files to parse
  - Manage database state (deleting old records, updating summaries)
  - Schedule Celery tasks
  - Generate logs and metrics
- However, the logic to do this is split across multiple modules, and the reparsing path has its own backup / cleanup orchestration.
- When schemas or error-handling rules change, engineers must remember to update both flows, which increases the risk of subtle inconsistencies.

### 3.2 Tight coupling to Celery and logging

- `parse_data_file` is both a Celery task and a “business service”:
  - It contains domain logic (how we parse, validate, update summaries, etc.)
  - It also contains infrastructure concerns (Celery wiring, logging, email notifications, file rotation).
- This makes unit testing harder and encourages direct calls to the Celery task instead of to a clear, reusable parsing service.

### 3.3 Reparsing logic is scattered and not obviously idempotent

- `search_indexes/reparse.py` performs several responsibilities:
  - Safety checks (sequential execution, timeouts)
  - Backup orchestration
  - Bulk deletion of associated records
  - Scheduling reparse tasks for each `DataFile`
- Much of this logic operates directly on the DB and logging functions, which makes it harder to reason about/retry safely.
- While `ReparseMeta` / `ReparseFileMeta` provide state tracking, the actual transitions are implemented in different modules, making it non-obvious how to safely resume or inspect a partially finished reparse run.

### 3.4 Performance & operational concerns on large datasets

- `count_total_num_records(...)`, `count_all_records(...)`, and bulk deletions may become expensive as datasets grow.
- Parsing and reparsing touch several related tables (DataFile, ParserError, DataFileSummary, index tables, etc.), so the order and batching of operations matters for performance and locking behavior.
- Today, these concerns are embedded in the reparse utilities and Celery task without a single place to tune or monitor the pipeline behavior.


## 4. Proposed Refactor: Single-File Parsing Service + Reparse Orchestration Service

The core idea is to have a **single-file parsing service** that owns all parsing side effects for one `DataFile`, and a **reparse orchestration service** that manages reparse runs and delegates per-file work to the parsing service. This keeps SRP and makes the hierarchy explicit:

- The Celery task (`parse_data_file`) only wires arguments/logging and calls the parsing service.
- The reparse service manages `ReparseMeta` / `ReparseFileMeta` lifecycle and calls the parsing service for each file in a reparse run.
- No other caller should reach directly into parser classes or touch reparse metadata.


### 4.1 Introduce a `ParsingService` (single file only)

Create a new module, for example:

- `tdpservice/parsing/service.py` or
- `tdpservice/parsers/service.py`

with a class like:

```python
class ParsingService:
    def __init__(self, *, logger, now_fn=timezone.now):
        self.logger = logger
        self.now_fn = now_fn

    def parse_data_file(self, data_file_id: int) -> DataFileSummary:
        """
        Orchestrate the full lifecycle for parsing a single DataFile.

        - Load DataFile and related metadata
        - Select parser via ParserFactory
        - Invoke parser.parse_and_validate()
        - Update DataFileSummary / DataFile status
        - Generate error report
        - Return the refreshed DataFileSummary (no awareness of reparse metadata)
        """
```

This service should encapsulate **what it means** to fully process a `DataFile`, regardless of why it is being parsed (initial submit or reparse).


### 4.2 Make Celery task a thin wrapper around the service

Refactor `tdpservice/scheduling/parser_task.parse_data_file` to:

- Parse out its Celery-specific concerns (arguments, retries, logging context)
- Delegate the core work to `ParsingService.parse_data_file`

Example (conceptually):

```python
@shared_task(bind=True)
def parse_data_file(self, data_file_id: int, reparse_id: int | None = None):
    logger = get_task_logger(__name__)
    service = ParsingService(logger=logger)
    service.parse_data_file(data_file_id)
```

This keeps Celery wiring and logging but moves domain logic into the service.


### 4.3 Introduce a `ReparseService` (orchestration + metadata)

Refactor `tdpservice/search_indexes/reparse.py` and `search_indexes/utils.py` so that they:

1. Determine **which DataFiles** should be reparsed (by fiscal year, quarter, program type, STT, etc.).
2. Perform backup operations (if needed).
3. Clean out associated records (ParserError, summaries, index rows) in a coherent, batched way.
4. For each file, create/update `ReparseFileMeta`, then invoke `ParsingService.parse_data_file(...)`.
5. Aggregate per-file outcomes back into `ReparseMeta` (finished, success, counts).

`ReparseService` owns all `ReparseMeta` / `ReparseFileMeta` transitions; `ParsingService` stays focused on parsing a single file.

This makes state transitions explicit and easier to test, and avoids scattering them between the Celery task and reparse utilities.


### 4.5 Improve testability & observability

Once parsing and reparsing are routed through a single service class:
- **Unit tests** can exercise `ParsingService` directly using a small in-memory or test DB dataset.
- **Integration tests** can cover:
  - Initial parse of a sample file
  - Reparse run across a few files
  - Recovery from a mid-run failure
- Logging can be standardized around a single logger/context, making it easier to trace parsing results in logs or APM tooling.


## 5. Suggested Implementation Phases

To de-risk the refactor, implement in small, incremental steps:


### Phase 1 – Document & stabilize current behavior

- Capture current parsing and reparsing flows in sequence diagrams or text:
  - How `parse_data_file` is called
  - Which tables are touched and in what order
  - How ReparseMeta / ReparseFileMeta are created and updated
- Add any missing indexes or small performance improvements that are clearly safe (see separate performance tickets).


### Phase 2 – Introduce `ParsingService` without changing behavior

- Extract the body of `parse_data_file` into `ParsingService.parse_data_file`, keeping behavior identical.
- The Celery task delegates to the service, but inputs/outputs remain unchanged.
- Add tests that assert the service produces the same side effects as the existing Celery task for a small fixture.


### Phase 3 – Wire reparsing through `ParsingService`

- Refactor `search_indexes/reparse.py` and `search_indexes/utils.py` so that they:
  - Only perform backup + selection + deletion + Celey scheduling
  - Never run parsing logic directly
- Ensure that `ReparseMeta` / `ReparseFileMeta` updates are driven by `ReparseService` and not by ad-hoc logic outside the service.


### Phase 4 – Clean up and harden

- Remove now-dead code paths or duplicated logic.
- Add better failure handling and idempotency guarantees for reparse runs.

#### Phase 4 – Reparse hardening checklist (explicit requirements)

- **Separate batch vs single-file logic**
  - `ParsingService` owns exactly one `DataFile` parse end-to-end.
  - `ReparseService` owns reparse orchestration for *N files* and is the only place that updates `ReparseMeta` / `ReparseFileMeta`.
- **Idempotent reparse runs**
  - Define what happens if the same reparse is triggered twice (default: skip finished files; optional: force-restart with a new attempt id).
  - Ensure a reparse run does not double-create or double-count `DataFileSummary`, `ParserError`, or error reports.
- **Explicit reparse attempt tracking**
  - Record an `attempt` number (or `run_id`) per `DataFile` within a reparse so we can distinguish first-run vs retry outputs.
  - Avoid overwriting debugging signals (timestamps, success/failure) without keeping attempt history.
- **Batch progress aggregation**
  - Store or compute counts by child state: `pending`, `in_progress`, `succeeded`, `failed`, `stuck`, `canceled`.
  - Provide a derived overall reparse status for admin visibility and logs (with explicit precedence rules).
- **Better failure handling**
  - Decide policy for partial failures (recommended: continue processing remaining files; batch completes with failures).
  - Persist failure context on file meta (stage, exception type/message) and surface a summarized view on the reparse meta.
- **Stuck detection + recovery**
  - Track `started_at` and a “last progress” timestamp per file (e.g., `last_state_change_at` / `heartbeat_at`).
  - If a file remains in an active stage past a threshold, mark it `stuck` and provide a clear operator action (retry, fail, or cancel).
- **Concurrency controls**
  - Prevent two reparses from processing the same `DataFile` concurrently (DB guard/locking or explicit “in progress” ownership).
  - Optional: chunk large reparses to avoid overwhelming workers and to improve progress reporting.
- **Make side effects configurable**
  - Allow `ReparseService` to control whether to send submission emails and whether/when to regenerate error reports.
  - Default behavior: do not send “data submitted” emails for reparses unless explicitly requested.
- **Transactional boundaries**
  - Ensure per-file “start” and “finish” updates are atomic and durable even if a worker crashes mid-run.
  - Prefer explicit transactions around metadata updates so reparse progress cannot end up partially written.
- Add regression tests for:
  - Incremental reparsing (subset of files, STT-specific)
  - Large batches (e.g., dozens/hundreds of files)


## 6. Expected Benefits

1. **Reduced duplication**  
   Single source of truth for parsing logic, regardless of whether it is an initial parse or a reparse.

2. **Easier reasoning and debugging**  
   Parsing behavior is concentrated in `ParsingService`; reparse orchestration just chooses “what” to parse.

3. **Better testability**  
   Service-oriented design enables targeted unit tests instead of having to go through Celery + management commands for every behavior change.

4. **Improved performance tuning**  
   Backup, deletion, and parsing steps are separated more clearly, making it easier to profile and optimize the heaviest operations.

5. **Lower operational risk**  
   A more explicit lifecycle for ReparseMeta / ReparseFileMeta, with a single place where their states are updated, makes it easier to detect and recover from partial failures.
