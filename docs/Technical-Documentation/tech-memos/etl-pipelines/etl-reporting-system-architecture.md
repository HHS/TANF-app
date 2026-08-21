# ETL Reporting System Architecture

- **Status:** Review - system architecture
- **Scope:** TDP-managed ETL for feedback-reporting data products across TANF, SSP, Tribal TANF, and future report families
- **Last updated:** 2026-06-30

---

## Purpose

This document describes the high-level architecture for bringing ETL-style reporting calculations into TDP. It covers the broader reporting system implied by the prototype scripts in `tdrs-backend/etl_scripts/`.

Use this document to understand:

- how parsed submission data becomes reporting data products,
- how the TANF prototype scripts map to reusable pipeline families,
- how TANF, SSP, Tribal TANF, and FRA fit into the reporting architecture,
- where DAG execution, QA, publication, report packaging, and notifications belong,
- how this system relates to the existing feedback report file app.

For the first implementation slice and model-level implementation details, use `etl-statistical-weights-dataset.md`.

---

## System Goal

TDP should manage reporting ETL pipelines as approved, versioned, auditable data products. The system should support immediate production of Section 1 statistical weights for TANF, SSP, and Tribal TANF and later support the wider family of calculations currently represented by the prototype scripts:

- monthly case/work-participation derived datasets,
- statistical weights,
- weighted WPR summaries,
- unweighted review and error-flag tables,
- time-limit reports,
- yearly WPR rollups,
- generated feedback report packages for STTs.

The system should not expose arbitrary SQL execution. It should expose approved reporting pipelines with stable inputs, stable outputs, QA checks, run history, and role-based execution controls.

---

## Current Reporting Sources

TDP already receives and parses submitted data files into program-specific records.

| Program family | Submitted record sets | Current use in reporting architecture |
| --- | --- | --- |
| TANF | `T1` through `T7` | Primary source for the existing prototype ETL scripts. |
| SSP | `M1` through `M7` | Parallel structure to TANF with SSP-specific source tables and report variants. |
| Tribal TANF | Tribal `T1` through `T7` | Parallel structure to TANF with tribal-specific source tables and report variants. |
| FRA | FRA work outcome / education / supplemental sections | Existing feedback report type, but not covered by the current TANF ETL scripts. Future ETL pipelines can be added when FRA calculations are defined. |

The existing `DataFile` model owns submitted-file metadata: fiscal year, quarter, program type, section, STT, version, and lifecycle state. Parsed records are stored in program- and section-specific tables and exposed through Grafana-facing views.

---

## Architecture Overview

The reporting architecture has six layers:

```text
Submitted DataFiles
  -> Parsed Records
  -> Canonical Reporting Inputs
  -> ETL Pipelines
  -> Published Data Products
  -> Report Artifacts and Notifications
```

### 1. Submitted DataFiles

Users upload TANF, SSP, Tribal TANF, and FRA files. TDP validates, scans, parses, and stores metadata about those submissions. This is owned by the existing data-file and parser modules.

### 2. Parsed Records

Parsers write normalized records into program-specific tables. These are the raw material for reporting calculations. Report pipelines should prefer accepted, current parsed data according to explicit source-selection rules.

### 3. Canonical Reporting Inputs

Reporting pipelines should not duplicate source-selection logic in every calculation. A shared input layer should expose stable inputs such as:

- latest accepted TANF T1/T2/T3/T6/T7 records by fiscal period,
- latest accepted SSP M1/M2/M3/M6/M7 records by fiscal period,
- latest accepted Tribal TANF T1/T2/T3/T6/T7 records by fiscal period,
- STT metadata and sample-state indicators,
- fiscal-year and reporting-month derived dimensions.

This layer should be implemented as backend-owned query modules over parsed-record models and submitted-file metadata. Database views can still support read-only reporting access and reconciliation, but calculation nodes should depend on named input contracts, not on user-facing views or ad hoc table scans.

### 4. ETL Pipelines

ETL pipelines are approved DAGs. Each DAG is made of named nodes with declared inputs, outputs, parameters, QA checks, and publication behavior.

This layer is owned by the `tdpservice.etl` Django app. It provides:

- pipeline registry,
- DAG runner,
- run history,
- node history,
- QA result storage,
- output publication.

### 5. Published Data Products

Published data products are durable database tables or views that can be queried, compared, or consumed by downstream report-generation nodes.

Examples:

- statistical weights,
- monthly case/work-participation derived datasets,
- monthly weighted WPR summaries,
- yearly WPR rollups,
- time-limit report summaries,
- report-ready detail tables.

