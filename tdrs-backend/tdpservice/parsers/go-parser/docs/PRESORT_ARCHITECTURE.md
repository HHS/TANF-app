# Presort Architecture

This document describes the architecture for sorting input files before parsing. Sorting ensures records are grouped by key fields, enabling streaming accumulation and purely in-memory duplicate detection and case/grouping validation.

## Motivation

The accumulator groups records by composite key (e.g., `RPT_MONTH_YEAR|CASE_NUMBER`) and relies on key-change detection to flush completed groups. Today, files are **assumed** to be sorted by the user. This assumption is fragile: if a file arrives with interleaved case records, the accumulator creates multiple incomplete groups for the same logical case, causing spurious group validation errors and missed duplicate detection.

Presort eliminates this assumption and unlocks three benefits:

1. **Purely in-memory duplicate detection.** With all records for a case guaranteed to be adjacent, duplicate records can be detected within the group during accumulation, without database queries against previously written data.

2. **Purely in-memory case/grouping validation.** Group validators (e.g., `t1_has_t2_or_t3`, `t2_requires_t1`) operate on complete groups. Without presort, records for the same case scattered across the file produce incomplete groups, and the validator either misses errors or must reconcile across groups via the database.

3. **No reliance on user-sorted data.** Users submit data as-is. The parser handles ordering internally, producing correct results regardless of input order.

4. **Bounded memory for the accumulator.** When the file is sorted, the accumulator holds only one active group at a time and flushes completed groups immediately on key change.

## Core Requirement: Original Line Number Preservation

When the parser sorts records before processing, the position of a record in the sorted order differs from its position in the original file. **Error messages must reference the original line number** so users can locate issues in their submitted file to make corrections for resubmission.

This is a hard requirement, not an optimization. The `row_number` column in `parser_error` and the `LineNumber` field in error message templates must always reflect the record's position in the original file.

### Solution: In-Memory Sort with Natural Line Number Preservation

Sorting inherently requires reading all rows into memory (you cannot sort without seeing all data). Since the rows are already in memory, iterate them directly in sorted order rather than writing to a temp file.

Each `decoder.Row` carries its `LineNum()` from the original decode pass. Sorting reorders the slice of Row objects but does not mutate their `lineNum` field. When the accumulator, parser, and error converter subsequently read `Row.LineNum()` and `ParsedRecord.LineNumber`, they get the original file position automatically.

```
Original file:           In-memory after sort:
  Line 1: HEADER           rows[0] = Row{lineNum: 1, data: "HEADER..."}
  Line 2: T1 CASE002       rows[1] = Row{lineNum: 4, data: "T1 CASE001..."}  <- was line 4
  Line 3: T2 CASE002       rows[2] = Row{lineNum: 5, data: "T2 CASE001..."}  <- was line 5
  Line 4: T1 CASE001       rows[3] = Row{lineNum: 2, data: "T1 CASE002..."}  <- was line 2
  Line 5: T2 CASE001       rows[4] = Row{lineNum: 3, data: "T2 CASE002..."}  <- was line 3
  Line 6: TRAILER          rows[5] = Row{lineNum: 6, data: "TRAILER..."}
```

If a validation error fires on `rows[3]` (T1 CASE002), `record.LineNumber` is `2` — the user looks at line 2 of their original file. No mapping table needed.

**Why not a temp file?** Writing sorted rows to a temp file and re-decoding would assign new sequential line numbers from the decoder, destroying the original positions. Carrying metadata (prefixed line numbers, sidecar mapping file) adds complexity for no benefit since the rows are already in memory.

## Processing Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Raw File   │ ──► │   Decoder   │ ──► │  All Rows   │ ──► │   Sorter    │
│             │     │ (streaming) │     │ (in memory) │     │ (stable)    │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
                         Sorted rows iterated directly             │
                         (no temp file, lineNum preserved)         │
                                                                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Database   │ ◄── │   Router    │ ◄── │ ParserPool  │ ◄── │ Accumulator │
│  (COPY)     │     │ (validate   │     │ (N workers) │     │ (streaming) │
│             │     │  + write)   │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

1. **Decoder** reads the raw file, producing `decoder.Row` objects with original `lineNum` set
2. **Sorter** collects all data rows in memory, stable-sorts by key fields, separates HEADER/TRAILER
3. **Accumulator** iterates sorted rows, detects key changes, flushes completed groups as `DecodedBatch`
4. **ParserPool** workers parse batches into `ParsedBatch` (field extraction, type conversion)
5. **ResultRouter** dispatchers validate groups via `ValidationOrchestrator` and route to database writers
6. **Writer** bulk-loads records and errors via `COPY FROM`

## Components

### Sorter

Responsible for reading all rows, separating non-grouped records, and stable-sorting data records by key:

```go
type Sorter struct {
    spec         *filespec.FileSpec
    detector     *RecordTypeDetector
    keyExtractor KeyExtractor
}

// SortResult contains the sorted rows and separated non-grouped records.
type SortResult struct {
    Header       decoder.Row   // HEADER row (nil if absent)
    Trailer      decoder.Row   // TRAILER row (nil if absent)
    SortedRows   []decoder.Row // Data rows sorted by key, lineNum preserved
}

func (s *Sorter) Sort(dec decoder.Decoder) (*SortResult, error)
```

**Sorting algorithm:**
1. Read all rows from decoder into a slice
2. Separate HEADER, TRAILER, and data records using `grouped_schemas` config
3. Extract sort key from each data record via `KeyExtractor`
4. Stable sort data records by key (preserves relative order within same key)
5. Return `SortResult` with sorted rows — each row's `LineNum()` is unchanged

