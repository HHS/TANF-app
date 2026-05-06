# Go Parser

The Go parser replaces the Python parser for processing TANF, SSP, Tribal TANF, and FRA data files. It uses a YAML-driven, parallel pipeline that decodes, parses, validates, and writes records concurrently.

For architecture details, see [docs/GO_PARSER_ARCHITECTURE.md](docs/GO_PARSER_ARCHITECTURE.md).

---

## Prerequisites

- **Go 1.25+** (see `go.mod` for exact version)
- **gotestsum** (test runner): `go install gotest.tools/gotestsum@latest`
- **sqlc** (database code generation): `go install github.com/sqlc-dev/sqlc/cmd/sqlc@latest`
- **PostgreSQL** (for integration tests and database mode)

---

## Project Structure

```
parser/
├── cmd/
│   ├── parser/          # Main parser binary
│   └── docgen/          # Validation error documentation generator
├── config/
│   ├── parser.yaml      # Primary configuration file
│   ├── filespecs/       # File specifications per (program, section)
│   ├── schemas/         # Field layouts per record type
│   └── validation/      # Validator definitions
├── internal/            # Private implementation packages
├── schema.sql           # PostgreSQL schema (mirrors Django models)
├── query.sql            # SQL queries for SQLC
├── sqlc.yaml            # SQLC configuration
└── Makefile             # Build and test targets
```

---

## Building

```sh
# Build the parser for your current platform
make build
# Output: build/go-parser

# Build the docgen tool
make build-docgen
# Output: build/docgen

# Build for all platforms (linux, darwin, windows - amd64 + arm64)
make build-all

# Run directly without building
go run ./cmd/parser [flags]
go run ./cmd/docgen [flags]
```

---

## Configuration

The parser uses a layered configuration system. Override precedence (lowest to highest):

1. Compiled defaults
2. Config file (`config/parser.yaml`)
3. Environment variable interpolation (`${VAR}` syntax in YAML)
4. CLI flags (`--section.key=value`)

### Config File

The primary config file is `config/parser.yaml`. Key sections:

| Section      | Controls                                                         |
| ------------ | ---------------------------------------------------------------- |
| `server`     | How the parser receives work (`local`, `celery`, `grpc`, `http`) |
| `pipeline`   | Worker pool sizes and buffer depths                              |
| `writer`     | Output mode (`database` or `file`), flush thresholds             |
| `validation` | Short-circuit behavior, validator file paths                     |
| `database`   | PostgreSQL connection pool settings                              |
| `storage`    | File acquisition (`local` or `s3`)                               |

### Environment Variables

The config file supports `${VAR}` interpolation. Common variables:

| Variable             | Used In                   | Purpose                         |
| -------------------- | ------------------------- | ------------------------------- |
| `DATABASE_URL`       | `database.url`            | PostgreSQL connection string    |
| `GO_PARSER_SHADOW_MODE` | `database.shadow_mode` | `true` writes to shadow tables; `false` writes to production tables |
| `DATABASE_TABLE_PREFIX` | `database.table_prefix` | Prefix for Go parser-owned output tables (default `shadow_`) |
| `REDIS_URL`          | `server.celery.redis_url` | Redis broker for Celery mode    |
| `S3_BUCKET`          | `storage.s3.bucket`       | S3 bucket for file storage      |
| `S3_ENDPOINT`        | `storage.s3.endpoint`     | Custom S3 endpoint (LocalStack) |
| `AWS_DEFAULT_REGION` | `storage.s3.region`       | AWS region                      |

---

## Running the Parser

### Local Mode (Most Common for Development)

Local mode processes a single file from the local filesystem. No Redis, S3, or Celery required.

```sh
# Parse a TANF Section 1 file, writing results to database
go run ./cmd/parser \
  --server.mode=local \
  --server.local.file-path=path/to/file.txt \
  --server.local.program=TANF \
  --server.local.section=1 \
  --server.local.fiscal-year=2020 \
  --server.local.quarter=1

# Dry run — same parsing and validation, but output to local files instead of database
go run ./cmd/parser \
  --server.mode=local \
  --server.local.file-path=path/to/file.txt \
  --server.local.program=TANF \
  --server.local.section=1 \
  --server.local.fiscal-year=2020 \
  --server.local.quarter=1 \
  --dry-run

# Dry run outputs NDJSON by default. Use --writer.format=csv for CSV:
go run ./cmd/parser \
  --dry-run \
  --writer.format=csv \
  --server.local.file-path=path/to/file.txt \
  --server.local.program=SSP \
  --server.local.section=2 \
  --server.local.fiscal-year=2021 \
  --server.local.quarter=3

# Output goes to ./output/ by default (configurable via --writer.output-dir)
```

