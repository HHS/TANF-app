# Go Parser Architecture Design Document

This document outlines the architectural design for rewriting the TDRS data file parser in Go. The design prioritizes parallel processing, clean separation of concerns, and maintainability while preserving the exact parsing behavior of the existing Python implementation.

## Table of Contents

1. [Overview](#overview)
2. [Background: Understanding TDRS Data Files](#background-understanding-tdrs-data-files)
3. [Current Python Architecture Analysis](#current-python-architecture-analysis)
4. [Go Architecture Overview](#go-architecture-overview)
5. [File Specification System](#file-specification-system)
6. [Schema Definition System](#schema-definition-system)
7. [Registry](#registry)
8. [Multi-Format Support](#multi-format-support)
9. [Record Type Detection](#record-type-detection)
10. [Record Grouping and Batching](#record-grouping-and-batching)
11. [Accumulator](#accumulator)
12. [Worker Pool Implementation](#worker-pool-implementation)
13. [SQLC Integration](#sqlc-integration)
14. [Complete Data Flow](#complete-data-flow)
15. [Code Structure](#code-structure)
16. [Implementation Examples](#implementation-examples)

---

## Overview

### What This Document Covers

This document describes how to build a parser that:

1. Reads data files submitted by states/tribes to the TANF Data Reporting System (TDRS)
2. Extracts individual records from these files
3. Parses each record into structured data
4. Prepares the data for database storage

### Goals

1. **Parallel Processing**: Parse records concurrently while maintaining data integrity
2. **Multi-Format Support**: Handle both fixed-width positional files and columnar files (CSV/XLSX)
3. **Declarative Configuration**: Define file structures and record formats in YAML files
4. **Separation of Concerns**: Keep parsing logic separate from validation and database operations
5. **Extensibility**: Make it easy to add new file formats, programs, or record types
6. **Behavioral Parity**: Produce identical parsing results to the Python implementation

### Key Terminology

Before diving in, let's define some terms used throughout this document:

| Term | Definition |
|------|------------|
| **Program** | The type of assistance program: TANF, SSP, Tribal TANF, or FRA |
| **Section** | A category of data within a program (1-4). Each section contains different types of records |
| **Record Type** | A specific type of record within a file (e.g., T1, T2, T3, HEADER, TRAILER) |
| **Schema** | The definition of fields within a single record type |
| **FileSpec** | The specification of which schemas comprise a file for a given (program, section) |
| **Positional Format** | Fixed-width text files where fields are at specific byte positions |
| **Columnar Format** | CSV or XLSX files where fields are in specific columns |

---

## Background: Understanding TDRS Data Files

### What Are These Data Files?

States and tribes submit data files to report information about families receiving assistance. These files contain records about:

- **Cases**: Family-level information (benefits received, sanctions, etc.)
- **Adults**: Information about adult family members
- **Children**: Information about child family members
- **Aggregate Data**: Summary statistics

### Programs and Their File Formats

Different programs use different file formats:

| Program | Description | File Format | Record Types |
|---------|-------------|-------------|--------------|
| **TANF** | Temporary Assistance for Needy Families | Positional (fixed-width UTF-8) | T1, T2, T3, T4, T5, T6, T7 |
| **SSP** | State Supplemental Program | Positional (fixed-width UTF-8) | M1, M2, M3, M4, M5, M6, M7 |
| **Tribal TANF** | Tribal TANF Program | Positional (fixed-width UTF-8) | T1, T2, T3, T4, T5, T6, T7 |
| **FRA** | Follow-up Research on Assistance | Columnar (CSV or XLSX) | TE1 |

### Sections Within Each Program

Each program (except FRA) has four sections:

| Section | Contains | Record Types (TANF) |
|---------|----------|---------------------|
| **Section 1** | Active case data | T1 (case), T2 (adult), T3 (child) |
| **Section 2** | Closed case data | T4 (case), T5 (adult) |
| **Section 3** | Aggregate data | T6 |
| **Section 4** | Stratum data | T7 |

### Example: TANF Section 1 File Structure

A TANF Section 1 file looks like this:

```
HEADER20204A06   TAN1ED
T12020101111111111223003403361110212120000300000000000008730010000000000000000000000000000000000222222000000002229012
T2202010111111111121219740114WTTTTTY@W2221222222221012212110014722011500000000000000000000000000000000000000000000000000000000000000000000000000000000000291
T320201011111111112120190127WTTTT90W022212222204398100000000
T12020101111111111524503401311110232110374300000000000005450320000000000000000000000000000000000222222000000002229021
T2202010111111111152219730113WTTTT@#Z@2221222122211012210110630023080700000000000000000000000000000000000000000000000000000000000000000000000551019700000000
T320201011111111115120160401WTTTT@BTB22212212204398100000000
TRAILER0002643
```

Let's break this down:

1. **Line 1 (HEADER)**: File metadata - year, quarter, state, program type, etc.
2. **Lines 2-4**: First case (case number `11111111112`)
   - T1: Case-level data
   - T2: Adult in the case
   - T3: Child in the case
3. **Lines 5-7**: Second case (case number `11111111115`)
   - T1: Case-level data
   - T2: Adult in the case
   - T3: Child in the case
4. **Line 8 (TRAILER)**: Record count for validation

### Key Insight: Records Are Grouped by Case

For TANF/SSP/Tribal Section 1 and 2 files, records with the same `RPT_MONTH_YEAR` and `CASE_NUMBER` belong together. This is critical for:

1. **Validation**: Some validation rules check consistency across records in a case
2. **Parallel Processing**: We can process different cases in parallel, but records within a case must be processed together

### FRA Files Are Different

FRA files use a completely different format (CSV or XLSX) and structure:

```csv
202010,11111111111
202010,22222222222
202010,33333333333
```

Key differences:
- **Columnar format**: Fields are separated by commas (CSV) or in spreadsheet columns (XLSX)
- **Single record type**: All rows are TE1 records
- **No case grouping**: Each record is independent and can be processed separately

---

## Current Python Architecture Analysis

### How the Python Parser Works

The existing Python implementation uses a class-based schema definition system. Understanding this helps us design a better Go implementation.

#### Schema Definition (Python)

Each record type is defined as a list of `Field` objects:

```python
# From tdpservice/parsers/schema_defs/tanf/t1.py
t1 = [
    TanfDataReportSchema(
        record_type="T1",
        model=TANF_T1,
        preparsing_validators=[...],
        postparsing_validators=[...],
        fields=[
            Field(
                item="0",
                name="RecordType",
                friendly_name="Record Type",
                type=FieldType.ALPHA_NUMERIC,
                startIndex=0,
                endIndex=2,
                required=True,
                validators=[],
            ),
            Field(
                item="4",
                name="RPT_MONTH_YEAR",
                friendly_name="Reporting Year and Month",
                type=FieldType.NUMERIC,
                startIndex=2,
                endIndex=8,
                required=True,
                validators=[
                    category2.dateYearIsLargerThan(1998),
                    category2.dateMonthIsValid(),
                ],
            ),
            # ... 40+ more fields
        ],
    )
]
```

#### Multi-Format Handling (Python)

Python uses different `Decoder` classes and `Row` types for different formats:

```python
# For positional files (TANF/SSP/Tribal)
class RawRow:
    data: str  # The raw line as a string

    def value_at(self, position):
        return self.data[position.start:position.end]

# For columnar files (FRA CSV/XLSX)
class TupleRow(RawRow):
    data: tuple  # The row as a tuple of column values

    def value_at(self, position):
        # position.start is actually a column index here
        return self.data[position.start:position.end]
```

### Problems with the Python Approach

1. **Tight Coupling**: Validators are embedded in field definitions, mixing parsing and validation
2. **Mutable State**: Schema objects hold mutable state, making them non-thread-safe
3. **Ambiguous Positions**: The `Position` class means different things for different formats (byte positions vs column indices)
4. **No File-Level Configuration**: The relationship between (program, section) and valid schemas is implicit in code

### What We'll Improve in Go

1. **Explicit Format Declaration**: Schemas declare whether they're for positional or columnar data
2. **File Specifications**: Explicit configuration of which schemas belong to which (program, section)
3. **Immutable Schemas**: Schemas are loaded once and shared safely across goroutines
4. **Separate Validation**: Parsing is a pure function; validation is a separate pass
5. **Clear Field Access**: Positional fields use `start`/`end`, columnar fields use `column`

---

## Go Architecture Overview

### Design Principles

1. **Configuration as Data**: File specs and schemas are defined in YAML, not code
2. **Explicit Over Implicit**: No magic - the configuration clearly states what's happening
3. **Format-Aware Design**: Different formats (positional, columnar) are handled explicitly
4. **Parallel-Safe**: All shared data structures are immutable after initialization
5. **Separation of Concerns**: Each component has a single responsibility

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURATION                                  │
│                                                                             │
│   ┌─────────────────────┐         ┌─────────────────────────────────────┐   │
│   │     FileSpecs       │         │            Schemas                  │   │
│   │                     │         │                                     │   │
│   │  tanf_section1.yaml │────────▶│  tanf/t1.yaml, t2.yaml, t3.yaml     │   │
│   │  tanf_section2.yaml │         │  ssp/m1.yaml, m2.yaml, ...          │   │
│   │  fra_section1.yaml  │         │  fra/te1.yaml                       │   │
│   │  ...                │         │  common/header.yaml, trailer.yaml   │   │
│   └─────────────────────┘         └─────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               REGISTRY                                      │
│                                                                             │
│   Loads and indexes all FileSpecs and Schemas at startup                    │
│   Provides lookup by (program, section) and by record type                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FILE PROCESSING                                  │
│                                                                             │
│  ┌──────────────┐                                                           │
│  │  Input File  │                                                           │
│  └──────┬───────┘                                                           │
│         │                                                                   │
│         ▼                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         DECODER LAYER                                │   │
│  │                                                                      │   │
│  │   Positional Files          │           Columnar Files               │   │
│  │   (TANF/SSP/Tribal)         │           (FRA)                        │   │
│  │                             │                                        │   │
│  │   ┌─────────────────┐       │       ┌─────────────┐ ┌─────────────┐  │   │
│  │   │  UTF-8 Decoder  │       │       │ CSV Decoder │ │XLSX Decoder │  │   │
│  │   └────────┬────────┘       │       └──────┬──────┘ └──────┬──────┘  │   │
│  │            │                │              │               │         │   │
│  │            ▼                │              └───────┬───────┘         │   │
│  │     PositionalRow           │                      ▼                 │   │
│  │     (string data)           │               ColumnarRow              │   │
│  │                             │               ([]any data)             │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│         │                                            │                      │
│         ▼                                            ▼                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                    RECORD TYPE DETECTION                             │   │
│  │                                                                      │   │
│  │   Uses FileSpec configuration to determine which schema applies      │   │
│  │   to each row based on prefix (positional) or column (columnar)      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         ACCUMULATOR                                  │   │
│  │                                                                      │   │
│  │   Unified collection of records into processable units (Batches)     │   │
│  │                                                                      │   │
│  │   Strategy determined by config:                                     │   │
│  │   - key_fields: groups records by composite key (RPT_MONTH_YEAR,     │   │
│  │                 CASE_NUMBER) into RecordGroups                       │   │
│  │   - batch_size: batches N groups together into a Batch               │   │
│  │   - Both: groups by key, then batches N groups together              │   │
│  │   - Neither: per-record (each record is its own group in a batch)    │   │
│  │                                                                      │   │
│  │   Outputs: Batch { Groups: []RecordGroup }                           │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         WORKER POOL                                  │   │
│  │                                                                      │   │
│  │   N goroutines that process Batches in parallel                      │   │
│  │   Each worker parses all records in all groups within the batch      │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        TYPE CONVERTER                                │   │
│  │                                                                      │   │
│  │   Converts ParsedRecord (internal types) to SQLC types (DB types)    │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                 │                                           │
│                                 ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                       DATABASE WRITER                                │   │
│  │                                                                      │   │
│  │   Bulk inserts parsed records into PostgreSQL                        │   │
│  │                                                                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## File Specification System

### What Is a File Specification?

A **FileSpec** defines everything about a particular type of data file:

1. Which program and section it belongs to
2. What file format it uses (positional or columnar)
3. Which record types (schemas) can appear in the file
4. How to detect which record type each row is
5. Whether records should be grouped by case or batched independently

### Why Do We Need FileSpecs?

Without FileSpecs, the parser would need to hardcode knowledge about:
- "TANF Section 1 files contain T1, T2, T3, HEADER, and TRAILER records"
- "FRA files are CSV or XLSX and only contain TE1 records"
- "T1, T2, T3 records with the same case number should be grouped together"

By putting this in configuration files, we can:
- Add new programs or sections without changing code
- Clearly document what each file type contains
- Test file specifications independently from parsing logic

### FileSpec YAML Structure

Here's a complete, annotated example:

```yaml
# config/filespecs/tanf_section1.yaml
#
# File Specification for TANF Section 1 (Active Case Data)
#
# This file defines:
# - What format TANF Section 1 files use
# - What record types can appear in these files
# - How to identify each record type
# - How records should be grouped for processing

# ============================================================================
# BASIC IDENTIFICATION
# ============================================================================

# The program this file spec belongs to.
# Valid values: TANF, SSP, TRIBAL, FRA
program: TANF

# The section number within the program.
# Sections 1-4 exist for TANF, SSP, and TRIBAL.
# FRA only has section 1.
section: 1

# Human-readable description of what this file contains.
# Used for logging and documentation.
description: "TANF Active Case Data - Contains case, adult, and child records for active TANF cases"

# ============================================================================
# FILE FORMAT
# ============================================================================

# The format of data files matching this specification.
#
# Valid values:
#   - positional: Fixed-width text files where fields are at specific byte positions
#   - columnar: CSV or XLSX files where fields are in specific columns
#
# TANF, SSP, and TRIBAL files are always positional.
# FRA files are always columnar.
format: positional

# ============================================================================
# VALID SCHEMAS
# ============================================================================

# List of schema names that can appear in files matching this specification.
# These names correspond to schema files in the schemas/ directory.
#
# The parser will reject any record type not in this list.
schemas:
  - header      # File header (first line)
  - t1          # Case-level data (one per case)
  - t2          # Adult data (one or more per case)
  - t3          # Child data (one or more per case)
  - trailer     # File trailer (last line)

# ============================================================================
# RECORD TYPE DETECTION
# ============================================================================

# Configuration for how to determine which schema applies to each row.
#
# For positional files, we look at the beginning of each line (prefix).
# For columnar files, we look at a specific column value.
record_type_detection:

  # The detection method to use.
  #
  # Valid values:
  #   - prefix: Look at the first N characters of the line (for positional files)
  #   - column: Look at a specific column value (for columnar files)
  #   - fixed: All rows use the same schema (for single-record-type files)
  method: prefix

  # For prefix method: mapping of prefixes to schema names.
  # Prefixes are checked in order, so put longer prefixes first.
  # This ensures "HEADER" is matched before "H" would be (if we had an "H" record type).
  prefixes:
    - prefix: "HEADER"
      schema: header
    - prefix: "TRAILER"
      schema: trailer
    - prefix: "T1"
      schema: t1
    - prefix: "T2"
      schema: t2
    - prefix: "T3"
      schema: t3

# ============================================================================
# ACCUMULATOR CONFIGURATION
# ============================================================================

# Configuration for how records are collected and grouped for processing.
#
# The accumulator has two independent, inclusive settings:
#   - key_fields: Groups records by composite key (creates RecordGroups)
#   - batch_size: Batches N groups together (creates Batches)
#
# The four modes are:
#   | key_fields | batch_size | Behavior                                      |
#   |------------|------------|-----------------------------------------------|
#   | []         | 0          | Per-record: each record emitted individually  |
#   | []         | 100        | Batches of 100 individual records             |
#   | [X, Y]     | 0          | Group by key, emit each group individually    |
#   | [X, Y]     | 10         | Group by key, then batch 10 groups together   |
#
# For TANF/SSP/TRIBAL Section 1 and 2 files, records with the same
# RPT_MONTH_YEAR and CASE_NUMBER belong to the same "case" and must be
# processed together. We use key_fields for this.
#
# For FRA files, records are independent. We can batch them for efficiency.
accumulator:

  # Fields to use for grouping records together.
  # If empty, each record is its own group.
  # If specified, records with the same composite key are grouped.
  key_fields:
    # Position of RPT_MONTH_YEAR field (6 digits: YYYYMM)
    rpt_month_year:
      start: 2    # Byte position where the field starts (0-indexed)
      end: 8      # Byte position where the field ends (exclusive)

    # Position of CASE_NUMBER field (11 characters)
    case_number:
      start: 8    # Byte position where the field starts (0-indexed)
      end: 19     # Byte position where the field ends (exclusive)

  # Number of groups to batch together before dispatching to workers.
  # If 0, each group is dispatched individually (one batch per group).
  # If > 0, groups are collected until batch_size is reached, then dispatched.
  # Use this to tune worker efficiency vs. memory usage.
  batch_size: 0

  # Which schemas participate in grouping.
  # HEADER and TRAILER are excluded because they're not case data.
  # T1, T2, T3 records with the same case number form a case group.
  grouped_schemas:
    - t1
    - t2
    - t3
```

### FileSpec for Non-Grouped Data (Section 3/4)

```yaml
# config/filespecs/tanf_section3.yaml
#
# File Specification for TANF Section 3 (Aggregate Data)
#
# Section 3 contains aggregate (summary) data, not individual case data.
# Records are independent and don't need case-based grouping.

program: TANF
section: 3
description: "TANF Aggregate Data - Summary statistics"
format: positional

schemas:
  - header
  - t6          # Aggregate data record
  - trailer

record_type_detection:
  method: prefix
  prefixes:
    - prefix: "HEADER"
      schema: header
    - prefix: "TRAILER"
      schema: trailer
    - prefix: "T6"
      schema: t6

# Accumulator config: batch records for parallel processing.
# No key_fields means each record is its own group.
# batch_size of 100 means dispatch batches of 100 records.
accumulator:
  key_fields: {}        # Empty: no case-based grouping
  batch_size: 100       # Batch 100 records together for workers
  grouped_schemas: []   # No schemas use key-based grouping
```

### FileSpec for Columnar Format (FRA)

```yaml
# config/filespecs/fra_section1.yaml
#
# File Specification for FRA Section 1 (TANF Exiter Data)
#
# FRA files are ALWAYS in columnar format (CSV or XLSX).
# They contain a single record type (TE1) with one record per exiter.

program: FRA
section: 1
description: "Follow-up Research on Assistance - TANF Exiter records"

# FRA files are columnar (CSV or XLSX), not positional
format: columnar

schemas:
  - te1         # Only one record type in FRA files

record_type_detection:
  # All rows are the same record type, so use "fixed" method
  method: fixed
  schema: te1

  # Alternative: if the file had a record type column, we could use:
  # method: column
  # column: 0          # Column index containing record type
  # column_header: "Record Type"  # Or identify by header name

# Accumulator config: batch independent records for parallel processing.
# No key_fields since FRA records don't relate to each other.
accumulator:
  key_fields: {}        # Empty: each record is independent
  batch_size: 100       # Batch 100 records together for workers
  grouped_schemas: []   # No schemas use key-based grouping
```

### Go Types for FileSpec

```go
// internal/filespec/types.go
package filespec

// Format represents the file format type.
// This determines how fields are extracted from row data.
type Format string

const (
    // FormatPositional is for fixed-width text files where fields are at specific byte positions.
    // Used by TANF, SSP, and Tribal TANF programs.
    FormatPositional Format = "positional"

    // FormatColumnar is for CSV or XLSX files where fields are in specific columns.
    // Used by FRA program.
    FormatColumnar Format = "columnar"
)

// FileSpec defines the structure and processing rules for a specific (program, section) file type.
type FileSpec struct {
    // Program is the assistance program: TANF, SSP, TRIBAL, or FRA
    Program string `yaml:"program"`

    // Section is the section number (1-4 for most programs, 1 for FRA)
    Section int `yaml:"section"`

    // Description is a human-readable description of the file type
    Description string `yaml:"description"`

    // Format specifies whether this is a positional or columnar file
    Format Format `yaml:"format"`

    // Schemas lists the schema names that can appear in this file type.
    // These correspond to schema files in the schemas/ directory.
    Schemas []string `yaml:"schemas"`

    // RecordTypeDetection configures how to determine the schema for each row
    RecordTypeDetection RecordTypeDetection `yaml:"record_type_detection"`

    // Accumulator configures how records are collected and grouped for processing
    Accumulator AccumulatorConfig `yaml:"accumulator"`
}

// RecordTypeDetection configures how to determine which schema applies to a row.
type RecordTypeDetection struct {
    // Method is the detection method: "prefix", "column", or "fixed"
    Method string `yaml:"method"`

    // Prefixes maps line prefixes to schema names (for positional files)
    // Only used when Method is "prefix"
    Prefixes []PrefixMapping `yaml:"prefixes,omitempty"`

    // Column is the column index containing the record type (for columnar files)
    // Only used when Method is "column"
    Column int `yaml:"column,omitempty"`

    // ColumnHeader is the column header name containing the record type
    // Alternative to Column - used when columns might be reordered
    ColumnHeader string `yaml:"column_header,omitempty"`

    // Schema is the fixed schema name when all rows are the same type
    // Only used when Method is "fixed"
    Schema string `yaml:"schema,omitempty"`
}

// PrefixMapping maps a line prefix to a schema name.
type PrefixMapping struct {
    // Prefix is the string that appears at the start of the line
    Prefix string `yaml:"prefix"`

    // Schema is the name of the schema to use for lines with this prefix
    Schema string `yaml:"schema"`
}

// AccumulatorConfig configures how records are collected and grouped for processing.
//
// The accumulator uses two independent, inclusive settings:
//   - KeyFields: Groups records by composite key (creates RecordGroups)
//   - BatchSize: Batches N groups together (creates Batches)
//
// The four modes are:
//   | KeyFields | BatchSize | Behavior                                      |
//   |-----------|-----------|-----------------------------------------------|
//   | nil       | 0         | Per-record: each record emitted individually  |
//   | nil       | 100       | Batches of 100 individual records             |
//   | set       | 0         | Group by key, emit each group individually    |
//   | set       | 10        | Group by key, then batch 10 groups together   |
type AccumulatorConfig struct {
    // KeyFields defines how to extract grouping keys from raw data.
    // If nil or empty, each record is its own group (no case-based grouping).
    // If set, records with the same composite key are grouped together.
    KeyFields *KeyFieldsConfig `yaml:"key_fields,omitempty"`

    // BatchSize is the number of groups to batch together before dispatch.
    // If 0, each group is dispatched individually (one batch per group).
    // If > 0, groups are collected until batch_size is reached.
    BatchSize int `yaml:"batch_size,omitempty"`

    // GroupedSchemas lists which schemas participate in key-based grouping.
    // Schemas not in this list (e.g., HEADER, TRAILER) are processed individually.
    GroupedSchemas []string `yaml:"grouped_schemas,omitempty"`
}

// HasKeyFields returns true if key-based grouping is configured.
func (c *AccumulatorConfig) HasKeyFields() bool {
    return c.KeyFields != nil && (c.KeyFields.RptMonthYear.End > 0 || c.KeyFields.CaseNumber.End > 0)
}

// KeyFieldsConfig defines byte positions for extracting the grouping key.
type KeyFieldsConfig struct {
    // RptMonthYear is the position of the reporting month/year field
    RptMonthYear PositionDef `yaml:"rpt_month_year"`

    // CaseNumber is the position of the case number field
    CaseNumber PositionDef `yaml:"case_number"`
}

// PositionDef defines a byte range within a line.
type PositionDef struct {
    // Start is the starting byte position (0-indexed, inclusive)
    Start int `yaml:"start"`

    // End is the ending byte position (0-indexed, exclusive)
    End int `yaml:"end"`
}
```

---

## Schema Definition System

### What Is a Schema?

A **Schema** defines the structure of a single record type:

1. What fields the record contains
2. Where each field is located (byte positions for positional, column index for columnar)
3. The data type of each field (string or integer)
4. Whether each field is required or optional

### Schema vs FileSpec: Understanding the Difference

| Aspect | FileSpec | Schema |
|--------|----------|--------|
| **Scope** | One per (program, section) | One per record type |
| **Defines** | Which schemas are valid, how to detect them, grouping rules | Field definitions for a single record type |
| **Example** | "TANF Section 1 files contain T1, T2, T3 records" | "A T1 record has these 45 fields at these positions" |

### Schema for Positional Format

For positional (fixed-width) files, fields are defined by byte positions:

```yaml
# config/schemas/tanf/t1.yaml
#
# Schema Definition for TANF T1 Record
#
# T1 records contain case-level data for active TANF cases.
# This includes family composition, benefits received, and sanctions.
#
# IMPORTANT: This schema is for POSITIONAL format files.
# Fields are extracted using byte positions (start/end).

# ============================================================================
# RECORD IDENTIFICATION
# ============================================================================

# The record type identifier that appears at the start of each line.
# For T1 records, lines start with "T1".
record_type: "T1"

# The program this schema belongs to.
# Used for organizing schemas and validation.
program: TANF

# Human-readable description of what this record contains.
description: "TANF Active Case Data - Family-level information for active cases"

# ============================================================================
# FIELD DEFINITIONS
# ============================================================================

# Each field definition includes:
#   - name: Internal field name (used in code and database)
#   - item: Item number from the federal specification document
#   - friendly_name: Human-readable name for error messages
#   - start: Starting byte position (0-indexed, inclusive)
#   - end: Ending byte position (0-indexed, exclusive)
#   - type: Data type - "string" or "int"
#   - required: Whether the field must have a non-empty value
#   - transform: Optional transformation to apply (e.g., "zero_pad_3")

fields:
  # --------------------------------------------------------------------------
  # Record Identification Fields
  # --------------------------------------------------------------------------

  - name: RecordType
    item: "0"
    friendly_name: "Record Type"
    start: 0
    end: 2
    type: string
    required: true
    # Example value: "T1"
    # This field identifies the record type and should always be "T1"

  - name: RPT_MONTH_YEAR
    item: "4"
    friendly_name: "Reporting Year and Month"
    start: 2
    end: 8
    type: int
    required: true
    # Example value: 202010 (October 2020)
    # Format: YYYYMM
    # This field indicates which month the data is for

  - name: CASE_NUMBER
    item: "6"
    friendly_name: "Case Number"
    start: 8
    end: 19
    type: string
    required: true
    # Example value: "11111111112"
    # This is the unique identifier for the case
    # Combined with RPT_MONTH_YEAR, it forms the grouping key

  # --------------------------------------------------------------------------
  # Location Fields
  # --------------------------------------------------------------------------

  - name: COUNTY_FIPS_CODE
    item: "2"
    friendly_name: "County FIPS Code"
    start: 19
    end: 22
    type: string
    required: true
    transform: zero_pad_3
    # Example value: "003"
    # The transform ensures the value is always 3 digits with leading zeros

  - name: STRATUM
    item: "5"
    friendly_name: "Stratum"
    start: 22
    end: 24
    type: string
    required: false
    # Example value: "01"
    # Optional field - used for sampling

  - name: ZIP_CODE
    item: "7"
    friendly_name: "ZIP Code"
    start: 24
    end: 29
    type: string
    required: true
    # Example value: "12345"

  # --------------------------------------------------------------------------
  # Case Information Fields
  # --------------------------------------------------------------------------

  - name: FUNDING_STREAM
    item: "8"
    friendly_name: "Funding Stream"
    start: 29
    end: 30
    type: int
    required: true
    # Values: 1 = Federal TANF, 2 = State MOE

  - name: DISPOSITION
    item: "9"
    friendly_name: "Disposition"
    start: 30
    end: 31
    type: int
    required: true
    # Value should be 1 for active cases

  - name: NEW_APPLICANT
    item: "10"
    friendly_name: "Newly-Approved Applicant"
    start: 31
    end: 32
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  - name: NBR_FAMILY_MEMBERS
    item: "11"
    friendly_name: "Number of Family Members"
    start: 32
    end: 34
    type: int
    required: true
    # Total number of people in the assistance unit

  - name: FAMILY_TYPE
    item: "12"
    friendly_name: "Type of Family for Work Participation"
    start: 34
    end: 35
    type: int
    required: true
    # Values: 1 = Two-parent, 2 = One-parent, 3 = No parent

  # --------------------------------------------------------------------------
  # Benefits Received Fields
  # --------------------------------------------------------------------------

  - name: RECEIVES_SUB_HOUSING
    item: "13"
    friendly_name: "Receives Subsidized Housing"
    start: 35
    end: 36
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  - name: RECEIVES_MED_ASSISTANCE
    item: "14"
    friendly_name: "Receives Medical Assistance"
    start: 36
    end: 37
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  - name: RECEIVES_FOOD_STAMPS
    item: "15"
    friendly_name: "Receives SNAP Assistance"
    start: 37
    end: 38
    type: int
    required: false
    # Values: 0 = Unknown, 1 = Yes, 2 = No

  - name: AMT_FOOD_STAMP_ASSISTANCE
    item: "16"
    friendly_name: "SNAP Benefits Amount"
    start: 38
    end: 42
    type: int
    required: true
    # Dollar amount of SNAP benefits

  - name: RECEIVES_SUB_CC
    item: "17"
    friendly_name: "Receives Subsidized Child Care"
    start: 42
    end: 43
    type: int
    required: false
    # Values: 0 = Unknown, 1 = Yes from TANF, 2 = Yes from other, 3 = No

  - name: AMT_SUB_CC
    item: "18"
    friendly_name: "Subsidized Child Care Amount"
    start: 43
    end: 47
    type: int
    required: true
    # Dollar amount of child care subsidy

  - name: CHILD_SUPPORT_AMT
    item: "19"
    friendly_name: "Amount of Child Support"
    start: 47
    end: 51
    type: int
    required: true
    # Dollar amount of child support received

  - name: FAMILY_CASH_RESOURCES
    item: "20"
    friendly_name: "Family Cash Resources"
    start: 51
    end: 55
    type: int
    required: true
    # Dollar amount of family's cash resources

  # --------------------------------------------------------------------------
  # TANF Assistance Fields
  # --------------------------------------------------------------------------

  - name: CASH_AMOUNT
    item: "21A"
    friendly_name: "Cash Assistance Amount"
    start: 55
    end: 59
    type: int
    required: true
    # Dollar amount of cash assistance

  - name: NBR_MONTHS
    item: "21B"
    friendly_name: "Cash Assistance: Number of Months"
    start: 59
    end: 62
    type: int
    required: true
    # Number of months cash assistance received

  - name: CC_AMOUNT
    item: "22A"
    friendly_name: "TANF Child Care Amount"
    start: 62
    end: 66
    type: int
    required: true
    # Dollar amount of TANF-funded child care

  - name: CHILDREN_COVERED
    item: "22B"
    friendly_name: "TANF Child Care: Children Covered"
    start: 66
    end: 68
    type: int
    required: true
    # Number of children receiving TANF child care

  - name: CC_NBR_MONTHS
    item: "22C"
    friendly_name: "TANF Child Care: Number of Months"
    start: 68
    end: 71
    type: int
    required: true
    # Number of months TANF child care received

  - name: TRANSP_AMOUNT
    item: "23A"
    friendly_name: "Transportation Amount"
    start: 71
    end: 75
    type: int
    required: true
    # Dollar amount of transportation assistance

  - name: TRANSP_NBR_MONTHS
    item: "23B"
    friendly_name: "Transportation: Number of Months"
    start: 75
    end: 78
    type: int
    required: true
    # Number of months transportation assistance received

  - name: TRANSITION_SERVICES_AMOUNT
    item: "24A"
    friendly_name: "Transitional Services Amount"
    start: 78
    end: 82
    type: int
    required: false
    # Dollar amount of transitional services

  - name: TRANSITION_NBR_MONTHS
    item: "24B"
    friendly_name: "Transitional Services: Number of Months"
    start: 82
    end: 85
    type: int
    required: false
    # Number of months transitional services received

  - name: OTHER_AMOUNT
    item: "25A"
    friendly_name: "Other Assistance Amount"
    start: 85
    end: 89
    type: int
    required: false
    # Dollar amount of other assistance

  - name: OTHER_NBR_MONTHS
    item: "25B"
    friendly_name: "Other Assistance: Number of Months"
    start: 89
    end: 92
    type: int
    required: false
    # Number of months other assistance received

  # --------------------------------------------------------------------------
  # Sanction Fields
  # --------------------------------------------------------------------------

  - name: SANC_REDUCTION_AMT
    item: "26AI"
    friendly_name: "Sanction Reduction Amount"
    start: 92
    end: 96
    type: int
    required: true
    # Total dollar amount of benefit reductions due to sanctions

  - name: WORK_REQ_SANCTION
    item: "26AII"
    friendly_name: "Work Requirements Sanction"
    start: 96
    end: 97
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  - name: FAMILY_SANC_ADULT
    item: "26AIII"
    friendly_name: "Family Sanction for Adult"
    start: 97
    end: 98
    type: int
    required: false
    # Values: 0 = N/A, 1 = Yes, 2 = No

  - name: SANC_TEEN_PARENT
    item: "26AIV"
    friendly_name: "Teen Parent School Sanction"
    start: 98
    end: 99
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  - name: NON_COOPERATION_CSE
    item: "26AV"
    friendly_name: "Child Support Non-Cooperation Sanction"
    start: 99
    end: 100
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  - name: FAILURE_TO_COMPLY
    item: "26AVI"
    friendly_name: "Failure to Comply Sanction"
    start: 100
    end: 101
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  - name: OTHER_SANCTION
    item: "26AVII"
    friendly_name: "Other Sanction"
    start: 101
    end: 102
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  # --------------------------------------------------------------------------
  # Other Reduction Fields
  # --------------------------------------------------------------------------

  - name: RECOUPMENT_PRIOR_OVRPMT
    item: "26B"
    friendly_name: "Recoupment of Prior Overpayment"
    start: 102
    end: 106
    type: int
    required: true
    # Dollar amount recouped from prior overpayment

  - name: OTHER_TOTAL_REDUCTIONS
    item: "26CI"
    friendly_name: "Other Total Reductions"
    start: 106
    end: 110
    type: int
    required: true
    # Total dollar amount of other reductions

  - name: FAMILY_CAP
    item: "26CII"
    friendly_name: "Family Cap Reduction"
    start: 110
    end: 111
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  - name: REDUCTIONS_ON_RECEIPTS
    item: "26CIII"
    friendly_name: "Time Limit Reductions"
    start: 111
    end: 112
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  - name: OTHER_NON_SANCTION
    item: "26CIV"
    friendly_name: "Other Non-Sanction Reduction"
    start: 112
    end: 113
    type: int
    required: true
    # Values: 1 = Yes, 2 = No

  # --------------------------------------------------------------------------
  # Additional Fields
  # --------------------------------------------------------------------------

  - name: WAIVER_EVAL_CONTROL_GRPS
    item: "27"
    friendly_name: "Waiver Evaluation Group"
    start: 113
    end: 114
    type: string
    required: false
    # Values: "0", "9", or blank

  - name: FAMILY_EXEMPT_TIME_LIMITS
    item: "28"
    friendly_name: "Federal Time Limit Exemption"
    start: 114
    end: 116
    type: int
    required: true
    # Exemption code for federal time limits

  - name: FAMILY_NEW_CHILD
    item: "29"
    friendly_name: "New Child-Only Family"
    start: 116
    end: 117
    type: int
    required: false
    # Values: 0 = N/A, 1 = Yes, 2 = No

  - name: BLANK
    item: "-1"
    friendly_name: "Blank"
    start: 117
    end: 156
    type: string
    required: false
    # Filler space at end of record
```

### Schema for Columnar Format (FRA)

For columnar (CSV/XLSX) files, fields are defined by column index:

```yaml
# config/schemas/fra/te1.yaml
#
# Schema Definition for FRA TE1 Record
#
# TE1 records contain data about individuals who exited TANF.
# Each record represents one exiter.
#
# IMPORTANT: This schema is for COLUMNAR format files (CSV or XLSX).
# Fields are extracted using column indices, not byte positions.

# ============================================================================
# RECORD IDENTIFICATION
# ============================================================================

record_type: "TE1"
program: FRA
description: "TANF Exiter Record - Individual-level data for TANF exiters"

# ============================================================================
# FIELD DEFINITIONS
# ============================================================================

# For columnar files, each field has a 'column' property instead of 'start'/'end'.
# The column index is 0-based (first column is 0, second is 1, etc.)
#
# Note: For XLSX files, the values may already be typed (numbers, dates).
# For CSV files, all values are strings and need type conversion.

fields:
 - name: RPT_MONTH_YEAR
    item: "1"
    friendly_name: "Reporting Year and Month"
    column: 0
    type: int
    required: true
    # Format: YYYYMM
 - name: SSN
    item: "2"
    friendly_name: "Reporting Year and Month"
    column: 2
    type: int
    required: true
    # Format: YYYYMM
```

### Go Types for Schema

```go
// internal/schema/types.go
package schema

// FieldDef represents a single field within a record.
type FieldDef struct {
    // Name is the internal field name (used in code and database)
    Name string `yaml:"name"`

    // Item is the item number from the federal specification
    Item string `yaml:"item"`

    // FriendlyName is a human-readable name for error messages
    FriendlyName string `yaml:"friendly_name"`

    // Type is the data type: "string" or "int"
    Type string `yaml:"type"`

    // Required indicates whether the field must have a non-empty value
    Required bool `yaml:"required"`

    // Transform is an optional transformation to apply (e.g., "zero_pad_3")
    Transform string `yaml:"transform,omitempty"`

    // === Positional Format Fields ===
    // Used when the schema is for a positional (fixed-width) file

    // Start is the starting byte position (0-indexed, inclusive)
    Start int `yaml:"start,omitempty"`

    // End is the ending byte position (0-indexed, exclusive)
    End int `yaml:"end,omitempty"`

    // === Columnar Format Fields ===
    // Used when the schema is for a columnar (CSV/XLSX) file

    // Column is the column index (0-indexed)
    Column int `yaml:"column,omitempty"`

    // ColumnHeader is the expected column header name (optional)
    ColumnHeader string `yaml:"column_header,omitempty"`
}

// SchemaDef defines the structure of a single record type.
type SchemaDef struct {
    // RecordType is the identifier (e.g., "T1", "TE1")
    RecordType string `yaml:"record_type"`

    // Program is the program this schema belongs to
    Program string `yaml:"program"`

    // Description is a human-readable description
    Description string `yaml:"description"`

    // Fields defines all fields in the record
    Fields []FieldDef `yaml:"fields"`
}

// CompiledSchema wraps a SchemaDef with precomputed lookup structures.
type CompiledSchema struct {
    *SchemaDef

    // FieldsByName provides O(1) lookup by field name
    FieldsByName map[string]*FieldDef

    // FieldsByItem provides O(1) lookup by item number
    FieldsByItem map[string]*FieldDef
}

// Compile creates a CompiledSchema with lookup maps.
func (s *SchemaDef) Compile() *CompiledSchema {
    cs := &CompiledSchema{
        SchemaDef: s,
        FieldsByName: make(map[string]*FieldDef, len(s.Fields)),
        FieldsByItem: make(map[string]*FieldDef, len(s.Fields)),
    }

    for i := range s.Fields {
        field := &s.Fields[i]
        cs.FieldsByName[field.Name] = field
        cs.FieldsByItem[field.Item] = field
    }

    return cs
}

// GetField returns a field by name, or nil if not found.
func (cs *CompiledSchema) GetField(name string) *FieldDef {
    return cs.FieldsByName[name]
}
```

---

## Registry

### What Is the Registry?

The **Registry** is the central configuration store that loads and manages all FileSpecs and Schemas at startup. It provides lookup methods for the rest of the system to access configuration without needing to know about file paths or YAML parsing.

### Why Do We Need a Registry?

Without a Registry, every component would need to:
- Know where configuration files are located
- Parse YAML files on demand
- Handle caching to avoid repeated parsing
- Deal with missing or invalid configuration

The Registry centralizes all of this:
- Loads all configuration once at startup
- Validates configuration and fails fast if invalid
- Provides simple lookup methods by program/section or schema path
- Compiles schemas into efficient runtime structures

### Registry Implementation

```go
// internal/registry/registry.go
package registry

import (
    "fmt"
    "os"
    "path/filepath"
    "strings"

    "gopkg.in/yaml.v3"

    "go-parser/internal/filespec"
    "go-parser/internal/schema"
)

// Registry holds all loaded FileSpecs and Schemas.
// It is created once at startup and provides read-only access
// to configuration throughout the application lifetime.
type Registry struct {
    // fileSpecs indexed by "PROGRAM:SECTION" (e.g., "TANF:1")
    fileSpecs map[string]*filespec.FileSpec

    // schemas indexed by path (e.g., "tanf/t1", "common/header")
    schemas map[string]*schema.CompiledSchema

    // metadata holds database info derived from schemas (table names, columns)
    // Built during Load() from YAML schema field definitions
    // See SchemaMetadata type in schema_metadata.go (same package)
    metadata map[string]*SchemaMetadata

    // configDir is the root configuration directory
    configDir string
}

// Load reads all configuration files from the given directory and builds the Registry.
// Directory structure expected:
//
//	configDir/
//	├── filespecs/
//	│   ├── tanf_section1.yaml
//	│   ├── tanf_section2.yaml
//	│   └── ...
//	└── schemas/
//	    ├── common/
//	    │   ├── header.yaml
//	    │   └── trailer.yaml
//	    └── tanf/
//	        ├── t1.yaml
//	        ├── t2.yaml
//	        └── t3.yaml
func Load(configDir string) (*Registry, error) {
    r := &Registry{
        fileSpecs: make(map[string]*filespec.FileSpec),
        schemas:   make(map[string]*schema.CompiledSchema),
        metadata:  make(map[string]*SchemaMetadata),
        configDir: configDir,
    }

    // Load schemas first (FileSpecs reference them)
    if err := r.loadSchemas(); err != nil {
        return nil, fmt.Errorf("loading schemas: %w", err)
    }

    // Load FileSpecs
    if err := r.loadFileSpecs(); err != nil {
        return nil, fmt.Errorf("loading filespecs: %w", err)
    }

    // Validate that all FileSpec schema references are valid
    if err := r.validateReferences(); err != nil {
        return nil, fmt.Errorf("validating references: %w", err)
    }

    // Build database metadata from schema field definitions
    r.buildAllMetadata()

    return r, nil
}

// loadSchemas walks the schemas directory and loads all .yaml files.
func (r *Registry) loadSchemas() error {
    schemasDir := filepath.Join(r.configDir, "schemas")

    return filepath.Walk(schemasDir, func(path string, info os.FileInfo, err error) error {
        if err != nil {
            return err
        }

        // Skip directories and non-YAML files
        if info.IsDir() || !strings.HasSuffix(path, ".yaml") {
            return nil
        }

        // Read and parse the schema file
        data, err := os.ReadFile(path)
        if err != nil {
            return fmt.Errorf("reading %s: %w", path, err)
        }

        var schemaDef schema.SchemaDef
        if err := yaml.Unmarshal(data, &schemaDef); err != nil {
            return fmt.Errorf("parsing %s: %w", path, err)
        }

        // Compile the schema
        compiled, err := schema.Compile(&schemaDef)
        if err != nil {
            return fmt.Errorf("compiling %s: %w", path, err)
        }

        // Compute the schema key (relative path without .yaml extension)
        // e.g., "config/schemas/tanf/t1.yaml" -> "tanf/t1"
        relPath, err := filepath.Rel(schemasDir, path)
        if err != nil {
            return fmt.Errorf("computing relative path for %s: %w", path, err)
        }
        key := strings.TrimSuffix(relPath, ".yaml")

        r.schemas[key] = compiled
        return nil
    })
}

// loadFileSpecs reads all .yaml files from the filespecs directory.
func (r *Registry) loadFileSpecs() error {
    filespecsDir := filepath.Join(r.configDir, "filespecs")

    entries, err := os.ReadDir(filespecsDir)
    if err != nil {
        return fmt.Errorf("reading filespecs directory: %w", err)
    }

    for _, entry := range entries {
        if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".yaml") {
            continue
        }

        path := filepath.Join(filespecsDir, entry.Name())
        data, err := os.ReadFile(path)
        if err != nil {
            return fmt.Errorf("reading %s: %w", path, err)
        }

        var spec filespec.FileSpec
        if err := yaml.Unmarshal(data, &spec); err != nil {
            return fmt.Errorf("parsing %s: %w", path, err)
        }

        // Index by "PROGRAM:SECTION"
        key := fmt.Sprintf("%s:%d", spec.Program, spec.Section)
        r.fileSpecs[key] = &spec
    }

    return nil
}

// validateReferences ensures all schema references in FileSpecs point to loaded schemas.
func (r *Registry) validateReferences() error {
    for specKey, spec := range r.fileSpecs {
        // Validate schemas list
        for _, schemaPath := range spec.Schemas {
            if _, ok := r.schemas[schemaPath]; !ok {
                return fmt.Errorf("filespec %s references unknown schema: %s", specKey, schemaPath)
            }
        }

        // Validate record_type_detection prefixes
        for _, prefix := range spec.RecordTypeDetection.Prefixes {
            if _, ok := r.schemas[prefix.Schema]; !ok {
                return fmt.Errorf("filespec %s prefix %q references unknown schema: %s",
                    specKey, prefix.Prefix, prefix.Schema)
            }
        }

        // Validate grouped_schemas
        for _, schemaPath := range spec.Accumulator.GroupedSchemas {
            if _, ok := r.schemas[schemaPath]; !ok {
                return fmt.Errorf("filespec %s grouped_schemas references unknown schema: %s",
                    specKey, schemaPath)
            }
        }
    }

    return nil
}

// GetFileSpec returns the FileSpec for the given program and section.
// Returns nil if not found.
func (r *Registry) GetFileSpec(program string, section int) *filespec.FileSpec {
    key := fmt.Sprintf("%s:%d", program, section)
    return r.fileSpecs[key]
}

// GetSchema returns a compiled schema by its path (e.g., "tanf/t1").
// Returns nil if not found.
func (r *Registry) GetSchema(path string) *schema.CompiledSchema {
    return r.schemas[path]
}

// MustGetSchema returns a compiled schema by path, panicking if not found.
// Use this only when you're certain the schema exists (e.g., after validation).
func (r *Registry) MustGetSchema(path string) *schema.CompiledSchema {
    s := r.schemas[path]
    if s == nil {
        panic(fmt.Sprintf("schema not found: %s", path))
    }
    return s
}

// ListFileSpecs returns all loaded FileSpec keys (e.g., ["TANF:1", "TANF:2", ...]).
func (r *Registry) ListFileSpecs() []string {
    keys := make([]string, 0, len(r.fileSpecs))
    for k := range r.fileSpecs {
        keys = append(keys, k)
    }
    return keys
}

// ListSchemas returns all loaded schema paths (e.g., ["tanf/t1", "common/header", ...]).
func (r *Registry) ListSchemas() []string {
    keys := make([]string, 0, len(r.schemas))
    for k := range r.schemas {
        keys = append(keys, k)
    }
    return keys
}

// Stats returns statistics about loaded configuration.
func (r *Registry) Stats() (numFileSpecs, numSchemas int) {
    return len(r.fileSpecs), len(r.schemas)
}
```

### Using the Registry

```go
// At application startup
func main() {
    // Load all configuration
    reg, err := registry.Load("config")
    if err != nil {
        log.Fatalf("Failed to load configuration: %v", err)
    }

    numSpecs, numSchemas := reg.Stats()
    log.Printf("Loaded %d file specs and %d schemas", numSpecs, numSchemas)

    // Get a FileSpec for processing
    spec := reg.GetFileSpec("TANF", 1)
    if spec == nil {
        log.Fatal("No FileSpec for TANF Section 1")
    }

    // Get a schema directly (e.g., for testing)
    t1Schema := reg.GetSchema("tanf/t1")
    if t1Schema == nil {
        log.Fatal("No schema for tanf/t1")
    }

    // The RecordTypeDetector uses the registry to look up schemas
    detector := parser.NewRecordTypeDetector(spec, reg)
}
```

### Registry and SQLC Type Mapping

While the Registry handles YAML configuration, the mapping between schema paths and SQLC-generated types is defined statically in Go code. This is intentional because:

1. **Database schema is fixed**: The PostgreSQL tables are defined by Django migrations
2. **Type safety**: Go's type system catches mismatches at compile time
3. **Performance**: No runtime reflection or dynamic lookup needed

The schema-to-SQLC mapping is defined in `internal/registry/schema_metadata.go` (see SQLC Integration section for details). This allows:

```go
// The Registry provides schema configuration and metadata
schema := reg.GetSchema("tanf/t1")
meta := reg.GetSchemaMetadata("tanf/t1")  // Columns derived from YAML fields

// The converter registry maps record types to SQLC converters
conv := converter.GetConverter("T1")  // Returns func that creates db.SearchIndexesTanfT1

// The writer manager is created dynamically from the FileSpec
spec := reg.GetFileSpec("TANF", 1)
writerMgr := writer.NewWriterManager(pool, datafileID, spec, reg)
```

### Registry in the Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              APPLICATION STARTUP                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │    registry.Load()     │
                         │                        │
                         │  Reads config/schemas/ │
                         │  Reads config/filespecs│
                         │  Validates references  │
                         └───────────┬────────────┘
                                     │
                                     ▼
                         ┌────────────────────────┐
                         │       Registry         │
                         │                        │
                         │  fileSpecs: map[...]   │
                         │  schemas: map[...]     │
                         └───────────┬────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
    ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
    │  GetFileSpec()  │   │   GetSchema()   │   │  Used by:       │
    │                 │   │                 │   │  - Detector     │
    │  "TANF", 1      │   │  "tanf/t1"      │   │  - Accumulator  │
    │       ↓         │   │       ↓         │   │  - Worker Pool  │
    │  *FileSpec      │   │ *CompiledSchema │   │                 │
    └─────────────────┘   └─────────────────┘   └─────────────────┘
```

---

## Multi-Format Support

### The Challenge

TDRS needs to handle two (more?) fundamentally different file formats:

1. **Positional (Fixed-Width)**: Fields are at specific byte positions
   - Used by: TANF, SSP, Tribal TANF
   - Example: Characters 2-8 contain RPT_MONTH_YEAR

2. **Columnar (CSV/XLSX)**: Fields are in specific columns
   - Used by: FRA
   - Example: Column 1 contains RPT_MONTH_YEAR

The parser must handle both formats cleanly without mixing concerns.

### Solution: Format-Aware Row Types

We define different row types for different formats, each with appropriate field access methods:

```go
// internal/decoder/row.go
package decoder

// Row is the interface that all row types implement.
// This allows the parser to work with any row format.
type Row interface {
    // LineNum returns the 1-indexed line number in the source file
    LineNum() int

    // RecordType returns the detected record type (e.g., "T1", "TE1")
    RecordType() string

    // RawData returns the underlying data for debugging/error messages
    RawData() any
}

// PositionalRow represents a row from a positional (fixed-width) file.
// The data is a string, and fields are accessed by byte positions.
type PositionalRow struct {
    lineNum    int
    recordType string
    data       string
}

// NewPositionalRow creates a new PositionalRow.
func NewPositionalRow(lineNum int, recordType, data string) *PositionalRow {
    return &PositionalRow{
        lineNum:    lineNum,
        recordType: recordType,
        data:       data,
    }
}

func (r *PositionalRow) LineNum() int       { return r.lineNum }
func (r *PositionalRow) RecordType() string { return r.recordType }
func (r *PositionalRow) RawData() any       { return r.data }

// Slice extracts a substring from the row data.
// start is inclusive, end is exclusive (Python slice convention).
// Returns empty string if positions are out of bounds.
func (r *PositionalRow) Slice(start, end int) string {
    if start < 0 || end > len(r.data) || start >= end {
        return ""
    }
    return r.data[start:end]
}

// Data returns the full row data as a string.
func (r *PositionalRow) Data() string {
    return r.data
}

// ColumnarRow represents a row from a columnar (CSV/XLSX) file.
// The data is a slice of values, and fields are accessed by column index.
type ColumnarRow struct {
    lineNum    int
    recordType string
    columns    []any // Can be string, int, float64, etc. (especially from XLSX)
}

// NewColumnarRow creates a new ColumnarRow.
func NewColumnarRow(lineNum int, recordType string, columns []any) *ColumnarRow {
    return &ColumnarRow{
        lineNum:    lineNum,
        recordType: recordType,
        columns:    columns,
    }
}

func (r *ColumnarRow) LineNum() int       { return r.lineNum }
func (r *ColumnarRow) RecordType() string { return r.recordType }
func (r *ColumnarRow) RawData() any       { return r.columns }

// Column returns the value at the specified column index.
// Returns nil if the index is out of bounds.
func (r *ColumnarRow) Column(index int) any {
    if index < 0 || index >= len(r.columns) {
        return nil
    }
    return r.columns[index]
}

// ColumnCount returns the number of columns in the row.
func (r *ColumnarRow) ColumnCount() int {
    return len(r.columns)
}
```

### Decoder Interface

Different decoders produce different row types:

```go
// internal/decoder/decoder.go
package decoder

import (
    "iter"

    "go-parser/internal/filespec"
)

// Decoder reads a data file and produces rows.
type Decoder interface {
    // Format returns the format this decoder produces.
    Format() filespec.Format

    // Rows returns an iterator over all rows in the file.
    // The first row is typically the header, and the last row is typically the trailer.
    Rows() iter.Seq2[Row, error]

    // Close releases any resources held by the decoder.
    Close() error
}
```

### UTF-8 Decoder (Positional Format)

```go
// internal/decoder/utf8.go
package decoder

import (
    "bufio"
    "io"
    "iter"
    "strings"

    "go-parser/internal/filespec"
)

// UTF8Decoder reads positional (fixed-width) UTF-8 text files.
// Each line becomes a PositionalRow.
type UTF8Decoder struct {
    reader  *bufio.Reader
    closer  io.Closer
    lineNum int
}

// NewUTF8Decoder creates a decoder for UTF-8 positional files.
func NewUTF8Decoder(r io.ReadCloser) *UTF8Decoder {
    return &UTF8Decoder{
        reader: bufio.NewReader(r),
        closer: r,
        lineNum: 0,
    }
}

func (d *UTF8Decoder) Format() filespec.Format {
    return filespec.FormatPositional
}

func (d *UTF8Decoder) Close() error {
    if d.closer != nil {
        return d.closer.Close()
    }
    return nil
}

func (d *UTF8Decoder) Rows() iter.Seq2[Row, error] {
    return func(yield func(Row, error) bool) {
        for {
            // Read a line from the file
            line, err := d.reader.ReadString('\n')
            if err != nil && err != io.EOF {
                yield(nil, err)
                return
            }

            // Handle end of file
            if len(line) == 0 && err == io.EOF {
                return
            }

            d.lineNum++

            // Remove trailing newline characters
            line = strings.TrimRight(line, "\r\n")

            // Detect record type from line prefix
            recordType := detectRecordTypeFromPrefix(line)

            // Create the row
            row := NewPositionalRow(d.lineNum, recordType, line)

            // Yield the row to the caller
            if !yield(row, nil) {
                return // Caller wants to stop iteration
            }

            // If we hit EOF after reading this line, we're done
            if err == io.EOF {
                return
            }
        }
    }
}

// detectRecordTypeFromPrefix determines record type from line start.
// This is a basic implementation - the full logic uses FileSpec configuration.
func detectRecordTypeFromPrefix(line string) string {
    if strings.HasPrefix(line, "HEADER") {
        return "HEADER"
    }
    if strings.HasPrefix(line, "TRAILER") {
        return "TRAILER"
    }
    if len(line) >= 2 {
        return line[:2]
    }
    return ""
}
```

### CSV Decoder (Columnar Format)

```go
// internal/decoder/csv.go
package decoder

import (
    "encoding/csv"
    "io"
    "iter"

    "go-parser/internal/filespec"
)

// CSVDecoder reads CSV files.
// Each row becomes a ColumnarRow with string values.
type CSVDecoder struct {
    reader  *csv.Reader
    closer  io.Closer
    lineNum int

    // recordType is the fixed record type for this file.
    // For FRA files, this is always "TE1".
    recordType string
}

// NewCSVDecoder creates a decoder for CSV files.
func NewCSVDecoder(r io.ReadCloser, recordType string) *CSVDecoder {
    csvReader := csv.NewReader(r)
    // Configure CSV reader
    csvReader.FieldsPerRecord = -1 // Allow variable number of fields
    csvReader.TrimLeadingSpace = true

    return &CSVDecoder{
        reader:     csvReader,
        closer:     r,
        lineNum:    0,
        recordType: recordType,
    }
}

func (d *CSVDecoder) Format() filespec.Format {
    return filespec.FormatColumnar
}

func (d *CSVDecoder) Close() error {
    if d.closer != nil {
        return d.closer.Close()
    }
    return nil
}

func (d *CSVDecoder) Rows() iter.Seq2[Row, error] {
    return func(yield func(Row, error) bool) {
        for {
            // Read a row from the CSV
            record, err := d.reader.Read()
            if err == io.EOF {
                return
            }
            if err != nil {
                yield(nil, err)
                return
            }

            d.lineNum++

            // Skip empty rows or comment rows
            if len(record) == 0 || (len(record) > 0 && strings.HasPrefix(record[0], "#")) {
                continue
            }

            // Convert []string to []any for consistent interface
            columns := make([]any, len(record))
            for i, v := range record {
                columns[i] = v
            }

            // Create the row
            row := NewColumnarRow(d.lineNum, d.recordType, columns)

            if !yield(row, nil) {
                return
            }
        }
    }
}
```

### XLSX Decoder (Columnar Format)

```go
// internal/decoder/xlsx.go
package decoder

import (
    "iter"

    "github.com/xuri/excelize/v2"

    "go-parser/internal/filespec"
)

// XLSXDecoder reads XLSX (Excel) files.
// Each row becomes a ColumnarRow with typed values (string, int, float64).
type XLSXDecoder struct {
    file    *excelize.File
    sheet   string
    rows    *excelize.Rows
    lineNum int

    recordType string
}

// NewXLSXDecoder creates a decoder for XLSX files.
func NewXLSXDecoder(path string, recordType string) (*XLSXDecoder, error) {
    f, err := excelize.OpenFile(path)
    if err != nil {
        return nil, err
    }

    // Get the first sheet
    sheets := f.GetSheetList()
    if len(sheets) == 0 {
        return nil, fmt.Errorf("xlsx file has no sheets")
    }
    sheet := sheets[0]

    rows, err := f.Rows(sheet)
    if err != nil {
        return nil, err
    }

    return &XLSXDecoder{
        file:       f,
        sheet:      sheet,
        rows:       rows,
        lineNum:    0,
        recordType: recordType,
    }, nil
}

func (d *XLSXDecoder) Format() filespec.Format {
    return filespec.FormatColumnar
}

func (d *XLSXDecoder) Close() error {
    if d.rows != nil {
        d.rows.Close()
    }
    if d.file != nil {
        return d.file.Close()
    }
    return nil
}

func (d *XLSXDecoder) Rows() iter.Seq2[Row, error] {
    return func(yield func(Row, error) bool) {
        for d.rows.Next() {
            d.lineNum++

            cols, err := d.rows.Columns()
            if err != nil {
                yield(nil, err)
                return
            }

            // Skip empty rows
            if len(cols) == 0 || allEmpty(cols) {
                continue
            }

            // Skip comment rows
            if len(cols) > 0 && strings.HasPrefix(cols[0], "#") {
                continue
            }

            // Convert to []any
            columns := make([]any, len(cols))
            for i, v := range cols {
                columns[i] = v
            }

            row := NewColumnarRow(d.lineNum, d.recordType, columns)

            if !yield(row, nil) {
                return
            }
        }
    }
}

func allEmpty(cols []string) bool {
    for _, c := range cols {
        if strings.TrimSpace(c) != "" {
            return false
        }
    }
    return true
}
```

### Field Extraction Strategy

The parser uses different extraction logic based on the format:

```go
// internal/parser/extractor.go
package parser

import (
    "fmt"
    "strconv"
    "strings"

    "go-parser/internal/decoder"
    "go-parser/internal/filespec"
    "go-parser/internal/schema"
)

// FieldExtractor extracts field values from rows based on the file format.
type FieldExtractor interface {
    Extract(row decoder.Row, field *schema.FieldDef) (any, error)
}

// GetExtractor returns the appropriate extractor for the given format.
func GetExtractor(format filespec.Format) FieldExtractor {
    switch format {
    case filespec.FormatPositional:
        return &PositionalExtractor{}
    case filespec.FormatColumnar:
        return &ColumnarExtractor{}
    default:
        panic(fmt.Sprintf("unknown format: %s", format))
    }
}

// PositionalExtractor extracts fields from positional (fixed-width) rows.
type PositionalExtractor struct{}

func (e *PositionalExtractor) Extract(row decoder.Row, field *schema.FieldDef) (any, error) {
    // Type assert to PositionalRow
    pr, ok := row.(*decoder.PositionalRow)
    if !ok {
        return nil, fmt.Errorf("expected PositionalRow, got %T", row)
    }

    // Extract raw string value using byte positions
    rawValue := pr.Slice(field.Start, field.End)

    // Apply transformation if specified
    if field.Transform != "" {
        rawValue = applyTransform(rawValue, field.Transform)
    }

    // Convert to appropriate type
    return convertValue(rawValue, field.Type)
}

// ColumnarExtractor extracts fields from columnar (CSV/XLSX) rows.
type ColumnarExtractor struct{}

func (e *ColumnarExtractor) Extract(row decoder.Row, field *schema.FieldDef) (any, error) {
    // Type assert to ColumnarRow
    cr, ok := row.(*decoder.ColumnarRow)
    if !ok {
        return nil, fmt.Errorf("expected ColumnarRow, got %T", row)
    }

    // Extract value using column index
    val := cr.Column(field.Column)
    if val == nil {
        return nil, nil // Column doesn't exist
    }

    // Apply transformation if specified
    if field.Transform != "" {
        // Convert to string first for transformation
        strVal := fmt.Sprintf("%v", val)
        strVal = applyTransform(strVal, field.Transform)
        return convertValue(strVal, field.Type)
    }

    // Handle type conversion
    // XLSX may return typed values, CSV returns strings
    switch v := val.(type) {
    case string:
        return convertValue(v, field.Type)
    case int, int64, float64:
        // Already numeric - return as-is if type matches
        if field.Type == "int" {
            return toInt(v), nil
        }
        return fmt.Sprintf("%v", v), nil
    default:
        return convertValue(fmt.Sprintf("%v", v), field.Type)
    }
}

// convertValue converts a string value to the appropriate Go type.
func convertValue(rawValue, fieldType string) (any, error) {
    // Check for empty value
    trimmed := strings.TrimSpace(rawValue)
    if trimmed == "" {
        return nil, nil
    }

    switch fieldType {
    case "int":
        i, err := strconv.Atoi(trimmed)
        if err != nil {
            return nil, fmt.Errorf("cannot convert %q to int: %w", rawValue, err)
        }
        return i, nil

    case "string":
        return rawValue, nil // Don't trim - preserve exact value

    default:
        return nil, fmt.Errorf("unknown field type: %s", fieldType)
    }
}

// toInt converts various numeric types to int.
func toInt(v any) int {
    switch n := v.(type) {
    case int:
        return n
    case int64:
        return int(n)
    case float64:
        return int(n)
    default:
        return 0
    }
}

// Transform function registry
var transforms = map[string]func(string) string{
    "zero_pad_3": func(s string) string {
        trimmed := strings.TrimSpace(s)
        if len(trimmed) < 3 {
            return fmt.Sprintf("%03s", trimmed)
        }
        return trimmed
    },
    "zero_pad_5": func(s string) string {
        trimmed := strings.TrimSpace(s)
        if len(trimmed) < 5 {
            return fmt.Sprintf("%05s", trimmed)
        }
        return trimmed
    },
    // Add more transforms as needed
}

func applyTransform(value, transformName string) string {
    if fn, ok := transforms[transformName]; ok {
        return fn(value)
    }
    return value // Unknown transform - return unchanged
}
```

---

## Record Type Detection

### What Is Record Type Detection?

When processing a file, we need to determine which schema applies to each row. This is called **record type detection**.

- For **positional files**: We look at the first few characters (prefix) of each line
- For **columnar files**: We either look at a specific column or assume all rows are the same type

### Record Type Detector Implementation

```go
// internal/parser/detector.go
package parser

import (
    "fmt"
    "strings"

    "go-parser/internal/decoder"
    "go-parser/internal/filespec"
    "go-parser/internal/schema"
)

// RecordTypeDetector determines which schema applies to each row.
type RecordTypeDetector struct {
    spec     *filespec.FileSpec
    registry *Registry

    // Cached lookup for prefix detection (sorted by prefix length, longest first)
    sortedPrefixes []filespec.PrefixMapping
}

// NewRecordTypeDetector creates a detector for the given file specification.
func NewRecordTypeDetector(spec *filespec.FileSpec, registry *Registry) *RecordTypeDetector {
    d := &RecordTypeDetector{
        spec:     spec,
        registry: registry,
    }

    // Sort prefixes by length (longest first) for correct matching
    // This ensures "HEADER" matches before "H" would
    if spec.RecordTypeDetection.Method == "prefix" {
        d.sortedPrefixes = sortPrefixesByLength(spec.RecordTypeDetection.Prefixes)
    }

    return d
}

// Detect determines the schema for a given row.
// Returns the compiled schema or an error if no matching schema is found.
func (d *RecordTypeDetector) Detect(row decoder.Row) (*schema.CompiledSchema, error) {
    switch d.spec.RecordTypeDetection.Method {
    case "prefix":
        return d.detectByPrefix(row)
    case "column":
        return d.detectByColumn(row)
    case "fixed":
        return d.detectFixed()
    default:
        return nil, fmt.Errorf("unknown detection method: %s", d.spec.RecordTypeDetection.Method)
    }
}

// detectByPrefix determines schema by looking at line prefix (for positional files).
func (d *RecordTypeDetector) detectByPrefix(row decoder.Row) (*schema.CompiledSchema, error) {
    pr, ok := row.(*decoder.PositionalRow)
    if !ok {
        return nil, fmt.Errorf("prefix detection requires PositionalRow, got %T", row)
    }

    data := pr.Data()

    // Try each prefix in order (longest first)
    for _, mapping := range d.sortedPrefixes {
        if strings.HasPrefix(data, mapping.Prefix) {
            sch := d.registry.GetSchema(mapping.Schema)
            if sch == nil {
                return nil, fmt.Errorf("schema not found: %s", mapping.Schema)
            }
            return sch, nil
        }
    }

    // No matching prefix found
    preview := data
    if len(preview) > 20 {
        preview = preview[:20] + "..."
    }
    return nil, fmt.Errorf("no matching prefix for line: %q", preview)
}

// detectByColumn determines schema by looking at a column value (for columnar files).
func (d *RecordTypeDetector) detectByColumn(row decoder.Row) (*schema.CompiledSchema, error) {
    cr, ok := row.(*decoder.ColumnarRow)
    if !ok {
        return nil, fmt.Errorf("column detection requires ColumnarRow, got %T", row)
    }

    colIdx := d.spec.RecordTypeDetection.Column
    val := cr.Column(colIdx)
    if val == nil {
        return nil, fmt.Errorf("column %d is empty or missing", colIdx)
    }

    recordType := strings.TrimSpace(fmt.Sprintf("%v", val))

    sch := d.registry.GetSchema(recordType)
    if sch == nil {
        return nil, fmt.Errorf("unknown record type: %s", recordType)
    }

    return sch, nil
}

// detectFixed returns the fixed schema configured for this file type.
func (d *RecordTypeDetector) detectFixed() (*schema.CompiledSchema, error) {
    schemaName := d.spec.RecordTypeDetection.Schema
    sch := d.registry.GetSchema(schemaName)
    if sch == nil {
        return nil, fmt.Errorf("fixed schema not found: %s", schemaName)
    }
    return sch, nil
}

// sortPrefixesByLength returns prefixes sorted by length (longest first).
func sortPrefixesByLength(prefixes []filespec.PrefixMapping) []filespec.PrefixMapping {
    // Make a copy to avoid modifying the original
    sorted := make([]filespec.PrefixMapping, len(prefixes))
    copy(sorted, prefixes)

    // Sort by prefix length, longest first
    sort.Slice(sorted, func(i, j int) bool {
        return len(sorted[i].Prefix) > len(sorted[j].Prefix)
    })

    return sorted
}
```

---

## Record Grouping and Batching

### Why Do We Need Grouping?

For TANF/SSP/Tribal Section 1 and 2 files, records with the same `RPT_MONTH_YEAR` and `CASE_NUMBER` belong to the same case. These records must be:

1. **Parsed together**: So we have complete case data
2. **Validated together**: Some rules check consistency across records in a case
3. **Written together**: Database transactions should be per-case

### Why Do We Need Batching?

For files without case grouping (Section 3/4 aggregate data, FRA files), records are independent. However, processing one record at a time is inefficient due to:

1. **Goroutine overhead**: Starting a goroutine for each record wastes resources
2. **Channel overhead**: Sending one item at a time has more overhead than batches
3. **Database overhead**: Individual inserts are slower than batch inserts

Batching groups N independent records together for efficient processing.

### Unified Accumulator Flow

The accumulator uses two independent, inclusive settings to determine behavior:

```
                         ┌─────────────────────┐
                         │     FileSpec        │
                         │  AccumulatorConfig  │
                         └──────────┬──────────┘
                                    │
          ┌─────────────────────────┴─────────────────────────┐
          │                                                   │
          ▼                                                   ▼
┌─────────────────────┐                         ┌─────────────────────┐
│   key_fields set?   │                         │   batch_size > 0?   │
└─────────────────────┘                         └─────────────────────┘
     │          │                                    │          │
   yes │        │ no                              yes │        │ no
     │          │                                    │          │
     ▼          ▼                                    ▼          ▼
 Group by    Each record                        Batch N      Each group
 composite   is its own                         groups       dispatched
 key         group                              together     individually
```

**The Four Modes:**

| key_fields | batch_size | Behavior                                        | Use Case           |
|------------|------------|-------------------------------------------------|--------------------|
| `{}`       | `0`        | Per-record: each record is Batch{1 group, 1 rec}| Debugging/Testing  |
| `{}`       | `100`      | Batch{100 groups}, each group has 1 record      | FRA, Section 3/4   |
| `{X,Y}`    | `0`        | Each case group is its own Batch                | Low-memory TANF    |
| `{X,Y}`    | `10`       | Batch{10 case groups}, each group has N records | High-perf TANF     |

### Unified Output Types

```go
// internal/processor/types.go
package processor

import (
    "go-parser/internal/decoder"
    "go-parser/internal/schema"
)

// RawLine holds a raw row along with its detected schema.
type RawLine struct {
    Row    decoder.Row
    Schema *schema.CompiledSchema
}

// RecordGroup holds all raw lines belonging to a logical group.
// For key-based grouping: all records with the same (RPT_MONTH_YEAR, CASE_NUMBER).
// For non-keyed: each record is its own group (Key is empty).
type RecordGroup struct {
    // Key is the composite grouping key: "YYYYMM|CASE_NUMBER"
    // Empty string if no key_fields are configured (each record is its own group).
    Key string

    // RptMonthYear is extracted from the key for convenience (empty if no key_fields)
    RptMonthYear string

    // CaseNumber is extracted from the key for convenience (empty if no key_fields)
    CaseNumber string

    // Lines contains all rows for this group
    Lines []RawLine
}

// TotalRecords returns the total number of records in this group.
func (g *RecordGroup) TotalRecords() int {
    return len(g.Lines)
}

// Batch is the unit of work dispatched to workers.
// Contains one or more RecordGroups depending on batch_size configuration.
type Batch struct {
    // BatchID is a sequential identifier for this batch
    BatchID int

    // Groups contains the record groups in this batch.
    // - If key_fields set + batch_size=0: 1 group with N records (a case)
    // - If key_fields set + batch_size=M: M groups, each with N records
    // - If no key_fields + batch_size=N: N groups, each with 1 record
    // - If no key_fields + batch_size=0: 1 group with 1 record
    Groups []*RecordGroup
}

// TotalGroups returns the number of groups in this batch.
func (b *Batch) TotalGroups() int {
    return len(b.Groups)
}

// TotalRecords returns the total number of records across all groups.
func (b *Batch) TotalRecords() int {
    total := 0
    for _, g := range b.Groups {
        total += len(g.Lines)
    }
    return total
}
```

---

## Accumulator

### What Does the Accumulator Do?

The Accumulator is a unified component that collects records and outputs Batches for worker processing. It handles all four modes based on the `key_fields` and `batch_size` configuration:

**Mode 1: Key-based grouping, no batching** (`key_fields` set, `batch_size` = 0)
```
Input:  T1 (case A), T2 (case A), T1 (case B), T3 (case A), T2 (case B)

Accumulator groups by case key:
  Group A: [T1, T2, T3]
  Group B: [T1, T2]

Output (on Drain):
  Batch{ Groups: [Group A] }
  Batch{ Groups: [Group B] }
```

**Mode 2: Key-based grouping with batching** (`key_fields` set, `batch_size` = 2)
```
Input:  (same as above)

Output (on Drain):
  Batch{ Groups: [Group A, Group B] }  // Both cases in one batch
```

**Mode 3: No grouping, with batching** (`key_fields` empty, `batch_size` = 3)
```
Input:  R1, R2, R3, R4, R5

Output (streaming):
  Batch{ Groups: [{R1}, {R2}, {R3}] }  // Each record is its own group
  Batch{ Groups: [{R4}, {R5}] }        // Remaining on Drain
```

**Mode 4: Per-record** (`key_fields` empty, `batch_size` = 0)
```
Input:  R1, R2, R3

Output (streaming):
  Batch{ Groups: [{R1}] }
  Batch{ Groups: [{R2}] }
  Batch{ Groups: [{R3}] }
```

### Accumulator Implementation

```go
// internal/processor/accumulator.go
package processor

import (
    "fmt"

    "go-parser/internal/decoder"
    "go-parser/internal/filespec"
    "go-parser/internal/schema"
)

// Accumulator collects records into Batches based on the AccumulatorConfig.
//
// The accumulator handles four modes based on key_fields and batch_size:
//   - key_fields set, batch_size=0:  Group by key, emit each group as its own Batch
//   - key_fields set, batch_size=N:  Group by key, batch N groups together
//   - key_fields empty, batch_size=N: Each record is a group, batch N groups together
//   - key_fields empty, batch_size=0: Each record is its own Batch (per-record mode)
type Accumulator struct {
    spec     *filespec.FileSpec
    detector *RecordTypeDetector

    // Configuration derived from spec
    hasKeyFields   bool
    batchSize      int
    groupedSchemas map[string]bool

    // State for key-based grouping
    groups map[string]*RecordGroup

    // State for batching
    pendingGroups []*RecordGroup
    batchCounter  int
}

// NewAccumulator creates an accumulator for the given file specification.
func NewAccumulator(spec *filespec.FileSpec, detector *RecordTypeDetector) *Accumulator {
    // Build set of grouped schemas for quick lookup
    groupedSchemas := make(map[string]bool)
    for _, name := range spec.Accumulator.GroupedSchemas {
        groupedSchemas[name] = true
    }

    return &Accumulator{
        spec:           spec,
        detector:       detector,
        hasKeyFields:   spec.Accumulator.HasKeyFields(),
        batchSize:      spec.Accumulator.BatchSize,
        groupedSchemas: groupedSchemas,
        groups:         make(map[string]*RecordGroup),
        pendingGroups:  make([]*RecordGroup, 0),
        batchCounter:   0,
    }
}

// Add processes a row from the file.
//
// Returns:
//   - batch: A complete Batch if one is ready (only in non-keyed or per-record mode)
//   - schema: The detected schema for this row
//   - isAccumulated: true if the row was added to a group (not HEADER/TRAILER)
//   - err: Any error encountered
//
// For key-based grouping, batches are only returned from Drain() after all rows are processed.
// For non-keyed mode with batch_size > 0, batches are returned as they fill up.
// For per-record mode (no keys, batch_size=0), each row returns its own batch.
func (a *Accumulator) Add(row decoder.Row) (batch *Batch, sch *schema.CompiledSchema, isAccumulated bool, err error) {
    // Detect which schema this row belongs to
    sch, err = a.detector.Detect(row)
    if err != nil {
        return nil, nil, false, err
    }

    // Check if this schema participates in accumulation
    schemaName := sch.RecordType
    if len(a.groupedSchemas) > 0 && !a.groupedSchemas[schemaName] {
        // Not accumulated (e.g., HEADER, TRAILER) - return for immediate processing
        return nil, sch, false, nil
    }

    line := RawLine{Row: row, Schema: sch}

    if a.hasKeyFields {
        // Key-based grouping mode
        return a.addWithKey(line, sch)
    }

    // Non-keyed mode: each record is its own group
    return a.addWithoutKey(line, sch)
}

// addWithKey handles rows when key_fields is configured.
// Groups are accumulated in memory and only returned via Drain().
func (a *Accumulator) addWithKey(line RawLine, sch *schema.CompiledSchema) (*Batch, *schema.CompiledSchema, bool, error) {
    // Extract the grouping key
    key, rptMonth, caseNum, err := a.extractKey(line.Row)
    if err != nil {
        return nil, nil, false, fmt.Errorf("line %d: failed to extract key: %w", line.Row.LineNum(), err)
    }

    // Get or create the group
    group, exists := a.groups[key]
    if !exists {
        group = &RecordGroup{
            Key:          key,
            RptMonthYear: rptMonth,
            CaseNumber:   caseNum,
            Lines:        make([]RawLine, 0, 8), // Pre-allocate for typical case size
        }
        a.groups[key] = group
    }

    // Add the row to the group
    group.Lines = append(group.Lines, line)

    // For key-based grouping, batches are only returned from Drain()
    return nil, sch, true, nil
}

// addWithoutKey handles rows when key_fields is empty.
// Each record is its own group. Batches may be returned immediately.
func (a *Accumulator) addWithoutKey(line RawLine, sch *schema.CompiledSchema) (*Batch, *schema.CompiledSchema, bool, error) {
    // Create a single-record group
    group := &RecordGroup{
        Key:   "", // No key for non-grouped records
        Lines: []RawLine{line},
    }

    // Per-record mode: batch_size = 0 means emit immediately
    if a.batchSize == 0 {
        batch := &Batch{
            BatchID: a.batchCounter,
            Groups:  []*RecordGroup{group},
        }
        a.batchCounter++
        return batch, sch, true, nil
    }

    // Batching mode: collect groups until batch is full
    a.pendingGroups = append(a.pendingGroups, group)

    if len(a.pendingGroups) >= a.batchSize {
        batch := &Batch{
            BatchID: a.batchCounter,
            Groups:  a.pendingGroups,
        }
        a.batchCounter++
        a.pendingGroups = make([]*RecordGroup, 0, a.batchSize)
        return batch, sch, true, nil
    }

    return nil, sch, true, nil
}

// extractKey extracts the grouping key from a row.
func (a *Accumulator) extractKey(row decoder.Row) (key, rptMonth, caseNum string, err error) {
    pr, ok := row.(*decoder.PositionalRow)
    if !ok {
        return "", "", "", fmt.Errorf("key-based grouping requires PositionalRow, got %T", row)
    }

    data := pr.Data()
    keyConfig := a.spec.Accumulator.KeyFields

    // Validate line length
    minLen := keyConfig.CaseNumber.End
    if len(data) < minLen {
        return "", "", "", fmt.Errorf("line too short: need %d bytes, got %d", minLen, len(data))
    }

    // Extract key components
    rptMonth = data[keyConfig.RptMonthYear.Start:keyConfig.RptMonthYear.End]
    caseNum = data[keyConfig.CaseNumber.Start:keyConfig.CaseNumber.End]

    // Composite key with separator
    key = rptMonth + "|" + caseNum

    return key, rptMonth, caseNum, nil
}

// Drain returns all accumulated groups as Batches and resets the accumulator.
// Call this after all rows have been processed.
//
// For key-based grouping:
//   - If batch_size=0: Each group becomes its own Batch
//   - If batch_size=N: Groups are batched together (N groups per Batch)
//
// For non-keyed mode:
//   - Returns any remaining partial batch
func (a *Accumulator) Drain() []*Batch {
    var batches []*Batch

    if a.hasKeyFields {
        // Collect all groups from the map
        allGroups := make([]*RecordGroup, 0, len(a.groups))
        for _, group := range a.groups {
            allGroups = append(allGroups, group)
        }

        if a.batchSize == 0 {
            // Each group is its own batch
            for _, group := range allGroups {
                batches = append(batches, &Batch{
                    BatchID: a.batchCounter,
                    Groups:  []*RecordGroup{group},
                })
                a.batchCounter++
            }
        } else {
            // Batch groups together
            for i := 0; i < len(allGroups); i += a.batchSize {
                end := i + a.batchSize
                if end > len(allGroups) {
                    end = len(allGroups)
                }
                batches = append(batches, &Batch{
                    BatchID: a.batchCounter,
                    Groups:  allGroups[i:end],
                })
                a.batchCounter++
            }
        }

        // Clear accumulated groups
        a.groups = make(map[string]*RecordGroup)
    } else {
        // Non-keyed mode: return any remaining pending groups
        if len(a.pendingGroups) > 0 {
            batches = append(batches, &Batch{
                BatchID: a.batchCounter,
                Groups:  a.pendingGroups,
            })
            a.batchCounter++
            a.pendingGroups = make([]*RecordGroup, 0)
        }
    }

    return batches
}

// Stats returns statistics about accumulated state.
func (a *Accumulator) Stats() (numGroups, totalLines, pendingGroups int) {
    for _, g := range a.groups {
        numGroups++
        totalLines += len(g.Lines)
    }
    pendingGroups = len(a.pendingGroups)
    return
}
```

---

## Worker Pool Implementation

### What Is the Worker Pool?

The worker pool is a fixed number of goroutines that process Batches in parallel. This provides:

1. **Controlled concurrency**: We don't spawn unlimited goroutines
2. **Backpressure**: If workers are busy, producers slow down
3. **Resource efficiency**: Goroutines are reused

With the unified Accumulator, the worker pool now uses a single channel that receives `*Batch` objects regardless of whether they contain keyed groups or independent records.

### Worker Pool Implementation

```go
// internal/worker/pool.go
package worker

import (
    "context"
    "sync"

    "go-parser/internal/filespec"
    "go-parser/internal/parser"
    "go-parser/internal/processor"
    "go-parser/internal/schema"
)

// ParsedRecord represents a successfully parsed record.
// The Fields map contains parsed values using Go's native types (string, int, etc.).
// These are converted to SQLC-generated types (db.SearchIndexesTanfT1, etc.)
// by the converter package when writing to the database.
// See: internal/converter/tanf_t1.go for conversion implementation.
type ParsedRecord struct {
    Schema     *schema.CompiledSchema
    LineNumber int
    Fields     map[string]any // Converted to SQLC types by converter.ToTanfT1(), etc.
}

// ParseError represents a parsing error for a single row.
type ParseError struct {
    LineNumber int
    RecordType string
    Message    string
}

// ParsedGroup contains parsing results for a single RecordGroup.
type ParsedGroup struct {
    // Key is the grouping key (empty for non-keyed records)
    Key          string
    RptMonthYear string
    CaseNumber   string

    // Records contains all successfully parsed records in this group
    Records []*ParsedRecord

    // Errors contains any parsing errors encountered
    Errors []ParseError
}

// ParsedBatch contains parsing results for a Batch (one or more groups).
type ParsedBatch struct {
    BatchID int
    Groups  []*ParsedGroup
}

// TotalRecords returns the total number of successfully parsed records.
func (pb *ParsedBatch) TotalRecords() int {
    total := 0
    for _, g := range pb.Groups {
        total += len(g.Records)
    }
    return total
}

// TotalErrors returns the total number of parsing errors.
func (pb *ParsedBatch) TotalErrors() int {
    total := 0
    for _, g := range pb.Groups {
        total += len(g.Errors)
    }
    return total
}

// Pool manages worker goroutines for parallel parsing.
type Pool struct {
    numWorkers int
    extractor  parser.FieldExtractor

    // Single work input channel for all Batches
    work chan *processor.Batch

    // Single result output channel
    results chan *ParsedBatch

    wg sync.WaitGroup
}

// PoolConfig configures the worker pool.
type PoolConfig struct {
    NumWorkers       int
    WorkBufferSize   int
    ResultBufferSize int
}

// DefaultPoolConfig returns sensible defaults.
func DefaultPoolConfig() PoolConfig {
    return PoolConfig{
        NumWorkers:       8,
        WorkBufferSize:   256,
        ResultBufferSize: 256,
    }
}

// NewPool creates a worker pool.
func NewPool(format filespec.Format, config PoolConfig) *Pool {
    return &Pool{
        numWorkers: config.NumWorkers,
        extractor:  parser.GetExtractor(format),
        work:       make(chan *processor.Batch, config.WorkBufferSize),
        results:    make(chan *ParsedBatch, config.ResultBufferSize),
    }
}

// Start launches the worker goroutines.
func (p *Pool) Start(ctx context.Context) {
    for i := 0; i < p.numWorkers; i++ {
        p.wg.Add(1)
        go p.worker(ctx)
    }
}

// Submit submits a Batch for processing.
// Blocks if the work channel is full (backpressure).
func (p *Pool) Submit(batch *processor.Batch) {
    p.work <- batch
}

// CloseInputs signals that no more work will be submitted.
func (p *Pool) CloseInputs() {
    close(p.work)
}

// Wait blocks until all workers finish, then closes result channels.
func (p *Pool) Wait() {
    p.wg.Wait()
    close(p.results)
}

// Results returns the channel for receiving parsed batch results.
func (p *Pool) Results() <-chan *ParsedBatch {
    return p.results
}

// worker is the main worker goroutine.
func (p *Pool) worker(ctx context.Context) {
    defer p.wg.Done()

    for {
        select {
        case <-ctx.Done():
            return

        case batch, ok := <-p.work:
            if !ok {
                return // Channel closed, exit
            }
            p.results <- p.processBatch(batch)
        }
    }
}

// processBatch parses all records in all groups within a batch.
func (p *Pool) processBatch(batch *processor.Batch) *ParsedBatch {
    result := &ParsedBatch{
        BatchID: batch.BatchID,
        Groups:  make([]*ParsedGroup, 0, len(batch.Groups)),
    }

    for _, group := range batch.Groups {
        parsedGroup := p.processGroup(group)
        result.Groups = append(result.Groups, parsedGroup)
    }

    return result
}

// processGroup parses all records in a single group.
func (p *Pool) processGroup(group *processor.RecordGroup) *ParsedGroup {
    result := &ParsedGroup{
        Key:          group.Key,
        RptMonthYear: group.RptMonthYear,
        CaseNumber:   group.CaseNumber,
        Records:      make([]*ParsedRecord, 0, len(group.Lines)),
        Errors:       make([]ParseError, 0),
    }

    for _, line := range group.Lines {
        record, err := p.parseRow(line)
        if err != nil {
            result.Errors = append(result.Errors, ParseError{
                LineNumber: line.Row.LineNum(),
                RecordType: line.Schema.RecordType,
                Message:    err.Error(),
            })
            continue
        }
        result.Records = append(result.Records, record)
    }

    return result
}

// parseRow parses a single row into a ParsedRecord.
func (p *Pool) parseRow(line processor.RawLine) (*ParsedRecord, error) {
    record := &ParsedRecord{
        Schema:     line.Schema,
        LineNumber: line.Row.LineNum(),
        Fields:     make(map[string]any, len(line.Schema.Fields)),
    }

    for i := range line.Schema.Fields {
        field := &line.Schema.Fields[i]

        value, err := p.extractor.Extract(line.Row, field)
        if err != nil {
            // Log but continue - validation will catch missing required fields
            continue
        }

        if value != nil {
            record.Fields[field.Name] = value
        }
    }

    return record, nil
}
```

---

## SQLC Integration

### Overview

SQLC generates type-safe Go structs directly from your PostgreSQL schema. These types are the **single source of truth** for database operations and should be used throughout the Database Writer for:

1. **Type safety**: Compile-time validation that fields match the database schema
2. **Performance**: Direct use with pgx's `CopyFromSlice` for efficient bulk inserts
3. **Maintainability**: Regenerate types when schema changes via `sqlc generate`

### Generated Types

SQLC generates Go types from your database schema (managed by Django). These types use `pgtype` wrappers for nullable fields:

```go
// internal/db/models.go - Generated by SQLC
type SearchIndexesTanfT1 struct {
    ID                       pgtype.UUID
    DatafileID               pgtype.Int4
    LineNumber               pgtype.Int4
    RecordType               pgtype.Text
    RPTMONTHYEAR             pgtype.Int4
    CASENUMBER               pgtype.Text
    DISPOSITION              pgtype.Int4
    FIPSCODE                 pgtype.Text
    COUNTYFIPSCODE           pgtype.Text
    STRATUM                  pgtype.Text
    ZIPCODE                  pgtype.Text
    FUNDINGSTREAM            pgtype.Int4
    // ... all 46 fields matching the database table
}

type SearchIndexesTanfT2 struct {
    ID                       pgtype.UUID
    DatafileID               pgtype.Int4
    LineNumber               pgtype.Int4
    RecordType               pgtype.Text
    RPTMONTHYEAR             pgtype.Int4
    CASENUMBER               pgtype.Text
    FAMILYAFFILIATION        pgtype.Int4
    // ... all 65 fields matching the database table
}

type ParserError struct {
    ID            int32
    RowNumber     pgtype.Int4
    ColumnNumber  pgtype.Text
    ItemNumber    pgtype.Text
    FieldName     pgtype.Text
    CaseNumber    pgtype.Text
    RptMonthYear  pgtype.Int4
    ErrorMessage  pgtype.Text
    ErrorType     string
    // ...
}
```

### The Conversion Challenge

Our parsed records use simple Go types (`int`, `string`, `*int`, `*string`). We need a conversion layer to transform parsed fields into SQLC struct fields.

### Type Conversion

```go
// internal/converter/helpers.go
package converter

import (
    "github.com/jackc/pgx/v5/pgtype"
)

// toPgText converts a string pointer to pgtype.Text.
func toPgText(s *string) pgtype.Text {
    if s == nil {
        return pgtype.Text{Valid: false}
    }
    return pgtype.Text{String: *s, Valid: true}
}

// toPgTextFromString converts a string to pgtype.Text.
func toPgTextFromString(s string) pgtype.Text {
    if s == "" {
        return pgtype.Text{Valid: false}
    }
    return pgtype.Text{String: s, Valid: true}
}

// toPgInt4 converts an int pointer to pgtype.Int4.
func toPgInt4(i *int) pgtype.Int4 {
    if i == nil {
        return pgtype.Int4{Valid: false}
    }
    return pgtype.Int4{Int32: int32(*i), Valid: true}
}

// toPgInt4FromInt converts an int to pgtype.Int4.
func toPgInt4FromInt(i int) pgtype.Int4 {
    return pgtype.Int4{Int32: int32(i), Valid: true}
}
```

### Record Converter

```go
// internal/converter/tanf_t1.go
package converter

import (
    "github.com/google/uuid"
    "github.com/jackc/pgx/v5/pgtype"

    "go-parser/internal/db"
    "go-parser/internal/worker"
)

// ToTanfT1 converts a ParsedRecord to the SQLC-generated type.
func ToTanfT1(record *worker.ParsedRecord, datafileID int32) *db.SearchIndexesTanfT1 {
    // Helper to get int pointer from fields
    getInt := func(name string) *int {
        if v, ok := record.Fields[name]; ok {
            if i, ok := v.(int); ok {
                return &i
            }
        }
        return nil
    }

    // Helper to get string pointer from fields
    getString := func(name string) *string {
        if v, ok := record.Fields[name]; ok {
            if s, ok := v.(string); ok {
                return &s
            }
        }
        return nil
    }

    return &db.SearchIndexesTanfT1{
        ID:                       pgtype.UUID{Bytes: uuid.New(), Valid: true},
        DatafileID:               toPgInt4FromInt(int(datafileID)),
        LineNumber:               toPgInt4FromInt(record.LineNumber),
        RecordType:               toPgText(getString("RecordType")),
        RPTMONTHYEAR:             toPgInt4(getInt("RPT_MONTH_YEAR")),
        CASENUMBER:               toPgText(getString("CASE_NUMBER")),
        COUNTYFIPSCODE:           toPgText(getString("COUNTY_FIPS_CODE")),
        STRATUM:                  toPgText(getString("STRATUM")),
        ZIPCODE:                  toPgText(getString("ZIP_CODE")),
        FUNDINGSTREAM:            toPgInt4(getInt("FUNDING_STREAM")),
        DISPOSITION:              toPgInt4(getInt("DISPOSITION")),
        NEWAPPLICANT:             toPgInt4(getInt("NEW_APPLICANT")),
        NBRFAMILYMEMBERS:         toPgInt4(getInt("NBR_FAMILY_MEMBERS")),
        FAMILYTYPE:               toPgInt4(getInt("FAMILY_TYPE")),
        RECEIVESSUBHOUSING:       toPgInt4(getInt("RECEIVES_SUB_HOUSING")),
        RECEIVESMEDASSISTANCE:    toPgInt4(getInt("RECEIVES_MED_ASSISTANCE")),
        RECEIVESFOODSTAMPS:       toPgInt4(getInt("RECEIVES_FOOD_STAMPS")),
        AMTFOODSTAMPASSISTANCE:   toPgInt4(getInt("AMT_FOOD_STAMP_ASSISTANCE")),
        RECEIVESSUBCC:            toPgInt4(getInt("RECEIVES_SUB_CC")),
        AMTSUBCC:                 toPgInt4(getInt("AMT_SUB_CC")),
        CHILDSUPPORTAMT:          toPgInt4(getInt("CHILD_SUPPORT_AMT")),
        FAMILYCASHRESOURCES:      toPgInt4(getInt("FAMILY_CASH_RESOURCES")),
        CASHAMOUNT:               toPgInt4(getInt("CASH_AMOUNT")),
        NBRMONTHS:                toPgInt4(getInt("NBR_MONTHS")),
        CCAMOUNT:                 toPgInt4(getInt("CC_AMOUNT")),
        CHILDRENCOVERED:          toPgInt4(getInt("CHILDREN_COVERED")),
        CCNBRMONTHS:              toPgInt4(getInt("CC_NBR_MONTHS")),
        TRANSPAMOUNT:             toPgInt4(getInt("TRANSP_AMOUNT")),
        TRANSPNBRMONTHS:          toPgInt4(getInt("TRANSP_NBR_MONTHS")),
        TRANSITIONSERVICESAMOUNT: toPgInt4(getInt("TRANSITION_SERVICES_AMOUNT")),
        TRANSITIONNBRMONTHS:      toPgInt4(getInt("TRANSITION_NBR_MONTHS")),
        OTHERAMOUNT:              toPgInt4(getInt("OTHER_AMOUNT")),
        OTHERNBRMONTHS:           toPgInt4(getInt("OTHER_NBR_MONTHS")),
        SANCREDUCTIONAMT:         toPgInt4(getInt("SANC_REDUCTION_AMT")),
        WORKREQSANCTION:          toPgInt4(getInt("WORK_REQ_SANCTION")),
        FAMILYSANCADULT:          toPgInt4(getInt("FAMILY_SANC_ADULT")),
        SANCTEENPARENT:           toPgInt4(getInt("SANC_TEEN_PARENT")),
        NONCOOPERATIONCSE:        toPgInt4(getInt("NON_COOPERATION_CSE")),
        FAILURETOCOMPLY:          toPgInt4(getInt("FAILURE_TO_COMPLY")),
        OTHERSANCTION:            toPgInt4(getInt("OTHER_SANCTION")),
        RECOUPMENTPRIOROVRPMT:    toPgInt4(getInt("RECOUPMENT_PRIOR_OVRPMT")),
        OTHERTOTALREDUCTIONS:     toPgInt4(getInt("OTHER_TOTAL_REDUCTIONS")),
        FAMILYCAP:                toPgInt4(getInt("FAMILY_CAP")),
        REDUCTIONSONRECEIPTS:     toPgInt4(getInt("REDUCTIONS_ON_RECEIPTS")),
        OTHERNONSANCTION:         toPgInt4(getInt("OTHER_NON_SANCTION")),
        WAIVEREVALCONTROLGRPS:    toPgInt4(getInt("WAIVER_EVAL_CONTROL_GRPS")),
        FAMILYEXEMPTTIMELIMITS:   toPgInt4(getInt("FAMILY_EXEMPT_TIME_LIMITS")),
        FAMILYNEWCHILD:           toPgInt4(getInt("FAMILY_NEW_CHILD")),
    }
}
```

### Schema to Database Mapping

The Registry derives database metadata from YAML schemas. Column names come directly from the schema field definitions - no separate hardcoded column lists needed.

```go
// internal/registry/schema_metadata.go
package registry

import (
    "fmt"
    "strings"

    "go-parser/internal/schema"
)

// SchemaMetadata holds database information derived from a schema.
type SchemaMetadata struct {
    TableName  string   // PostgreSQL table name (e.g., "search_indexes_tanf_t1")
    Columns    []string // Ordered column names for COPY (derived from schema fields)
    RecordType string   // e.g., "T1", "M2"
}

// buildSchemaMetadata derives database metadata from a compiled schema.
// Column names are extracted from the YAML schema fields - no duplication needed.
func buildSchemaMetadata(schemaPath string, compiled *schema.CompiledSchema) *SchemaMetadata {
    // Standard columns that appear in all record tables
    columns := []string{"id", "datafile_id", "line_number"}

    // Add columns from schema fields in order
    // Schema field names (e.g., "RPT_MONTH_YEAR") map directly to DB columns
    for _, field := range compiled.Fields {
        // PostgreSQL quoted identifiers for uppercase field names
        columns = append(columns, fmt.Sprintf(`"%s"`, field.Name))
    }

    return &SchemaMetadata{
        TableName:  schemaPathToTableName(schemaPath),
        Columns:    columns,
        RecordType: compiled.RecordType,
    }
}

// schemaPathToTableName converts a schema path to its database table name.
// Examples:
//   "tanf/t1"    -> "search_indexes_tanf_t1"
//   "ssp/m2"     -> "search_indexes_ssp_m2"
//   "tribal/t1"  -> "search_indexes_tribal_tanf_t1"
func schemaPathToTableName(schemaPath string) string {
    // Convert path separators and normalize
    normalized := strings.ReplaceAll(schemaPath, "/", "_")
    return "search_indexes_" + normalized
}

// buildAllMetadata derives database metadata from all loaded schemas.
// Called during Load() after schemas are loaded.
func (r *Registry) buildAllMetadata() {
    for path, compiled := range r.schemas {
        // Skip header/trailer - they don't have database tables
        if compiled.RecordType == "HEADER" || compiled.RecordType == "TRAILER" {
            continue
        }
        r.metadata[path] = buildSchemaMetadata(path, compiled)
    }
}

// GetSchemaMetadata returns database metadata for a schema path.
func (r *Registry) GetSchemaMetadata(schemaPath string) *SchemaMetadata {
    return r.metadata[schemaPath]
}
```

### Converter Registry

Each record type needs a converter function that transforms a parsed record to database row values. Converters use SQLC types internally for type safety, but return `[]any` for flexibility with the dynamic WriterManager.

```go
// internal/converter/registry.go
package converter

import (
    "go-parser/internal/worker"
)

// RowConverter converts a ParsedRecord to row values for COPY.
// Uses SQLC types internally for type safety, returns []any for flexibility.
type RowConverter func(record *worker.ParsedRecord, datafileID int32) []any

// converterRegistry maps record types to their converter functions.
var converterRegistry = map[string]RowConverter{
    // TANF record types
    "T1": convertT1,
    "T2": convertT2,
    "T3": convertT3,
    "T4": convertT4,
    "T5": convertT5,
    "T6": convertT6,
    "T7": convertT7,
    // SSP record types
    "M1": convertM1,
    "M2": convertM2,
    "M3": convertM3,
    "M4": convertM4,
    "M5": convertM5,
    "M6": convertM6,
    "M7": convertM7,
    // Tribal uses same T1-T7 prefixes but different tables
    // The WriterManager routes based on FileSpec, not just record type
}

// convertT1 converts a T1 record using SQLC types for type safety.
func convertT1(record *worker.ParsedRecord, datafileID int32) []any {
    sqlc := ToTanfT1(record, datafileID)  // Creates *db.SearchIndexesTanfT1
    return TanfT1RowValues(sqlc)           // Extracts []any for COPY
}

// GetConverter returns the converter for a record type.
func GetConverter(recordType string) RowConverter {
    return converterRegistry[recordType]
}
```

---

## Database Writer

### Design Constraints

The Database Writer is designed for write-heavy workloads with the following constraints:

1. **Memory limit**: 2GB maximum for the entire Go binary
2. **Single file processing**: One file at a time
3. **Limited record types**: Maximum 3 record types + parser errors per file
4. **All inserts**: No updates or upserts - all records are new
5. **High throughput**: Must handle millions to tens of millions of records

### Memory Budget

```
┌─────────────────────────────────────────────────────────────┐
│                    2GB MEMORY BUDGET                         │
├─────────────────────────────────────────────────────────────┤
│  Go runtime + GC headroom:     ~200MB                       │
│  File reading buffers:          ~50MB                       │
│  Decoder/parsing:               ~50MB                       │
│  Accumulator (case groups):    ~500MB  ← Largest consumer   │
│  Worker pool channels:         ~100MB                       │
│  Write buffers (4 writers):    ~200MB                       │
│  Safety margin:                ~900MB                       │
└─────────────────────────────────────────────────────────────┘
```

### Architecture Overview

```
                    ┌─────────────────────────────────────┐
                    │         WriterManager               │
                    │                                     │
                    │  datafileID: int32                  │
                    │  flushThreshold: 5000               │
                    │                                     │
                    │  ┌─────────┐ ┌─────────┐            │
                    │  │T1 Writer│ │T2 Writer│            │
                    │  │ buffer  │ │ buffer  │            │
                    │  │  5000   │ │  5000   │            │
                    │  └─────────┘ └─────────┘            │
                    │  ┌─────────┐ ┌───────────┐          │
                    │  │T3 Writer│ │Err Writer │          │
                    │  │ buffer  │ │  buffer   │          │
                    │  │  5000   │ │   5000    │          │
                    │  └─────────┘ └───────────┘          │
                    │                                     │
                    └─────────────────┬───────────────────┘
                                      │
                          Flush when buffer full
                          (acquires conn from pool)
                                      │
                                      ▼
                           ┌───────────────────┐
                           │   pgxpool.Pool    │
                           │   MaxConns: 8-10  │
                           └───────────────────┘
```

### Why COPY Protocol?

PostgreSQL's COPY protocol is 10-100x faster than INSERT for bulk data:

| Method | Throughput | Use Case |
|--------|------------|----------|
| Single INSERT | ~1,000-5,000 rec/sec | Small updates |
| Batched INSERT | ~10,000-50,000 rec/sec | Medium batches |
| **COPY protocol** | ~100,000-500,000 rec/sec | Bulk loading |

For 10 million records:
- Single INSERT: ~30-60 minutes
- COPY: ~20-100 seconds

### TableWriter Implementation (Dynamic)

The TableWriter stores `[]any` row data for flexibility. This allows the WriterManager to create writers dynamically based on the FileSpec without needing compile-time knowledge of record types.

```go
// internal/writer/table_writer.go
package writer

import (
    "context"
    "fmt"

    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

const (
    // DefaultFlushThreshold is the number of records per table before auto-flush.
    // With ~1KB per record, 5000 records = ~5MB per writer.
    DefaultFlushThreshold = 5000

    // MaxFlushThreshold is a hard cap to prevent memory issues.
    MaxFlushThreshold = 10000
)

// TableWriter accumulates row data for a database table and flushes
// using PostgreSQL's COPY protocol.
//
// Memory usage: threshold * avg_row_size (e.g., 5000 * 1KB = 5MB)
type TableWriter struct {
    tableName string
    columns   []string
    rows      [][]any
    threshold int
}

// NewTableWriter creates a writer for the specified table.
// Columns are derived from the schema metadata.
func NewTableWriter(tableName string, columns []string, threshold int) *TableWriter {
    if threshold <= 0 {
        threshold = DefaultFlushThreshold
    }
    if threshold > MaxFlushThreshold {
        threshold = MaxFlushThreshold
    }

    return &TableWriter{
        tableName: tableName,
        columns:   columns,
        rows:      make([][]any, 0, threshold),
        threshold: threshold,
    }
}

// Add appends a row to the buffer.
// Returns true if the flush threshold has been reached.
func (tw *TableWriter) Add(row []any) bool {
    tw.rows = append(tw.rows, row)
    return len(tw.rows) >= tw.threshold
}

// Flush writes all buffered rows to the database via COPY protocol.
// Clears the buffer immediately after copying to release memory.
func (tw *TableWriter) Flush(ctx context.Context, pool *pgxpool.Pool) (int64, error) {
    if len(tw.rows) == 0 {
        return 0, nil
    }

    // Capture rows and clear buffer immediately to release memory
    rows := tw.rows
    tw.rows = make([][]any, 0, tw.threshold)

    count, err := pool.CopyFrom(
        ctx,
        pgx.Identifier{tw.tableName},
        tw.columns,
        pgx.CopyFromRows(rows),
    )

    if err != nil {
        return 0, fmt.Errorf("COPY to %s: %w", tw.tableName, err)
    }

    return count, nil
}

// Pending returns the number of rows waiting to be flushed.
func (tw *TableWriter) Pending() int {
    return len(tw.rows)
}

// TableName returns the table this writer targets.
func (tw *TableWriter) TableName() string {
    return tw.tableName
}
```

### WriterManager Implementation (Dynamic from FileSpec)

The WriterManager creates writers dynamically based on the FileSpec. This allows it to handle any program/section combination without hardcoded record types.

```go
// internal/writer/manager.go
package writer

import (
    "context"
    "fmt"
    "log"

    "github.com/jackc/pgx/v5/pgxpool"

    "go-parser/internal/converter"
    "go-parser/internal/filespec"
    "go-parser/internal/registry"
    "go-parser/internal/worker"
)

// RecordWriter pairs a TableWriter with its converter function.
type RecordWriter struct {
    writer    *TableWriter
    converter converter.RowConverter
}

// WriterManager coordinates writes for any file type.
// Writers are created dynamically based on the FileSpec.
type WriterManager struct {
    pool       *pgxpool.Pool
    datafileID int32

    // Dynamic writers keyed by record type (e.g., "T1", "M2")
    writers     map[string]*RecordWriter
    errorWriter *TableWriter

    // Stats tracking
    totalWritten map[string]int64
    totalErrors  int64
}

// Error table columns (same for all file types)
var parserErrorColumns = []string{
    "row_number", "column_number", "item_number", "field_name",
    "case_number", "rpt_month_year", "error_message", "error_type",
    "created_at", "fields_json", "content_type_id", "file_id",
    "object_id", "deprecated", "values_json",
}

// NewWriterManager creates a manager based on the FileSpec.
// Writers are created only for the record types in this specific file.
func NewWriterManager(
    pool *pgxpool.Pool,
    datafileID int32,
    spec *filespec.FileSpec,
    reg *registry.Registry,
) *WriterManager {
    wm := &WriterManager{
        pool:         pool,
        datafileID:   datafileID,
        writers:      make(map[string]*RecordWriter),
        totalWritten: make(map[string]int64),
    }

    // Create a writer for each data record type in the FileSpec
    for _, schemaPath := range spec.Schemas {
        schema := reg.GetSchema(schemaPath)

        // Skip header/trailer - they don't get written to database
        if schema.RecordType == "HEADER" || schema.RecordType == "TRAILER" {
            continue
        }

        // Get metadata (table name, columns derived from schema)
        meta := reg.GetSchemaMetadata(schemaPath)
        if meta == nil {
            continue
        }

        // Get the converter for this record type
        conv := converter.GetConverter(schema.RecordType)
        if conv == nil {
            log.Printf("Warning: no converter for record type %s", schema.RecordType)
            continue
        }

        wm.writers[schema.RecordType] = &RecordWriter{
            writer:    NewTableWriter(meta.TableName, meta.Columns, DefaultFlushThreshold),
            converter: conv,
        }

        log.Printf("Created writer for %s -> %s (%d columns)",
            schema.RecordType, meta.TableName, len(meta.Columns))
    }

    // Error writer is always the same
    wm.errorWriter = NewTableWriter("parser_error", parserErrorColumns, DefaultFlushThreshold)

    return wm
}

// WriteBatch processes all records from a ParsedBatch.
// Records are converted and routed to the appropriate writer.
func (wm *WriterManager) WriteBatch(ctx context.Context, batch *worker.ParsedBatch) error {
    for _, group := range batch.Groups {
        // Write successful records
        for _, record := range group.Records {
            if err := wm.writeRecord(ctx, record); err != nil {
                return err
            }
        }

        // Write parser errors
        for _, perr := range group.Errors {
            if err := wm.writeError(ctx, perr); err != nil {
                return err
            }
        }
    }

    return nil
}

// writeRecord converts and writes a single record.
func (wm *WriterManager) writeRecord(ctx context.Context, record *worker.ParsedRecord) error {
    rw, ok := wm.writers[record.Schema.RecordType]
    if !ok {
        return fmt.Errorf("no writer for record type: %s", record.Schema.RecordType)
    }

    // Convert ParsedRecord to row values using the registered converter
    // The converter uses SQLC types internally for type safety
    row := rw.converter(record, wm.datafileID)

    // Add to buffer; flush if threshold reached
    if rw.writer.Add(row) {
        count, err := rw.writer.Flush(ctx, wm.pool)
        if err != nil {
            return err
        }
        wm.totalWritten[rw.writer.TableName()] += count
        log.Printf("Flushed %d %s records", count, record.Schema.RecordType)
    }

    return nil
}

// writeError writes a parser error.
func (wm *WriterManager) writeError(ctx context.Context, perr worker.ParseError) error {
    row := converter.ToParserErrorRow(perr, wm.datafileID)

    if wm.errorWriter.Add(row) {
        count, err := wm.errorWriter.Flush(ctx, wm.pool)
        if err != nil {
            return err
        }
        wm.totalErrors += count
        log.Printf("Flushed %d errors", count)
    }

    return nil
}

// FlushAll flushes all writers. Call this at the end of file processing.
func (wm *WriterManager) FlushAll(ctx context.Context) error {
    // Flush all record writers
    for recordType, rw := range wm.writers {
        count, err := rw.writer.Flush(ctx, wm.pool)
        if err != nil {
            return fmt.Errorf("final flush %s: %w", recordType, err)
        }
        wm.totalWritten[rw.writer.TableName()] += count
        if count > 0 {
            log.Printf("Final flush: %d %s records", count, recordType)
        }
    }

    // Flush error writer
    count, err := wm.errorWriter.Flush(ctx, wm.pool)
    if err != nil {
        return fmt.Errorf("final flush errors: %w", err)
    }
    wm.totalErrors += count
    if count > 0 {
        log.Printf("Final flush: %d errors", count)
    }

    return nil
}

// Stats returns the total records written per table.
func (wm *WriterManager) Stats() (records map[string]int64, errors int64) {
    // Return a copy to prevent modification
    result := make(map[string]int64)
    for k, v := range wm.totalWritten {
        result[k] = v
    }
    return result, wm.totalErrors
}

// Pending returns the total number of unflushed records across all writers.
func (wm *WriterManager) Pending() int {
    total := wm.errorWriter.Pending()
    for _, rw := range wm.writers {
        total += rw.writer.Pending()
    }
    return total
}
```

### Connection Pool Configuration

```go
// internal/db/pool.go
package db

import (
    "context"
    "time"

    "github.com/jackc/pgx/v5/pgxpool"
)

// NewPool creates a connection pool optimized for write-heavy workloads.
func NewPool(ctx context.Context, connString string) (*pgxpool.Pool, error) {
    config, err := pgxpool.ParseConfig(connString)
    if err != nil {
        return nil, err
    }

    // Connection limits
    // With 4 table writers that may flush concurrently, plus some headroom
    config.MaxConns = 10
    config.MinConns = 2

    // Connection lifecycle
    // Connections are recycled periodically to handle PostgreSQL maintenance
    config.MaxConnLifetime = 30 * time.Minute
    config.MaxConnIdleTime = 5 * time.Minute

    // Health checks
    config.HealthCheckPeriod = 30 * time.Second

    return pgxpool.NewWithConfig(ctx, config)
}
```

### Integration with Result Collector

```go
// collectResults receives parsed batches and writes them to the database.
func collectResults(
    ctx context.Context,
    workerPool *worker.Pool,
    writerMgr *writer.WriterManager,
) error {
    for batch := range workerPool.Results() {
        if err := writerMgr.WriteBatch(ctx, batch); err != nil {
            return fmt.Errorf("writing batch %d: %w", batch.BatchID, err)
        }
    }

    // Flush any remaining records
    if err := writerMgr.FlushAll(ctx); err != nil {
        return fmt.Errorf("final flush: %w", err)
    }

    // Log final stats
    records, errors := writerMgr.Stats()
    for table, count := range records {
        log.Printf("Written to %s: %d records", table, count)
    }
    log.Printf("Total errors: %d", errors)

    return nil
}

// Example usage - the WriterManager is created dynamically from the FileSpec
func processFile(
    ctx context.Context,
    pool *pgxpool.Pool,
    reg *registry.Registry,
    program string,
    section int,
    datafileID int32,
) error {
    // Get the FileSpec for this program/section
    spec := reg.GetFileSpec(program, section)
    if spec == nil {
        return fmt.Errorf("no FileSpec for %s section %d", program, section)
    }

    // Create WriterManager dynamically based on the FileSpec
    // This works for ANY program/section - TANF, SSP, Tribal, etc.
    writerMgr := writer.NewWriterManager(pool, datafileID, spec, reg)

    // ... set up worker pool and process file ...

    return collectResults(ctx, workerPool, writerMgr)
}
```

### Expected Performance

With this architecture and COPY protocol:

| File Size | Records | Expected Time | Memory Usage |
|-----------|---------|---------------|--------------|
| Small | 10,000 | < 1 second | ~100MB |
| Medium | 100,000 | ~2-5 seconds | ~200MB |
| Large | 1,000,000 | ~20-60 seconds | ~500MB |
| Very Large | 10,000,000 | ~3-10 minutes | ~1GB |

Memory stays bounded because:
- Each writer flushes at 5,000 records (~5MB)
- 4 writers × 5MB = 20MB for write buffers
- Accumulator is the main memory consumer (case groups)

---

## Complete Data Flow

### Main Processing Function

```go
// cmd/parser/main.go
package main

import (
    "context"
    "fmt"
    "log"
    "os"

    "github.com/jackc/pgx/v5/pgxpool"

    "go-parser/internal/decoder"
    "go-parser/internal/filespec"
    "go-parser/internal/parser"
    "go-parser/internal/processor"
    "go-parser/internal/registry"
    "go-parser/internal/worker"
    "go-parser/internal/writer"
)

func main() {
    ctx := context.Background()

    // Connect to database
    pool, err := pgxpool.New(ctx, os.Getenv("DATABASE_URL"))
    if err != nil {
        log.Fatalf("Failed to connect to database: %v", err)
    }
    defer pool.Close()

    // Load configuration
    reg, err := registry.Load("config")
    if err != nil {
        log.Fatalf("Failed to load configuration: %v", err)
    }

    // Get file parameters (in real code, these come from the job queue)
    program := "TANF"
    section := 1
    filePath := os.Args[1]
    datafileID := int32(123) // From database

    // Process the file
    if err := processFile(ctx, pool, reg, program, section, filePath, datafileID); err != nil {
        log.Fatalf("Failed to process file: %v", err)
    }

    log.Println("File processed successfully")
}

func processFile(
    ctx context.Context,
    pool *pgxpool.Pool,
    reg *registry.Registry,
    program string,
    section int,
    filePath string,
    datafileID int32,
) error {
    // Step 1: Get the file specification
    spec := reg.GetFileSpec(program, section)
    if spec == nil {
        return fmt.Errorf("no file spec for %s section %d", program, section)
    }

    log.Printf("Processing %s Section %d file: %s", program, section, filePath)
    log.Printf("Format: %s, KeyFields: %v, BatchSize: %d",
        spec.Format, spec.Accumulator.HasKeyFields(), spec.Accumulator.BatchSize)

    // Step 2: Open the file and create decoder
    file, err := os.Open(filePath)
    if err != nil {
        return fmt.Errorf("failed to open file: %w", err)
    }
    defer file.Close()

    dec, err := createDecoder(file, spec)
    if err != nil {
        return fmt.Errorf("failed to create decoder: %w", err)
    }
    defer dec.Close()

    // Step 3: Create record type detector
    detector := parser.NewRecordTypeDetector(spec, reg)

    // Step 4: Create worker pool
    poolConfig := worker.DefaultPoolConfig()
    workerPool := worker.NewPool(spec.Format, poolConfig)
    workerPool.Start(ctx)

    // Step 5: Create database writer (dynamically from FileSpec)
    writerMgr := writer.NewWriterManager(pool, datafileID, spec, reg)

    // Step 6: Start result collector
    var collectorErr error
    var wg sync.WaitGroup
    wg.Add(1)
    go func() {
        defer wg.Done()
        collectorErr = collectResults(ctx, workerPool, writerMgr)
    }()

    // Step 7: Process rows through the unified Accumulator
    err = processRows(dec, spec, detector, workerPool)

    if err != nil {
        workerPool.CloseInputs()
        workerPool.Wait()
        return err
    }

    // Step 8: Wait for everything to complete
    workerPool.CloseInputs()
    workerPool.Wait()
    wg.Wait()

    if collectorErr != nil {
        return collectorErr
    }

    return nil
}

func createDecoder(file *os.File, spec *filespec.FileSpec) (decoder.Decoder, error) {
    switch spec.Format {
    case filespec.FormatPositional:
        return decoder.NewUTF8Decoder(file), nil
    case filespec.FormatColumnar:
        // Determine if CSV or XLSX based on file extension
        // For now, assume CSV
        recordType := spec.RecordTypeDetection.Schema // Fixed schema for FRA
        return decoder.NewCSVDecoder(file, recordType), nil
    default:
        return nil, fmt.Errorf("unknown format: %s", spec.Format)
    }
}

// processRows uses the unified Accumulator to process all rows.
// The Accumulator handles all four modes (keyed, batched, both, neither)
// based on the AccumulatorConfig in the FileSpec.
func processRows(
    dec decoder.Decoder,
    spec *filespec.FileSpec,
    detector *parser.RecordTypeDetector,
    pool *worker.Pool,
) error {
    acc := processor.NewAccumulator(spec, detector)

    for row, err := range dec.Rows() {
        if err != nil {
            return err
        }

        batch, sch, isAccumulated, err := acc.Add(row)
        if err != nil {
            log.Printf("Line %d: %v", row.LineNum(), err)
            continue
        }

        // Non-accumulated rows (HEADER, TRAILER) could be processed here
        if !isAccumulated && sch != nil {
            log.Printf("Line %d: %s (not accumulated)", row.LineNum(), sch.RecordType)
        }

        // For non-keyed modes, batches may be returned during iteration
        if batch != nil {
            pool.Submit(batch)
        }
    }

    // Dispatch all remaining batches (for keyed modes, this is where groups are emitted)
    for _, batch := range acc.Drain() {
        pool.Submit(batch)
    }

    return nil
}

// collectResults receives parsed batches from the worker pool and writes to database.
func collectResults(
    ctx context.Context,
    pool *worker.Pool,
    writerMgr *writer.WriterManager,
) error {
    for pb := range pool.Results() {
        // Log any parsing errors
        for _, group := range pb.Groups {
            for _, e := range group.Errors {
                log.Printf("Parse error at line %d (%s): %s",
                    e.LineNumber, e.RecordType, e.Message)
            }
        }

        // Write the batch to the database
        if err := writerMgr.WriteBatch(ctx, pb); err != nil {
            log.Printf("Failed to write batch %d: %v", pb.BatchID, err)
        }
    }

    // Flush remaining records and report stats
    if err := writerMgr.FlushAll(ctx); err != nil {
        return fmt.Errorf("final flush: %w", err)
    }

    records, errors := writerMgr.Stats()
    for table, count := range records {
        log.Printf("Written to %s: %d records", table, count)
    }
    log.Printf("Total errors: %d", errors)

    return nil
}
```

---

## Code Structure

### Recommended Directory Layout

```
go-parser/
├── cmd/
│   └── parser/
│       └── main.go                 # Entry point
│
├── config/
│   ├── filespecs/                  # File specifications
│   │   ├── tanf_section1.yaml
│   │   ├── tanf_section2.yaml
│   │   ├── tanf_section3.yaml
│   │   ├── tanf_section4.yaml
│   │   ├── ssp_section1.yaml
│   │   ├── ssp_section2.yaml
│   │   ├── ssp_section3.yaml
│   │   ├── ssp_section4.yaml
│   │   ├── tribal_section1.yaml
│   │   ├── tribal_section2.yaml
│   │   ├── tribal_section3.yaml
│   │   ├── tribal_section4.yaml
│   │   └── fra_section1.yaml
│   │
│   └── schemas/                    # Record schemas
│       ├── common/
│       │   ├── header.yaml
│       │   └── trailer.yaml
│       ├── tanf/
│       │   ├── t1.yaml
│       │   ├── t2.yaml
│       │   ├── t3.yaml
│       │   ├── t4.yaml
│       │   ├── t5.yaml
│       │   ├── t6.yaml
│       │   └── t7.yaml
│       ├── ssp/
│       │   ├── m1.yaml
│       │   ├── m2.yaml
│       │   ├── m3.yaml
│       │   ├── m4.yaml
│       │   ├── m5.yaml
│       │   ├── m6.yaml
│       │   └── m7.yaml
│       ├── tribal/
│       │   ├── t1.yaml
│       │   ├── t2.yaml
│       │   ├── t3.yaml
│       │   ├── t4.yaml
│       │   ├── t5.yaml
│       │   ├── t6.yaml
│       │   └── t7.yaml
│       └── fra/
│           └── te1.yaml
│
├── internal/
│   ├── converter/                  # SQLC type converters
│   │   ├── helpers.go
│   │   ├── tanf_t1.go
│   │   ├── tanf_t2.go
│   │   └── ...
│   │
│   ├── db/                         # SQLC generated code
│   │   ├── db.go
│   │   ├── models.go
│   │   └── query.sql.go
│   │
│   ├── decoder/                    # File decoders
│   │   ├── decoder.go              # Interface
│   │   ├── row.go                  # Row types
│   │   ├── utf8.go                 # Positional decoder
│   │   ├── csv.go                  # CSV decoder
│   │   └── xlsx.go                 # XLSX decoder
│   │
│   ├── filespec/                   # File specification types
│   │   └── types.go
│   │
│   ├── parser/                     # Parsing logic
│   │   ├── detector.go             # Record type detection
│   │   ├── extractor.go            # Field extraction
│   │   └── transforms.go           # Field transforms
│   │
│   ├── processor/                  # Grouping and batching
│   │   ├── types.go                # WorkUnit types
│   │   ├── accumulator.go          # Case grouping
│   │   └── batcher.go              # Record batching
│   │
│   ├── registry/                   # Configuration loading
│   │   └── registry.go
│   │
│   ├── schema/                     # Schema types
│   │   └── types.go
│   │
│   ├── worker/                     # Worker pool
│   │   └── pool.go
│   │
│   └── writer/                     # Database writer
│       └── writer.go
│
├── docs/
│   └── PARSER_ARCHITECTURE.md      # This document
│
├── go.mod
├── go.sum
├── sqlc.yaml
├── schema.sql
└── query.sql
```

---

## Implementation Examples

### Example 1: Processing a TANF Section 1 File (Key-based Grouping)

**Input file (`tanf_s1.txt`):**
```
HEADER20204A06   TAN1ED
T12020101111111111223003403361110212120000300000000000008730010000000000000000000000000000000000222222000000002229012
T2202010111111111121219740114WTTTTTY@W2221222222221012212110014722011500000000...
T320201011111111112120190127WTTTT90W022212222204398100000000
T12020101111111111524503401311110232110374300000000000005450320000000000000000000000000000000000222222000000002229021
T2202010111111111152219730113WTTTT@#Z@2221222122211012210110630023080700000000...
T320201011111111115120160401WTTTT@BTB22212212204398100000000
TRAILER0002643
```

**Accumulator config:** `key_fields` set, `batch_size` = 0

**Processing flow:**

1. **Load FileSpec**: `tanf_section1.yaml` - format=positional, key_fields configured
2. **Create UTF-8 Decoder**: Reads lines, produces PositionalRow objects
3. **For each row**:
   - Detector identifies record type by prefix (HEADER, T1, T2, T3, TRAILER)
   - Accumulator extracts case key (e.g., `202010|11111111112`)
   - Rows added to corresponding RecordGroup (HEADER/TRAILER skipped)
4. **After all rows read** (Drain):
   - RecordGroup 1: `202010|11111111112` with T1, T2, T3
   - RecordGroup 2: `202010|11111111115` with T1, T2, T3
   - Each group becomes its own Batch (batch_size=0)
5. **Worker pool processes each Batch**:
   - Each Batch has 1 RecordGroup (a case)
   - Extractor reads fields by byte position
   - ParsedRecords created for each row
6. **Converter transforms to SQLC types**
7. **Writer inserts into database**

### Example 2: Processing an FRA CSV File (Batching Only)

**Input file (`fra_exiters.csv`):**
```csv
TE1,202010,11111111111,01,1,19740114,123456789,...
TE1,202010,22222222222,01,1,19850623,234567890,...
TE1,202010,33333333333,01,2,19900101,345678901,...
```

**Accumulator config:** `key_fields` empty, `batch_size` = 100

**Processing flow:**

1. **Load FileSpec**: `fra_section1.yaml` - format=columnar, batch_size=100
2. **Create CSV Decoder**: Reads CSV rows, produces ColumnarRow objects
3. **For each row**:
   - Detector returns fixed schema (TE1) since method=fixed
   - Accumulator creates single-record RecordGroup (no key_fields)
   - Adds group to pending batch
   - When 100 groups accumulated, Batch is returned and dispatched
4. **After all rows read** (Drain):
   - Remaining partial batch dispatched
5. **Worker pool processes each Batch**:
   - Each Batch has N RecordGroups, each with 1 record
   - Extractor reads fields by column index
   - ParsedRecords created for each row
6. **Converter transforms to SQLC types**
7. **Writer inserts into database**

### Example 3: High-Performance TANF (Key-based + Batching)

**Accumulator config:** `key_fields` set, `batch_size` = 10

**Processing flow:**

1. Same as Example 1 for steps 1-4
2. **After all rows read** (Drain):
   - RecordGroups batched in groups of 10
   - Batch 1: Groups for cases 1-10
   - Batch 2: Groups for cases 11-20, etc.
3. **Worker pool processes each Batch**:
   - Each Batch has up to 10 RecordGroups (cases)
   - More efficient than individual case dispatch

---

## Summary

This architecture provides:

| Feature | Implementation |
|---------|---------------|
| **Multi-format support** | Separate decoders (UTF-8, CSV, XLSX) producing format-specific Row types |
| **Declarative configuration** | YAML FileSpecs and Schemas loaded at startup |
| **Explicit record type detection** | Prefix-based for positional, column-based or fixed for columnar |
| **Unified Accumulator** | Single component handles all grouping/batching via `key_fields` and `batch_size` |
| **Flexible grouping modes** | Four modes: per-record, batch-only, key-only, key+batch |
| **Parallel processing** | Worker pool with single Batch channel, configurable goroutines |
| **Database integration** | Converters transform parsed records to SQLC types |
| **Extensibility** | Add new programs/formats by adding YAML config files |

The key insight is that **configuration drives behavior**. The AccumulatorConfig tells the parser:
- `key_fields`: How to group records (empty = no grouping)
- `batch_size`: How many groups per batch (0 = one batch per group)

This allows the same parsing code to handle very different file types with no code changes.