Published products must be versioned by run and scoped by program, fiscal period, STT where relevant, section where relevant, and calculation version.

### 6. Report Artifacts and Notifications

Some pipelines end at database products. Others produce downloadable report packages for STTs.

When a pipeline produces downloadable feedback report files, publication should reuse the existing `reports` app:

- `ReportFile` stores a downloadable report bundle,
- existing report permissions control access,
- existing report notification patterns can be reused or extended.

The ETL module remains the owner of the data product. The `reports` app remains the owner of file storage and distribution.

---

## Prototype Script Families

The TANF scripts in `tdrs-backend/etl_scripts/` map to reporting pipeline families.

| Prototype script | High-level pipeline family | Main data product |
| --- | --- | --- |
| `generating_weights.sql` | Statistical weights | Weights by STT, month, stratum, section. |
| `step1.sql` | Monthly case/work-participation derivation | Canonical monthly TAN dataset for WPR and review reports. |
| `step2.sql` | Weighted WPR summary | Weighted monthly WPR denominators, numerators, rates, and supporting counts. |
| `step3.sql` | Unweighted review and error reports | Review tables and error-flag detail/frequency tables. |
| `step4.sql` | Time-limit reporting | Time-limit error, exemption, over-60-month, and family-count summaries. |
| `step5.sql` | Yearly WPR rollup | Yearly state/STT WPR summary assembled from monthly weighted products. |

These should not become one giant pipeline. They should become related pipelines or subgraphs with explicit data products between them.

---

## Query Translation Architecture

The prototype scripts are Databricks/Spark SQL notebook exports. Production TDP pipelines should translate that logic into backend-owned Django and PostgreSQL code. The goal is not a mechanical SQL dialect conversion; the goal is to preserve the business logic while making source selection, intermediate outputs, QA, publication, and downstream dependencies explicit.

### Translation Unit

Translate scripts by data product and DAG node, not by notebook file.

For each script or script segment, produce a translation map:

| Legacy artifact | New architecture artifact | Translation decision |
| --- | --- | --- |
| temporary view | CTE, query helper, or run-scoped intermediate table | Chosen based on reuse, size, and debugging needs. |
| final notebook table | versioned published data product | Stored with run ID, output scope, and output version. |
| notebook QA query | `ETLQAResult` | Stored as structured QA data. |
| `%python` / Spark dataframe cell | Python node or PostgreSQL query | Chosen based on whether the logic is orchestration or set-based calculation. |
| hardcoded fiscal period or table name | pipeline parameter or input contract | Validated by the pipeline registry. |

The translation map should live with the pipeline implementation or its technical memo. It should make it easy to answer: "Which new node replaced this Databricks temp view?"

### Query Implementation Choices

The ETL module should support two approved query styles.

| Query style | Use when | Avoid when |
| --- | --- | --- |
| Django ORM/querysets | Source filtering, joins through model relationships, simple grouping, counts, annotations, and small reference lookups. | The query becomes hard to read, creates inefficient SQL, or needs database-specific set operations. |
| Raw PostgreSQL | Multi-CTE transforms, `INSERT INTO ... SELECT`, window functions, complex joins, bulk publication, measured performance hotspots, and logic that is clearer as SQL. | The query is simple enough for the ORM or requires dynamic user-supplied SQL. |

Both styles are code-owned and reviewed. Admin users never submit SQL. Raw SQL must be parameterized, stored with the pipeline code, and called through a small query helper that records row counts and errors.

Do not use row-by-row ORM loops for large reporting transformations. Prefer set-based database operations, `bulk_create` for bounded inserts, or raw `INSERT INTO ... SELECT` for large derived products.

### Source Selection

Translated queries should read from parsed-record models and `DataFile` metadata.

Each program-family adapter provides the source model mapping:

| Concept | TANF model | SSP model | Tribal TANF model |
| --- | --- | --- | --- |
| Active family | `TANF_T1` | `SSP_M1` | `Tribal_TANF_T1` |
| Active adult | `TANF_T2` | `SSP_M2` | `Tribal_TANF_T2` |
| Active child | `TANF_T3` | `SSP_M3` | `Tribal_TANF_T3` |
| Aggregate | `TANF_T6` | `SSP_M6` | `Tribal_TANF_T6` |
| Stratum | `TANF_T7` | `SSP_M7` | `Tribal_TANF_T7` |

Every translated query must apply the same source-selection contract:

- selected program family,
- selected fiscal year and reporting period,
- required section,
- non-program-audit files unless the pipeline explicitly says otherwise,
- latest accepted `DataFile` version per STT, period, program type, and section,
- parser lifecycle states approved for that pipeline.

The default parser state for calculations should be successfully parsed data.

Pipelines that read submitted files should declare their `DataFileSource` inputs and use the shared `DataFileSourceSnapshot` helper to freeze latest accepted `DataFile` IDs once per run. Downstream nodes should consume that run-scoped snapshot instead of recalculating latest files independently.

---

## Core Data Products

### Statistical Weights

Purpose: make active caseload measures representative of the STT active caseload.

Inputs:

- active-case records,
- aggregate family counts,
- stratum counts,
- STT sample metadata.

First implementation:

- Section 1 for TANF, SSP, and Tribal TANF,
- fiscal-year and program scoped,
- one shared pipeline with program adapters,
- database output plus QA email.

Later extensions:

- section expansion when business rules are approved.

### Monthly Case/Work-Participation Dataset

Purpose: create a canonical monthly derived dataset from active-case records. This corresponds to the `tan{ym}` output in `step1.sql`.

Inputs:

- TANF T1/T2/T3 for TANF,
- SSP M1/M2/M3 for SSP,
- Tribal TANF T1/T2/T3 for Tribal TANF.

Outputs:

- one monthly derived table per program family and reporting month,
- all-family WPR fields,
- two-parent WPR fields,
- deeming fields,
- error flags,
- supporting case and adult fields used by downstream reports.

This should be treated as a reusable data product, not an invisible temporary table, because weighted and unweighted reports both depend on it.

### Weighted WPR Summary

Purpose: apply weights to monthly work-participation counts and calculate WPR rates.

Inputs:

- monthly case/work-participation dataset,
- statistical weights,
- program/STT metadata.

Outputs:

- weighted sample counts,
- weighted work counts,
- denominator and numerator fields,
- adjusted denominator/numerator fields,
- WPR and adjusted WPR rates.

This corresponds to `step2.sql`.

### Unweighted Review And Error Reports

Purpose: generate detail and frequency tables that identify questionable cases or values for review.

Inputs:

- monthly case/work-participation dataset.

Outputs:

- all-family error flag frequency,
- two-parent error flag frequency,
- error flag detail table,
- zero-assistance cases,
- excused absence over threshold,
- holiday hours over max,
- 80+ participation hours,
- work requirement met with disregarded work participation status.

This corresponds to `step3.sql`.

### Time-Limit Reports

Purpose: calculate federal time-limit fields and create time-limit-focused summaries.

Inputs:

- active-case family records,
- adult records.

Outputs:

- time-limit error flags,
- exemption buckets,
- over-60-month case lists and counts,
- head-of-household over-60-month reports,
- federal assistance month distributions.

This corresponds to `step4.sql`.

### Yearly WPR Rollups

Purpose: assemble monthly weighted WPR products into annual report-ready summaries.

Inputs:

- monthly weighted WPR summaries for all months in the report year.

Outputs:

- month-by-month state/STT fields,
- yearly adjusted numerator and denominator fields,
- WPR rate tables suitable for feedback reports.

This corresponds to `step5.sql`.

### Feedback Report Packages

Purpose: turn one or more published data products into downloadable files for STTs.

Inputs:

- published ETL products,
- STT and region metadata,
- report templates.

Outputs:

- STT-specific files,
- bundled report ZIP files,
- `ReportFile` records,
- notification emails.

This is downstream of ETL node. It should not be the first implementation slice unless explicitly prioritized.

---

## Program Family Architecture

Pipelines should share orchestration and publication behavior across program families while isolating program-specific source mappings and business rules.

### Shared Across TANF, SSP, And Tribal TANF

- run history,
- DAG execution,
- QA persistence,
- publication, versioning, and retention rules,
- admin execution controls,
- notification patterns,
- Grafana access patterns,
- report packaging path.

---

## DAG Strategy

The reporting system uses DAGs to make calculations composable without making execution arbitrary.

High-level product DAG:

```text
canonical_reporting_inputs
  -> statistical_weights
  -> monthly_case_work_participation
  -> weighted_wpr_summary
  -> yearly_wpr_rollup

monthly_case_work_participation
  -> unweighted_review_reports

canonical_reporting_inputs
  -> time_limit_reports

published_data_products
  -> feedback_report_packages
  -> report_distribution
```

DAG principles:

- nodes are code-reviewed modules,
- dependencies are declared by output contract,
- node outputs are scoped by run ID,
- nodes consume upstream artifact manifests rather than transient task payloads,
- publication is explicit and transactional,
- QA is stored as data,
- run history is durable,
- admins execute approved pipelines, not arbitrary graphs.