### Filtering Output

```sh
# Only write T1 records (skip T2, T3, etc.)
go run ./cmd/parser \
  --server.mode=local \
  --server.local.file-path=path/to/file.txt \
  --server.local.program=TANF \
  --server.local.section=1 \
  --server.local.fiscal-year=2020 \
  --server.local.quarter=1 \
  --dry-run \
  --writer.include-schemas=tanf/t1

# Write only errors (no records)
go run ./cmd/parser \
  --server.mode=local \
  --server.local.file-path=path/to/file.txt \
  --server.local.program=TANF \
  --server.local.section=1 \
  --server.local.fiscal-year=2020 \
  --server.local.quarter=1 \
  --dry-run \
  --writer.include-records=false
```

### Tuning the Pipeline

```sh
# Adjust worker count and buffer sizes
go run ./cmd/parser \
  --pipeline.num-workers=4 \
  --pipeline.work-buffer-size=64 \
  ...
```

### Celery Mode

Celery mode connects to Redis and consumes parse tasks dispatched by Django. This is the production deployment mode.

```sh
DATABASE_URL=postgres://user:pass@localhost:5432/tdrs \
REDIS_URL=redis://localhost:6379 \
go run ./cmd/parser --server.mode=celery
```

### Profiling

```sh
# CPU profile
go run ./cmd/parser --cpuprofile=cpu.prof ...
go tool pprof cpu.prof

# Memory profile
go run ./cmd/parser --memprofile=mem.prof ...
go tool pprof mem.prof
```

---

## Running Docgen

The `docgen` tool generates an HTML reference of every possible validation error, directly from the same YAML configuration the parser uses at runtime.

```sh
# Generate full documentation to stdout
go run ./cmd/docgen

# Write to a file
go run ./cmd/docgen --output=validation-reference.html

# Filter to a specific filespec
go run ./cmd/docgen --filespec=TANF:1

# Filter to a specific record type
go run ./cmd/docgen --record=T1

# Combine filters
go run ./cmd/docgen --filespec=TANF:1 --record=T1 --output=tanf-t1-errors.html

# Use a custom config file
go run ./cmd/docgen --config-file=path/to/parser.yaml
```

---

## Testing

Tests use `gotestsum` for formatted output. All Makefile targets pass `-count=1` to disable test caching.

```sh
# Run unit tests
make test

# Run with verbose per-test output
make test-verbose

# Run only short tests (skip long-running ones)
make test-short

# Run tests with coverage report
make test-coverage

# Run all tests with coverage
make test-all-coverage

# Compile all packages and tests without executing them
make compile-check

# Run Go static analysis
make lint

# Verify sqlc-generated code is in sync with schema.sql and query.sql
make sqlc-diff

# Run sqlc static analysis checks
make sqlc-vet

# Verify parser SQL against the configured engine and schema
make sqlc-verify

# Load config and compile validator expressions from YAML
make validate-config

# Run the non-test CI checks together
make ci-checks

# Watch mode — re-runs tests on file changes
make test-watch

# CI mode — outputs JUnit XML
make test-ci
```

### Running a Single Test

```sh
# Run a specific test by name
gotestsum -- -count=1 -run TestAccumulatorKeyedGrouping ./internal/parser/...

# Run tests in a specific package
gotestsum -- -count=1 ./internal/validation/...
```

## SQLC (Database Code Generation)

