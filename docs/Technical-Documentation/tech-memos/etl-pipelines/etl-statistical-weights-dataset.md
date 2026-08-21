# ETL Calculation Architecture

- **Status:** Review - implementation guide
- **Scope:** TDP-managed ETL pipelines, beginning with the TANF statistical weights dataset
- **Last updated:** 2026-06-30

---

## Purpose

This document describes the architecture for moving ETL-style calculations into TDP. The first implementation slice is the Section 1 statistical weights dataset for TANF, SSP, and Tribal TANF. The architecture should let the team deliver that dataset quickly while establishing a reusable DAG-shaped ETL module for later feedback reports and generic ETL style workloads.

For the system-level architecture across TANF, SSP, Tribal TANF, FRA, and future report families, start with `etl-reporting-system-architecture.md`.

Use this document when implementing:

- statistical weights generation,
- admin-triggered ETL runs,
- scheduled ETL runs,
- ETL run history and QA output,
- future weighted or unweighted feedback report calculations.

---

## Current State

The prototype scripts in `tdrs-backend/etl_scripts/` are notebook-export SQL files. They contain useful business logic, but they are not production modules:

- they mix SQL, Databricks/Spark SQL constructs, notebook cells, and `%python`,
- several values are hardcoded, including fiscal periods and sandbox table names,
- most outputs are temporary views,
- QA checks are query results, not persisted records,
- there is no run history, idempotency guard, retry path, or admin execution surface.

The scripts split into two related lanes:

| Script | Role |
| --- | --- |
| `generating_weights.sql` | Closest to issue #5699. Builds `s1`, `s3`, `s4`, `weight1`, final weights, and four QA checks. |
| `step1.sql` | Builds monthly `tan{ym}` data from TANF T1/T2/T3. |
| `step2.sql` | Builds weighted WPR summaries from monthly TAN data and weights. |
| `step3.sql` | Builds unweighted feedback-style tables from monthly TAN data. |
| `step4.sql` | Builds time-limit reports from TANF T1/T2. |
| `step5.sql` | Builds yearly TANF WPR rollups from prior weighted summary data. |

The backend already has useful foundations:

- Django and DRF for authenticated backend interfaces,
- Celery, Redis, and `django-celery-beat` for async and scheduled work,
- existing group and permission patterns for OFA System Admin, DIGIT Team, Data Analyst, and Regional Staff users,
- existing email helpers and SendGrid integration,
- S3-backed file models in the current `reports` app,
- parsed TANF, SSP, and Tribal TANF data in program-specific tables and Grafana-facing views,
- `STT` metadata, including `stt_code` and `sample`.

The current `reports` app should not own calculation logic. It stores, versions, bundles, distributes, and notifies for feedback report files. ETL calculation needs its own module, with the `reports` app used later only when a calculation produces downloadable report artifacts.

---

## Target Architecture

### Module Shape

Add a new backend Django app at `tdpservice.etl`. It owns approved calculation pipelines, run history, DAG execution, QA output, and durable computed datasets.

Planned layout:

```text
tdpservice/
  etl/
    apps.py
    models.py
    serializers.py
    urls.py
    views.py
    permissions.py
    tasks.py
    scheduler.py
    registry.py
    runner.py
    pipelines/
      base.py
      sources.py
      statistical_weights/
        __init__.py
        definition.py
        adapters.py
        candidates.py
        qa.py
        publishing.py
        nodes.py
    notifications.py
```

The external seam is intentionally small:

- admins create and inspect runs through DRF endpoints,
- `PipelineDefinition` defines the base interface for approved pipelines,
- Celery executes a pipeline-owned `chain`/`chord` Canvas for each run,
- pipeline definitions are code-defined and reviewed,
- nodes receive typed run context and write declared artifact manifests.


### Pipeline Registry

