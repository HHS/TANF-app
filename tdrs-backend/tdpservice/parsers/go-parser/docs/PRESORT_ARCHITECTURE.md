# Presort Architecture

This document describes the architecture for optionally sorting input files before parsing. Sorting ensures records are grouped by key fields, enabling memory-efficient streaming accumulation.

## Motivation

The accumulator groups records by composite key (e.g., `RPT_MONTH_YEAR|CASE_NUMBER`). When files are sorted by this key, the accumulator can flush completed groups immediately upon detecting a key change, rather than holding all groups in memory until EOF.

**Without presort (unsorted file):**
- All groups held in memory until file is fully read
- Memory usage grows with number of unique groups
- Risk of OOM for large files with many cases

**With presort:**
- Groups flushed as soon as key changes
- Only one active group in memory at a time
- Bounded memory usage regardless of file size

## Processing Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Raw File   │ ──► │   Sorter    │ ──► │  Temp File  │ ──► │  Decoder    │
│             │     │             │     │  (sorted)   │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └──────┬──────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │ Accumulator │
                                                            │ (streaming) │
                                                            └──────┬──────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │   Batches   │
                                                            └─────────────┘
```

1. **Sorter** reads the raw file, sorts records by key fields, writes to temp file
2. **Decoder** streams through the sorted temp file
3. **Accumulator** detects key changes and flushes completed groups immediately
4. **Temp file** is deleted after processing

## Configuration

### FileSpec Configuration

```yaml
accumulator:
  key_fields:
    # Positional format (TANF, SSP, Tribal)
    - field: rpt_month_year
      position: { start: 2, end: 8 }
    - field: case_number
      position: { start: 8, end: 19 }

    # Columnar format (CSV, XLSX) - alternative syntax
    # - field: reporting_month
    #   column: 0
    # - field: case_id
    #   column_header: "CASE_ID"

  batch_size: 0

  grouped_schemas:
    - tanf/t1
    - tanf/t2
    - tanf/t3

  # Presort configuration
  presort: true              # Enable sorting before accumulation
  new_group_on: key_change   # Flush previous group when key differs
```

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `presort` | bool | When `true`, sort the file by `key_fields` before accumulation |
| `new_group_on` | string | Flush strategy. `key_change` flushes when key differs from previous row |

## Components

### KeyExtractor Interface

Abstracts key extraction across file formats:

```go
type KeyExtractor interface {
    // ExtractKey returns the composite grouping key from a row
    ExtractKey(row decoder.Row) (string, error)
}

// Format-specific implementations
type PositionalKeyExtractor struct {
    KeyFields []PositionalKeyField
}

type ColumnarKeyExtractor struct {
    KeyFields []ColumnarKeyField
}
```

### Sorter

Responsible for reading, sorting, and writing the sorted output:

```go
type Sorter struct {
    spec         *filespec.FileSpec
    keyExtractor KeyExtractor
    writer       SortedWriter
}

func (s *Sorter) SortFile(inputPath string) (tempPath string, err error)
```

**Sorting Algorithm:**
1. Read all rows using format-appropriate Decoder
2. Separate non-grouped records (HEADER, TRAILER) from data records
3. Extract sort key from each data record
4. Stable sort data records by key
5. Write to temp file: HEADER, sorted data records, TRAILER

### SortedWriter Interface

Abstracts writing sorted output across formats:

```go
type SortedWriter interface {
    // WriteRow writes a single row to the output
    WriteRow(row decoder.Row) error

    // Close finalizes the output and returns the temp file path
    Close() (tempPath string, err error)
}

// Format-specific implementations
type PositionalWriter struct { /* writes raw line bytes */ }
type CSVWriter struct { /* writes CSV-formatted lines */ }
```

### Generalized KeyFieldsConfig

Support both positional and columnar key extraction:

```go
type KeyFieldConfig struct {
    Field        string       `yaml:"field"`

    // Positional format
    Position     *PositionDef `yaml:"position,omitempty"`

    // Columnar format (one of these)
    Column       *int         `yaml:"column,omitempty"`
    ColumnHeader *string      `yaml:"column_header,omitempty"`
}

