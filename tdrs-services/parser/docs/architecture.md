# Go Parser Architecture

A high-level overview of the Go parser's design, why it replaces the Python parser, and how its architecture enables parallel, configuration-driven data file processing.

For integration and deployment details, see [Architecture and Integration Plan](../../../docs/Technical-Documentation/tech-memos/go-parser/architecture_and_integration_plan.md). For feature tracking, see the [Feature Parity Matrix](../../../docs/Technical-Documentation/tech-memos/go-parser/feature_parity_matrix.md).

---

## Why Replace the Python Parser?

The Python parser was built as a tightly coupled, single-threaded system embedded in the Django application. It works, but its architecture creates concrete operational problems:

| Problem | Root Cause | Consequence |
|---------|------------|-------------|
| Bulk reparses take hours | Single-threaded, one record at a time through the Django ORM | Administrators wait hours for data corrections to propagate |
| Schema changes require code changes | Field definitions, validators, and record types are Python classes | Every schema update is a code deploy |
| Validators are embedded in field definitions | Parsing and validation are interleaved in the same class hierarchy | Cannot run validation independently, cannot generate error documentation |
| Mutable state in schema objects | Python schema objects hold state during parsing | Not thread-safe, no path to parallelism |
| Single deployment mode | Parser is a Celery task | Cannot run locally without Celery, cannot deploy as a standalone service |

The Go parser is not a port. It is a ground-up redesign that addresses each of these by separating configuration from code, separating parsing from validation, and building parallelism into the core pipeline.

---

## Architecture at a Glance

```
                          ┌──────────────────────────────┐
                          │     YAML Configuration       │
                          │                              │
                          │  FileSpecs   Schemas         │
                          │  Validators  Pipeline Config │
                          └──────────────┬───────────────┘
                                         │
                                    loads once at
                                      startup
                                         │
                                         ▼
                          ┌──────────────────────────────┐
                          │     Immutable Registry       │
                          │                              │
                          │  O(1) lookup by (program,    │
                          │  section) or record type     │
                          │                              │
                          │  Compiled expression-based   │
                          │  validators (bytecode)       │
                          └──────────────┬───────────────┘
                                         │
                                    shared across
                                    all workers
                                         │
                                         ▼
          ┌──────────────────────────────────────────────────────────┐
          │                  Processing Pipeline                     │
          │                                                          │
          │   Decode ─▶ Presort ─▶ Accumulate ─▶ Parse ─▶ Validate   │
          │                                        ▲         ▲       │
          │                                        │         │       │
          │                                   parallel   parallel    │
          │                                   workers    workers     │
          │                                                          │
          └────────────────────────┬─────────────────────────────────┘
                                   │
                                   ▼
                          ┌──────────────────────────────┐
                          │     Bulk Database Writes     │
                          │                              │
                          │   pgx COPY FROM              │
                          │   Buffered flushes at        │
                          │   configurable thresholds    │
                          └──────────────────────────────┘
```

---

## Configuration-Driven Design

All parsing behavior is defined in YAML, not code. The Python parser embeds field definitions, validators, and record types in Python classes. The Go parser externalizes all of this into configuration files loaded once at startup into an immutable registry.

```
config/
├── filespecs/           # Which schemas belong to each (program, section)
│   ├── tanf/            # section1.yaml through section4.yaml
│   ├── ssp/
│   ├── tribal/
│   └── fra/
├── schemas/             # Field layouts for each record type
│   ├── common/          # header.yaml, trailer.yaml
│   ├── tanf/            # t1.yaml through t7.yaml
│   ├── ssp/             # m1.yaml through m7.yaml
│   ├── tribal_tanf/
│   └── fra/
├── validation/
│   └── validators.yaml  # All field, record, and group validators
└── pipeline.yaml        # Worker pool sizes, buffer depths, flush thresholds
```

### What Each Layer Defines

**FileSpecs** declare the structure of a file type: which schemas it contains, how to detect record types (prefix matching for positional files, fixed schema for columnar), and how records group together (by case key or independently).