Pipeline definitions are code-defined classes. The base `PipelineDefinition` is an abstract interface that provides shared node lookup, duplicate node-key validation, and API serialization. Each concrete pipeline class owns its own parameter validation, output scope, node metadata, Celery Canvas, schedule metadata, and permission metadata.

A concrete pipeline definition declares:

- `key`, such as `statistical_weights`,
- `version`,
- display name and description,
- allowed parameters and validation rules,
- output scope construction,
- node metadata,
- executable Celery Canvas builder,
- schedule metadata,
- required Django permissions or groups.

Node definitions declare:

- node key,
- input contracts,
- output contracts,
- execution class,
- whether outputs are temporary, run-scoped, or durable,
- expected QA checks or row-count reporting.

`PipelineNode` is the execution interface for a node. Each concrete node owns its `execute(context)` behavior, while the shared `PipelineNode.run()` method claims and updates the matching `ETLNodeRun`, validates input artifact contracts, builds the run-scoped `NodeContext`, records row counts and metadata, and marks failures. `NodeContext` carries the pipeline run and available artifacts only. The Celery task boundary remains thin and serializable: `run_pipeline_node` receives the run ID and node key, reloads the definition, and calls `definition.nodes[node_key].run(pipeline_run)`.

The first implementation should use a lightweight internal run launcher. The base `PipelineDefinition` validates shared node metadata, and each concrete pipeline builds its own code-owned Celery Canvas for the run. Runner services create runs, launch the Canvas, and finalize run status; node execution happens through `PipelineNode.run()`:

| DAG shape | Celery primitive | Use |
| --- | --- | --- |
| Linear dependency | `chain` | Run ordered nodes where each node depends on the prior node's output. |
| Fan-out/fan-in dependency | `chord` | Run parallel header nodes, then run the body once after every header node succeeds. |

Concrete pipeline classes remain the executable DAG definitions. The registry only maps approved pipeline keys to those classes. Pipeline authors hand-write the Celery Canvas for each approved pipeline. Node metadata is limited to the details the registry and API need: node key and input/output contracts. The Canvas should make the DAG visible: linear dependencies use `chain`, and parallel fan-in uses `chord` with a single fan-in body task. Remaining downstream nodes continue from that body task through an immutable link chain when needed.

Celery tasks should receive stable identifiers: pipeline run ID and node key. Node and finalize signatures should be immutable (`.si`) so upstream return values and chord header results are not appended to task arguments. Tasks load run context and available artifact manifests from the database, validate declared input contracts, update `ETLNodeRun`, and persist any produced `ETLArtifact` manifests. The database remains the source of truth for orchestration state; Celery is the execution mechanism.


### Run Lifecycle

An ETL run moves through these states:

| Status | Meaning |
| --- | --- |
| `PENDING` | Run row exists; Celery task has not started execution. |
| `RUNNING` | At least one node is executing or ready to execute. |
| `SUCCEEDED` | Every required node succeeded and outputs were published. |
| `FAILED` | A required node failed. Published outputs remain unchanged unless publication had already completed transactionally. |
| `CANCELED` | Admin or scheduler canceled before successful publication. |

Node runs use:

- `PENDING`,
- `RUNNING`,
- `SUCCEEDED`,
- `FAILED`.

QA results use:

- `PASSED`,
- `WARNING`,
- `FAILED`.

`WARNING` means the pipeline can publish but humans should review the result. `FAILED` means the pipeline must not publish unless the pipeline definition explicitly marks the check as non-blocking.

### Run History Models

Add these models in `tdpservice.etl.models`:

#### `ETLPipelineRun`

Stores one execution of one approved pipeline.

Required fields:

- pipeline key,
- pipeline version,
- status,
- parameters as JSON,
- output scope as JSON,
- output scope key as a canonical SHA-256 hash,
- structured run metadata as JSON,
- trigger source: `ADMIN`, `SCHEDULED`, or `RETRY`,
- triggered-by user, nullable for scheduled runs,
- retry-of run, nullable,
- final output, nullable until publication succeeds,
- started_at,
- finished_at,
- error message,
- created_at,
- updated_at.

