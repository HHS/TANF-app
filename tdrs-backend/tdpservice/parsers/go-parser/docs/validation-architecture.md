f# Go Validation Architecture Design

## Overview

This document describes a clean, modular validation architecture for the TANF Go parser. The design addresses the shortcomings of the existing Python implementation by providing:

- **Clear separation of concerns** between parsing, validation, and error generation
- **Hierarchical validation** with configurable short-circuit behavior
- **Parallel processing** at record and group levels
- **Configuration-driven validators** with extensible error message templates
- **First-class category support** making it trivial to add new validation stages

---

## 1. High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CONFIGURATION LAYER                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│   │  Schema YAML    │    │  FileSpec YAML  │    │ Validation YAML │            │
│   │  (field defs)   │    │  (accumulator)  │    │ (rules+messages)│            │
│   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘            │
│            │                      │                      │                      │
│            └──────────────────────┴──────────────────────┘                      │
│                                   │                                             │
│                                   ▼                                             │
│                      ┌────────────────────────┐                                 │
│                      │    Config Loader       │                                 │
│                      │  (internal/config)     │                                 │
│                      └────────────┬───────────┘                                 │
│                                   │                                             │
└───────────────────────────────────┼─────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               REGISTRY LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐    │
│   │  Schema Registry    │  │ Validator Registry  │  │  Message Registry   │    │
│   │  (compiled schemas) │  │ (validator impls)   │  │ (error templates)   │    │
│   └─────────┬───────────┘  └─────────┬───────────┘  └─────────┬───────────┘    │
│             │                        │                        │                 │
│             └────────────────────────┴────────────────────────┘                 │
│                                      │                                          │
└──────────────────────────────────────┼──────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               PIPELINE LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────────┐   ┌───────────────────────────┐│
│  │  File    │──▶│ Decoder  │──▶│  Accumulator │──▶│    Validation Pipeline    ││
│  │  Input   │   │ (rows)   │   │  (groups)    │   │                           ││
│  └──────────┘   └──────────┘   └──────────────┘   │  ┌─────────────────────┐  ││
│                                                    │  │ Category Orchestrator│  ││
│                                                    │  │ (ordering, routing)  │  ││
│                                                    │  └──────────┬──────────┘  ││
│                                                    │             │             ││
│                                                    │             ▼             ││
│                                                    │  ┌─────────────────────┐  ││
│                                                    │  │  Category Engine    │  ││
│                                                    │  │  (per-category exec)│  ││
│                                                    │  └──────────┬──────────┘  ││
│                                                    │             │             ││
│                                                    │             ▼             ││
│                                                    │  ┌─────────────────────┐  ││
│                                                    │  │  Error Engine       │  ││
│                                                    │  │  (message+context)  │  ││
│                                                    │  └─────────────────────┘  ││
│                                                    └───────────────────────────┘│
│                                                                                  │
└──────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               OUTPUT LAYER                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│   │  Record Writer  │    │  Error Writer   │    │  Stats/Metrics  │            │
│   │  (valid recs)   │    │  (ParserError)  │    │  (observability)│            │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘            │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Detailed Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           VALIDATION PIPELINE (internal/validation)                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌────────────────────────────────────────────────────────────────────────────────┐ │
│  │                         Category Orchestrator                                   │ │
│  │  ┌──────────────────────────────────────────────────────────────────────────┐  │ │
│  │  │  Responsibilities:                                                        │  │ │
│  │  │  • Defines category execution order (configurable)                        │  │ │
│  │  │  • Routes batches to appropriate category engines                         │  │ │
│  │  │  • Implements short-circuit logic between categories                      │  │ │
│  │  │  • Collects and aggregates results from all categories                    │  │ │
│  │  └──────────────────────────────────────────────────────────────────────────┘  │ │
│  │                                                                                 │ │
│  │  ┌─────────────┐                                                               │ │
│  │  │ Config:     │  execution_order: [4, 1, 2, 3]  # Cat4 first for grouping    │ │
│  │  │ (YAML)      │  short_circuit:                                               │ │
│  │  │             │    - on_fail: 1                                               │ │
│  │  │             │      skip: [2, 3]                                             │ │
│  │  │             │    - on_fail: 4                                               │ │
│  │  │             │      skip: [2, 3]                                             │ │
│  │  │             │      reject_group: true                                       │ │
│  │  └─────────────┘                                                               │ │
│  └───────────────────────────────────────────────────────────────────────────────-┘ │
│                                         │                                           │
│            ┌────────────────────────────┼────────────────────────────┐              │
│            │                            │                            │              │
│            ▼                            ▼                            ▼              │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐         │
│  │  Category 1 Engine  │  │  Category 2 Engine  │  │  Category 3 Engine  │         │
│  │  (PreParsing)       │  │  (Field-Level)      │  │  (Cross-Field)      │         │
│  ├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤         │
│  │ Scope: Raw Row      │  │ Scope: Field        │  │ Scope: Record       │         │
│  │ Input: RawLine      │  │ Input: FieldValue   │  │ Input: ParsedRecord │         │
│  │ Parallel: per-row   │  │ Parallel: per-field │  │ Parallel: per-rec   │         │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘         │
│                                                                                      │
│            ┌─────────────────────┐  ┌─────────────────────┐                         │
│            │  Category 4 Engine  │  │  Category N Engine  │                         │
│            │  (Group-Level)      │  │  (Future Extension) │                         │
│            ├─────────────────────┤  ├─────────────────────┤                         │
│            │ Scope: RecordGroup  │  │ Scope: Configurable │                         │
│            │ Input: []ParsedRec  │  │ Input: Any          │                         │
│            │ Parallel: per-group │  │ Parallel: per-scope │                         │
│            └─────────────────────┘  └─────────────────────┘                         │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Concurrency Model

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              PARALLEL PROCESSING MODEL                               │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  File Input                                                                          │
│      │                                                                               │
│      ▼                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                        Accumulator (Grouping)                                │    │
│  │  Groups records by key_fields (RPT_MONTH_YEAR + CASE_NUMBER)                │    │
│  │  Emits RecordGroups when group boundary detected or batch_size reached      │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│      │                                                                               │
│      │ RecordGroup (batch of groups)                                                │
│      ▼                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                     Validation Worker Pool                                   │    │
│  │  ┌─────────────────────────────────────────────────────────────────────┐    │    │
│  │  │                        Work Queue (channel)                          │    │    │
│  │  │  [Group1] [Group2] [Group3] [Group4] [Group5] ...                   │    │    │
│  │  └─────────────────────────────────────────────────────────────────────┘    │    │
│  │                                                                              │    │
│  │        ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐              │    │
│  │        │ Worker 1 │  │ Worker 2 │  │ Worker 3 │  │ Worker N │              │    │
│  │        │          │  │          │  │          │  │          │              │    │
│  │        │ Process  │  │ Process  │  │ Process  │  │ Process  │              │    │
│  │        │ Group    │  │ Group    │  │ Group    │  │ Group    │              │    │
│  │        └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘              │    │
│  │             │             │             │             │                     │    │
│  │             └─────────────┴─────────────┴─────────────┘                     │    │
│  │                                   │                                         │    │
│  │                                   ▼                                         │    │
│  │  ┌─────────────────────────────────────────────────────────────────────┐   │    │
│  │  │                      Result Queue (channel)                          │   │    │
│  │  │  [Result1] [Result2] [Result3] [Result4] [Result5] ...              │   │    │
│  │  └─────────────────────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│      │                                                                               │
│      ▼                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                          Result Aggregator                                   │    │
│  │  • Collects validation results from workers                                 │    │
│  │  • Routes valid records to Record Writer                                    │    │
│  │  • Routes errors to Error Writer                                            │    │
│  │  • Maintains deterministic error ordering (sort by line number)             │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────────────┐
│                     WITHIN-GROUP VALIDATION (per worker)                             │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  RecordGroup {Key: "202001-CASE123", Records: [R1, R2, R3, ...]}                    │
│      │                                                                               │
│      ▼                                                                               │
│  ┌──────────────────────────────────────────────────┐                               │
│  │  Category 4 Validation (Group-Level)             │                               │
│  │  • T1 has matching T2/T3 records?                │                               │
│  │  • T4 has matching T5 records?                   │                               │
│  │  • Family affiliation rules                      │                               │
│  └──────────────────────────────────────────────────┘                               │
│      │                                                                               │
│      │ If Cat4 fails → Mark group rejected, skip Cat 1/2/3 for all records         │
│      │ If Cat4 passes → Continue to per-record validation                           │
│      ▼                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────────────┐   │
│  │  Per-Record Validation Loop                                                   │   │
│  │                                                                               │   │
│  │  for each record in group {                                                   │   │
│  │      ┌─────────────────────────────────────────────────────────────────┐     │   │
│  │      │  Category 1 (Pre-Parsing)                                        │     │   │
│  │      │  • Record length check                                           │     │   │
│  │      │  • Required fields present                                       │     │   │
│  │      │  • Format consistency                                            │     │   │
│  │      └─────────────────────────────────────────────────────────────────┘     │   │
│  │          │                                                                    │   │
│  │          │ If Cat1 fails → Mark record rejected, skip Cat 2/3                │   │
│  │          │ If Cat1 passes → Continue                                         │   │
│  │          ▼                                                                    │   │
│  │      ┌─────────────────────────────────────────────────────────────────┐     │   │
│  │      │  Category 2 (Field-Level) - PARALLEL per field                   │     │   │
│  │      │                                                                  │     │   │
│  │      │   Field1 ─┬─▶ [v1, v2] ──▶ Results                              │     │   │
│  │      │   Field2 ─┤                                                      │     │   │
│  │      │   Field3 ─┤   (parallel)                                         │     │   │
│  │      │   ...     ─┘                                                      │     │   │
│  │      └─────────────────────────────────────────────────────────────────┘     │   │
│  │          │                                                                    │   │
│  │          │ Collect field errors                                              │   │
│  │          ▼                                                                    │   │
│  │      ┌─────────────────────────────────────────────────────────────────┐     │   │
│  │      │  Category 3 (Cross-Field)                                        │     │   │
│  │      │  • Conditional rules (if A then B)                               │     │   │
│  │      │  • Aggregate checks (sum > threshold)                            │     │   │
│  │      └─────────────────────────────────────────────────────────────────┘     │   │
│  │          │                                                                    │   │
│  │          ▼                                                                    │   │
│  │      Aggregate record results                                                 │   │
│  │  }                                                                            │   │
│  └──────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow With Short-Circuit Behavior