The Go parser uses [SQLC](https://sqlc.dev) to generate type-safe Go code from SQL. The schema in `schema.sql` mirrors the Django model definitions, with Go-owned output tables prefixed as `shadow_*` so Python/Django parser output remains isolated.

```sh
# Regenerate Go code from schema.sql and query.sql
sqlc generate

# Check if generated code is up to date (useful for CI)
sqlc diff

# Run sqlc lint-style checks
sqlc vet
```

Generated code lives in `internal/db/` and should not be edited by hand.

---

## CircleCI Checks

The CircleCI parser job runs these checks from `tdrs-services/parser/`:

```sh
task parser:compile-check
task parser:lint
task parser:sqlc-diff
task parser:sqlc-vet
task parser:sqlc-verify
task parser:validate-config
task parser:test-all-coverage
```

Live Go parser integration coverage runs through the backend pytest suite:

```sh
task backend-pytest-go-integration
```

For integration tests in CI, CircleCI reuses the existing backend docker-compose stack, including PostgreSQL and the Django migration flow, before running the Go parser integration suite with `DATABASE_URL` pointed at that migrated test database. By default, Go parser records, parser errors, datafile metadata, and summaries are written to `shadow_*` tables in that same database. Set `GO_PARSER_SHADOW_MODE=false` to target production tables instead.

---

## Debugging with VS Code

### Prerequisites

1. Install the [Go extension](https://marketplace.visualstudio.com/items?itemName=golang.Go) for VS Code
2. When prompted, install `dlv` (Delve) via the extension, or manually: `go install github.com/go-delve/delve/cmd/dlv@latest`

### Example Launch Configurations

| Configuration | Description                                                                  |
| ------------- | ---------------------------------------------------------------------------- |
| **Go DB**     | Parse a local file and write results to PostgreSQL                           |
| **Go DryRun** | Parse a local file with `--dry-run` (CSV output to local files, no database) |

```jsonc
{
    "name": "Go DB",
    "type": "go",
    "request": "launch",
    "mode": "auto",
    "program": "${workspaceFolder}/tdrs-services/parser/cmd/parser",
    "cwd": "${workspaceFolder}/tdrs-services/parser",
    "env": {},
    "args": ["--database.url", "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable",
              "--server.local.file-path", "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.NDM1.TS53_fake.txt",
              "--server.local.program", "TAN",
              "--server.local.section", "1",
              "--server.local.fiscal-year", "2023",
              "--server.local.quarter", "2"]
},
{
    "name": "Go Celery",
    "type": "go",
    "request": "launch",
    "mode": "auto",
    "program": "${workspaceFolder}/tdrs-services/parser/cmd/parser",
    "cwd": "${workspaceFolder}/tdrs-services/parser",
    "env": {
        "AWS_ACCESS_KEY_ID": "test",
        "AWS_SECRET_ACCESS_KEY": "test"
    },
    "args": ["--database.url", "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable",
              "--server.mode=celery",
              "--server.celery.redis-url=redis://localhost:6379/0",
              "--storage.source=s3",
              "--storage.s3.key-prefix=dev",
              "--storage.s3.bucket=tdp-datafiles-localstack",
              "--storage.s3.endpoint=http://localhost:4566",
              "--storage.s3.region=us-gov-west-1",
              "--writer.mode=database"]
},
{
    "name": "Go DryRun",
    "type": "go",
    "request": "launch",
    "mode": "auto",
    "program": "${workspaceFolder}/tdrs-services/parser/cmd/parser",
    "cwd": "${workspaceFolder}/tdrs-services/parser",
    "env": {},
    "args": ["--dry-run", "--writer.format=csv",
              "--server.local.file-path", "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.NDM1.TS53_fake.txt",
              "--server.local.program", "TAN",
              "--server.local.section", "1",
              "--server.local.fiscal-year", "2023",
              "--server.local.quarter", "2"]
}
```

**Important**: `cwd` must point to `cmd/parser` so the parser can resolve `config/` relative paths correctly.

### Debugging Tips

- Set breakpoints in any `internal/` package -- Delve will step into them
- Use the **Go DryRun** configuration to debug parsing and validation without needing a database
- The **Go DB** configuration requires a running PostgreSQL instance and a valid `--database.url` argument
- To debug a specific record type, add `--writer.include-schemas=tanf/t1` to the `args` array to limit output and reduce noise
- To debug tests, use VS Code's built-in "Debug Test" CodeLens that appears above each `func Test...` in the editor

---

## Common Workflows

### Adding a New Record Type

1. Create a schema YAML in `config/schemas/<program>/<type>.yaml`
2. Add the schema path to the relevant filespec in `config/filespecs/`
3. Add validators for the new fields in `config/validation/validators.yaml`
4. Add a row serializer in `internal/storage/writer/`
5. Add the table to `schema.sql` and run `sqlc generate`

### Modifying a Validator

1. Edit the rule in `config/validation/validators.yaml`
2. Run `make test` to verify
3. Run `go run ./cmd/docgen` to confirm the error message renders correctly

### Checking Parser Output Against a File

```sh
# Quick dry-run check with JSON output
go run ./cmd/parser \
  --dry-run \
  --server.local.file-path=testdata/my-file.txt \
  --server.local.program=TANF \
  --server.local.section=1 \
  --server.local.fiscal-year=2020 \
  --server.local.quarter=1

# Inspect the output
cat output/search_indexes_tanf_t1.ndjson | head
cat output/parser_error.ndjson | head
```