The output scope is the idempotency key. For statistical weights it is:

```text
pipeline=statistical_weights
fiscal_year=<year>
program=<TAN|SSP|TRIBAL>
section=1
```

Only one active run may exist for a given output scope. The implementation stores a canonical `output_scope_key` generated from sorted compact JSON and enforces uniqueness for `PENDING` and `RUNNING` runs at the database level.

#### `ETLNodeRun`

Stores one node execution inside a pipeline run.

Required fields:

- pipeline run,
- node key,
- status,
- dependency status summary,
- started_at,
- finished_at,
- input row count,
- output row count,
- error message,
- structured metadata as JSON.

#### `ETLQAResult`

Stores structured QA output.

Required fields:

- pipeline run,
- check key,
- status,
- summary,
- result payload as JSON,
- blocking flag,
- created_at.

QA output must be queryable by admins and suitable for inclusion in notification emails.

#### `ETLArtifact`

Stores run-scoped artifact manifests for both intermediate and final pipeline products. The manifest is the graph contract; large row payloads live in typed tables or future object storage, not in JSON fields.

Required fields:

- pipeline run,
- key,
- artifact role: `INTERMEDIATE` or `FINAL`,
- artifact kind: `DATASET`, `FILE`, or `SCALAR`,
- storage kind: `POSTGRES_TABLE`, `OBJECT`, or `INLINE_JSON`,
- table name, object key, or inline reference,
- schema key,
- schema version,
- version, nullable for non-versioned artifacts,
- row count,
- published flag,
- metadata as JSON,
- created_at.
- updated_at.

Each pipeline run has at most one artifact per key. Final statistical weights are represented by a final `ETLArtifact` with `artifact_role = FINAL`, `storage_kind = POSTGRES_TABLE`, `reference = StatisticalWeight._meta.db_table`, `version = <published version>`, and `published = true`. `ETLPipelineRun.final_output` points to that final artifact; final outputs are represented by artifact manifests rather than a separate output model.

Intermediate artifacts use the same manifest table with `artifact_role = INTERMEDIATE`. The statistical weights MVP uses table-backed intermediate artifacts for `weights.s1`, `weights.s3`, and `weights.s4`. These artifact manifests point at a typed staging table and carry the relevant slice metadata, such as `count_kind = S1`.

Use `INLINE_JSON` only for small scalar or metadata-style values. Do not store large intermediate datasets as JSON payloads.

#### `StatisticalWeightsCaseCount`

Stores run-scoped `s1`, `s3`, and `s4` aggregate rows for statistical weights in one typed table.

Required fields:

- pipeline run,
- count kind: `S1`, `S3`, or `S4`,
- STT code,
- reporting month,
- stratum, blank for `S3`,
- count.

The unique key is pipeline run, count kind, STT code, reporting month, and stratum. `S3` uses an empty string for stratum rather than `NULL` so uniqueness is deterministic. The artifact keys remain separate (`weights.s1`, `weights.s3`, `weights.s4`) even though they reference the same physical table; this keeps the graph contract readable while reducing staging model surface area.

### Statistical Weights Output Model

Add a durable weights table. It is a calculation output, not an uploaded file.

#### `StatisticalWeight`

Represents current and retained historical weights.

Required fields:

- fiscal year,
- reporting month,
- program,
- section,
- STT code,
- stratum,
- version,
- case count,
- cases,
- weight rounded to four decimals,
- pipeline run,
- published_at,
- retention_expires_at, nullable.

The grain is one row per STT, section, reporting month, stratum, and version.

Weights are versioned outputs. A rerun for the same output scope inserts a new version instead of updating row state or copying rows into a second table. Calculated fields are immutable after publication; retention metadata may be set when a later version supersedes the output.