### 4.1 Overall Flow

```
Raw File Bytes
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. DECODE: File → Rows                                         │
│     • Positional, CSV, or XLSX decoding                         │
│     • Each row tagged with line number                          │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. DETECT: Row → RawLine (row + schema)                        │
│     • Record type detection (prefix/column/fixed)               │
│     • Schema assignment                                         │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. ACCUMULATE: RawLines → RecordGroups                         │
│     • Group by key_fields (RPT_MONTH_YEAR + CASE_NUMBER)        │
│     • Batch groups for efficient parallel processing            │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. PARSE: RawLine → ParsedRecord                               │
│     • Extract field values from raw row                         │
│     • Apply transforms (trim, decrypt, etc.)                    │
│     • Store in ParsedRecord.Fields[]                            │
└─────────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. VALIDATE: ParsedRecords → ValidationResults                 │
│                                                                  │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │  CATEGORY 4 (Group-Level) - FIRST                       │ │
│     │  • Validates relationships between records in group     │ │
│     │  • T1 ↔ T2/T3 matching, T4 ↔ T5 matching               │ │
│     │  • If FAIL: reject entire group, skip Cat 1/2/3        │ │
│     └─────────────────────────────────────────────────────────┘ │
│         │                                                        │
│         │ Per-record loop (if Cat4 passed):                     │
│         ▼                                                        │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │  CATEGORY 1 (Pre-Parsing)                               │ │
│     │  • Record length, format checks                         │ │
│     │  • If FAIL: reject record, skip Cat 2/3                 │ │
│     └─────────────────────────────────────────────────────────┘ │
│         │                                                        │
│         ▼                                                        │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │  CATEGORY 2 (Field-Level)                               │ │
│     │  • Type checks, ranges, allowed values                  │ │
│     │  • Runs for all fields, collects all errors             │ │
│     └─────────────────────────────────────────────────────────┘ │
│         │                                                        │
│         ▼                                                        │
│     ┌─────────────────────────────────────────────────────────┐ │
│     │  CATEGORY 3 (Cross-Field)                               │ │
│     │  • Conditional rules between fields                     │ │
│     │  • Aggregate calculations                               │ │
│     └─────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
    │
    ├──────────────────────────────────────┐
    │                                      │
    ▼                                      ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│  6A. Valid Records      │    │  6B. Validation Errors  │
│  • Convert to DB rows   │    │  • Generate ParserError │
│  • Buffer and COPY      │    │  • Write to error table │
└─────────────────────────┘    └─────────────────────────┘
```