**Schemas** define field layouts: byte positions (positional) or column indices (columnar), data types, transforms, and which segment of a multi-record line each field belongs to.

**Validators** are expression-based rules written in `expr` syntax. They are co-located with their error messages so the configuration is the single source of truth for what gets validated and what the user sees when validation fails.

Example validator definition:

```yaml
field_validators:
  - id: dateYearIsLargerThan
    params: [threshold]
    expr: "year(value) >= threshold"
    message: "Year must be >= {threshold}"

group_validators:
  - id: t1_has_t2_or_t3
    expr: "RecordCounts['T3'] > 0 or RecordCounts['T2'] > 0"
    message: "Every T1 should have at least one corresponding T2 or T3"
```

### Why This Matters

Because schemas, validators, and error messages live in YAML:

- **Adding or changing a field** is a config change, not a code change
- **Error documentation can be auto-generated** by reading the same config files the parser uses (see the `cmd/docgen` tool)
- **The registry is immutable after startup**, making it safe to share across parallel workers with zero synchronization
- **Validators compile to bytecode at load time**, catching syntax errors before any files are processed

---

## The Processing Pipeline

The pipeline transforms a raw data file into validated database records through six stages. The first three stages are sequential (single goroutine); the last three are parallel.

```
┌────────────────────────────────────────────────────────────────────────┐
│                                                                        │
│   SEQUENTIAL STAGES (single goroutine)                                 │
│                                                                        │
│   ┌─────────┐     ┌──────────┐     ┌──────────────┐                    │
│   │ DECODE  │────▶│ PRESORT  │────▶│  ACCUMULATE  │                    │
│   │         │     │          │     │              │                    │
│   │ Raw file│     │ Stable   │     │ Stream rows  │                    │
│   │ → Rows  │     │ sort by  │     │ into groups  │                    │
│   │         │     │ case key │     │ by key change│                    │
│   └─────────┘     └──────────┘     └──────┬───────┘                    │
│                                           │                            │
│                                    emits batches                       │
│                                    via channel                         │
│                                           │                            │
├───────────────────────────────────────────┼────────────────────────────┤
│                                           │                            │
│   PARALLEL STAGES (N worker goroutines)   │                            │
│                                           ▼                            │
│                              ┌───────────────────────┐                 │
│                              │   WORKER POOL (N=16)  │                 │
│                              │                       │                 │
│                              │  ┌──────┐ ┌──────┐    │                 │
│                              │  │ W[0] │ │ W[1] │ …  │                 │
│                              │  └──┬───┘ └──┬───┘    │                 │
│                              │     │        │        │                 │
│                              └─────┼────────┼────────┘                 │
│                                    │        │                          │
│               Each worker does ALL THREE of these per batch:           │
│                                                                        │
│     ┌─────────────────┬─────────────────────┬──────────────────┐       │
│     │                 │                     │                  │       │
│     │     PARSE       │     VALIDATE        │     ROUTE        │       │
│     │                 │                     │                  │       │
│     │  Extract fields │  Group validators   │  Convert to DB   │       │
│     │  per schema,    │  Record pre-check   │  row format,     │       │
│     │  convert types  │  Field validators   │  send to writer  │       │
│     │                 │  Record consistency │  channels        │       │
│     │                 │                     │                  │       │
│     └─────────────────┴─────────────────────┴──────────────────┘       │
│                                                                        │
│                                    │                                   │
│                                    ▼                                   │
│                         ┌──────────────────────┐                       │
│                         │    TABLE WRITERS     │                       │
│                         │                      │                       │
│                         │  One per record type │                       │
│                         │  + one for errors    │                       │
│                         │                      │                       │
│                         │  Buffer → flush at   │                       │
│                         │  threshold via       │                       │
│                         │  pgx COPY FROM       │                       │
│                         └──────────────────────┘                       │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

### Stage Details

**Decode** -- Reads the raw file into `Row` objects. The decoder is format-aware: a `PositionalDecoder` for fixed-width TANF/SSP/Tribal files, a `CSVDecoder` or `XLSXDecoder` for columnar FRA files. The decoder is selected automatically based on the FileSpec. Each row carries its original line number for error reporting.

**Presort** -- Stable-sorts rows by case key (`RPT_MONTH_YEAR | CASE_NUMBER`) so that records belonging to the same case are contiguous. This enables streaming group detection without holding the entire file in memory. Original line numbers are preserved through the sort.

**Accumulate** -- Streams through sorted rows, detecting key changes to form groups. When the key changes, the completed group is added to a batch. Batch size is configurable: `batch_size=1` emits each group immediately, `batch_size=N` batches N groups together, `batch_size=0` accumulates everything into a single batch. For non-keyed files (aggregate data, FRA), each record is its own group.

**Parse** -- Extracts field values from each row according to its schema. Handles multi-segment records (e.g., a single T3 line produces multiple child records). Uses object pools to reduce GC pressure: records are acquired from a pool, populated, and released back after database conversion.

**Validate** -- Runs validation in a strict order: group validators first, then record pre-checks, then field validators, then record consistency checks. Short-circuit logic skips downstream validators when blocking errors are found. Validators are compiled `expr` expressions evaluated against an environment populated from the parsed record.

**Route & Write** -- Converts validated records to database row format and sends them to per-table `TableWriter` goroutines via channels. Each writer buffers rows and flushes at a configurable threshold using `pgx COPY FROM`. Records with blocking validation errors are rejected (errors written, records discarded). Valid records are written with their non-blocking errors linked via UUID.

---

## Parallelism Model

The key design decision is **where** parallelism happens. The Go parser parallelizes at the batch level: each worker goroutine independently parses, validates, and routes an entire batch of record groups. This avoids fine-grained synchronization between stages.

```
                    Accumulator (1 goroutine)
                           │
                    emits batches via
                    buffered channel
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
          ┌───────┐   ┌───────┐   ┌───────┐
          │ W[0]  │   │ W[1]  │   │ W[2]  │  ...  N workers
          │       │   │       │   │       │
          │ parse │   │ parse │   │ parse │
          │ valid.│   │ valid.│   │ valid.│
          │ route │   │ route │   │ route │
          └───┬───┘   └───┬───┘   └───┬───┘
              │           │           │
              └─────┬─────┴─────┬─────┘
                    │           │
              ┌─────▼───┐ ┌────▼────┐
              │ Record  │ │  Error  │
              │ Writers │ │ Writer  │
              │ (per    │ │         │
              │  table) │ │         │
              └─────────┘ └─────────┘

    Workers share NOTHING mutable:
    - Registry is immutable (loaded at startup)
    - Object pools are per-schema with sync.Pool
    - Writers receive rows via channels
    - Each worker has its own stats counters