### Celery Canvas Execution

The pipeline registry maps approved keys to executable, code-reviewed pipeline definitions. Each concrete definition validates parameters, builds the output scope, declares its nodes, and builds its Celery Canvas directly. The orchestration path creates run and node execution records, queues the Canvas, and finalizes the run. Node execution remains owned by the node interface. The Canvas should make the business DAG visible in code instead of hiding progression behind a secondary layer scheduler or metadata-to-Canvas compiler.

| DAG shape | Celery primitive | Use |
| --- | --- | --- |
| Linear dependency | `chain` | Run ordered nodes where each node depends on the prior node's output. |
| Fan-out/fan-in dependency | `chord` | Run parallel header nodes, then run the body exactly once after every header node succeeds. |

Celery tasks should receive only stable identifiers, such as run ID and node key. The task boundary should be serializable and thin: reload run context, find the requested node in the approved definition, and delegate to the node execution interface. Nodes load available artifact manifests from the database, validate declared input contracts, execute their business logic, update execution state, and persist any produced artifact manifests. This keeps the database as the source of truth for run state while Celery handles scheduling and parallel execution.

A pipeline that validates inputs, performs parallel extraction, runs a fan-in quality gate, publishes output, and notifies users should keep that shape visible:

```text
validate_inputs
  -> chord header(
       extract_source_a,
       extract_source_b,
       extract_source_c
     )
  -> quality_gate
  -> publish_output
  -> notify_and_finalize
```

Use a single chord body for fan-in, then attach downstream continuation after that body. Avoid making a full downstream chain the chord body when Celery can append header results or duplicate downstream delivery in confusing ways. Use immutable task signatures where upstream return values should not become downstream arguments.

Each concrete pipeline definition should declare its exact Celery Canvas in code. Node metadata is limited to the details the registry and API need: node key and input/output contracts. Node implementations keep execution logic with the node itself. Node execution is claimed under a database lock, so duplicate task delivery does not run a completed or currently running node implementation again. A larger orchestrator is not needed until the team needs operator-managed DAGs, cross-environment backfills, or non-Django execution workers.

---

## Run And Publication Model

Every pipeline run records:

- pipeline key and version,
- parameters,
- output scope,
- trigger source,
- triggering user,
- node statuses,
- QA results,
- output references,
- start and finish times,
- error details.

Every published product records:

- program family,
- fiscal year,
- reporting month or period,
- STT scope where applicable,
- section scope where applicable,
- calculation version,
- producing run,
- publication timestamp.

Superseding a published product requires:

1. compute new output under a run ID,
2. persist QA,
3. block publication on blocking QA failures,
4. publish the new output version transactionally,
5. set retention metadata on superseded versions according to policy,
6. record the produced version in the output contract,
7. notify the configured audience.

---

## Access And Audiences

### Admin Execution

OFA System Admin users are the primary execution audience for approved ETL runs.

DIGIT Team users are the primary operational/reporting audience for statistical outputs and QA results. Their ability to execute runs should be a product decision per pipeline.

Data Analyst and Regional Staff users should not execute ETL pipelines.

### Output Access

Outputs have two surfaces:

- database tables/views for DIGIT, system admins, and Grafana,
- report files for STTs and regional users when the pipeline publishes feedback report artifacts.

Database outputs and report files should use separate permission decisions. A data product may be queryable by DIGIT without being downloadable by STTs.

---

## Scheduling And Operations

The reporting architecture uses Celery and `django-celery-beat`.

Scheduling should create the same run records as admin-triggered execution. Scheduled runs must not have a separate hidden code path.

For statistical weights, the required schedule is first workday of the month. MVP behavior can define workday as Monday through Friday. Excluding federal holidays requires a specific holiday calendar decision.

Operational views should show:

- latest run by pipeline,
- active runs,
- failed runs,
- last successful publication by data product,
- QA warnings,
- row counts,
- notification status.

---

## Relationship To Existing Modules

| Module | Role in the reporting architecture |
| --- | --- |
| `data_files` | Owns submitted file metadata, fiscal period, program, section, STT, and lifecycle. |
| `parsers` | Owns parsing, validation, parser errors, summaries, and parsed records. |
| `search_indexes` | Provides parsed record models used by query and reporting layers. |
| `reports` | Owns feedback report file upload/storage/distribution, not ETL logic. |
| `tdpservice.etl` | Django app that owns approved ETL pipelines, DAG execution, QA, run history, and published data products. |
| `email` | Sends ETL completion and report availability notifications. |
| `plg/grafana_views` | Provides and/or informs database views used for reporting access. |

