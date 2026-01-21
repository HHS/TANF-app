# Expression-Based Validation System Design

## Executive Summary

This document proposes migrating the Go parser's validation system from Go-based validator factories to an expression language approach using [expr](https://github.com/expr-lang/expr). This change centralizes all validation logic and error messages into human-readable configuration files, enabling non-technical stakeholders to review and verify validation rules.

**Key expr Documentation Links:**
- [Language Definition](https://expr-lang.org/docs/language-definition) - Operators, literals, built-in functions
- [Configuration](https://expr-lang.org/docs/configuration) - Compilation options (`expr.Env()`, `expr.AsBool()`, etc.)
- [Functions](https://expr-lang.org/docs/functions) - Defining and registering custom functions
- [Go Package Documentation](https://pkg.go.dev/github.com/expr-lang/expr) - API reference

---

## Part 1: Tradeoffs Analysis

### 1.1 Performance Overhead

**Tradeoff**: Expression evaluation (~70ns/op) is 2-3x slower than native Go closures (~20-30ns/op).

**Why it's acceptable**: The Go parser is **IO-bound**, not CPU-bound. Database serialization of validation errors dominates runtime:

| Operation | Time |
|-----------|------|
| Parse 500k records (Go) | ~2 seconds |
| Validation CPU time (50M evals × 70ns) | ~3.5 seconds |
| Database writes (millions of error rows) | **200+ seconds** |

The ~2.5 second difference between expr and native Go represents ~1% of total runtime. **CPU performance is not the bottleneck.**

### 1.2 Memory Overhead

**Tradeoff**: Each compiled expression consumes ~1-5KB as bytecode.

**Why it's acceptable**: With ~100 validator expressions, total memory is ~100-500KB. Compared to:
- Parsed record data in memory: hundreds of MB to GB
- Database connection pools: tens of MB
- Go runtime overhead: tens of MB

Expression memory overhead is **negligible** (<0.1% of application memory).

### 1.3 Runtime vs Compile-Time Errors

**Tradeoff**: Expression syntax errors occur at startup (config load time) rather than Go compile time.

**Why it's acceptable**:
1. Expressions are compiled at application startup, failing fast before processing begins
2. CI/CD pipeline can validate all expressions before deployment
3. Expression syntax is simpler than Go, reducing error likelihood
4. Unit tests can validate all expressions

### 1.4 Learning Curve

**Tradeoff**: Developers must learn expr syntax instead of writing Go.

**Why it's acceptable**:
1. expr syntax is intentionally simple and readable
2. Most expressions are trivial: `value > 0`, `FIELD_A == FIELD_B`
3. Complex logic still uses Go functions exposed to expressions
4. Net reduction in code to maintain (YAML vs Go factories)

### 1.5 Debugging Complexity

**Tradeoff**: Debugging bytecode execution is harder than stepping through Go code.

**Why it's acceptable**:
1. Expressions are simple enough to reason about without debugging
2. Validation logging can capture expression, input values, and result
3. Unit tests can verify expression behavior in isolation
4. The alternative (Go factories) has its own debugging challenges

### 1.6 Expressiveness Limits

**Tradeoff**: Some complex validators may not fit cleanly into expression syntax.

**Why it's acceptable**:
1. Complex logic can be encapsulated in Go functions exposed to expressions
2. Hybrid approach: simple logic as expressions, complex logic as registered functions
3. The expression becomes documentation even when calling Go functions:
   ```yaml
   expr: "hasMatchingChildren(group, 'T1', ['T2', 'T3'])"
   ```

---

## Part 2: Benefits

### 2.1 Stakeholder Visibility

**Primary benefit**: Non-technical stakeholders can review validation logic without reading code.

| Stakeholder | Current State | With Expressions |
|-------------|---------------|------------------|
| Product | Must read Go/Python code | Can read YAML directly |
| Customers | Cannot verify requirements | Can review validation rules |
| UX | Must request message changes | Can edit messages directly |
| QA | Derives tests from code | Tests from same source as impl |
| Compliance | Requires developer translation | Direct audit of rules |

### 2.2 Single Source of Truth

All validation rules and their error messages live in one place:
- No drift between documentation and implementation
- Changes are atomic (rule + message together)
- Version control shows exactly what changed in requirements

### 2.3 Reduced Boilerplate

**Current**: Each validator requires ~20-40 lines of Go code.

**With expressions**: Each validator is 2-4 lines of YAML.

```yaml
# Before: 35 lines of Go
# After: 3 lines of YAML
- id: cash_requires_months
  expr: "CASH_AMOUNT <= 0 or NBR_MONTHS > 0"
  message: "When cash amount is provided, months must be positive"
```

### 2.4 Composition Without Configuration Complexity

Current composition requires nested YAML structures:

```yaml
# Current: Verbose composition
- id: complex_rule
  compose: ifThen
  condition:
    id: isGreaterThan
    params: { value: 0 }
    field: CASH_AMOUNT
  then:
    id: isGreaterThan
    params: { value: 0 }
    field: NBR_MONTHS
```

Expressions make this natural:

```yaml
# With expressions: Natural syntax
- id: complex_rule
  expr: "CASH_AMOUNT <= 0 or NBR_MONTHS > 0"
```

---

## Part 3: Expression Syntax

> **Reference**: See the [expr Language Definition](https://expr-lang.org/docs/language-definition) for complete syntax documentation.

### 3.1 Core Language Features

The [expr language](https://expr-lang.org/docs/language-definition) provides:

| Feature | Example |
|---------|---------|
| Arithmetic | `a + b`, `a * b`, `a / b`, `a % b` |
| Comparison | `a == b`, `a != b`, `a > b`, `a >= b`, `a < b`, `a <= b` |
| Logical | `a and b`, `a or b`, `not a`, `a && b`, `a \|\| b`, `!a` |
| Ternary | `a ? b : c` |
| Nil coalescing | `a ?? b` (returns b if a is nil) |
| Membership | `a in [1, 2, 3]`, `a in ["foo", "bar"]` |
| String ops | `a + b` (concat), `a contains b`, `a startsWith b`, `a endsWith b` |
| Array ops | `len(a)`, `a[0]`, `a[1:3]` |
| Field access | `record.FieldName`, `Fields.CASH_AMOUNT` |

### 3.2 Built-in Functions (from expr)

> **Reference**: See [Built-in Functions](https://expr-lang.org/docs/language-definition#built-in-functions) in the expr documentation.

The following built-in functions are particularly useful for validation. Note that [predicate functions](https://expr-lang.org/docs/language-definition#predicate) use `#` to reference the current element, or `.Field` to access struct/map fields directly.

| Function | Description | Example |
|----------|-------------|---------|
| `len(x)` | Length of string/array | `len(value) >= 5` |
| `all(array, predicate)` | All elements match ([ref](https://expr-lang.org/docs/language-definition#all)) | `all(amounts, {# > 0})` |
| `any(array, predicate)` | Any element matches ([ref](https://expr-lang.org/docs/language-definition#any)) | `any(amounts, {# > 0})` |
| `none(array, predicate)` | No elements match ([ref](https://expr-lang.org/docs/language-definition#none)) | `none(amounts, {# < 0})` |
| `one(array, predicate)` | Exactly one matches ([ref](https://expr-lang.org/docs/language-definition#one)) | `one(flags, {# == 1})` |
| `filter(array, predicate)` | Filter elements ([ref](https://expr-lang.org/docs/language-definition#filter)) | `filter(records, {.Type == "T1"})` |
| `map(array, transform)` | Transform elements ([ref](https://expr-lang.org/docs/language-definition#map)) | `map(records, {.Amount})` |
| `count(array, predicate)` | Count matching ([ref](https://expr-lang.org/docs/language-definition#count)) | `count(records, {.Type == "T2"})` |

### 3.3 Custom Functions (Registered at Startup)

> **Reference**: See [Functions](https://expr-lang.org/docs/functions) for how to define and register custom functions in expr.

These Go functions will be exposed to expressions using the [`expr.Function()` option](https://expr-lang.org/docs/functions#function-option):

#### Date/Time Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `year(v)` | `any -> int` | Extract year from YYYYMM or YYYYMMDD |
| `month(v)` | `any -> int` | Extract month (1-12) |
| `day(v)` | `any -> int` | Extract day (1-31) |
| `quarter(v)` | `any -> int` | Extract quarter (1-4) |
| `isValidDate(v)` | `any -> bool` | Check if date components are valid |
| `isLeapYear(v)` | `any -> bool` | Check if year is leap year |
| `dateInPast(v)` | `any -> bool` | Check if date is before today |
| `dateInFuture(v)` | `any -> bool` | Check if date is after today |

#### String Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `trim(s)` | `string -> string` | Trim whitespace |
| `upper(s)` | `string -> string` | Convert to uppercase |
| `lower(s)` | `string -> string` | Convert to lowercase |
| `matches(s, pattern)` | `string, string -> bool` | Regex match |
| `isNumeric(s)` | `string -> bool` | Contains only digits |
| `isAlpha(s)` | `string -> bool` | Contains only letters |
| `isAlphanumeric(s)` | `string -> bool` | Contains only letters/digits |

#### Type Conversion Functions

| Function | Signature | Description |
|----------|-----------|-------------|
| `str(v)` | `any -> string` | Convert to string |
| `int(v)` | `any -> int` | Convert to integer |
| `float(v)` | `any -> float64` | Convert to float |
| `isEmpty(v)` | `any -> bool` | Check if nil/empty/whitespace |
| `isNotEmpty(v)` | `any -> bool` | Opposite of isEmpty |

#### Group Functions (Category 4)

| Function | Signature | Description |
|----------|-----------|-------------|
| `recordCount(type)` | `string -> int` | Count records of type in group |
| `hasRecordType(type)` | `string -> bool` | Check if type exists in group |
| `recordsOfType(type)` | `string -> []Record` | Get all records of type |
| `sumField(type, field)` | `string, string -> float64` | Sum field across records |
| `uniqueValues(type, field)` | `string, string -> []any` | Distinct values |
| `hasDuplicates(type, field)` | `string, string -> bool` | Check for duplicates |

---

## Part 4: Environment Structure

> **Reference**: The environment is passed to [`expr.Compile()`](https://expr-lang.org/docs/configuration) via the `expr.Env()` option. This provides type information for the expression compiler and defines what variables are available during evaluation. See [Configuration](https://expr-lang.org/docs/configuration) for details.

The environment struct defines what variables and fields are accessible within an expression. When an expression references a variable like `value` or `Fields.CASH_AMOUNT`, expr resolves it against the environment struct passed to `expr.Run()`.

### 4.1 Category 2 Environment (Field Validation)

Available variables when validating a single field:

```go
type Cat2Env struct {
    // The current field's value (primary validation target)
    Value any

    // Access to all fields in the record by name
    // Usage: Fields.CASH_AMOUNT, Fields.CASE_NUMBER
    Fields map[string]any

    // Record metadata
    RecordType   string  // "T1", "T2", etc.
    LineNumber   int     // Source file line number
    RecordLength int     // Length of raw record
}
```

**Example expressions:**

```yaml
# Simple field validation
- expr: "value > 0"
- expr: "value >= 1 and value <= 12"
- expr: "len(str(value)) == 11"
- expr: "value in [1, 2, 3, 4, 5]"
- expr: "isNotEmpty(value)"
- expr: "year(value) > 1998"
- expr: "matches(str(value), '^[A-Z]{2}\\d{4}$')"
```

### 4.2 Category 3 Environment (Cross-Field Validation)

Available variables when validating across fields in a record:

```go
type Cat3Env struct {
    // All fields accessible directly by name
    // Usage: CASH_AMOUNT, NBR_MONTHS, CASE_NUMBER
    // (Promoted to top level for readability)

    // Also available via Fields map
    Fields map[string]any

    // Record metadata
    RecordType   string
    LineNumber   int
    RecordLength int
}
```

**Example expressions:**

```yaml
# Cross-field comparisons
- expr: "CASH_AMOUNT <= 0 or NBR_MONTHS > 0"
- expr: "START_DATE <= END_DATE"
- expr: "FIELD_A == FIELD_B"
- expr: "CASH_AMOUNT + SNAP_AMOUNT + HOUSING_AMOUNT > 0"

# At least one of multiple fields
- expr: "isNotEmpty(FIELD_A) or isNotEmpty(FIELD_B) or isNotEmpty(FIELD_C)"

# All or none pattern
- expr: "(isEmpty(A) and isEmpty(B)) or (isNotEmpty(A) and isNotEmpty(B))"

# Conditional validation
- expr: "STATUS != 1 or REASON_CODE > 0"  # If status is 1, reason required
```

### 4.3 Category 1 Environment (Record Pre-Check)

Available variables for raw record validation:

```go
type Cat1Env struct {
    // Raw record properties
    RecordLength int     // Decoded length of record
    RecordType   string  // Detected record type
    RawRecord    string  // Raw record string (if needed)

    // Quick access to key fields (extracted before full parse)
    CaseNumber string

    // Metadata
    LineNumber int
}
```

**Example expressions:**

```yaml
# Record structure validation
- expr: "RecordLength >= 117 and RecordLength <= 156"
- expr: "RecordType startsWith 'T'"
- expr: "isNotEmpty(trim(CaseNumber))"
```

### 4.4 Category 4 Environment (Group Validation)

Available variables for case/group validation:

```go
type Cat4Env struct {
    // Group properties
    CaseNumber   string
    RecordCount  int              // Total records in group

    // Pre-computed aggregates for performance
    RecordCounts map[string]int   // "T1" -> 2, "T2" -> 5
    HasType      map[string]bool  // "T1" -> true

    // Access to all records (for complex validations)
    Records []RecordEnv

    // Helper: records filtered by type
    // Usage: T1Records, T2Records, T3Records
    T1Records []RecordEnv
    T2Records []RecordEnv
    T3Records []RecordEnv
    // ... etc
}

type RecordEnv struct {
    Type       string
    LineNumber int
    Fields     map[string]any
}
```

**Example expressions:**

```yaml
# Record type presence
- expr: "hasRecordType('T1')"
- expr: "recordCount('T1') >= 1"

# Parent-child relationships
- expr: "recordCount('T1') == 0 or recordCount('T2') + recordCount('T3') > 0"

# Record count ranges
- expr: "recordCount('T2') >= 1 and recordCount('T2') <= 99"

# Complex: T1 must have matching children
- expr: "all(T1Records, { any(T2Records, {.Fields.FAMILY_ID == #.Fields.FAMILY_ID}) })"

# Uniqueness (using helper function)
- expr: "not hasDuplicates('T2', 'SSN')"
```

---

## Part 5: Validator Definition Schema

### 5.1 Core Validator Structure

```yaml
# Single validator definition
- id: string              # Unique identifier (required)
  expr: string            # Expression to evaluate (required)
  message: string         # Error message template (required)
  error_type: string      # Override error type (optional)
  category: int           # 1, 2, 3, or 4 (context-dependent)
  deprecated: bool        # Mark as deprecated (optional)
  fields: [string]        # Fields involved (for error reporting, optional)
```

### 5.2 Complete Validators File

```yaml
# config/validation/validators.yaml

# ═══════════════════════════════════════════════════════════════════════════════
# TANF VALIDATION RULES
#
# This file defines all validation expressions and their error messages.
# It serves as the single source of truth for validation logic.
#
# Stakeholders: Product, Engineering, QA, Compliance
# Last Updated: 2024-XX-XX
# ═══════════════════════════════════════════════════════════════════════════════

# ───────────────────────────────────────────────────────────────────────────────
# CATEGORY 1: Record Pre-Check Validations
# Applied to raw records before field parsing
# ───────────────────────────────────────────────────────────────────────────────

category1:
  - id: record_length_t1
    expr: "RecordLength >= 117 and RecordLength <= 156"
    message: "T1 record length must be between 117 and 156 characters, got {{.RecordLength}}"
    applies_to: [T1]

  - id: record_length_t2
    expr: "RecordLength == 122"
    message: "T2 record length must be exactly 122 characters, got {{.RecordLength}}"
    applies_to: [T2]

  - id: case_number_not_empty
    expr: "isNotEmpty(trim(CaseNumber))"
    message: "Case number cannot be blank"
    applies_to: [T1, T2, T3, T4, T5]

# ───────────────────────────────────────────────────────────────────────────────
# CATEGORY 2: Field Value Validations
# Applied to individual parsed field values
# ───────────────────────────────────────────────────────────────────────────────

category2:
  # ─── Date Validations ───
  - id: year_after_1998
    expr: "year(value) > 1998"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Year must be after 1998, got {{.Value}}"

  - id: valid_month
    expr: "month(value) >= 1 and month(value) <= 12"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Month must be 01-12, got {{.Value}}"

  - id: valid_quarter
    expr: "quarter(value) >= 1 and quarter(value) <= 4"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Quarter must be 1-4, got {{.Value}}"

  # ─── Numeric Validations ───
  - id: not_negative
    expr: "value >= 0"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Must be zero or positive, got {{.Value}}"

  - id: positive_integer
    expr: "value > 0"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Must be positive, got {{.Value}}"

  - id: valid_percentage
    expr: "value >= 0 and value <= 100"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Must be 0-100, got {{.Value}}"

  # ─── String Validations ───
  - id: not_empty
    expr: "isNotEmpty(value)"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Cannot be blank"

  - id: ssn_format
    expr: "matches(str(value), '^\\d{9}$')"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): SSN must be 9 digits"

  # ─── Enumeration Validations ───
  - id: valid_state_code
    expr: "value in ['AL','AK','AZ','AR','CA','CO','CT','DE','FL','GA','HI','ID','IL','IN','IA','KS','KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK','OR','PA','RI','SC','SD','TN','TX','UT','VT','VA','WA','WV','WI','WY','DC','PR','VI','GU']"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Invalid state code '{{.Value}}'"

  - id: valid_gender
    expr: "value in [1, 2, 9]"
    message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Gender must be 1 (male), 2 (female), or 9 (unknown), got {{.Value}}"

# ───────────────────────────────────────────────────────────────────────────────
# CATEGORY 3: Cross-Field Validations
# Applied across multiple fields within a single record
# ───────────────────────────────────────────────────────────────────────────────

category3:
  - id: cash_requires_months
    expr: "CASH_AMOUNT <= 0 or NBR_MONTHS > 0"
    message: "When cash amount (${{.Fields.CASH_AMOUNT}}) is provided, number of months must be positive (got {{.Fields.NBR_MONTHS}})"
    fields: [CASH_AMOUNT, NBR_MONTHS]

  - id: benefits_sum_positive
    expr: "CASH_AMOUNT + SNAP_AMOUNT + CC_AMOUNT + TRANSPORT_AMOUNT + OTHER_AMOUNT > 0"
    message: "At least one benefit amount must be positive"
    fields: [CASH_AMOUNT, SNAP_AMOUNT, CC_AMOUNT, TRANSPORT_AMOUNT, OTHER_AMOUNT]

  - id: start_before_end_date
    expr: "isEmpty(END_DATE) or START_DATE <= END_DATE"
    message: "Start date ({{.Fields.START_DATE}}) must be on or before end date ({{.Fields.END_DATE}})"
    fields: [START_DATE, END_DATE]

  - id: closure_reason_when_closed
    expr: "DISPOSITION != 1 or isNotEmpty(CLOSURE_REASON)"
    message: "Closure reason is required when disposition is closed"
    fields: [DISPOSITION, CLOSURE_REASON]

  - id: employment_fields_consistency
    expr: "(EMPLOYED == 1 and HOURS_WORKED > 0 and EARNINGS > 0) or (EMPLOYED != 1 and HOURS_WORKED == 0)"
    message: "Employment status, hours worked, and earnings must be consistent"
    fields: [EMPLOYED, HOURS_WORKED, EARNINGS]

# ───────────────────────────────────────────────────────────────────────────────
# CATEGORY 4: Group/Case Validations
# Applied across all records in a case
# ───────────────────────────────────────────────────────────────────────────────

category4:
  - id: t1_required
    expr: "recordCount('T1') >= 1"
    message: "Each case must have at least one T1 (adult) record"

  - id: t1_has_children
    expr: "recordCount('T1') == 0 or recordCount('T2') + recordCount('T3') > 0"
    message: "T1 record must have at least one T2 (child) or T3 (family) record"

  - id: t2_count_limit
    expr: "recordCount('T2') <= 99"
    message: "Case cannot have more than 99 T2 records (got {{recordCount('T2')}})"

  - id: no_duplicate_ssn
    expr: "not hasDuplicates('T2', 'SSN')"
    message: "Duplicate SSN found in T2 records for this case"

  - id: family_affiliation_consistency
    expr: "all(T2Records, {.Fields.FAMILY_AFFILIATION in [1, 2, 3]})"
    message: "All T2 records must have valid family affiliation (1, 2, or 3)"
```

### 5.3 Schema Reference to Validators

Schemas reference validators by ID:

```yaml
# config/schemas/tanf/t1.yaml

name: t1
record_type: T1
model: tanf_t1

# Category 1 validators for this record type
category1:
  - record_length_t1
  - case_number_not_empty

fields:
  - name: RPT_MONTH_YEAR
    item: "4"
    friendly_name: "Reporting Month/Year"
    type: integer
    start: 2
    end: 8
    # Category 2 validators for this field
    validators:
      - year_after_1998
      - valid_month

  - name: CASE_NUMBER
    item: "6"
    friendly_name: "Case Number"
    type: string
    start: 8
    end: 19
    validators:
      - not_empty

  - name: CASH_AMOUNT
    item: "21A"
    friendly_name: "Cash and Cash Equivalents"
    type: integer
    start: 45
    end: 49
    validators:
      - not_negative

# Category 3 validators for this record type
category3:
  - cash_requires_months
  - benefits_sum_positive
```

### 5.4 FileSpec Reference to Validators

```yaml
# config/filespecs/tanf_section1.yaml

program: TANF
section: 1
format: positional

schemas:
  - common/header
  - tanf/t1
  - tanf/t2
  - tanf/t3
  - common/trailer

# Category 4 validators for this file type
category4:
  - t1_required
  - t1_has_children
  - t2_count_limit
  - no_duplicate_ssn
```

---

## Part 6: Implementation Architecture

### 6.1 Compilation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Application Startup                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. Load validators.yaml                                        │
│     - Parse all validator definitions                           │
│     - Store in ValidatorDefRegistry                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. Register Custom Functions                                   │
│     - year(), month(), day(), quarter()                         │
│     - isValidDate(), isEmpty(), matches()                       │
│     - recordCount(), hasRecordType(), hasDuplicates()           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Compile Expressions                                         │
│     For each validator definition:                              │
│     - expr.Compile(def.Expr, expr.Env(envType), functions...)   │
│     - Store *vm.Program in CompiledValidator                    │
│     - Parse message template                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Load Schemas & FileSpecs                                    │
│     - Resolve validator IDs to CompiledValidators               │
│     - Attach to schema fields and category lists                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Ready to Process Files                                         │
│  - All expressions pre-compiled to bytecode                     │
│  - All message templates pre-parsed                             │
│  - Thread-safe for parallel validation                          │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Core Types

> **Reference**: The compiled expression is stored as a [`*vm.Program`](https://pkg.go.dev/github.com/expr-lang/expr/vm#Program) which is thread-safe for concurrent execution via [`expr.Run()`](https://pkg.go.dev/github.com/expr-lang/expr#Run).

```go
// ValidatorDef represents a validator definition from YAML
type ValidatorDef struct {
    ID         string   `yaml:"id"`
    Expr       string   `yaml:"expr"`
    Message    string   `yaml:"message"`
    ErrorType  string   `yaml:"error_type,omitempty"`
    Category   int      `yaml:"category,omitempty"`
    Deprecated bool     `yaml:"deprecated,omitempty"`
    Fields     []string `yaml:"fields,omitempty"`
    AppliesTo  []string `yaml:"applies_to,omitempty"`
}

// CompiledValidator is ready for execution
type CompiledValidator struct {
    Def     *ValidatorDef
    Program *vm.Program          // Compiled expression bytecode
    Message *template.Template   // Parsed message template
}

// ValidatorRegistry holds all compiled validators
type ValidatorRegistry struct {
    validators map[string]*CompiledValidator
    exprEnv    []expr.Option  // Shared compilation options
}

// Compile a validator definition
// See: https://expr-lang.org/docs/configuration for compilation options
func (r *ValidatorRegistry) Compile(def *ValidatorDef) (*CompiledValidator, error) {
    // Determine environment type based on category
    envType := r.envTypeForCategory(def.Category)

    // Compile expression
    // - expr.Env(): provides type information for compilation
    // - expr.AsBool(): enforces boolean return type (https://expr-lang.org/docs/configuration#asbool)
    program, err := expr.Compile(def.Expr,
        expr.Env(envType),
        expr.AsBool(),  // Expressions must return bool
        r.exprEnv...,   // Custom functions
    )
    if err != nil {
        return nil, fmt.Errorf("compiling %s: %w", def.ID, err)
    }

    // Parse message template
    msgTmpl, err := template.New(def.ID).Parse(def.Message)
    if err != nil {
        return nil, fmt.Errorf("parsing message for %s: %w", def.ID, err)
    }

    return &CompiledValidator{
        Def:     def,
        Program: program,
        Message: msgTmpl,
    }, nil
}
```

### 6.3 Execution Flow

```go
// Execute a compiled validator
func (cv *CompiledValidator) Execute(env any) *ValidationResult {
    // Run expression (thread-safe, env is per-call)
    result, err := expr.Run(cv.Program, env)
    if err != nil {
        // Expression error - treat as validation failure
        return &ValidationResult{
            Valid:       false,
            ValidatorID: cv.Def.ID,
            Error:       err,
        }
    }

    // Expression must return bool
    valid, ok := result.(bool)
    if !ok {
        return &ValidationResult{
            Valid:       false,
            ValidatorID: cv.Def.ID,
            Error:       fmt.Errorf("expression returned %T, expected bool", result),
        }
    }

    if valid {
        return ValidResult()  // Singleton, no allocation
    }

    return &ValidationResult{
        Valid:       false,
        ValidatorID: cv.Def.ID,
        Def:         cv.Def,
    }
}
```

### 6.4 Environment Construction

```go
// Build environment for Category 2 (field validation)
func buildCat2Env(ctx *ValidationContext) *Cat2Env {
    return &Cat2Env{
        Value:        ctx.FieldValue(),
        Fields:       ctx.Record.FieldMap(),  // Cached map[string]any
        RecordType:   ctx.Record.Schema.RecordType,
        LineNumber:   ctx.Record.LineNumber,
        RecordLength: ctx.Record.DecodedSize,
    }
}

// Build environment for Category 3 (cross-field)
func buildCat3Env(ctx *ValidationContext) *Cat3Env {
    env := &Cat3Env{
        Fields:       ctx.Record.FieldMap(),
        RecordType:   ctx.Record.Schema.RecordType,
        LineNumber:   ctx.Record.LineNumber,
        RecordLength: ctx.Record.DecodedSize,
    }
    // Promote fields to top level for cleaner expressions
    // This allows "CASH_AMOUNT > 0" instead of "Fields.CASH_AMOUNT > 0"
    for name, value := range env.Fields {
        // expr will look up fields on the struct first, then fall back to map
    }
    return env
}

// Build environment for Category 4 (group validation)
func buildCat4Env(ctx *ValidationContext) *Cat4Env {
    group := ctx.Group
    env := &Cat4Env{
        CaseNumber:   group.CaseNumber,
        RecordCount:  len(group.Records),
        RecordCounts: make(map[string]int),
        HasType:      make(map[string]bool),
        Records:      make([]RecordEnv, len(group.Records)),
    }

    // Pre-compute aggregates
    for i, rec := range group.Records {
        recType := rec.Schema.RecordType
        env.RecordCounts[recType]++
        env.HasType[recType] = true
        env.Records[i] = RecordEnv{
            Type:       recType,
            LineNumber: rec.LineNumber,
            Fields:     rec.FieldMap(),
        }
    }

    // Pre-filter by type for convenience
    env.T1Records = filterByType(env.Records, "T1")
    env.T2Records = filterByType(env.Records, "T2")
    env.T3Records = filterByType(env.Records, "T3")

    return env
}
```

### 6.5 Custom Function Registration

> **Reference**: See [Functions](https://expr-lang.org/docs/functions) for the `expr.Function()` API and type signature patterns.

```go
// registerCustomFunctions returns expr.Option values for all custom functions.
// Each function is registered with expr.Function() which takes:
// - name: the function name as used in expressions
// - implementation: the Go function to call
// - type signature: used for compile-time type checking
// See: https://expr-lang.org/docs/functions#function-option
func registerCustomFunctions() []expr.Option {
    return []expr.Option{
        // Date functions
        expr.Function("year", func(params ...any) (any, error) {
            return extractYear(params[0]), nil
        }, new(func(any) int)),

        expr.Function("month", func(params ...any) (any, error) {
            return extractMonth(params[0]), nil
        }, new(func(any) int)),

        expr.Function("isValidDate", func(params ...any) (any, error) {
            v := params[0]
            y, m, d := extractYear(v), extractMonth(v), extractDay(v)
            return isValidDate(y, m, d), nil
        }, new(func(any) bool)),

        // String functions
        expr.Function("isEmpty", func(params ...any) (any, error) {
            return isEmptyValue(params[0]), nil
        }, new(func(any) bool)),

        expr.Function("isNotEmpty", func(params ...any) (any, error) {
            return !isEmptyValue(params[0]), nil
        }, new(func(any) bool)),

        expr.Function("matches", func(params ...any) (any, error) {
            s := fmt.Sprintf("%v", params[0])
            pattern := params[1].(string)
            matched, err := regexp.MatchString(pattern, s)
            return matched, err
        }, new(func(string, string) bool)),

        // Group functions
        expr.Function("recordCount", func(params ...any) (any, error) {
            // This requires access to the environment
            // Implementation depends on how env is structured
            return 0, nil // Placeholder
        }, new(func(string) int)),

        expr.Function("hasDuplicates", func(params ...any) (any, error) {
            // recordType, fieldName
            return false, nil // Placeholder
        }, new(func(string, string) bool)),
    }
}
```

---

## Part 7: Migration Path

### 7.1 Phased Approach

**Phase 1: Infrastructure (Week 1-2)**
- Implement expression compilation pipeline
- Register all custom functions
- Build environment construction for each category
- Unit test expression evaluation

**Phase 2: Validator Migration (Week 2-3)**
- Convert Category 2 validators (simplest)
- Convert Category 3 validators
- Convert Category 1 validators
- Convert Category 4 validators (most complex)

**Phase 3: Integration (Week 3-4)**
- Update schema loader to resolve validator references
- Update orchestrator to use expression-based validators
- Integration testing with real data files
- Performance benchmarking

**Phase 4: Cleanup (Week 4)**
- Remove old Go validator factories
- Update documentation
- Stakeholder review of validators.yaml

### 7.2 Validator Conversion Examples

**Before (Go):**
```go
func IsGreaterThanFactory(params map[string]any) (registry.ValidatorFunc, error) {
    target, ok := params["value"]
    if !ok {
        return nil, fmt.Errorf("isGreaterThan requires 'value' parameter")
    }
    return func(ctx *registry.ValidationContext) *registry.ValidationResult {
        value := ctx.FieldValue()
        if compareValues(value, target) > 0 {
            return registry.ValidResult()
        }
        result := registry.AcquireResult()
        result.Valid = false
        result.ValidatorID = "isGreaterThan"
        result.Category = ctx.Category
        result.Record = ctx.Record
        return result
    }, nil
}
```

**After (YAML):**
```yaml
- id: greater_than_zero
  expr: "value > 0"
  message: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): Must be greater than 0, got {{.Value}}"
```

**Before (Go - cross-field):**
```go
func CashRequiresMonthsFactory(params map[string]any) (registry.ValidatorFunc, error) {
    return func(ctx *registry.ValidationContext) *registry.ValidationResult {
        cashAmount, _ := toFloat64(ctx.GetField("CASH_AMOUNT"))
        if cashAmount <= 0 {
            return registry.ValidResult()
        }
        nbrMonths, _ := toFloat64(ctx.GetField("NBR_MONTHS"))
        if nbrMonths > 0 {
            return registry.ValidResult()
        }
        result := registry.AcquireResult()
        result.Valid = false
        result.ValidatorID = "cashRequiresMonths"
        result.FieldName = "CASH_AMOUNT, NBR_MONTHS"
        // ...
        return result
    }, nil
}
```

**After (YAML):**
```yaml
- id: cash_requires_months
  expr: "CASH_AMOUNT <= 0 or NBR_MONTHS > 0"
  message: "When cash amount (${{.Fields.CASH_AMOUNT}}) is provided, months must be positive"
  fields: [CASH_AMOUNT, NBR_MONTHS]
```

### 7.3 Keeping Complex Logic in Go

Some validators are better kept as Go functions exposed to expressions:

```go
// Complex Go function
func hasDuplicatesInGroup(records []RecordEnv, recordType, fieldName string) bool {
    seen := make(map[any]bool)
    for _, rec := range records {
        if rec.Type != recordType {
            continue
        }
        value := rec.Fields[fieldName]
        if value == nil {
            continue
        }
        if seen[value] {
            return true
        }
        seen[value] = true
    }
    return false
}

// Registered as expr function
expr.Function("hasDuplicates", func(params ...any) (any, error) {
    env := params[0].(*Cat4Env)
    recordType := params[1].(string)
    fieldName := params[2].(string)
    return hasDuplicatesInGroup(env.Records, recordType, fieldName), nil
})
```

**Usage in YAML:**
```yaml
- id: no_duplicate_ssn
  expr: "not hasDuplicates('T2', 'SSN')"
  message: "Duplicate SSN found in T2 records"
```

---

## Part 8: Testing Strategy

### 8.1 Expression Unit Tests

```go
func TestExpressions(t *testing.T) {
    tests := []struct {
        name     string
        expr     string
        env      any
        expected bool
    }{
        {
            name: "greater than - pass",
            expr: "value > 0",
            env:  Cat2Env{Value: 5},
            expected: true,
        },
        {
            name: "greater than - fail",
            expr: "value > 0",
            env:  Cat2Env{Value: -1},
            expected: false,
        },
        {
            name: "cross-field - cash requires months - pass",
            expr: "CASH_AMOUNT <= 0 or NBR_MONTHS > 0",
            env:  Cat3Env{Fields: map[string]any{"CASH_AMOUNT": 100, "NBR_MONTHS": 5}},
            expected: true,
        },
        // ... more tests
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            program, err := expr.Compile(tt.expr, expr.AsBool())
            require.NoError(t, err)

            result, err := expr.Run(program, tt.env)
            require.NoError(t, err)

            assert.Equal(t, tt.expected, result)
        })
    }
}
```

### 8.2 Validator Definition Tests

```go
func TestAllValidatorDefinitions(t *testing.T) {
    // Load all validator definitions
    defs, err := LoadValidatorDefs("config/validation/validators.yaml")
    require.NoError(t, err)

    registry := NewValidatorRegistry()

    for _, def := range defs {
        t.Run(def.ID, func(t *testing.T) {
            // Verify expression compiles
            cv, err := registry.Compile(&def)
            require.NoError(t, err, "expression should compile")

            // Verify message template parses
            assert.NotNil(t, cv.Message, "message template should parse")
        })
    }
}
```

### 8.3 CI Validation

```yaml
# .github/workflows/validate-expressions.yml
name: Validate Expressions

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - name: Validate all expressions compile
        run: go test -run TestAllValidatorDefinitions ./...
```

---

## Part 9: Observability

### 9.1 Validation Logging

```go
type ValidationLog struct {
    ValidatorID string
    Expression  string
    Category    int
    RecordType  string
    LineNumber  int
    FieldName   string
    InputValue  any
    Result      bool
    Duration    time.Duration
    Error       error
}

// Optional logging during validation
func (cv *CompiledValidator) ExecuteWithLogging(env any, logger Logger) *ValidationResult {
    start := time.Now()
    result := cv.Execute(env)

    if logger != nil {
        logger.Log(ValidationLog{
            ValidatorID: cv.Def.ID,
            Expression:  cv.Def.Expr,
            Result:      result.Valid,
            Duration:    time.Since(start),
            // ... other fields from env
        })
    }

    return result
}
```

### 9.2 Expression Introspection

```go
// List all validators for documentation/UI
func (r *ValidatorRegistry) ListValidators() []ValidatorInfo {
    var infos []ValidatorInfo
    for _, cv := range r.validators {
        infos = append(infos, ValidatorInfo{
            ID:          cv.Def.ID,
            Expression:  cv.Def.Expr,
            Message:     cv.Def.Message,
            Category:    cv.Def.Category,
            Fields:      cv.Def.Fields,
            Deprecated:  cv.Def.Deprecated,
        })
    }
    return infos
}
```

---

## Appendix A: Complete Function Reference

| Function | Category | Signature | Description |
|----------|----------|-----------|-------------|
| `year(v)` | 2,3 | `any → int` | Extract year from date |
| `month(v)` | 2,3 | `any → int` | Extract month (1-12) |
| `day(v)` | 2,3 | `any → int` | Extract day (1-31) |
| `quarter(v)` | 2,3 | `any → int` | Extract quarter (1-4) |
| `isValidDate(v)` | 2,3 | `any → bool` | Validate date components |
| `dateInPast(v)` | 2,3 | `any → bool` | Check if before today |
| `dateInFuture(v)` | 2,3 | `any → bool` | Check if after today |
| `isEmpty(v)` | 2,3 | `any → bool` | Nil/empty/whitespace |
| `isNotEmpty(v)` | 2,3 | `any → bool` | Has non-whitespace content |
| `trim(s)` | 2,3 | `string → string` | Remove whitespace |
| `str(v)` | 2,3 | `any → string` | Convert to string |
| `int(v)` | 2,3 | `any → int` | Convert to integer |
| `matches(s, p)` | 2,3 | `string, string → bool` | Regex match |
| `isNumeric(s)` | 2,3 | `string → bool` | Only digits |
| `isAlpha(s)` | 2,3 | `string → bool` | Only letters |
| `recordCount(type)` | 4 | `string → int` | Count records by type |
| `hasRecordType(type)` | 4 | `string → bool` | Type exists in group |
| `sumField(type, field)` | 4 | `string, string → float` | Sum field values |
| `hasDuplicates(type, field)` | 4 | `string, string → bool` | Check for duplicates |

---

## Appendix B: Expression Examples by Category

### Category 1 (Record Pre-Check)
```yaml
"RecordLength == 156"
"RecordLength >= 117 and RecordLength <= 156"
"RecordType startsWith 'T'"
"isNotEmpty(trim(CaseNumber))"
```

### Category 2 (Field Value)
```yaml
"value > 0"
"value >= 1 and value <= 12"
"value in [1, 2, 3, 4, 5, 9]"
"len(str(value)) == 9"
"isNotEmpty(value)"
"year(value) > 1998"
"matches(str(value), '^[A-Z]{2}\\d{4}$')"
"isValidDate(value)"
```

### Category 3 (Cross-Field)
```yaml
"FIELD_A == FIELD_B"
"FIELD_A > FIELD_B"
"CASH_AMOUNT <= 0 or NBR_MONTHS > 0"
"isEmpty(END_DATE) or START_DATE <= END_DATE"
"A + B + C > 0"
"isNotEmpty(A) or isNotEmpty(B) or isNotEmpty(C)"
"(isEmpty(A) and isEmpty(B)) or (isNotEmpty(A) and isNotEmpty(B))"
```

### Category 4 (Group/Case)
```yaml
"recordCount('T1') >= 1"
"hasRecordType('T1')"
"recordCount('T1') == 0 or recordCount('T2') + recordCount('T3') > 0"
"recordCount('T2') >= 1 and recordCount('T2') <= 99"
"not hasDuplicates('T2', 'SSN')"
"all(T1Records, {.Fields.STATUS in [1, 2, 3]})"
"sumField('T2', 'AMOUNT') > 0"
```