```

### Why Batch-Level Parallelism?

An alternative design would pipeline stages: decode in one goroutine, parse in another pool, validate in another, write in another, with channels between each. The Go parser tried this and simplified to batch-level parallelism because:

1. **No cross-stage synchronization** -- Each worker owns its batch from parse through route. No mutexes, no coordination, no ordering concerns.
2. **Better cache locality** -- A worker processes the same records through all stages. The data stays hot in the CPU cache.
3. **Simpler error handling** -- A worker that hits an error can short-circuit its entire batch without coordinating with other stages.
4. **Backpressure is natural** -- The buffered channel between accumulator and workers provides backpressure. If workers are slow, the accumulator blocks. No tuning required beyond buffer size.

### Concurrency Configuration

All pool sizes and buffer depths are configurable:

```yaml
pipeline:
  num_workers: 16
  work_buffer_size: 256
  pool_prewarm_size: 10000
writer:
  flush_threshold: 10000
  error_flush_threshold: 50000
validation:
  short_circuit: true
database:
  max_conns: 10
  min_conns: 4
```

---

## Validation Architecture

Validation is completely separated from parsing. All parsing occurs at the batch level first, then the batch is sent to be validated. This is in opposition to the Python parser parsing a single record and validating it in sequence.

### Validation Hierarchy

```
                    ┌──────────────────────────────────┐
                    │         GROUP VALIDATORS         │
                    │                                  │
                    │  Cross-record consistency within │
                    │  a case (e.g., T1 must have T2   │
                    │  or T3, SSN checks)              │
                    │                                  │
                    │  Blocking: entire group rejected │
                    └───────────────┬──────────────────┘
                                    │
                      if group passes (or short_circuit=false)
                                    │
                    ┌───────────────▼───────────────────┐
                    │      RECORD PRE-CHECK             │
                    │                                   │
                    │  Structural validity: correct     │
                    │  length, valid prefix, required   │
                    │  fields present                   │
                    │                                   │
                    │  Blocking: record rejected        │
                    └───────────────┬───────────────────┘
                                    │
                      if record passes (or short_circuit=false)
                                    │
              ┌─────────────────────┼──────────────────────┐
              │                                            │
  ┌───────────▼────────────┐             ┌─────────────────▼──────────┐
  │   FIELD VALIDATORS     │             │   RECORD CONSISTENCY       │
  │                        │             │                            │
  │  Per-field checks:     │             │  Cross-field checks:       │
  │  range, format, date   │             │  field A implies field B,  │
  │  validity              │             │  sum validations           │
  │                        │             │                            │
  │  Non-blocking: error   │             │  Non-blocking: error       │
  │  recorded, record      │             │  recorded, record          │
  │  still written         │             │  still written             │
  └────────────────────────┘             └────────────────────────────┘