### 4.2 Short-Circuit Decision Points

| Trigger | Condition | Action |
|---------|-----------|--------|
| Category 4 fails | Group has missing T1↔T2/T3 relationships | Reject entire group, skip Cat 1/2/3 for all records in group |
| Category 1 fails | Record length wrong, required field missing | Reject record, skip Cat 2/3 for that record |
| Category 2 fails | Field validation error | Record errors, continue to Cat 3 (configurable) |
| Category 3 fails | Cross-field rule violated | Record errors, mark record invalid |

### 4.3 Configurable Short-Circuit Rules

```yaml
# config/validation/orchestrator.yaml
execution_order:
  - category: 4    # Group-level first
    scope: group
  - category: 1    # Then per-record pre-parsing
    scope: record
  - category: 2    # Then field-level
    scope: field
  - category: 3    # Then cross-field
    scope: record

short_circuit_rules:
  - on_category_fail: 4
    action: reject_group
    skip_categories: [1, 2, 3]

  - on_category_fail: 1
    action: reject_record
    skip_categories: [2, 3]

  - on_category_fail: 2
    action: continue  # or "reject_record" if strict mode
    skip_categories: []
```

---

## 5. Error Generation Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              ERROR GENERATION SYSTEM                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  Validation Failure                                                                  │
│      │                                                                               │
│      ▼                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  ValidationResult                                                            │    │
│  │  {                                                                           │    │
│  │      Valid: false,                                                           │    │
│  │      ValidatorID: "isInRange",                                              │    │
│  │      Category: 2,                                                            │    │
│  │      FieldName: "FUNDING_STREAM",                                           │    │
│  │      FieldValue: "5",                                                        │    │
│  │      RuleConfig: {min: 1, max: 2},                                          │    │
│  │  }                                                                           │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│      │                                                                               │
│      ▼                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  Error Engine                                                                │    │
│  │                                                                              │    │
│  │  1. Look up message template by (ValidatorID, Category)                     │    │
│  │     Template: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}):       │    │
│  │                {{.Value}} is not between {{.Min}} and {{.Max}}."            │    │
│  │                                                                              │    │
│  │  2. Build template context from:                                            │    │
│  │     • ValidationResult                                                       │    │
│  │     • FieldMetadata (from schema)                                           │    │
│  │     • RecordMetadata (line number, record type)                             │    │
│  │     • GroupMetadata (case number, RPT_MONTH_YEAR)                           │    │
│  │                                                                              │    │
│  │  3. Execute template                                                         │    │
│  │     Output: "T1 Item 8 (Funding Stream): 5 is not between 1 and 2."        │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│      │                                                                               │
│      ▼                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │  ParserError                                                                 │    │
│  │  {                                                                           │    │
│  │      RowNumber: 42,                                                          │    │
│  │      ColumnNumber: "8",                                                      │    │
│  │      ItemNumber: "8",                                                        │    │
│  │      FieldName: "FUNDING_STREAM",                                           │    │
│  │      RptMonthYear: "202001",                                                │    │
│  │      CaseNumber: "CASE12345",                                               │    │
│  │      ErrorMessage: "T1 Item 8 (Funding Stream): 5 is not between 1 and 2.",│    │
│  │      ErrorType: "FIELD_VALUE",                                              │    │
│  │      Category: 2,                                                            │    │
│  │      ValidatorID: "isInRange",                                              │    │
│  │      SchemaPath: "tanf/t1",                                                 │    │
│  │      FieldsJSON: {...},                                                      │    │
│  │      ValuesJSON: {...},                                                      │    │
│  │  }                                                                           │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
│      │                                                                               │
│      ▼                                                                               │
│  Error Writer → PostgreSQL parser_errors table                                      │
│                                                                                      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Package Structure

