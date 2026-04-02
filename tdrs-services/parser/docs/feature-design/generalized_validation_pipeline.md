# Plan: Generalize Validation Architecture

## Problem Statement

The current Go parser validation architecture conflates two concepts:
1. **Scope** - what data the validator can access (field, record, group)
2. **Error type** - what category of error is produced and whether it blocks serialization

This breaks down for validators like `generate_funded_ssn_errors` (Python: `tdr_parser.py:436-464`) which:
- Needs **GROUP scope** (correlates T1 and T2 records across a case)
- Produces **VALUE_CONSISTENCY errors** (per-record, non-blocking)
- Currently impossible to express because Cat4 = group scope + CASE_CONSISTENCY + blocks group

Additionally, "record validators" currently has ambiguous meaning:
- Record precheck (structural validation, blocks serialization)
- Record consistency (cross-field validation, allows serialization)

---

## Design: Organize by Scope, Validators Define Error Type

### Core Principle
**Scope** and **error type** are independent concerns:
- **Scope**: What data the validator can access (`field`, `record`, `group`)
- **Error Type**: What category of error is produced, which determines serialization behavior

### New Configuration Structure
Replace `category1/2/3/4` with scope-based organization:

```yaml
# validators.yaml - organized by SCOPE
field:
  - id: is_numeric
    expr: "isNumeric(str(Value))"
    error_type: FIELD_VALUE  # Validators declare their error type
    message: "..."

record:
  # Precheck validators (block record serialization)
  - id: record_length_range
    expr: "RecordLength >= Params.min and RecordLength <= Params.max"
    error_type: RECORD_PRE_CHECK  # Blocks record

  # Consistency validators (allow serialization)
  - id: start_before_end
    expr: "GetString('START_DATE') <= GetString('END_DATE')"
    error_type: VALUE_CONSISTENCY  # Doesn't block

group:
  # Case-level validators (block group serialization)
  - id: t1_has_t2_or_t3
    expr: "RecordCounts['T2'] > 0 or RecordCounts['T3'] > 0"
    error_type: CASE_CONSISTENCY  # Blocks group

  # Group-scope but per-record errors (doesn't block)
  - id: federally_funded_ssn
    expr: "filterFundedRecordsWithInvalidSSN(Group)"
    error_type: VALUE_CONSISTENCY  # Doesn't block
    result_mode: per_record  # Returns list of failing records
```

### Error Type Controls Serialization

| Error Type | Blocks | Description |
|------------|--------|-------------|
| RECORD_PRE_CHECK | Record | Structural issues (length, format) |
| FIELD_VALUE | None | Single field validation errors |
| VALUE_CONSISTENCY | None | Cross-field/cross-record consistency |
| CASE_CONSISTENCY | Group | Case-level relationship violations |

### Default Error Types (Reduce Verbosity)

Each scope has a sensible default if `error_type` is not specified:

| Scope | Default Error Type |
|-------|-------------------|
| `group` | CASE_CONSISTENCY |
| `record` | VALUE_CONSISTENCY |
| `field` | FIELD_VALUE |

Validators only need to specify `error_type` when overriding the default:
```yaml
record:
  # Uses default VALUE_CONSISTENCY (no error_type needed)
  - id: start_before_end
    expr: "..."

  # Must specify because RECORD_PRE_CHECK differs from default
  - id: record_length_range
    expr: "..."
    error_type: RECORD_PRE_CHECK
```

### Scope Controls Data Access

| Scope | Environment | Access |
|-------|-------------|--------|
| `field` | FieldEnv | `Value`, `Params` |
| `record` | RecordEnv | `Get()`, `GetInt()`, `GetString()`, `RecordLength`, `Params` |
| `group` | GroupEnv | `Group`, `RecordCounts`, `HasType`, `getRecordsOfType()`, `Params` |

### Result Modes for Group Validators

Group-scope validators can produce:
- `single` (default): One error for the whole group
- `per_record`: Returns a list of failing records, each gets its own error

---

## Schema Validator References

### Current Structure
Schemas currently use `category1`, `category2`, `category3`:
```yaml
# Schema-level validators
category1:
  - id: record_length_min
    params: { min: 156 }
category3:
  - id: ifthenalso_range_to_range
    params: { ... }

# Field-level validators (inline on each field)
fields:
  - name: RPT_MONTH_YEAR
    category2:
      - id: year_after_1998
```