Add a unique constraint across fiscal year, reporting month, program, section, STT code, stratum, and version.

The MVP retention rule is one month after replacement. The current version keeps `retention_expires_at` null. When a later version supersedes it, the publication transaction sets `retention_expires_at` on the older version. A scheduled cleanup can delete non-current versions whose `retention_expires_at` has passed.

Pipeline contracts should treat version as part of the output contract. The final `ETLArtifact` records the produced statistical-weights version for the run, and downstream nodes should consume that explicit artifact instead of independently calculating `MAX(version)` during a run. If external consumers need a current-only surface, expose a read-only view or query helper that selects the latest version per output scope.

### DRF Interface

Add backend endpoints under `/v1/etl/`:

| Method | Path | Behavior |
| --- | --- | --- |
| `GET` | `/v1/etl/pipelines/` | List approved pipeline definitions and parameter metadata. |
| `POST` | `/v1/etl/runs/` | Start an approved pipeline run. |
| `GET` | `/v1/etl/runs/` | List run history. |
| `GET` | `/v1/etl/runs/{id}/` | Show run status, nodes, QA results, artifact manifests, and final output. |
| `POST` | `/v1/etl/runs/{id}/retry/` | Retry a failed run if its output scope is not active. |

The create endpoint accepts:

```json
{
  "pipeline_key": "statistical_weights",
  "parameters": {
    "fiscal_year": 2026,
    "program": "TAN"
  }
}
```

For the weights MVP, the backend derives reporting months from the fiscal year and program. It should not require the admin to submit raw SQL or source table names.

### Permissions

Reuse the existing Django model-permission pattern used by `reports`.

MVP behavior:

- approved OFA System Admin users can list pipelines, start runs, retry failed runs, and inspect all run history,
- approved DIGIT Team users can inspect run history and may start runs if product confirms that DIGIT should have execution access,
- Data Analyst and Regional Staff users cannot start ETL runs,
- all endpoints require approved users.

The first implementation should add explicit `etl` model permissions and permission tests. If DIGIT execution access is still undecided at implementation time, default to view-only for DIGIT and execution for OFA System Admin.

### Execution Flow

Admin-triggered run:

1. DRF validates pipeline key and parameters against the registry.
2. DRF computes output scope.
3. DRF rejects the request if another active run has the same output scope.
4. DRF creates `ETLPipelineRun` and initial `ETLNodeRun` rows.
5. DRF queues the pipeline launch task with the run ID.
6. The launch task loads the pipeline definition and run row.
7. The concrete `PipelineDefinition` validates node metadata and builds the pipeline-owned Celery Canvas.
8. Celery executes node tasks with stable run/node identifiers.
9. Each node claims its `ETLNodeRun` under a database lock, then records status, row counts, metadata, and errors.
10. The chord body runs `run_weights_qa` once after all extract nodes succeed, then its immutable link chain runs publish, notify, and finalize.
11. QA nodes persist `ETLQAResult` rows.
12. Publication happens in a database transaction.
13. The run is marked `SUCCEEDED` or `FAILED`.
14. Notification email is sent.

Scheduled run:

1. Celery beat invokes a scheduler check daily.
2. The scheduler determines whether today is the first workday of the month.
3. If yes, it creates the same `ETLPipelineRun` as an admin-triggered run with trigger source `SCHEDULED`.
4. Duplicate active or successful runs for the same monthly scheduler key are skipped.

For MVP, "workday" means Monday through Friday. If federal holiday exclusion is required, add a code-owned holiday calendar or a small approved dependency before relying on the scheduler for production commitments.

---

## Statistical Weights MVP

### Goal

Produce a database-resident statistical weights dataset for a selected fiscal year and program. The first version calculates Section 1 weights only. The formula is shared across TANF, SSP, and Tribal TANF; program adapters provide the parsed source models, aggregate count field, `DataFile.program_type`, and QA STT scope.

### Source Inputs

Use database-backed data.