```
internal/
├── validation/                    # NEW: Validation subsystem
│   ├── orchestrator.go           # Category execution ordering, short-circuit logic
│   ├── orchestrator_test.go
│   ├── engine.go                 # Per-category validation engine
│   ├── engine_test.go
│   ├── result.go                 # ValidationResult, GroupResult types
│   ├── context.go                # ValidationContext passed to validators
│   ├── pool.go                   # Validation worker pool
│   │
│   ├── registry/                 # Validator and message registries
│   │   ├── validators.go         # Validator registration and lookup
│   │   ├── messages.go           # Error message template registry
│   │   └── loader.go             # Load validators from config
│   │
│   ├── validators/               # Built-in validator implementations
│   │   ├── common.go             # Shared validator logic
│   │   ├── comparison.go         # isEqual, isGreaterThan, isBetween, etc.
│   │   ├── string.go             # isEmpty, startsWith, hasLength, etc.
│   │   ├── numeric.go            # isNumber, isInRange, etc.
│   │   ├── date.go               # dateYearIsLargerThan, dateMonthIsValid, etc.
│   │   ├── category1.go          # Pre-parsing validators
│   │   ├── category3.go          # Cross-field validators (ifThenAlso, etc.)
│   │   ├── category4.go          # Group-level validators
│   │   └── validators_test.go
│   │
│   ├── errors/                   # Error generation
│   │   ├── engine.go             # Error message rendering
│   │   ├── templates.go          # Template functions and helpers
│   │   └── types.go              # ParserError type
│   │
│   └── config/                   # Validation config types
│       ├── types.go              # ValidatorConfig, RuleConfig, etc.
│       └── loader.go             # Load validation rules from YAML
│
├── registry/                     # EXISTING: Schema registry (enhanced)
│   ├── registry.go
│   └── validation.go             # NEW: Attach validators to schemas
│
├── pipeline/                     # EXISTING: Enhanced with validation
│   ├── pipeline.go               # Add validation stage
│   └── validation.go             # NEW: Integration point
│
└── writer/                       # EXISTING: Enhanced with error writing
    ├── router.go
    └── error_writer.go           # NEW: Write ParserError records
```