### New Structure
Schemas will use `record` (schema-level) and `field` (inline):
```yaml
# Schema-level record validators (both precheck and consistency)
record:
  - id: record_length_min
    params: { min: 156 }
    error_type: RECORD_PRE_CHECK  # Override default since it blocks

  - id: ifthenalso_range_to_range
    params: { ... }
    # Uses default VALUE_CONSISTENCY

# Field-level validators (inline on each field) - unchanged format
fields:
  - name: RPT_MONTH_YEAR
    field:  # Renamed from category2
      - id: year_after_1998
      # Uses default FIELD_VALUE
```

The key change: All record-scope validators (both precheck and consistency) go in `record:`. They differentiate by `error_type`, not by section.

---

## Funded SSN Validator: Expr-Based Implementation

### Expr Expression
```yaml
group:
  - id: federally_funded_ssn
    expr: |
      filter(
        getRecordsOfType(Group, 'T2'),
        { .GetInt('FAMILY_AFFILIATION') == 1 and
          any(getRecordsOfType(Group, 'T1'), { #.GetInt('FUNDING_STREAM') == 1 }) and
          not isValidSSN(.GetString('SSN')) }
      )
    error_type: VALUE_CONSISTENCY
    result_mode: per_record
    message: "Federally funded recipients must have a valid Social Security number."
    fields: [FUNDING_STREAM, FAMILY_AFFILIATION, SSN]
```

### New Helper Function: `isValidSSN()`
Add to `functions.go`:
```go
func isValidSSN(ssn string) bool {
    // 1. Must be 9 digits
    // 2. Must be all numeric
    // 3. Area number (0-2) not in invalid set (000, 666, 9xx)
    // 4. Group number (3-4) not 00
    // 5. Serial number (5-8) not 0000
    // 6. Not a repeating pattern (111111111, etc.)
}
```

---

## Implementation Steps

### Step 1: Update ValidatorDef
**File**: `internal/config/validation/types.go`

```go
type ValidatorDef struct {
    ID          string         `yaml:"id"`
    Expr        string         `yaml:"expr"`
    Params      map[string]any `yaml:"params,omitempty"`
    Fields      []string       `yaml:"fields,omitempty"`
    Message     string         `yaml:"message,omitempty"`

    // NEW: Validator declares its behavior
    ErrorType   string `yaml:"error_type"`     // Required: RECORD_PRE_CHECK, FIELD_VALUE, etc.
    ResultMode  string `yaml:"result_mode"`    // "single" (default) or "per_record"

    Deprecated  bool   `yaml:"deprecated,omitempty"`
}
```

### Step 2: Reorganize validators.yaml
**File**: `config/validation/validators.yaml`

Replace `category1/2/3/4` sections with `field/record/group`:

```yaml
field:
  - id: is_numeric
    expr: "isNumeric(str(Value))"
    error_type: FIELD_VALUE
  # ... other field validators

record:
  # Precheck validators
  - id: record_length_range
    expr: "RecordLength >= Params.min and RecordLength <= Params.max"
    error_type: RECORD_PRE_CHECK

  # Consistency validators
  - id: start_before_end
    expr: "..."
    error_type: VALUE_CONSISTENCY
  # ... other record validators

group:
  - id: t1_has_t2_or_t3
    expr: "RecordCounts['T2'] > 0 or RecordCounts['T3'] > 0"
    error_type: CASE_CONSISTENCY

  - id: federally_funded_ssn
    expr: "filterFundedRecordsWithInvalidSSN(Group)"
    error_type: VALUE_CONSISTENCY
    result_mode: per_record
```

### Step 3: Update Registry
**File**: `internal/validation/registry.go`

- Change storage from `cat1/cat2/cat3/cat4` maps to `field/record/group` maps
- Load validators by scope section
- Compile with appropriate environment type based on scope

```go
type ValidatorRegistry struct {
    field  map[string][]*CompiledValidator  // [recordType] -> validators
    record map[string][]*CompiledValidator  // [recordType] -> validators
    group  map[string][]*CompiledValidator  // [filespecKey] -> validators
}
```

### Step 4: Update CompiledValidator and Results
**File**: `internal/validation/result.go`