**Stable sort is required.** Records within the same case must retain their original relative order (T1 before T2 before T3 for the same case). Go's `slices.SortStableFunc` provides this guarantee.

### KeyExtractor

Abstracts key extraction across file formats. Reuses the same key field definitions already in the accumulator config:

```go
type KeyExtractor interface {
    ExtractKey(row decoder.Row) (string, error)
}

// PositionalKeyExtractor extracts keys from fixed-width positional rows.
// Uses the same byte positions as accumulator.key_fields.
type PositionalKeyExtractor struct {
    RptMonthYear PositionDef // e.g., {Start: 2, End: 8}
    CaseNumber   PositionDef // e.g., {Start: 8, End: 19}
}

// ColumnarKeyExtractor extracts keys from CSV/XLSX rows by column index or header name.
type ColumnarKeyExtractor struct {
    KeyColumns []ColumnarKeyField
}
```

### Integration with Pipeline

The presort step inserts between file open and accumulator processing in `processRows`:

```go
func processFile(ctx context.Context, spec *filespec.FileSpec, filePath string) error {
    // Step 1: Open file and create decoder
    file, err := os.Open(filePath)
    if err != nil {
        return err
    }
    defer file.Close()

    dec, err := CreateDecoder(file, spec)
    if err != nil {
        return err
    }
    defer dec.Close()

    // Step 2: Read header
    headerRow, err := dec.ReadFirst()
    if err != nil {
        return err
    }

    // Step 3: Create detector
    detector := parser.NewRecordTypeDetector(spec, registry)

    // Step 4: Presort
    sorter := parser.NewSorter(spec, detector)
    sortResult, err := sorter.Sort(dec)
    if err != nil {
        return fmt.Errorf("presort failed: %w", err)
    }

    // Step 5: Feed sorted rows to accumulator
    acc := parser.NewAccumulator(spec, detector)
    for _, row := range sortResult.SortedRows {
        batch, _, _, err := acc.Add(row)
        if err != nil {
            continue
        }
        if batch != nil {
            parserPool.Submit(batch)
        }
    }

    // Step 6: Drain remaining
    for _, batch := range acc.Drain() {
        parserPool.Submit(batch)
    }

    return nil
}
```

The accumulator, parser pool, validation orchestrator, and writer are unchanged. They already consume `decoder.Row` objects and read `LineNum()` — which is the original file line number regardless of sort order.

## Configuration

### FileSpec Configuration

Presort uses the existing `accumulator.key_fields` to determine sort order. A `presort` flag enables the sort step:

```yaml
accumulator:
  key_fields:
    rpt_month_year:
      start: 2
      end: 8
    case_number:
      start: 8
      end: 19

  batch_size: 1

  grouped_schemas:
    - tanf/t1
    - tanf/t2
    - tanf/t3

  presort: true   # Sort by key_fields before accumulation
```

| Field | Type | Description |
|-------|------|-------------|
| `presort` | bool | When `true`, sort the file by `key_fields` before feeding rows to the accumulator. Requires `key_fields` to be set. |

When `presort` is `false` or absent, behavior is unchanged: rows are fed to the accumulator in file order, and the file is assumed to be sorted.

## Duplicate Detection

With presort, all records sharing a key are adjacent. This enables in-memory duplicate detection during accumulation or group validation:

**Within-group duplicates:** When building a `DecodedGroup`, the accumulator (or a dedicated step) can detect records with identical content or record type within the same case. For example, two T1 records in the same case with identical field values.

**Cross-group duplicates:** Since groups are processed in sorted key order, a simple "last seen key" check in the accumulator already prevents splitting the same case into multiple groups. Without presort, the same case appearing at lines 10 and 500 would create two separate groups — presort guarantees they merge into one.

This replaces any need to query the database for previously written records when checking for duplicates within a single file submission.

## Edge Cases

### HEADER/TRAILER Positioning

Non-grouped records (HEADER, TRAILER) are identified via `grouped_schemas` — any record whose schema path is not in `grouped_schemas` is excluded from sorting. The sorter separates these during the initial pass and returns them in `SortResult.Header` and `SortResult.Trailer`.

HEADER is already consumed before the sort step (via `dec.ReadFirst()`). TRAILER is detected during sorting and excluded from the sorted data rows.

### Malformed Records

Records that fail key extraction (too short, invalid format, unrecognized record type):
- Accumulate into a separate "unkeyed" collection in the `SortResult`
- Process after all sorted groups, generating appropriate pre-check errors
- Each malformed record still carries its original `LineNum()` for error reporting

### Empty Files / Header-Only Files

- Files with only HEADER/TRAILER: `SortResult.SortedRows` is empty, no data to sort
- Completely empty files: handled before the sort step (decoder produces no rows)

### Memory

Sorting requires holding all data rows in memory simultaneously. This is the same memory used by `batch_size: 0` mode today (accumulate all groups). For typical TANF submissions (tens of thousands of records), this is well within container memory limits.

For extremely large files, memory usage during the sort phase is bounded by `O(N)` where N is the number of data rows. After sorting, the accumulator processes rows one at a time and releases completed groups to the parser pool, so peak memory during the parsing/validation phase is unchanged.

### Disk Space

No temp files are written. The in-memory approach eliminates the disk space concern from the original design.

## File Format Support

| Format | Key Extraction | Sort Support | Notes |
|--------|----------------|--------------|-------|
| Positional | Byte positions | In-memory stable sort | TANF, SSP, Tribal — primary use case |
| CSV | Column index or header | In-memory stable sort | Standard library |
| XLSX | Column index or header | In-memory stable sort | Rows already loaded to memory by decoder |

XLSX files are binary and loaded fully into memory by the decoder. Presort adds no additional memory overhead for XLSX since all rows are already materialized.