type KeyFieldsConfig struct {
    Fields []KeyFieldConfig `yaml:"fields"`
}
```

## Updated Main Flow

```go
func processFile(ctx context.Context, spec *filespec.FileSpec, filePath string) error {
    inputPath := filePath

    // Step 1: Presort if configured
    if spec.Accumulator.Presort {
        sorter := processor.NewSorter(spec)
        tempPath, err := sorter.SortFile(filePath)
        if err != nil {
            return fmt.Errorf("presort failed: %w", err)
        }
        defer os.Remove(tempPath)
        inputPath = tempPath
    }

    // Step 2: Open file (original or sorted temp)
    file, err := os.Open(inputPath)
    if err != nil {
        return err
    }
    defer file.Close()

    // Step 3: Create decoder and process
    dec := createDecoder(file, spec)
    defer dec.Close()

    // Step 4: Accumulate with streaming (new_group_on: key_change)
    acc := processor.NewAccumulator(spec, detector)
    for row, err := range dec.Rows() {
        if err != nil {
            return err
        }
        batch, _, _, err := acc.Add(row)
        if err != nil {
            continue
        }
        if batch != nil {
            pool.Submit(batch)
        }
    }

    // Step 5: Drain remaining
    for _, batch := range acc.Drain() {
        pool.Submit(batch)
    }

    return nil
}
```

## File Format Support

| Format | Key Extraction | Write Strategy | Notes |
|--------|----------------|----------------|-------|
| Positional | Byte positions | Raw line bytes | TANF, SSP, Tribal |
| CSV | Column index or header | CSV serialization | Standard library |
| XLSX | Column index or header | Convert to CSV | Binary format requires conversion |

### XLSX Handling

XLSX files are binary and not line-based. Options:
1. **Convert to CSV** during sort (recommended for simplicity)
2. **Keep in memory** after sorting (skip temp file for XLSX)

## Accumulator Simplification

With presort guaranteeing sorted input, the accumulator simplifies:

**Before (dual-mode):**
```go
type Accumulator struct {
    sorted       bool
    groups       map[string]*RecordGroup  // unsorted mode
    currentGroup *RecordGroup             // sorted mode
}
```

**After (single-mode):**
```go
type Accumulator struct {
    newGroupOn   string        // "key_change"
    currentGroup *RecordGroup  // always streaming
}
```

The `groups` map is no longer needed when presort is enabled and `new_group_on: key_change` is configured.

## Considerations

### Line Number Preservation

When files are sorted, the position of a record in the sorted temp file differs from its position in the original file. Error messages must reference the original line number so users can locate issues in their submitted file.

**Option 1: Embed Line Number in Temp File**

Prefix each line in the temp file with the original line number:

```
Temp file format:
0000001|HEADER...
0000004|T1202401CASE001...    <- originally line 4
0000005|T2202401CASE001...    <- originally line 5
0000002|T1202401CASE002...    <- originally line 2
```

The decoder for the temp file parses the prefix to restore the original line number.

*Pros:* Memory-efficient during parsing (streaming)
*Cons:* Custom temp file format, encoding/decoding overhead

**Option 2: Sort In-Memory Without Write-Back**

Keep sorted rows in memory and iterate directly without writing to temp file:

```go
sortedRows := sorter.Sort(allRows)  // []decoder.Row with LineNum() preserved
for _, row := range sortedRows {
    acc.Add(row)  // LineNum() naturally preserved
}
```

*Pros:* Simple, no temp file, line numbers naturally preserved
*Cons:* All rows remain in memory during accumulation

**Option 3: Hybrid Approach**

1. Load all rows into memory (required for sorting)
2. Sort in memory
3. Write to temp file with line number metadata
4. Free in-memory rows
5. Stream through temp file during accumulation

*Pros:* Memory freed before heavy parsing/validation phase
*Cons:* More complex implementation

### HEADER/TRAILER Positioning

Non-grouped records (HEADER, TRAILER) need special handling:
- HEADER should remain at the start of the sorted output
- TRAILER should remain at the end
- These records are identified via `grouped_schemas` config

### Malformed Records

Records that fail key extraction (too short, invalid format):
- **Option A:** Sort to end of file, process last
- **Option B:** Fail fast with error
- **Option C:** Log warning, exclude from sorted output

### Disk Space

The temp file can be as large as the input file. Ensure adequate disk space is available, especially in containerized environments.

### Empty Files

Sorter should handle gracefully:
- Files with only HEADER/TRAILER (no data to sort)
- Completely empty files
