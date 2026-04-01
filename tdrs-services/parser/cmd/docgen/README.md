# docgen

Generates a validation error reference document from the parser's YAML configuration. The output is a structured listing of every filespec, record type, field, and validator — with rendered example error messages — intended as living documentation for users to understand what checks the parser performs and what errors they may encounter.

## Build

```bash
make build-docgen
```

## Usage

```bash
# Generate HTML to stdout
./build/docgen -c config/parser.yaml

# Generate HTML to a file
./build/docgen -c config/parser.yaml -o output.html

# Filter to a single filespec
./build/docgen -c config/parser.yaml --filespec TANF:1

# Filter to a single record type within a filespec
./build/docgen -c config/parser.yaml --filespec TANF:1 --record T1
```

### Flags

| Flag | Default | Description |
|------|---------|-------------|
| `-c`, `--config-file` | `config/parser.yaml` | Path to the parser config file (relative or absolute) |
| `-o`, `--output` | stdout | Output file path |
| `--filespec` | | Filter to a single filespec (e.g. `TANF:1`, `SSP:2`) |
| `--record` | | Filter to a single record type (e.g. `T1`, `M2`) |

## Testing the HTML output locally

The HTML output is designed to be served from the Knowledge Center static site at `product-updates/knowledge-center/`. To preview it locally with full styling:

```bash
# From the go-parser directory, generate directly into the knowledge center
./build/docgen -c config/parser.yaml -o ../../../../product-updates/knowledge-center/validation-reference.html

# Start a local server from the product-updates directory
cd ../../../../product-updates
python3 -m http.server 8000

# Open in your browser
open http://localhost:8000/knowledge-center/validation-reference.html
```

## How it works

docgen reuses the same config loading pipeline as the parser (`config.LoadConfig` + `config.NewRegistry` + `validation.NewRegistry`). It walks every filespec, schema, and compiled validator to build a documentation model, then renders it as HTML using an embedded Go template. Error message templates are rendered with a synthetic context so the output shows realistic example messages rather than raw Go template syntax.

Any changes to schemas, filespecs, or predefined validators in `config/` are automatically reflected the next time docgen is run.

## When docgen itself needs updating

Most config changes (adding validators, fields, schemas) are picked up automatically. The following changes require updating docgen's code:

- **New message template variables** — docgen renders example messages using a synthetic context map in `renderMessage()` (`main.go`). If `internal/storage/writer/error.go` adds a new context variable (beyond `RecordType`, `Item`, `Value`, `Params`, `RecordLength`, `LineNumber`, `FriendlyName`, `Fields`), docgen must be updated to supply it or templates using it will fall back to raw text.

- **New error type codes** — if a new error type is added beyond `RECORD_PRE_CHECK`, `FIELD_VALUE`, `VALUE_CONSISTENCY`, and `CASE_CONSISTENCY`, the `friendlyErrorType()` function in `main.go` needs a new case for the human-readable label.

- **Validators with no message template** — inline validators defined with `expr` but no `message` will render as `(no message)` in the output. This is not a bug in docgen but a gap in the validator definition.

- **Group validators using `{{.RecordType}}`** — docgen infers the record type from the `record_type` param (used by duplicate detection validators). Group validators that use `{{.RecordType}}` in their message but don't have a `record_type` param will render with the filespec key (e.g. `TANF:1`) instead of an actual record type.

- **Knowledge Center HTML structure changes** — if the USWDS layout, navigation components, or asset paths in `product-updates/` change, the embedded HTML template at `cmd/docgen/templates/validation-reference.html.tmpl` may need to be updated to match.