Required source models and metadata:

| Program | Active family model | Aggregate model | Stratum model | Aggregate count field | `DataFile.program_type` |
| --- | --- | --- | --- | --- | --- |
| TANF | `TANF_T1` | `TANF_T6` | `TANF_T7` | `NUM_FAMILIES` | `TAN` |
| SSP | `SSP_M1` | `SSP_M6` | `SSP_M7` | `SSPMOE_FAMILIES` | `SSP` |
| Tribal TANF | `Tribal_TANF_T1` | `Tribal_TANF_T6` | `Tribal_TANF_T7` | `NUM_FAMILIES` | `TRIBAL` |

Every run also uses submitted-file metadata from `data_files.DataFile` and STT metadata from `stts.STT`.

The first implementation should use backend-owned query helpers against the parsed-record models, joined through each record's `datafile` foreign key. Prefer Django ORM querysets for filtering, grouping, and simple aggregations. Use raw SQL only for query shapes that the ORM cannot express cleanly or that need measured performance improvements.

Do not depend on Grafana-facing views for the calculation path. Those views are useful for reporting access, reconciliation, and read-only output exposure, but the ETL pipeline should own its source-selection rules in code.

Source-selection rules must be explicit:

- selected fiscal year,
- selected program type,
- active case, aggregate, or stratum section as appropriate,
- non-program-audit files,
- latest accepted `DataFile` version per STT, quarter, program type, and section,
- parser lifecycle states approved for calculation.

The default accepted parser state should be `PARSE_COMPLETED`. If product or legacy parity requires including `PARSED_WITH_ERRORS`, document that decision in the pipeline definition and test it explicitly.

The first node declares three `DataFileSource` inputs, then uses the shared `DataFileSourceSnapshot` to snapshot the selected active, aggregate, and stratum `DataFile` IDs into `ETLPipelineRun.metadata["source_datafile_ids"]`. All later nodes read from that snapshot rather than recalculating "latest accepted" files. This keeps counts, QA, and publication stable if a newer file is accepted while a run is executing. The statistical weights pipeline fails validation if any required source family snapshots to an empty list; an empty source run must not reach publication as a successful zero-row output. The shared snapshot helper also rejects any source `DataFile` that is part of active reparse work, and reparse startup rejects files already snapshotted by active `PENDING` or `RUNNING` ETL runs. This disjointness rule applies to every future DataFile-backed pipeline that uses the shared snapshot helper. The snapshot helper is shared infrastructure for future pipelines; statistical weights only owns the source declarations.

The statistical weights implementation is split by responsibility under `tdpservice.etl.pipelines.statistical_weights`: `definition.py` owns parameter validation, output scope, shared node resources, node registration, and Celery Canvas declaration; `adapters.py` owns program-specific models and field names; `nodes.py` owns the concrete node subclasses, ORM extraction queries for `s1`, `s3`, and `s4`, and table-backed statistical-weights artifact persistence; and `candidates.py`, `qa.py`, and `publishing.py` own their respective domain behavior.

### DAG

The weights MVP pipeline is:

```text
validate_run_sources
  -> chord header(
       extract_active_family_counts,
       extract_aggregate_case_counts,
       extract_stratum_case_counts
     )
  -> run_weights_qa
  -> publish_weights
  -> notify_weights_run
```

The pipeline declares this as one pipeline-owned Canvas. Validation runs first. The three extract nodes run as the `chord` header. The chord body is the single fan-in node, `run_weights_qa`; its immutable link chain runs `publish_weights`, `notify_weights_run`, and `finalize_pipeline_run`.

Do not use a full `chain` as the chord body. In local Celery testing, using the whole QA-publish-notify-finalize chain directly as the chord body caused duplicate downstream task delivery. The safe shape is a single chord body task with the remaining chain attached through `link`.

Node responsibilities:

| Node | Responsibility |
| --- | --- |
| `validate_run_sources` | Validate fiscal year, program, section, and output scope; snapshot source `DataFile` IDs; fail when required source families have no accepted files. |
| `extract_active_family_counts` | Build `s1`: unique families by STT, reporting month, stratum; persist `weights.s1`. |
| `extract_aggregate_case_counts` | Build `s3`: aggregate cases by STT and reporting month; persist `weights.s3`. |
| `extract_stratum_case_counts` | Build `s4`: section cases by STT, reporting month, stratum for `TDRS_SECTION_IND = 1`; persist `weights.s4`. |
| `run_weights_qa` | Read persisted `s1`, `s3`, and `s4`; build candidates in memory; persist the four QA checks. |
| `publish_weights` | Read persisted `s1`, `s3`, and `s4`; rebuild candidates in memory; publish a new immutable weights version and record it as a final `ETLArtifact`; reject empty candidates. |
| `notify_weights_run` | Email run status, output, and QA summary to recipients. |

The implementation materializes `s1`, `s3`, and `s4` as table-backed `ETLArtifact` manifests. All three artifacts reference `StatisticalWeightsCaseCount`, with `metadata.count_kind` identifying the relevant slice. Candidates are not persisted as a database table or artifact because they are fully derived from `s1`, `s3`, `s4`, and run parameters. `PipelineNode.run()` validates declared input artifact contracts before calling `execute(context)`; a node with a missing input contract fails before its business logic runs.

### Calculation Rules

`s1`:

- source: active family records for the requested program,
- filter: selected fiscal year,
- grain: STT code, reporting month, stratum,
- value: count of distinct case numbers.

`s3`:

- source: aggregate records for the requested program,
- filter: selected fiscal year,
- grain: STT code, reporting month,
- value: `NUM_FAMILIES` for TANF and Tribal TANF; `SSPMOE_FAMILIES` for SSP.

`s4`:

- source: stratum records for the requested program,
- filter: selected fiscal year,
- filter: `TDRS_SECTION_IND = 1`,
- filter: `FAMILIES_MONTH > 0`,
- grain: STT code, reporting month, stratum,
- value: `FAMILIES_MONTH`.

Candidate weights:

- start from `s1`,
- left join `s3` by STT and reporting month,
- left join `s4` by STT, reporting month, and stratum,
- prefer `s4.cases` when present,
- otherwise use `s3.case_count`,
- use `GREATEST(s1.case_count, source cases)` so cases is never below observed T1 case count,
- exclude rows where cases is zero or case count is zero,
- `weight = ROUND(cases / case_count, 4)`.

Candidate rows are built in memory inside `run_weights_qa` and `publish_weights`. They are not passed through Celery result payloads and are not stored as JSON artifacts.

### QA Checks

QA logic lives in pipeline nodes. Persist the check results as `ETLQAResult` rows so admins can inspect them and notification emails can include them.

| Check | Description | Blocking |
| --- | --- | --- |
| `weights_row_counts` | Row counts for `s1`, `s3`, `s4`, and in-memory candidates. | No |
| `weights_missing_stts` | Required STTs missing from `s1`, `s3`, or program stratum `s4` for the reporting month under review. | Warning |
| `weights_active_aggregate_pair_mismatch` | STT/reporting-month pairs present in `s1` but not `s3`, or vice versa. | Warning |
| `weights_active_stratum_mismatch` | Program stratum STT/reporting-month/stratum pairs present in `s1` but not `s4`, or vice versa. | Warning |

Required active/aggregate STTs come from `STT` reference records, not from a hard-coded list. TANF uses state and territory entities. SSP uses state and territory entities with `ssp = true`. Tribal TANF uses tribe entities. Stratum QA uses `sample = true` for TANF, `sample = true` and `ssp = true` for SSP, and tribe entities for Tribal TANF.

### Publication And Idempotency

Weights publication must be transactional.

For output scope `<program> + Section 1 + fiscal year`:

1. Compute table-backed `s1`, `s3`, and `s4` under the run ID.
2. Build candidates in memory and persist QA under the run ID.
3. If a blocking QA check fails, mark the run `FAILED` and do not publish.
4. Rebuild candidates in memory for publication.
5. Lock or otherwise serialize publication for the output scope.
6. Determine the next output version as the current max version for the scope plus one.
7. Set `retention_expires_at` on the previous current version if it does not already have a retention date.
8. Insert the new `StatisticalWeight` rows with the current run ID, new version, and null `retention_expires_at`.
9. Create or update a final `ETLArtifact` row for `statistical_weights` with the output scope, row count, table reference, and version.
10. Mark the final artifact as published and set `ETLPipelineRun.final_output`.
11. Mark the run `SUCCEEDED`.

If any step fails before publication commits, existing published weights must remain available.

Active-run idempotency is enforced separately from publication versioning. `ETLPipelineRun.output_scope_key` prevents duplicate `PENDING` or `RUNNING` runs for the same canonical output scope, while completed or failed runs remain available for history and reruns.

Follow-on DAG nodes consume the final `ETLArtifact` from the dependency they declare. For example, a weighted WPR node should receive `statistical_weights.version = 3` from the artifact manifest and query that exact version. This keeps a DAG run reproducible and prevents different nodes from resolving "latest weights" at different times.

### Notifications

After every weights run, send email to:

- approved OFA System Admin users,
- approved DIGIT Team users.

The email should include:

- pipeline name,
- fiscal year,
- program,
- run ID,
- run status,
- trigger source,
- output version,
- row count,
- QA summary,
- link to `/v1/etl/runs/{id}/`.

Detailed QA payloads stay in the database; the email should summarize them.

### Grafana Access

The final `statistical_weights` table or an approved read-only view over it must be added to the Grafana read-only grant path. The existing Grafana role scripts support explicit tables/views; extend that list only after the output table name is finalized.

---

## Future Extension Path

The architecture should support additional pipelines without changing the node execution interface.

Likely next pipelines:

- weighted TANF WPR summaries,
- unweighted TANF feedback tables,
- TANF time-limit report tables,
- yearly WPR rollups,
- packaged feedback report files published through `ReportFile`.

Future report-file publication should add nodes after calculation:

```text
calculation nodes
  -> render_report_artifacts
  -> package_stt_feedback_reports
  -> publish_report_files
  -> notify_report_available
```

`publish_report_files` should reuse the existing `ReportFile` model and permissions so the current reports download and versioning behavior continues to apply.

Program-specific behavior lives behind adapters at the statistical weights node level. TANF, SSP, and Tribal TANF share one pipeline key, run launcher, run history, QA storage, notification path, and output publication rule set. The run parameter uses exact `DataFile.ProgramType` values: `TAN`, `SSP`, or `TRIBAL`; display aliases such as `TANF` or `Tribal TANF` are not accepted as request values.

---

## Failure Modes

| Failure | Required behavior |
| --- | --- |
| Invalid parameters | Reject before creating a pipeline runner task. |
| Active run already exists for scope | Reject or return the active run reference. |
| Missing source data | Fail validation before extraction when a required source family has no accepted files. |
| Source/reparse overlap | Reject ETL validation or reparse startup before either process mutates source data. |
| Empty in-memory candidates | Fail publication and preserve the previous published output. |
| Node exception | Mark node and pipeline failed; preserve error details. |
| Publication failure | Roll back publication transaction; keep previous published output. |
| Notification failure | Mark run succeeded if publication succeeded, but record notification failure in metadata/logs. |
| Retry requested for unsafe scope | Reject retry when another active run exists for the same output scope. |

Celery retries should be conservative. Retry transient database connection failures, but do not blindly retry validation failures or deterministic QA failures.

---

## Testing Strategy

### Unit Tests

- Node registry validation:
  - duplicate node key detection.
