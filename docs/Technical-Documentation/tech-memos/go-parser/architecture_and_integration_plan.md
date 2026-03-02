# Go Parser Integration Plan

High-level architecture plan for integrating the Go parser into the TDP production environment.

## Table of Contents

1. [Summary](#summary)
2. [Benefits](#benefits)
3. [System Architecture](#system-architecture)
4. [Data Flow](#data-flow)
5. [Integration Strategy](#integration-strategy)
6. [Configuration Management](#configuration-management)
7. [Infrastructure Requirements](#infrastructure-requirements)
8. [Migration Strategy](#migration-strategy)
9. [Risks, Dependencies, and Open Questions](#risks-dependencies-and-open-questions)

---

## Summary

The Go parser is a ground-up rewrite of the TDP data file parsing system. It replaces the Python parser's class-based, single-threaded approach with a YAML-driven, parallel pipeline written in Go. The parser handles all four program types (TANF, SSP, Tribal TANF, FRA) across all sections, producing identical database records and parser errors.

The integration strategy is designed so the Go parser slots into the existing infrastructure with minimal changes to the Django application. It consumes Celery tasks from the same Redis broker, reads files from the same S3-compatible blob storage, and writes to the same PostgreSQL tables. The Django frontend, API, and all downstream systems are unaffected.

---

## Benefits

### 20x Faster Parsing, Half the Memory

The Go parser's parallel pipeline delivers roughly 20x the throughput of the Python parser while consuming half the memory. The Python parser processes records single-threaded through the Django ORM; the Go parser decodes, parses, validates, and writes concurrently across worker pools and flushes records in bulk via `COPY FROM`. This isn't a marginal improvement — it changes what's operationally feasible.

### Minutes Instead of Hours for Bulk Reparse

Admin-triggered reparse events currently queue hundreds of files through the single-threaded Python parser, often taking hours to complete. With the Go parser's throughput, the same reparse operations complete in minutes. This directly improves the feedback loop for administrators correcting data quality issues or reprocessing after rule changes.

### Automated Error Documentation from Configuration

Because all schemas, validators, and error messages are defined in YAML configuration files and loaded through the registry at startup, a separate Go program can consume the same registry, filespecs, schemas, and validators to generate a comprehensive document of every possible error a given file type or record type can produce. This gives stakeholders, support staff, and submitters a complete, always-current reference — generated directly from the source of truth rather than maintained by hand.

### Flexible Deployment: Microservice, Lambda, or Celery Worker

The Go parser's core pipeline has no opinion about how work arrives. The ingestion layer is a thin adapter that can be swapped without touching parsing, validation, or writing logic. This means the parser can run as:

- **Celery worker** — the current integration path, consuming tasks from Redis alongside the Django application
- **HTTP service** — accepting file uploads directly, running as a standalone microservice behind a load balancer
- **gRPC service** — for high-throughput internal communication between services
- **Lambda function** — triggered by S3 upload events/HTTP for serverless, on-demand processing

Adding a new communication mode is a matter of writing a new entrypoint that calls `Pipeline.ProcessFile()`. The compiled binary, configuration loading, and all pipeline internals remain identical across deployment modes.

### Local Dry-Run Validation for Submitters

Because Go compiles to a single static binary with no runtime dependencies, the parser can be distributed directly to data submitters. Users can run the binary against their files locally before uploading to TDP, catching validation errors immediately without waiting for a round-trip through the system. The dry-run mode uses the same schemas, validators, and error messages as production — the output is identical to what the server would produce, minus the database writes. This reduces submission cycles, decreases the volume of rejected files, and gives submitters confidence in their data before they hit upload.

---

## System Architecture

### Current Production Architecture

```
┌────────────┐     ┌────────────────┐     ┌─────────────┐    ┌────────────┐
│  Frontend  │────▶│  Django API    │────▶│  S3 / Local │    │ PostgreSQL │
│  (React)   │     │  (upload)      │     │  Storage    │    │            │
└────────────┘     └───────┬────────┘     └──────┬──────┘    └─────▲──────┘
                           │                     │                 │
                           ▼                     │                 │
                    ┌─────────────┐              │                 │
                    │    Redis    │              │                 │
                    │   (broker)  │              │                 │
                    └──────┬──────┘              │                 │
                           │                     │                 │
                           ▼                     ▼                 │
                    ┌──────────────────────────────────────┐       │
                    │         Python Celery Worker         │       │
                    │                                      │───────┘
                    │  parse(data_file_id) task            │
                    │  - Reads file from S3                │
                    │  - Parses records (single-threaded)  │
                    │  - Validates fields/records          │
                    │  - Writes to Django ORM              │
                    └──────────────────────────────────────┘
```

### Target Architecture with Go Parser

```
┌────────────┐     ┌────────────────┐     ┌─────────────┐     ┌────────────┐
│  Frontend  │────▶│  Django API    │────▶│  S3 / Local │     │ PostgreSQL │
│  (React)   │     │  (upload)      │     │  Storage    │     │            │
└────────────┘     └───────┬────────┘     └───────┬─────┘     └─────▲──────┘
                           │                      │                 │
                           ▼                      │                 │
                    ┌─────────────┐               │                 │
                    │    Redis    │               │                 │
                    │   (broker)  │               │                 │
                    └──┬───────┬──┘               │                 │
                       │       │                  │                 │
            ┌──────────┘       └──────────┐       │                 │
            ▼                             ▼       ▼                 │
  ┌───────────────────┐      ┌─────────────────────────┐            │
  │  Python Celery    │      │     Go Parser Worker    │            │
  │  Worker           │      │                         │────────────┘
  │                   │──────│  - gocelery/Redis       │
  │  post-parse tasks │      │  - Parallel pipeline    │
  │  (email, summary  │      │  - YAML-driven config   │
  │   aggregation)    │      │  - pgx COPY writes      │
  └───────────────────┘      └─────────────────────────┘
```

Key architectural decisions:

- **Go parser runs as its own container** alongside the existing Django/Celery containers
- **Same Redis broker** — the Go worker uses `gocelery` to consume tasks from the same Redis instance
- **Same PostgreSQL database** — the Go parser writes directly to the existing `search_indexes_*` and `parser_error` tables using `pgx` and `COPY FROM`
- **Same S3 storage** — the Go parser uses `aws-sdk-go-v2` to read submitted files from the same bucket
- **Django remains the orchestrator** — Django enqueues parse tasks and handles all pre/post-parse logic (DataFile status, DataFileSummary, email notifications, reparsing)

### Subsystem Overview

| Subsystem | Package | Responsibility |
|-----------|---------|----------------|
| **Task Consumption** | `celery` | `gocelery` Redis worker receives `parse` tasks dispatched by Django |
| **Blob Storage** | `storage` | Retrieves submitted data files from S3 (or LocalStack in dev) |
| **Pipeline Orchestration** | `pipeline` | Coordinates the full decode → presort → parse → validate → write flow |
| **Decoding** | `decoder` | Reads raw files into `Row` objects (positional, CSV, XLSX) |
| **Pre-sorting** | `parser` | Stable-sorts data rows by case key for streaming group accumulation |
| **Parsing** | `parser` | Record type detection, field extraction, type conversion via worker pool |
| **Validation** | `validation` | Expression-based field and record validation using `expr` engine |
| **Writing** | `writer` | Bulk database writes via `pgx COPY FROM`, routed by record type |
| **Configuration** | `config` | YAML-driven schemas, filespecs, validators, and pipeline tuning |

---

## Data Flow

### End-to-End: File Submission Through Database Persistence

```
1. User uploads file via React frontend
         │
         ▼
2. Django API receives upload
   - Creates DataFile record
   - Stores file in S3 (or LocalStack)
   - Creates DataFileSummary (PENDING)
   - Enqueues Celery task: parse(data_file_id)
         │
         ▼
3. Redis broker holds the task
         │
         ▼
4. Go parser worker picks up the task
   a. Reads DataFile metadata from PostgreSQL (file path, program, section)
   b. Downloads file from S3 into memory
   c. Resolves FileSpec from (program, section) via config registry
         │
         ▼
5. Pipeline.ProcessFile() executes:

   ┌──────────────────────────────────────────────────────────────────────────────┐
   │                        PIPELINE STAGES                                       │
   │                                                                              │
   │  5a. DECODE                                                                  │
   │      Decoder reads raw file → []Row (with original line nums)                │
   │                         │                                                    │
   │  5b. PRESORT                                                                 │
   │      Stable-sort rows by `key_fields` (RPT_MONTH_YEAR, CASE_NUMBER)          │
   │      Preserves original line numbers for error reporting                     │
   │                         │                                                    │
   │  5c. ACCUMULATE                                                              │
   │      Stream sorted rows → detect key changes → emit batches                  │
   │      One active group in memory at a time                                    │
   │                         │                                                    │
   │  5d. PARSE (parallel, N worker goroutines)                                   │
   │      Extract fields per schema, convert types                                │
   │      Worker pool processes batches in parallel                               │
   │                         │                                                    │
   │  5e. VALIDATE (parallel, N validator goroutines)                             │
   │      Field-level validators (category 2)                                     │
   │      Record-level validators (category 1 & 3)                                │
   │      Group-level validators (category 4)                                     │
   │      Expression engine evaluates YAML-defined rules                          │
   │                         │                                                    │
   │  5f. WRITE (bulk)                                                            │
   │      Convert ParsedRecords → DB model structs                                │
   │      Bulk insert via pgx COPY FROM                                           │
   │      Flush at configurable thresholds (10k records, 50k errors)              │
   └──────────────────────────────────────────────────────────────────────────────┘
         │
         ▼
6. Go parser updates DataFileSummary status
         │
         ▼
7. Python Celery worker handles post-parse tasks
   - Email notifications
   - Reparse bookkeeping
   - Summary aggregation
```

### Pipeline Concurrency Model

```
                    ┌──────────────────────────┐
                    │      Accumulator         │
                    │   (single goroutine)     │
                    └────────────┬─────────────┘
                                 │ batches (channel, buffer=256)
                    ┌────────────▼─────────────┐
                    │      Parser Pool         │
                    │   (N worker goroutines)  │
                    └────────────┬─────────────┘
                                 │ parsed results (channel, buffer=256)
                    ┌────────────▼─────────────┐
                    │     Result Routers       │
                    │   (N router goroutines)  │
                    │   - Validate per group   │
                    │   - Route to writer      │
                    └────────────┬─────────────┘
                                 │
                    ┌────────────▼─────────────┐
                    │      Writer              │
                    │  (Writer pre record type)│
                    │   - Buffered flushes     │
                    │   - 10k record threshold │
                    └──────────────────────────┘
```

All pool sizes and buffer depths are configurable via `config/pipeline.yaml`:

```yaml
pipeline:
  num_workers: 16
  work_buffer_size: 256
  result_buffer_size: 256
  num_routers: 16
  num_validators: 16
  pool_prewarm_size: 10000
writer:
  flush_threshold: 10000
  error_flush_threshold: 50000
database:
  max_conns: 10
  min_conns: 4
```

---

## Integration Strategy

### Celery Task Consumption

The Go parser integrates with the existing Django task dispatch system through a shared Redis broker:

1. **Django dispatches** — `scheduling/parser_task.py` enqueues `parse(data_file_id)` to Redis (unchanged)
2. **Go worker consumes** — `internal/celery/redis_worker.go` uses `gocelery` to listen on the same Redis queue
3. **Task routing** — Celery task routing directs parse tasks to the Go worker's queue while other tasks (email, reparse) remain on the Python worker's queue

```python
# Django settings addition for task routing
CELERY_TASK_ROUTES = {
    'tdpservice.scheduling.parser_task.parse': {'queue': 'go_parser'},
}
```

```go
// Go worker registers the parse task handler
tasks := map[string]interface{}{
    "tdpservice.scheduling.parser_task.parse": parseHandler,
}
worker := celery.NewRedisWorker(redisURL, tasks)
worker.Start()
```

### Shared Database

The Go parser writes to the same PostgreSQL tables as the Python parser:

| Table | Purpose | Write Method |
|-------|---------|--------------|
| `search_indexes_tanf_t1` through `t7` | Parsed TANF records | `COPY FROM` |
| `search_indexes_ssp_m1` through `m7` | Parsed SSP records | `COPY FROM` |
| `search_indexes_tribal_tanf_t1` through `t7` | Parsed Tribal records | `COPY FROM` |
| `search_indexes_fra_te1` | Parsed FRA records | `COPY FROM` |
| `parser_error` | Validation errors | `COPY FROM` |
| `parsers_datafilesummary` | Processing status | UPDATE via query |

Schema compatibility is enforced by SQLC: `schema.sql` mirrors the Django model definitions, and `sqlc generate` produces Go structs that match the database columns exactly. The `writer/convert` package handles the translation from internal `ParsedRecord` types to these DB model structs.

### Blob Storage

The Go parser uses `aws-sdk-go-v2` to access the same S3 bucket (or LocalStack in development):

- **Production**: Real S3 bucket configured via `AWS_S3_DATAFILES_BUCKET_NAME`
- **Development**: LocalStack S3 at `http://localstack:4566`
- **Credentials**: Same IAM role / environment variables used by the Django application

### Post-Parse Orchestration

After the Go parser completes file processing, the Python Celery worker handles remaining tasks that depend on Django ORM and application logic:

- DataFileSummary status update (accepted/rejected counts, error aggregation)
- Email notifications to submitters
- Reparse bookkeeping and cleanup

This can be done by having the Go parser enqueue a `post_parse(data_file_id)` task back to the Python worker's queue upon completion, or by having Django poll the DataFileSummary status.

---

## Configuration Management

### YAML-Driven Architecture

All parsing behavior is defined in YAML configuration files, not in code. This is a fundamental design difference from the Python parser, where schemas, validators, and field definitions are embedded in Python classes.

```
config/
├── filespecs/                  # One YAML per (program, section)
│   ├── tanf/
│   │   ├── section1.yaml       # TANF Active Case Data
│   │   ├── section2.yaml       # TANF Closed Case Data
│   │   ├── section3.yaml       # TANF Aggregate Data
│   │   └── section4.yaml       # TANF Stratum Data
│   ├── ssp/                    # Same structure for SSP
│   ├── tribal/                 # Same structure for Tribal TANF
│   └── fra/
│       └── section1.yaml       # FRA Exiter Data
├── schemas/                    # One YAML per record type
│   ├── common/
│   │   ├── header.yaml         # Shared HEADER schema
│   │   └── trailer.yaml        # Shared TRAILER schema
│   ├── tanf/
│   │   ├── t1.yaml through t7.yaml
│   ├── ssp/
│   │   ├── m1.yaml through m7.yaml
│   ├── tribal_tanf/
│   │   ├── t1.yaml through t7.yaml
│   └── fra/
│       └── te1.yaml
├── validation/
│   └── validators.yaml         # All field and record validators
└── pipeline.yaml               # Worker pool sizes, buffer depths, flush thresholds
```

### FileSpecs

Define which schemas belong to a file, how to detect record types, and how to group records:

- **Format**: positional (TANF/SSP/Tribal) or columnar (FRA)
- **Record type detection**: prefix matching (positional) or fixed schema (FRA)
- **Accumulator**: key-based grouping for case data (sections 1-2), batching for independent records (sections 3-4, FRA)
- **Presort**: enabled for grouped schemas to guarantee in-memory duplicate detection

### Schemas

Define the field layout for each record type:

- Field name, item number, friendly name (for error messages)
- Byte positions (positional) or column indices (columnar)
- Data types (`string`, `int`)
- Transform functions (e.g., `zero_pad_3`)

### Validators

Expression-based validation rules defined in `validators.yaml`:

- **Field validators**: range checks, date validation, format validation, conditional rules
- **Record validators**: cross-field consistency, sum validations
- **Group Validators**: case-level rules (e.g., `t1_has_t2_or_t3`), valid ssn for federally funded individuals
- Rules are written in `expr` syntax — a human-readable expression language
- Error messages are co-located with rules for single-source-of-truth

```yaml
field_validators:
  - id: dateYearIsLargerThan
    params: [threshold]
    expr: "year(value) >= threshold"
    message: "Year must be >= {threshold}"

group_validators:
  - id: t1_has_t2_or_t3
    expr: "RecordCounts['T3'] > 0 or RecordCounts['T2'] > 0"
    message: "Every T1 record should have at least one corresponding T2 or T3 record with the same RPT_MONTH_YEAR and CASE_NUMBER"
```

### Configuration Loading

All configuration is loaded once at startup into an immutable registry. Schemas and filespecs are compiled and indexed for O(1) lookup by (program, section) or record type. Expression-based validators are compiled to bytecode at load time, failing fast on syntax errors before any files are processed.

---

## Infrastructure Requirements

### Docker

The Go parser requires a new container in the docker-compose stack:

```yaml
# docker-compose.yml addition
go-parser:
  build:
    context: ./tdpservice/parsers/go-parser
    dockerfile: Dockerfile
  environment:
    - REDIS_URL=redis://redis-server:6379
    - DATABASE_URL=postgres://tdpuser:tdppass@postgres:5432/tdrs
    - AWS_S3_DATAFILES_BUCKET_NAME=tdp-datafiles
    - AWS_S3_ENDPOINT=http://localstack:4566  # dev only
  depends_on:
    - redis-server
    - postgres
    - localstack
```

A `Dockerfile` needs to be created for the Go parser:

```dockerfile
FROM golang:1.25-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 go build -o /go-parser .

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=builder /go-parser /go-parser
COPY --from=builder /app/config /config
ENTRYPOINT ["/go-parser"]
```

### CI/CD Changes

| Change | Description |
|--------|-------------|
| **Go build step** | Add `go build` and `go test` to the CI pipeline |
| **SQLC validation** | Run `sqlc diff` to ensure generated code matches schema |
| **Expression validation** | Compile all YAML validators at CI time to catch syntax errors |
| **Docker image build** | Build and push the `go-parser` image alongside the existing `tdp` image |
| **Integration tests** | Run Go integration tests against a test database |

### Resource Requirements

| Resource | Recommendation | Notes |
|----------|---------------|-------|
| **CPU** | 2-4 vCPU | Parallel pipeline benefits from multiple cores |
| **Memory** | 1-2 GB | In-memory presort + object pools for large files |
| **Disk** | Minimal | No temp files; config is bundled in image |
| **Network** | Same VPC | Must reach Redis, PostgreSQL, and S3 |

---

## Migration Strategy

### Phase 1: Canary Routing (Controlled Cutover)

Route a small, controlled subset of real submissions to the Go parser writing to production tables. Gradually widen the canary until all traffic is handled by Go.

Because the Cloud.gov environment does not support network-level traffic splitting, the routing decision is made **programmatically in Django** at task dispatch time. A configuration table or environment-backed setting defines which submissions are routed to the Go parser based on attributes such as program type, STT, or section:

```python
# Example: routing logic in Django task dispatch
GO_PARSER_CANARY = {
    "enabled": True,
    "mode": "allowlist",          # "allowlist", "percentage", or "all"
    "allowlist_stts": ["ST01"],   # specific STTs routed to Go
    "allowlist_programs": [],     # specific program types routed to Go
    "percentage": 0,              # percentage of remaining traffic routed to Go
}

def dispatch_parse(data_file_id):
    data_file = DataFile.objects.get(id=data_file_id)
    if should_use_go_parser(data_file, GO_PARSER_CANARY):
        parse.apply_async(args=[data_file_id], queue="go_parser")
    else:
        parse.apply_async(args=[data_file_id], queue="python_parser")
```

Canary progression:

1. Start with a single STT or program type on the allowlist (smallest blast radius)
2. Monitor record counts, error counts, and DataFileSummary outcomes against historical baselines
3. If the Go parser fails (crashes, times out, returns error), the file can easily be reparsed via the Python parser
4. Widen the allowlist to additional STTs and program types as confidence grows
5. Switch mode to `percentage` and ramp from 10% → 25% → 50% → 100%

**Exit criteria**: 100% of traffic routed to Go parser with zero fallback events over a sustained period (e.g., 30 days).

### Phase 2: Python Parser Decommission

Remove the Python parser from the parsing path entirely.

1. Remove canary routing logic — Go parser is the only consumer of `parse` tasks
2. Keep Python Celery worker for non-parse tasks (email, reparse scheduling, admin). Consider moving the Python Celery worker back into the backend VM
3. Remove Python parser code, schema definitions, and validators from the codebase

### Feature Parity Checklist

Before widening the canary beyond the initial allowlist, the Go parser must handle:

- [ ] All TANF sections (1-4) with all record types (T1-T7)
- [ ] All SSP sections (1-4) with all record types (M1-M7)
- [ ] All Tribal TANF sections (1-4) with all record types (T1-T7)
- [ ] FRA section 1 (CSV and XLSX)
- [ ] HEADER and TRAILER validation
- [ ] All field-level validators
- [ ] All record-level validators
- [ ] All group-level validators
- [ ] Duplicate detection
- [ ] DataFileSummary status updates
- [ ] Parser error records with correct line numbers, field names, and error messages
- [ ] Reparse handling (The Reparse Service should handle the queing, deleting, etc.)

---

## Risks, Dependencies, and Open Questions

### Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **Schema drift** — Django model migrations diverge from SQLC schema | Go parser writes fail or corrupt data | Medium | CI step runs `sqlc diff`; integration tests run against migrated DB |
| **Validation parity gaps** — Go parser misses edge cases in Python validators | Incorrect acceptance or rejection of records | Medium | Canary routing with narrow allowlist; automatic Python fallback; comprehensive integration test suite |
| **Memory pressure** — Large files during presort exhaust container memory | OOM kill, failed parse | Low | Monitor container memory; set memory limits; most files are well under 100MB |
| **gocelery compatibility** — `gocelery` library may not support all Celery protocol features | Task consumption failures | Low | Validate against actual Redis task payloads; the library is used only for basic task/result protocol |
| **Expression engine bugs** — `expr` library edge cases in validation | Incorrect validation results | Low | Pinned dependency version; comprehensive validator unit tests |

### Dependencies

| Dependency | Owner | Status |
|------------|-------|--------|
| PostgreSQL schema access | DevOps / Django | Existing — Go parser needs read/write on existing tables |
| Redis broker access | DevOps | Existing — same Redis instance |
| S3 bucket access | DevOps | Existing — same IAM role or credentials |
| Go runtime in Docker | DevOps | **New** — Dockerfile and CI pipeline needed |
| Celery task routing | Backend team | **New** — Django settings change to route parse tasks |
| Canary routing config | Backend team | **New** — Django routing logic and canary configuration |

### Open Questions

| Question | Context | Proposed Answer |
|----------|---------|-----------------|
| What is the rollback strategy if issues arise during transition? | Production safety | Phase 1 is canary based, and configurable. If issues arise revert config to route 100% of traffic to Python parser — no deployment needed. |
| Are there compliance or security review requirements for introducing Go? | FedRAMP / ATO considerations | Go is a compiled, memory-safe language with no additional runtime dependencies. Security review should focus on: dependency audit (`go.mod`), container scanning, and network access patterns (same as Python worker). |
| How will monitoring and observability differ? | Operational visibility | The Go parser should emit structured logs (JSON) and expose Prometheus metrics for: files processed, records parsed, errors generated, pipeline stage latencies, and worker pool utilization. These integrate with the existing Grafana/Prometheus stack already in docker-compose. |
| What is the desired timeline for production readiness? | Planning | Depends on team capacity. Suggested: Phase 1 (canary routing) can begin as soon as the Dockerfile, CI pipeline, and canary routing logic are in place. |