The key separation is:

- `etl` produces data products,
- `reports` distributes files,
- `parsers` produces parsed records,
- `data_files` tracks submitted files.

---

## Migration Path

### Phase 1: Statistical Weights MVP

Deliver the first production data product:

- Section 1 statistical weights for TANF, SSP, and Tribal TANF,
- admin-triggered DRF execution,
- scheduled first-workday execution,
- run history,
- QA persistence,
- database publication,
- QA notification email.

This phase is detailed in `etl-statistical-weights-dataset.md`.

### Phase 2: Canonical Monthly Dataset

Port the durable data product currently represented by `step1.sql`.

Goal:

- create reusable monthly case/work-participation outputs,
- verify parity with known TANF outputs,
- make downstream WPR and review-report pipelines depend on this product.

Translation focus:

- map the many `step1.sql` temporary views into a smaller node/intermediate-product graph,
- keep the final monthly dataset as a stable versioned table instead of dynamic `tan{ym}` tables,
- use raw PostgreSQL for the large set-based family/adult/child joins where ORM readability or query plans are poor.

### Phase 3: Weighted And Unweighted TANF Reports

Port `step2.sql` and `step3.sql` as downstream pipelines.

Goal:

- weighted WPR summaries,
- unweighted review/error report tables,
- QA and reconciliation against legacy outputs.

Translation focus:

- consume the explicit statistical-weights version and monthly dataset version from upstream final `ETLArtifact` manifests,
- translate report-specific temporary views into report-ready data products,
- persist notebook comparison checks as QA results rather than manual dataframe comparisons.

### Phase 4: Time-Limit And Yearly Rollups

Port `step4.sql` and `step5.sql`.

Goal:

- time-limit report products,
- annual WPR rollups,
- report-ready data products.

Translation focus:

- split time-limit details and yearly WPR rollups into separate products,
- replace monthly hardcoding with parameterized reporting-period inputs,
- treat yearly rollups as consumers of published monthly WPR output versions.

### Phase 5: Feedback Report Artifact Generation

Add report rendering and packaging.

Goal:

- produce STT-specific files from published data products,
- publish through `ReportFile`,
- notify STTs and regional audiences through existing report access patterns.

### Phase 6: SSP And Tribal TANF Report Expansion

Extend the post-weights report products to SSP and Tribal TANF.

Goal:

- reuse the same orchestration path and run history,
- isolate non-weight source mappings and calculation differences,
- avoid copying TANF-specific assumptions into program families where they do not apply.

---

## Design Rules

- Treat each calculation output as a data product with a contract.
- Translate prototype scripts by node and data product, not by notebook file.
- Require a translation map for each ported script family.
- Keep calculation logic out of the current `reports` file-distribution module.
- Use database-resident parsed data as the source of truth.
- Avoid arbitrary SQL execution.
- Prefer ORM for simple source selection and aggregation; use raw PostgreSQL for complex set-based transformations.
- Keep raw SQL code-owned, parameterized, and covered by parity tests.
- Avoid row-by-row ORM loops for large reporting transformations.
- Make QA structured, persisted, and visible.
- Make publication transactional.
- Record every run and node execution.
- Represent executable DAGs with Celery `chain` and `chord` primitives declared by code-owned pipeline definitions.
- Prefer code-owned pipeline definitions until there is a clear need for operator-authored DAGs.
- Add program-family adapters only when a second implementation makes the seam real.
- Keep the statistical weights MVP small enough to deliver quickly.

---

## Where To Look

Related architecture docs:

- `docs/Technical-Documentation/tech-memos/etl-pipelines/etl-statistical-weights-dataset.md` - first implementation slice and lower-level ETL module shape.
- `docs/Technical-Documentation/parsing-reparsing-architecture.md` - existing parsed-record and parser-output architecture.
- `docs/Technical-Documentation/datafile-lifecycle-orchestrator.md` - existing data-file lifecycle orchestration direction.

Current source areas:

- `tdrs-backend/etl_scripts/` - prototype TANF ETL scripts.
- `tdrs-backend/tdpservice/data_files/` - submitted data files.
- `tdrs-backend/tdpservice/parsers/` - parsed records and parser outcomes.
- `tdrs-backend/tdpservice/reports/` - feedback report file storage and distribution.
- `tdrs-backend/plg/grafana_views/` - generated database views for reporting access.