- Pipeline-owned Canvas declaration:
  - statistical weights validation and extract fan-in use `chain` and `chord`,
  - the chord body is the single fan-in node, `run_weights_qa`,
  - the body task links to the downstream publish, notify, and finalize chain,
  - node tasks receive run ID and node key.
- Duplicate task handling: duplicate node task delivery does not run an already running or succeeded implementation again.
- Node contract validation.
- Output scope/idempotency key generation.
- Exact `DataFile.ProgramType` program parameter validation and supported-program rejection.
- Active-run partial unique constraint behavior.
- Active-run scoping allows the same fiscal year to run concurrently for different programs.
- Source snapshot reuse across nodes.
- Output version resolution for downstream DAG dependencies.
- First-workday scheduler helper.
- Program adapter mapping for TANF, SSP, and Tribal TANF parsed models and aggregate count fields.
- Weights case-selection logic:
  - T7 cases preferred when present,
  - T6 cases used as fallback,
  - cases never below T1 case count,
  - zero cases and zero case-count rows excluded,
  - weight rounded to four decimals.

### Integration Tests

- Admin creates a weights run through DRF.
- Pipeline runner launches the pipeline-owned Celery `chain`/`chord` Canvas.
- Celery executes node tasks and updates pipeline/node statuses.
- QA results are persisted.
- Published weights are inserted.
- Rerun inserts the next `StatisticalWeight` version and sets retention on the previous version.
- Extract nodes create table-backed `ETLArtifact` manifests for `weights.s1`, `weights.s3`, and `weights.s4`.
- QA and publication rebuild candidates in memory from those persisted artifacts.
- The final `ETLArtifact` records the produced statistical-weights version for downstream nodes.
- Failed run does not replace existing published weights.
- Concurrent run for the same output scope is rejected.
- Scheduled first-workday run creates exactly one run per program scope.

### Permission Tests

- OFA System Admin can list pipelines, create runs, inspect runs, and retry failed runs.
- DIGIT Team can inspect runs and, if enabled, create runs.
- Data Analyst and Regional Staff cannot create runs.
- Unapproved users cannot access ETL endpoints.

### Reconciliation Tests

During migration from the SAS/notebook process, compare MVP outputs against known legacy outputs for the same fiscal year and reporting month. Store comparison results as QA payloads or implementation test artifacts until parity is accepted.

---

## Dependency Assessment

Use existing dependencies for v1:

- Django and DRF for models and endpoints,
- Celery and Redis for execution,
- `django-celery-beat` for scheduling,
- existing email helpers for notifications,
- PostgreSQL for set-based calculations and durable outputs.


Potential future dependency decisions:

- add a holiday/calendar dependency only if "first workday" must exclude federal holidays,
- add report rendering dependencies only when the feedback report artifact pipeline is implemented,
- add a larger orchestration platform only if ETL workflows outgrow Celery-based execution and code-defined DAGs.

---

## Where To Look

Current source areas:

- `tdrs-backend/etl_scripts/` - prototype SQL and notebook-export scripts.
- `tdrs-backend/tdpservice/reports/` - existing feedback report file storage and distribution.
- `tdrs-backend/tdpservice/data_files/` - submitted file metadata and lifecycle.
- `tdrs-backend/tdpservice/parsers/` - parsed record models and parser outcomes.
- `tdrs-backend/plg/grafana_views/` - generated Grafana-facing views.
- `tdrs-backend/tdpservice/settings/common.py` - Celery and beat configuration.

Planned source areas:

- `tdrs-backend/tdpservice/etl/` - pipeline registry, runner, models, views, tasks, scheduler, and statistical weights nodes.
- `tdrs-backend/tdpservice/email/helpers/` - ETL notification helper if the existing helpers are not a clean fit.
- `tdrs-backend/scripts/create_grafana_postgres_role.py` - add finalized weights table/view grants when ready.