```go
type CompiledValidator struct {
    ID         string
    Scope      string  // "field", "record", "group"
    ErrorType  string  // The declared error type
    ResultMode string  // "single" or "per_record"
    Expr       *CompiledExpr
    Message    *template.Template
    Fields     []string
    Params     map[string]any
}

type ValidationResult struct {
    Valid       bool
    ErrorType   string  // Use this for serialization decisions
    ValidatorID string
    FieldName   string
    LineNumber  int     // For per-record attribution
    RecordType  string
    Error       error
    Validator   *CompiledValidator
}

func (vr *ValidationResult) BlocksRecord() bool {
    return vr.ErrorType == "RECORD_PRE_CHECK"
}

func (vr *ValidationResult) BlocksGroup() bool {
    return vr.ErrorType == "CASE_CONSISTENCY"
}
```

### Step 5: Update Orchestrator
**File**: `internal/validation/orchestrator.go`

```go
func (o *Orchestrator) ValidateGroup(group WrappedGroup, filespecKey string) *GroupValidationResult {
    result := &GroupValidationResult{Group: group}

    // Phase 1: Run all group-scope validators
    for _, cv := range o.registry.GetGroupValidators(filespecKey) {
        if cv.ResultMode == "per_record" {
            // Expression returns []Record of failing records
            failedRecords := ExecuteReturningRecords(cv, NewGroupEnv(group))
            for _, rec := range failedRecords {
                result.AddRecordError(rec, cv)
            }
        } else {
            if vr := Execute(cv, NewGroupEnv(group)); !vr.Valid {
                result.GroupErrors = append(result.GroupErrors, vr)
            }
        }
    }

    // Check if blocked by CASE_CONSISTENCY errors
    groupBlocked := result.HasBlockingGroupErrors()

    // Phase 2: Run record-scope and field-scope validators
    for _, rec := range group.GetRecords() {
        recResult := o.validateRecord(rec, groupBlocked)
        result.RecordResults = append(result.RecordResults, recResult)
    }

    return result
}
```

### Step 6: Add isValidSSN Function
**File**: `internal/validation/functions.go`

```go
func isValidSSN(ssn string) bool {
    if len(ssn) != 9 || !isNumeric(ssn) {
        return false
    }
    // Check for repeating patterns
    repeating := []string{"000000000", "111111111", ...}
    if contains(repeating, ssn) {
        return false
    }
    // Check area number (positions 0-2)
    area := ssn[0:3]
    if area == "000" || area == "666" || area[0] == '9' {
        return false
    }
    // Check group number (positions 3-4)
    if ssn[3:5] == "00" {
        return false
    }
    // Check serial number (positions 5-8)
    if ssn[5:9] == "0000" {
        return false
    }
    return true
}
```

Register: `expr.Function("isValidSSN", ..., new(func(string) bool))`

### Step 7: Update Result Router
**File**: `internal/pipeline/result_router.go`

Use `ErrorType` for blocking decisions:
```go
// Record serialization: blocked by RECORD_PRE_CHECK
if recResult.HasBlockingRecordErrors() { ... }

// Group serialization: blocked by CASE_CONSISTENCY
if gvr.HasBlockingGroupErrors() { ... }
```

### Step 8: Update Schema/Filespec References
Update schemas and filespecs to reference validators by scope section.

---

## Files to Modify

| File | Changes |
|------|---------|
| `internal/config/validation/types.go` | Make ErrorType required, remove Category inference |
| `internal/validation/result.go` | Add Scope, update blocking logic to use ErrorType |
| `internal/validation/registry.go` | Reorganize by scope (field/record/group) |
| `internal/validation/orchestrator.go` | Handle per_record result mode |
| `internal/validation/functions.go` | Add isValidSSN() |
| `config/validation/validators.yaml` | Reorganize from category1/2/3/4 to field/record/group |
| `config/schemas/*.yaml` | Rename `category1`→`record` (with error_type), rename `category3`→`record`, rename `category2`→`field` |
| `config/filespecs/*.yaml` | Rename `category4`→`group` |
| `internal/pipeline/result_router.go` | Use ErrorType for blocking |

---

## Verification Plan

1. **Unit tests**: Test validators with different scope + error_type combinations
2. **Integration test**:
   - Create test case with federally funded T1 + T2 records with invalid SSN
   - Verify VALUE_CONSISTENCY errors generated per-record
   - Verify group still serializes (not blocked)
3. **Expr test**: Verify the `filterFundedRecordsWithInvalidSSN` expression works correctly
4. **Manual verification**: Parse a TANF Section 1 file, verify correct error attribution
