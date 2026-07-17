# Go Parser Service Context

This context covers the Go parser service under `tdrs-services/parser/`.

## Boundaries

- The Go parser replaces the Python parser for TANF, SSP, Tribal TANF, and FRA data files.
- Parser implementation, parser-specific Go tests, parser configuration, SQLC inputs, generated DB access code, and parser service Docker assets live here.
- The parser uses a YAML-driven pipeline to decode, parse, validate, and write records.
- Production-like local integration runs the parser in Celery mode as the `go-parser` Docker Compose service from `tdrs-backend/docker-compose.yml`.
- Parsing output, validation results, task status, and database writes are product behavior and may affect backend workflows.
- Cross-service changes should also read `tdrs-backend/CONTEXT.md`.

## Important Paths

- `cmd/parser/`: main parser binary.
- `cmd/docgen/`: validation error documentation generator.
- `config/parser.yaml`: primary parser configuration.
- `config/validation/validators.yaml`: validation rule configuration.
- `internal/decoder/`: CSV, XLSX, positional, and row decoding.
- `internal/parser/`: parsing, transformation, sorting, accumulation, and orchestration.
- `internal/pipeline/`: worker pool, routing, and pipeline execution.
- `internal/validation/`: validation registry, execution, environment, and results.
- `internal/db/`: SQLC-generated and DB-facing code.
- `schema.sql`, `query.sql`, `sqlc.yaml`: SQLC schema/query/code generation inputs.
- `docs/architecture.md`: parser architecture overview.

## Read With

- Root `CONTEXT.md`
- `CONTEXT-MAP.md`
- Backend context when parser behavior is consumed by Django or Celery workflows
- Parser README or package-level documentation near the code being changed
- `tdrs-backend/pytest-go-parser.ini` and `tdrs-backend/tdpservice/parsers/test/integration/` when changing Django/Go parser integration behavior

## Test Strategy

There are two distinct integration-test surfaces:

- Go package tests live under `tdrs-services/parser/internal/**` and run from `tdrs-services/parser`.
- Django-to-Go parser integration tests live under `tdrs-backend/tdpservice/parsers/test/integration/` and are executed by pytest in a separate pytest suite.

Use these commands for the common cases:

```sh
# Go unit tests
cd tdrs-services/parser
make test

# Backend live integration suite for Django fixtures + live Go parser worker
task backend-pytest-go-integration
```

The backend integration suite is intentionally isolated from the default `task backend-pytest` run. It uses `tdrs-backend/pytest-go-parser.ini`, `tdpservice.settings.go_parser_integration`, and the `GoParserIntegration` Django configuration so pytest fixtures are committed to the shared Docker database that the Go parser worker can observe.

The `go-parser` Docker Compose service is built from `../tdrs-services/parser` and runs with:

```sh
--server.mode=celery --storage.source=s3
```

It consumes Redis/Celery work from the `go-parser` queue, connects to the shared PostgreSQL database, and reads files from the LocalStack-backed S3 bucket in local integration.