```

### Short-Circuit Behavior

When `short_circuit: true` (the default), blocking errors at a higher scope prevent lower-scope validators from running. This enhances the Python parser's behavior and avoids generating cascading errors that add noise without information.

For example, if a record fails its pre-check (wrong length), the parser does not also report that every individual field failed validation. The pre-check error is sufficient.

---

## Database Write Strategy

The Python parser writes a single batch of records through the Django ORM. Each table has to be written to sequentially. The Go parser also buffers records for batch serialization. However, it uses PostgreSQL's `COPY FROM` protocol (as opposed to an ORM), which is the fastest way to load data into Postgres possible.

```
   Worker goroutine                    TableWriter goroutine
        │                                     │
        │   SendRow([]any)                    │
        │──────────────────────▶ channel ────▶│
        │                                     │  append to buffer
        │                                     │
        │                                     │  buffer.len >= threshold?
        │                                     │       │
        │                                     │       ▼
        │                                     │  ┌──────────────┐
        │                                     │  │  COPY FROM   │
        │                                     │  │  (bulk flush)│
        │                                     │  └──────────────┘
        │                                     │
        │   Stop()                            │
        │──────────────────────▶ close ──────▶│  flush remaining
        │                                     │  return total count
```

Each record type gets its own `TableWriter` goroutine. An additional writer handles parser error rows with a higher flush threshold (errors are typically more numerous than records). When `database.shadow_mode` is true, database writes use the configured `database.table_prefix` (`shadow_` by default) for Go parser-owned output tables. When `database.shadow_mode` is false, the effective prefix is empty and the Go parser writes to production tables.

The write layer uses a `Sink` interface, enabling two backends:
- **DatabaseSink** -- Production path. Uses `pgx.CopyFrom` to write to PostgreSQL.
- **FileSink** -- Local/dry-run path. Writes NDJSON or CSV files. Enables submitters to validate files locally without a database.

---

## Multi-Format Support

The parser handles two fundamentally different file formats through a unified pipeline:

```
   POSITIONAL FILES                          COLUMNAR FILES
   (TANF, SSP, Tribal)                      (FRA)

   Fixed-width UTF-8 text                   CSV or XLSX spreadsheet
   ┌────────────────────────────┐           ┌──────────────────────┐
   │T120201011111111112230034…  │           │ 202010,1111111111    │
   │T220201011111111112121974…  │           │ 202010,2222222222    │
   │T320201011111111112120190…  │           │ 202010,3333333333    │
   └────────────────────────────┘           └──────────────────────┘
         │                                        │
         ▼                                        ▼
   PositionalDecoder                        CSV/XLSX Decoder
   (bytes at positions)                     (values at columns)
         │                                        │
         ▼                                        ▼
   PositionalRow                            ColumnarRow
   row.Slice(start, end)                    row.Column(index)
         │                                        │
         └───────────────┬────────────────────────┘
                         │
                         ▼
                  Unified Row interface
                  (same pipeline from here down)
                         │
                         ▼
              Record Type Detection
              (prefix match vs fixed schema)
                         │
                         ▼
              Accumulate → Parse → Validate → Write