---

## 7. Configuration File Structure

```
config/
├── schemas/                      # EXISTING
│   └── tanf/t1.yaml
│
├── filespecs/                    # EXISTING
│   └── tanf/s1.yaml
│
└── validation/                   # NEW
    ├── orchestrator.yaml         # Category ordering, short-circuit rules
    ├── messages/                 # Error message templates
    │   ├── common.yaml           # Shared templates
    │   ├── category1.yaml        # Cat 1 specific messages
    │   ├── category2.yaml        # Cat 2 specific messages
    │   ├── category3.yaml        # Cat 3 specific messages
    │   └── category4.yaml        # Cat 4 specific messages
    │
    └── rules/                    # Validation rules per schema
        ├── common/
        │   └── header.yaml
        ├── tanf/
        │   ├── t1.yaml           # T1 validation rules
        │   ├── t2.yaml
        │   └── t3.yaml
        └── ssp/
            └── m1.yaml
```

### Example: Validation Rules File

```yaml
# config/validation/rules/tanf/t1.yaml
schema: tanf/t1

category1:  # Pre-parsing validators
  - validator: recordHasLengthBetween
    params:
      min: 117
      max: 156
    message_override: null  # Use default message

  - validator: caseNumberNotEmpty
    params:
      start: 8
      end: 19

category2:  # Field-level validators
  fields:
    RPT_MONTH_YEAR:
      - validator: dateYearIsLargerThan
        params:
          year: 1998
      - validator: dateMonthIsValid

    FUNDING_STREAM:
      - validator: isInRange
        params:
          min: 1
          max: 2
          inclusive: true

    COUNTY_FIPS_CODE:
      - validator: hasLength
        params:
          length: 3
      - validator: isNumeric

category3:  # Cross-field validators
  - validator: ifThenAlso
    params:
      condition_field: CASH_AMOUNT
      condition: isGreaterThan
      condition_value: 0
      result_field: NBR_MONTHS
      result: isGreaterThan
      result_value: 0

  - validator: sumIsGreaterThan
    params:
      fields: [CASH_AMOUNT, CC_AMOUNT, TRANSP_AMOUNT]
      threshold: 0
```

### Example: Error Message Templates

```yaml
# config/validation/messages/category2.yaml
validators:
  isInRange:
    template: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} is not between {{.Min}} and {{.Max}}."

  isOneOf:
    template: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} is not in {{.AllowedValues | formatList}}."

  hasLength:
    template: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): value has length {{.ActualLength}} but must be {{.ExpectedLength}}."

  isNumeric:
    template: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} is not a valid number."

# Schema-specific overrides
overrides:
  tanf/t1:
    FUNDING_STREAM:
      isInRange:
        template: "Funding Stream must be 1 (Federal TANF) or 2 (Separate State Program), but got {{.Value}}."
```

---

## Next: Part 2 - Extensibility Strategy and Go Interfaces
