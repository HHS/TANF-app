# Parsing and Reparsing Architecture

- **Status:** Internal reference documentation
- **Scope:** TDP data file upload, parsing, validation, error reporting, and reparsing
- **Last updated:** 2026-06-05

---

## Purpose

This document explains how TDP moves a submitted data file from upload through parser outcome, and how admin-triggered reparsing reuses that same path. It is intended to explain the system structure, behavior rules, and operational tradeoffs. It is not a line-by-line guide to the implementation.

Use this document when you need to understand:

- which part of the system owns each stage of a submission,
- how parser outcomes are represented,
- how validation errors affect records, summaries, reports, and emails,
- what reparsing resets before it runs, and
- which behavior is important to preserve during refactors.

For implementation details, use the source files referenced in [Where to Look](#where-to-look).

---

## Core Concepts

### `DataFile`

`DataFile` represents the uploaded submission. It owns metadata such as program, section, reporting period, uploader, STT, and the uploaded file itself. It also has a lifecycle `state` that describes where the submission is in the upload and parsing process.

Examples of lifecycle state:

- uploaded,
- virus scan started or completed,
- parse started,
- parse completed,
- parse completed with errors,
- parse failed.

### `DataFileSummary`

`DataFileSummary` represents the parser outcome for one `DataFile`. It is the primary source used by parser emails, error report views, aggregate counts, and user-facing parse status.

The important distinction is:

- `DataFile.state` describes the lifecycle of processing the file.
- `DataFileSummary.status` describes the parser outcome.

Those two concepts usually move together, but they answer different questions. Refactors should keep that distinction explicit.

### Parsed Records

Parsed records are stored in program- and section-specific search index models, such as TANF, SSP, Tribal TANF, FRA, and audit record tables. They are tied back to the `DataFile`.

The parser may create records before it knows whether every cross-record validation has passed. Some later validation results can remove records that were already written.

### `ParserError`

`ParserError` stores validation and parser errors for a submitted file. Active errors are the source for parser outcome, aggregate summaries, and generated Excel reports.

Errors are categorized by severity and behavior. Some errors allow records to remain accepted with errors; others reject records or cases.

### Error Report

The Excel error report is generated after parsing from active `ParserError` rows and stored on the `DataFileSummary`. It is a derived artifact, not the source of truth.

### Reparse Metadata

Reparse metadata tracks admin-triggered reparse batches and per-file progress. It lets admins see which files were selected, which files finished, whether a file succeeded, and how record counts changed.

---

## System Shape

The parsing path has five broad stages:

1. **Upload and scan**
   The API validates the request, creates a `DataFile` metadata row without storing the uploaded file, runs antivirus scanning, and queues parsing only if the file is safe.

2. **Background parse orchestration**
   A Celery worker loads the file, creates a summary, selects the parser family, runs parsing and validation, and updates lifecycle state.

3. **Parsing and validation**
   The selected parser converts rows into structured records and validation errors. Some validation is local to a row or field; some validation compares records in the same case or file.

4. **Persistence and summarization**
   The parser writes records and errors to the database, computes the parser outcome, updates aggregate counts, and applies cleanup rules for rejected cases or duplicate records.

5. **Reports and notifications**
   TDP generates an Excel error report and sends the appropriate notification email when the parse outcome calls for one.

The same background parse path is used for first-time submissions and reparses. Reparsing changes the setup and tracking around the parse, not the core parser behavior.

---

## First-Time Submission Flow

When a user uploads a file:

1. The API validates the submission metadata and file extension.
2. `DataFileSerializer.create()` creates a `DataFile` row in the initial upload state, with no uploaded file stored yet.
3. TDP advances the row to virus-scan-started and scans the uploaded file with ClamAV during the request.
4. If the file is unsafe or the scanner is unavailable, the request fails, the `DataFile` remains for lifecycle visibility, the uploaded file is not stored, and no parser task is queued.
5. If the file is safe, TDP marks the scan complete, stores the uploaded file, and queues a parse task.
6. The API returns after the task is queued; parsing continues asynchronously.

When the parse task runs:

1. It creates a `DataFileSummary` in a pending parser-outcome state.
2. It selects the parser family based on program, section, and audit status.
3. It parses rows, writes valid records, and records validation errors.
4. It applies cross-record rules such as case consistency and duplicate handling.
5. It computes the final `DataFileSummary.status`.
6. It maps the parser outcome back onto `DataFile.state`.
7. It generates an error report and performs aggregate calculations according to the file type, stores them on the summary.
8. It sends a notification when the outcome should be surfaced to users.

---

## File Shapes and Decoders

TDP ingests two structurally different kinds of file:

- **Fixed-width text files.** TANF, SSP-MOE, Tribal TANF, and program-audit submissions are line-oriented UTF-8 text files where each row is a single string and every field has a known character position and length. The first line is a `HEADER` row, the last line is a `TRAILER` row, and detail rows are identified by a two-character record-type code (e.g. `T1`, `T2`, `M1`, `T7`).
- **Columnar files.** FRA submissions are tabular: either a CSV file or an XLSX workbook. Rows are sequences of typed cell values rather than a single string, and there is one logical record type per FRA section (for example, `TE1` for FRA Work Outcome / TANF Exiters).

Decoders normalize those two shapes into a uniform row stream consumed by the parsers. There are three concrete decoders, all returning a row object that exposes a record-type tag, a row number, and a way to read values out of the row:

| Decoder | Used for | Row representation | How fields are addressed |
|---|---|---|---|
| `Utf8Decoder` | TANF / SSP / Tribal / program audit | `RawRow` wrapping the line as a single string | `Position(start, end)` slice into the string |
| `CsvDecoder` | FRA CSV uploads | `TupleRow` wrapping the row as a tuple of cell values | `Position` used as a column index |
| `XlsxDecoder` | FRA XLSX uploads | `TupleRow` wrapping cell values from the first worksheet | `Position` used as a column index |

The shared `Position` abstraction is what lets one schema/field model serve both file shapes: in fixed-width files a `Position` is a character range, in FRA files it is a column index into the row tuple.

The FRA CSV and XLSX decoders currently report every detail row as record type `TE1`, because FRA has only one implemented record type.

`DecoderFactory.get_suggested_decoder` picks the decoder by sniffing the uploaded file:

1. If the file is empty, it falls back to the file extension (`.csv` → CSV, `.xlsx` → XLSX, otherwise UTF-8).
2. Otherwise it reads the first 4 KB and runs `chardet`. If the detected encoding is ASCII or UTF-8 it returns CSV when the extension is `.csv`, otherwise UTF-8.
3. If the encoding is not text-like, it runs `puremagic` against the same buffer and returns XLSX when the magic bytes match.
4. Anything else surfaces as an unknown decoder, which the parser turns into a file-level pre-check error and a `DecoderUnknownException`.

Decoder selection is independent of the parser family: it is driven entirely by the file's bytes and extension, not by the program type or section. The parser family decides what to *do* with the rows the decoder produces.

---

## Parser Families and Parser Selection

TDP currently has three parser families:

| Parser family | Handles | Notes |
|---|---|---|
| TANF data report parser | TANF, SSP-MOE, and Tribal TANF active, closed, aggregate, and stratum files | Uses record schemas, header/trailer schemas, and case-level validation. |
| FRA parser | FRA Work Outcome / TANF Exiters files | Reads CSV/XLSX via the columnar decoders and uses FRA-specific schemas and reporting. |
| Program audit parser | Program Integrity Audit submissions | Inherits from the TANF parser but preserves duplicate records while still reporting duplicate errors. |

The parser family determines how the row stream is interpreted, which schemas are used, which validation rules apply, and which destination models receive parsed records.

The parse task selects the parser family in two short steps:

1. **Family from `program_type` and `is_program_audit`.** `ParserFactory.get_class(program_type, is_program_audit)` returns:
   - `TanfDataReportParser` for `TANF`, `SSP`, or `TRIBAL` when the file is not a program audit submission;
   - `ProgramAuditParser` for `TANF`/`SSP`/`TRIBAL` when `is_program_audit` is true;
   - `FRAParser` for `FRA`.

   Both `program_type` and `is_program_audit` are stored on the `DataFile` at upload time, so this decision does not depend on parsing the file.

2. **Schema set from `program_type` + `section`.** Once the parser is constructed, it loads the appropriate schemas via `ProgramManager.get_schemas(program_type, section, is_program_audit)`. The mapping is:

   | Program | Section | Record types |
   |---|---|---|
   | TANF | Active Case Data | `T1`, `T2`, `T3` (or program-audit `T1`/`T2`/`T3` when `is_program_audit`) |
   | TANF | Closed Case Data | `T4`, `T5` |
   | TANF | Aggregate Data | `T6` |
   | TANF | Stratum Data | `T7` |
   | SSP | Active / Closed / Aggregate / Stratum | `M1`–`M3` / `M4`–`M5` / `M6` / `M7` |
   | Tribal TANF | Active / Closed / Aggregate / Stratum | mirrors TANF (`T1`–`T7`) |
   | FRA | Work Outcome / TANF Exiters | `TE1` |

   For TANF-family files, the parser also reads the file's `HEADER` row before loading record schemas; the header determines the final program type passed to the schema manager (for example, when the header has a non-empty `tribe_code`, the parser uses `DataFile.ProgramType.TRIBAL`) and whether record fields are encrypted.

Program-audit overrides only exist for Active Case Data (`T1`/`T2`/`T3`); other sections use the standard TANF schemas even when `is_program_audit` is true.

FRA's two other planned sections (Secondary School Attainment, Supplement Work Outcomes) are recognized by the section enum but currently have no schemas, so the schema manager returns an empty map for them.

---

## Schema Definitions

Schemas are declarative Python objects that describe one record type. They live under `tdrs-backend/tdpservice/parsers/schema_defs/` organized by program and record type (for example, `schema_defs/tanf/t1.py`, `schema_defs/fra/te1.py`). Each module exports a list of one or more schema instances so a single record type can have multiple schemas (used for header/trailer variants and for program-audit overrides).

There are two base concrete schema classes, plus one header/trailer subclass:

- `TanfDataReportSchema` for TANF/SSP/Tribal/program-audit detail records.
- `FRASchema` for FRA detail records.
- `HeaderSchema`, a subclass of `TanfDataReportSchema`, for the `HEADER` and `TRAILER` rows of TANF-family files.

A schema is composed from:

- **`record_type`** — the two-character (or short) tag the decoder reports for this row (e.g. `T1`, `M4`, `TE1`).
- **`model`** — the Django/search-index model the parser writes successful records into (e.g. `TANF_T1`, `TANF_Exiter1`).
- **`fields`** — a list of `Field` or `TransformField` entries describing each column. A field has an item number, name, friendly name, `FieldType` (`NUMERIC` or `ALPHA_NUMERIC`), `Position`, `required` flag, and a list of field-level validators. `TransformField` adds a `transform_func` applied to the raw value before validation (used, for example, to coerce an XLSX `datetime` cell into the FRA `EXIT_DATE` integer or to zero-pad fixed-width values).
- **`preparsing_validators`** — record/row-level checks that run against the raw row after `parse_row` builds the in-memory record but before field-level validation. They cover length, record-type position, reporting period alignment, and similar category 1 rules.
- **`postparsing_validators`** — cross-field checks applied to the parsed record (TANF-family schemas only).
- **`partial_dup_exclusion_query` / `get_partial_dup_fields`** — control which records are exempt from partial-duplicate detection and which fields define a partial duplicate for this record type (`get_partial_dup_fields` is TANF-family schemas only).
- **`quiet_preparser_errors`** — when true, preparsing failures are dropped silently instead of surfaced as parser errors. Used for rows that are expected to be ignored (e.g. lines that only matter to a different record type).

Validators are factory functions that return a callable. They live in `tdpservice/parsers/validators/` and are split into categories that map directly to the validation layers below:

- **`validators/category1.py`** — preparsing/record-level validators that operate on the raw row (e.g. `recordHasLengthOfAtLeast`, `validateRptMonthYear`, `validate_exit_date_against_fiscal_period`).
- **`validators/category2.py`** — field-level validators that operate on a single parsed value (e.g. `isOneOf`, `isBetween`, `intHasLength`, `fraSSNAllOf`).
- **`validators/category3.py`** — postparsing validators that compare fields within the same record (e.g. `ifThenAlso(...)` for conditional rules like "if `CASH_AMOUNT > 0` then `NBR_MONTHS > 0`").
- **`validators/base.py`** — shared building blocks that both category 2 and category 3 wrap with category-specific error messages.

Cross-record ("category 4") rules are not declared on the schema. They are enforced by `CaseConsistencyValidator` at the parser level after each row has been parsed and added to its case (see [Validation Model](#validation-model)).

A condensed example of a TANF `T1` schema:

```python
t1 = [
    TanfDataReportSchema(
        record_type="T1",
        model=TANF_T1,
        get_partial_dup_fields=get_t1_t4_partial_dup_fields,
        preparsing_validators=[
            category1.recordHasLengthOfAtLeast(117),
            category1.caseNumberNotEmpty(8, 19),
            category1.or_priority_validators([
                category1.validate_fieldYearMonth_with_headerYearQuarter(),
                category1.validateRptMonthYear(),
            ]),
        ],
        postparsing_validators=[
            category3.ifThenAlso(
                condition_field_name="CASH_AMOUNT",
                condition_function=category3.isGreaterThan(0),
                result_field_name="NBR_MONTHS",
                result_function=category3.isGreaterThan(0),
            ),
            # ... more conditional rules
        ],
    ),
]
```

Program-audit schemas mirror the TANF active schemas for the same record types but are kept as a separate set so audit-specific behavior (for example, retaining duplicate records) can diverge without forking the TANF rules.

---

## Validation Model

Validation is layered. The layers matter because each one has a different effect on parser outcome and persisted records, and they are run in a fixed order so later layers can rely on the guarantees of earlier ones.

| Layer | Where it lives | What it checks | Typical outcome |
|---|---|---|---|
| File pre-check | Parser class (decoder selection, header/trailer handling) | File-level viability: encoding, presence and shape of header/trailer, multiple headers, completely missing detail rows | Can reject the entire file. |
| Record pre-check (category 1) | `preparsing_validators` on each schema | Whether an individual raw row can be interpreted as a known record shape (length, record-type position, reporting period vs header) | Can drop the row before field validation. |
| Field validation (category 2) | `validators` on each `Field` / `TransformField` | Field-level format, range, allowed values, and required-value rules on the parsed record | Usually accepts the file with errors. |
| Value consistency (category 3) | `postparsing_validators` on each schema | Cross-field rules inside a single record (e.g. "if amount > 0 then months > 0") | Usually accepts the file with errors. |
| Case consistency (category 4) | `CaseConsistencyValidator` in the parser | Cross-record rules for a case or grouped records, accumulated as rows arrive | Can reject related records after they were parsed. |
| Duplicate detection | Parser cleanup phase | Exact and partial duplicates among already-written records for this file | Removes duplicates (TANF/FRA) or reports duplicates while keeping records (program audit). |

### Order of Operations

For each detail row, the schema runs its layers in this fixed order (`TanfDataReportSchema.parse_and_validate` and `FRASchema.parse_and_validate`):

1. **Parse row → record.** `parse_row` walks the schema's fields, reads each `Position` from the decoded row, applies any `TransformField.transform_func`, coerces to the declared `FieldType`, and assigns the result to the model instance.
2. **Preparsing validators (cat 1).** Run against the raw row after the in-memory record has been built. In TANF-family schemas, if any fail, the row is dropped and no further layers run. In quiet mode (`quiet_preparser_errors`), the errors are suppressed and the row is dropped silently; otherwise the errors are reported as category 1 parser errors. FRA schemas keep the parsed row and continue to field validation so the parser can return both preparsing and field-level errors for that row.
3. **Field validators (cat 2).** Run against each required, non-empty field on the parsed record. Empty required fields generate their own "field is required" error.
4. **Postparsing validators (cat 3).** Run against the parsed record once field validation has completed. (TANF-family schemas only — FRA schemas currently stop after field validation.)

The parser then takes that per-row result and applies the cross-record layers:

5. **Case consistency (cat 4).** Each successfully parsed record is added to `CaseConsistencyValidator`, which accumulates records by case and emits cross-record errors as cases close. Errors generated here can mark records or whole cases for removal even though they were already written in a bulk-create batch.
6. **Duplicate detection.** After all rows have been processed and records bulk-created, TANF-family parsers run exact-duplicate and partial-duplicate sweeps against the written records. FRA currently deletes exact duplicate records. The program-audit parser reports duplicates while keeping records.
7. **Case removal and trailer checks.** For TANF-family files, cases marked for removal by case consistency are deleted, then the parser validates the trailer record count and the "no records created" pre-check error is generated if applicable. FRA skips trailer and case-consistency cleanup, but still generates the "no records created" pre-check error when applicable.

This layered model lets TDP keep useful records when errors are limited, while still rejecting data that cannot be trusted structurally.

### Example: Field Error

A TANF record may parse successfully while one field contains a value outside the allowed range. In that case:

- the parsed record can remain stored,
- a `ParserError` is written,
- the summary may become `Accepted with Errors`, and
- the error report includes the field-level error.

### Example: Case Consistency Error

A TANF case may contain individually valid records that do not make sense together. In that case:

- the parser writes case-consistency errors,
- affected case records may be removed from the accepted record tables,
- the file may become partially accepted, and
- the error report explains which records were rejected.

### Example: Program Audit Duplicates

Program audit submissions report duplicate records differently from standard TANF parsing. Duplicate records are reported as errors, but the records are retained. This preserves audit review data while still flagging the problem.

### Example: FRA Error

FRA files follow a different shape from TANF fixed-width submissions — they are CSV or XLSX rather than fixed-width text, and use the columnar decoders described in [File Shapes and Decoders](#file-shapes-and-decoders). FRA validation still writes `ParserError` rows and produces an Excel error report, but the parser family, schemas, validators, and report format are FRA-specific and do not currently include cross-field (cat 3) or case-consistency (cat 4) rules.

---

## Parser Outcome Rules

`DataFileSummary.status` is derived from parser errors and record outcomes. The exact database values live in the model, but the behavior is:

- **Accepted** means no active parser errors remain.
- **Accepted with errors** means records were created and errors exist that do not require rejecting those records.
- **Partially accepted** means some records or cases were rejected while others were accepted.
- **Rejected** means the file did not produce acceptable records or hit a file-level failure.
- **Pending** means parsing has not finished or the summary has not been updated yet.

`DataFile.state` is then updated from that parser outcome so the submission lifecycle reflects parse completion, completion with errors, or failure.

---

## Error Reports and Notifications

Error reports and emails are downstream of parser outcome.

The error report:

- is generated from active `ParserError` rows,
- is stored on `DataFileSummary`,
- is attempted for both successful and failed parses, and
- can be missing if parsing fails before the summary exists or if report generation itself fails.

Notification emails:

- are sent to approved Data Analysts for the submitting STT,
- use FRA access rules for FRA files,
- use parser outcome to choose the email content, and
- are not the source of parser status.

Because reports are generated after parsing, there is a short timing window where the parse outcome may be known before the error report file is stored.

---

## Reparsing

Reparsing is an admin operation for rerunning parser logic against existing submissions. It exists because parser logic, schemas, and error handling can change after a file was originally submitted.

Before a reparse starts, TDP creates a batch-level reparse record and cleans old parser output for selected files:

- previous parser errors,
- parsed search index records,
- the old `DataFileSummary`,
- and related derived parser artifacts.

Each selected file is then queued through the same parse task used by a first-time submission. Per-file reparse metadata tracks start time, finish time, success, and record-count changes.

### Why Reparsing Cleans First

The parser is not designed as an idempotent upsert pipeline. It expects to create a new summary and write a fresh set of records and errors. Cleaning first avoids mixing old parser results with new ones.

The tradeoff is that a failed or interrupted reparse can leave a file without the previous successful parser outputs until the issue is repaired and rerun.

### Reparse Notifications

Reparse notifications are intentionally quieter than first-time submission notifications. If a file was previously accepted and remains accepted after reparse, notification can be suppressed. Other outcome changes can trigger reprocessed email templates.

---

## Retry and Failure Behavior

The parse task does not automatically retry when it crashes. Operationally, that means:

- a failed or stalled parse needs human inspection,
- admins usually recover by reparsing,
- partial database writes are possible if failure happens mid-parse, and
- cleanup behavior is important but not a substitute for a whole-file transaction.

TDP has scheduled monitoring for stuck files. It identifies submissions that have not reached a completed parser outcome within the expected window and notifies OFA System Admins. It does not repair the file automatically.

---

## Refactor Considerations

These are the behavior contracts that are easy to break accidentally:

1. **Keep lifecycle state and parser outcome distinct.**
   `DataFile.state` and `DataFileSummary.status` should not be collapsed unless the replacement clearly supports both lifecycle tracking and parser outcome reporting.

2. **Clarify ownership before changing shared parser state.**
   `DataFile`, `DataFileSummary`, `ParserError`, error reports, notification logic, and reparse metadata are updated by different parts of the pipeline. Refactors should make the owner of each write explicit so status, counts, and user-facing artifacts do not drift apart.

3. **Do not treat the parser as idempotent without changing cleanup.**
   First-time parsing assumes no existing summary for the file. Reparsing works by deleting old parser output before queuing a fresh parse.

4. **Preserve severity semantics.**
   Field, value, record, case, and file-level errors affect records and user-facing status differently.

5. **Be careful with mid-parse persistence.**
   Records and errors are written in batches. Any change to rollback behavior should account for partial writes.

6. **Keep error reports derived from `ParserError`.**
   The report should reflect stored active errors, not a separate source of truth.

7. **Preserve program-specific differences.**
   TANF, SSP, Tribal TANF, FRA, and program audit submissions share concepts but do not all share duplicate handling, file shape, or report behavior.

8. **Handle reparse progress independently from parse success.**
   Reparse metadata is the only batch-level view of progress across multiple files.

9. **Treat reparsing and duplicate task delivery as race-condition risks.**
   Reparse cleanup, parse task enqueueing, and parser writes happen in separate steps. Overlapping reparses or duplicate task execution can race unless the workflow explicitly coordinates file selection, cleanup, and final status writes.

---

## Where to Look

The following files are useful anchors when you need implementation details:

| Area | Primary files |
|---|---|
| Upload and lifecycle transitions | `tdrs-backend/tdpservice/data_files/views.py`, `tdrs-backend/tdpservice/data_files/submission_lifecycle.py` |
| Submission validation | `tdrs-backend/tdpservice/data_files/serializers.py` |
| Parse task orchestration | `tdrs-backend/tdpservice/scheduling/parser_task.py` |
| Parser selection | `tdrs-backend/tdpservice/parsers/factory.py` |
| File decoders and decoder selection | `tdrs-backend/tdpservice/parsers/decoders.py` |
| Shared parser behavior | `tdrs-backend/tdpservice/parsers/parser_classes/base_parser.py` |
| TANF, SSP, Tribal parser behavior | `tdrs-backend/tdpservice/parsers/parser_classes/tdr_parser.py` |
| FRA parser behavior | `tdrs-backend/tdpservice/parsers/parser_classes/fra_parser.py` |
| Program audit behavior | `tdrs-backend/tdpservice/parsers/parser_classes/program_audit_parser.py` |
| Schema base classes and per-row validation order | `tdrs-backend/tdpservice/parsers/row_schema.py` |
| Schema manager and program/section → schema mapping | `tdrs-backend/tdpservice/parsers/schema_manager.py`, `tdrs-backend/tdpservice/parsers/schema_defs/utils.py` |
| Schema definitions per record type | `tdrs-backend/tdpservice/parsers/schema_defs/` |
| Field and transform definitions | `tdrs-backend/tdpservice/parsers/fields.py`, `tdrs-backend/tdpservice/parsers/transforms.py` |
| Validator categories (cat 1–3 + base) | `tdrs-backend/tdpservice/parsers/validators/` |
| Case consistency (cat 4) | `tdrs-backend/tdpservice/parsers/case_consistency_validator.py` |
| Error report generation | `tdrs-backend/tdpservice/data_files/error_reports.py` |
| Reparse setup and cleanup | `tdrs-backend/tdpservice/search_indexes/reparse.py`, `tdrs-backend/tdpservice/data_files/tasks.py` |
| Parser outcome models | `tdrs-backend/tdpservice/parsers/models.py` |

---

## Documentation Maintenance Guidance

Keep this document stable by documenting behavior rather than control flow. Avoid adding:

- method-level call chains,
- argument names,
- exception-handling mechanics,
- diagrams that duplicate code structure,
- or implementation details that must be updated with every refactor.

When behavior changes, update the relevant rule or example here and link to the implementation for details.