```

The `Row` interface abstracts over format differences so everything downstream of decoding is format-agnostic. The `FieldExtractor` knows how to read positional fields (byte slice) or columnar fields (column index) based on the FileSpec's declared format.

---

## Object Pooling and Memory Efficiency

The Go parser uses `sync.Pool` to reuse `ParsedRecord` objects, reducing garbage collection pressure during high-throughput parsing. Each schema has its own pool, pre-warmed at startup with a configurable number of records.

```
   Schema Pool (per record type)
   ┌─────────────────────────────────────┐
   │  ┌────┐ ┌────┐ ┌────┐ ┌────┐        │
   │  │ Rec│ │ Rec│ │ Rec│ │ Rec│ ...    │  pre-warmed at startup
   │  └────┘ └────┘ └────┘ └────┘        │
   └──────────┬──────────────────────────┘
              │
     Acquire ─┤── worker gets a pre-allocated record
              │
     Parse ───┤── fields populated in-place
              │
     Validate ┤── validators read fields
              │
     Convert ─┤── record → []any database row
              │
     Release ─┘── record returned to pool, fields zeroed
```

This means the parser allocates most of its `ParsedRecord` memory once at startup and reuses it throughout the file. For a file with 100,000 records processed by 16 workers, only ~10,000 records exist in memory at any time (the pool pre-warm size), not 100,000.

---

## Python Parser vs. Go Parser Comparison

| Dimension | Python Parser | Go Parser |
|-----------|---------------|-----------|
| **Processing** | Single-threaded, sequential | Parallel worker pool (configurable N) |
| **Schema definition** | Python classes with embedded validators | YAML files, loaded into immutable registry |
| **Validation** | Interleaved with field definitions | Separate phase, expression-based (`expr` engine) |
| **Database writes** | Django ORM, sequential bulk insert | no ORM, parallel `pgx COPY FROM` |
| **Thread safety** | Mutable schema objects, not safe | Immutable registry, `sync.Pool` for records |
| **Configuration** | Code changes for any schema update | YAML changes, no code deploy needed |
| **Deployment** | Embedded in Django/Celery | Standalone binary; runs as Celery worker, HTTP service, Lambda, or CLI |
| **Error documentation** | Manually maintained | Auto-generated from same YAML validators use |
| **Local validation** | Not possible (requires Django + DB) | Single binary, dry-run mode with file output |
| **Memory model** | Creates and discards objects per record | Object pools, pre-warmed, reused across records |

---

## Package Structure

```
parser/
├── cmd/
│   ├── parser/          # Main binary entrypoint
│   └── docgen/          # Error documentation generator
├── config/              # YAML configuration files
│   ├── filespecs/       # Per (program, section)
│   ├── schemas/         # Per record type
│   ├── validation/      # Validator definitions
│   └── pipeline.yaml    # Runtime tuning
└── internal/
    ├── config/          # Config loading, registry, schema compilation
    ├── decoder/         # Format-specific decoders (positional, CSV, XLSX)
    ├── parser/          # Accumulator, orchestrator, field extraction
    ├── pipeline/        # Worker pool, routing, pipeline orchestration
    ├── storage/
    │   ├── reader/      # S3 and local file readers
    │   └── writer/      # Table writers, sinks, record converters
    └── validation/      # Expression engine, validator registry, execution
```

Each package has a single responsibility. The `internal/` prefix enforces that these are private implementation details -- the only public API is the pipeline's `ProcessFile()` method.
