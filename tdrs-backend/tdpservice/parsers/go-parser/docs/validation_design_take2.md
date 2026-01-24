# Go Parser Validation System Design

## Part 1: Requirements

### R1. Validator Definition & Registration
- [ ] **R1.1** Add new validators without code changes (config-driven)
- [ ] **R1.2** Simple, consistent interface for all validators regardless of category
- [ ] **R1.3** Validators are composable - build complex validators from simple ones
- [ ] **R1.4** Registry of all available validators with introspection
- [ ] **R1.5** Validators are stateless and reusable

### R2. Error Messages & Templates
- [ ] **R2.1** Registry of all error message templates
- [ ] **R2.2** Custom message templates per validator, per field, or per schema
- [ ] **R2.3** Static exact error messages for one-off cases
- [ ] **R2.4** Error messages decoupled from validator logic
- [ ] **R2.5** Lazy evaluation of error messages (generate at write time, not validation time)

### R3. Validation Categories & Hierarchy
- [ ] **R3.1** Well-defined category system with clear interfaces
- [ ] **R3.2** Configurable execution order between categories
- [ ] **R3.3** Short-circuiting: skip later categories if earlier ones fail
- [ ] **R3.4** Easy to add new categories/stages without major refactoring
- [ ] **R3.5** Each category can have different error types

### R4. Performance & Memory
- [ ] **R4.1** Parallel validation at appropriate granularity (record/group level)
- [ ] **R4.2** Object pooling for validation contexts and results
- [ ] **R4.3** Minimal allocations during hot path
- [ ] **R4.4** Batch error writing to database

### R5. Debugging & Observability
- [ ] **R5.1** Clear error tracing - know which validator, field, record caused error
- [ ] **R5.2** Easy to debug why a validator failed
- [ ] **R5.3** Logging of validation decisions (optional, for troubleshooting)

### R6. Extensibility
- [ ] **R6.1** Plugin-style validator registration
- [ ] **R6.2** Support for custom validator implementations

### R7. Validation Scopes
- [ ] **R7.1** Cat 1, 2, 3: Record scope (validate individual records)
- [ ] **R7.2** Cat 4: Group scope (validate groups of related records)
- [ ] **R7.3** Clear separation between record-level and group-level validation

---

## Part 2: Architecture Design

### Core Types

```go
// ValidationContext - unified context for all validators (pooled)
type ValidationContext struct {
    // File-level (set once per file)
    DatafileID  int32
    ParseCtx    *schema.ParseContext  // Year, Quarter, IsEncrypted

    // Record-level (Cat 1, 2, 3)
    Record      *schema.ParsedRecord  // Has .Schema pointer for field metadata
    Schema      *schema.CompiledSchema

    // Field-level (Cat 2 only)
    FieldIndex  int  // Index into Record.Fields and Schema.Fields

    // Group-level (Cat 4 only)
    Group       *ParsedGroup  // Parsed group of records
}

// Helper methods
func (ctx *ValidationContext) FieldValue() any          // Returns Record.Fields[FieldIndex]
func (ctx *ValidationContext) FieldDef() *FieldDef      // Returns Schema.Fields[FieldIndex]
func (ctx *ValidationContext) GetField(name string) any // Get any field by name
func (ctx *ValidationContext) Reset()                   // Clear for pool reuse

// ValidationResult - outcome of a validator (pooled)
type ValidationResult struct {
    Valid       bool
    ValidatorID string           // e.g., "isGreaterThan"
    Category    int              // 1, 2, 3, or 4
    FieldName   string           // For Cat 2, which field failed

    // Pointers for lazy error generation
    Record      *schema.ParsedRecord
    Schema      *schema.CompiledSchema
    Group       *ParsedGroup
    Rule        *RuleConfig      // Config that triggered this validation
}

// ValidatorFunc - unified signature for ALL validators
type ValidatorFunc func(ctx *ValidationContext) *ValidationResult

// ValidatorFactory - creates parameterized validators
type ValidatorFactory func(params map[string]any) (ValidatorFunc, error)
```

### Validator Registry

```go
// ValidatorRegistry - holds all available validators
type ValidatorRegistry struct {
    factories map[string]ValidatorFactory
}

func (r *ValidatorRegistry) Register(id string, factory ValidatorFactory)
func (r *ValidatorRegistry) Get(id string) (ValidatorFactory, bool)
func (r *ValidatorRegistry) List() []string  // For introspection
```

**Built-in validators** (registered at startup):
- Comparison: `isEqual`, `isGreaterThan`, `isLessThan`, `isBetween`, `isOneOf`
- String: `isEmpty`, `isNotEmpty`, `hasLength`, `matchesPattern`
- Date: `dateYearIsLargerThan`, `dateMonthIsValid`
- Record: `recordHasLength`, `caseNumberNotEmpty`
- Cross-field: `ifThenAlso`, `sumIsGreaterThan`, `atLeastOneOf`
- Group: `recordTypePresent`, `recordCountInRange`

### Composable Validators

Validators can be composed using logical operators and conditionals:

```go
// Logical composition
func And(validators ...ValidatorFunc) ValidatorFunc
func Or(validators ...ValidatorFunc) ValidatorFunc
func Not(validator ValidatorFunc) ValidatorFunc

// Conditional composition
func IfThen(condition ValidatorFunc, then ValidatorFunc) ValidatorFunc
func IfThenElse(condition ValidatorFunc, then ValidatorFunc, else ValidatorFunc) ValidatorFunc
```

**Config examples:**

```yaml
# Simple logical composition
- id: positive_under_100    # ID for message lookup
  compose: and
  validators:
    - validator: isGreaterThan
      params: { value: 0 }
    - validator: isLessThan
      params: { value: 100 }
  message: "Value must be between 0 and 100"

# Conditional composition
- id: cash_requires_months
  compose: ifThen
  condition:
    validator: isGreaterThan
    params: { value: 0 }
    field: CASH_AMOUNT
  then:
    validator: isGreaterThan
    params: { value: 0 }
    field: NBR_MONTHS
  message: "When cash amount is positive, months must also be positive"

# Nested/chained composition
- id: complex_rule
  compose: and
  validators:
    - compose: or
      validators:
        - validator: isEqual
          params: { value: 1 }
        - validator: isEqual
          params: { value: 2 }
    - compose: ifThen
      condition:
        validator: isEqual
        params: { value: 1 }
      then:
        validator: isNotEmpty
        field: RELATED_FIELD
  message: "Complex validation failed"
```

Each composition has:
- **`id`**: Unique identifier for message lookup
- **`compose`**: Type (`and`, `or`, `not`, `ifThen`, `ifThenElse`)
- **`validators`** or **`condition`/`then`/`else`**: Child validators
- **`message`**: Override message (optional, can be template or static)
- **`error_type`**: Override error type (optional)

### Unified Validator Config Schema

Every validator follows this unified schema where `id` is the primary identifier:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Validator identifier. For simple validators, this IS the validator type (e.g., "isGreaterThan"). For compositions, this is a custom name. |
| `compose` | string | No | Composition type (`and`, `or`, `not`, `ifThen`, `ifThenElse`). If absent, `id` is looked up as a simple validator. |
| `params` | map | No | Parameters for simple validators |
| `validators` | []config | No | Child validators for `and`/`or`/`not` |
| `condition` | config | No | Condition validator for `ifThen`/`ifThenElse` |
| `then` | config | No | Then validator for `ifThen`/`ifThenElse` |
| `else` | config | No | Else validator for `ifThenElse` |
| `field` | string | No | Target field (for cross-field access in compositions) |
| `message` | string | No | Override error message (template or static) |
| `error_type` | string | No | Override error type |

**Examples:**

```yaml
# Simple validator - id IS the validator type
- id: isGreaterThan
  params:
    value: 0

# Simple validator with message override
- id: isGreaterThan
  params:
    value: 0
  message: "Value must be positive"

# And composition with custom id
- id: valid_range
  compose: and
  validators:
    - id: isGreaterThan
      params: { value: 0 }
    - id: isLessThan
      params: { value: 100 }
  message: "Value must be between 0 and 100"

# Conditional composition
- id: cash_requires_months
  compose: ifThen
  condition:
    id: isGreaterThan
    params: { value: 0 }
    field: CASH_AMOUNT
  then:
    id: isGreaterThan
    params: { value: 0 }
    field: NBR_MONTHS
  message: "When cash is positive, months must be positive"

# Nested composition
- id: complex_rule
  compose: and
  validators:
    - id: value_is_1_or_2
      compose: or
      validators:
        - id: isEqual
          params: { value: 1 }
        - id: isEqual
          params: { value: 2 }
    - id: isNotEmpty
      field: RELATED_FIELD
```

**Registry logic:**
```go
func (r *ValidatorRegistry) Build(config ValidatorConfig) ValidatorFunc {
    if config.Compose != "" {
        // Build composition using compose type
        return r.buildComposition(config)
    }
    // Simple validator - id is the validator type
    factory := r.factories[config.ID]
    return factory(config.Params)
}
```

### Composable Validator Construction

#### Config Types

```go
// ValidatorConfig - unified config for all validators
type ValidatorConfig struct {
    ID         string                 `yaml:"id"`
    Compose    string                 `yaml:"compose,omitempty"`    // "and", "or", "not", "ifThen", "ifThenElse"
    Params     map[string]any         `yaml:"params,omitempty"`
    Validators []ValidatorConfig      `yaml:"validators,omitempty"` // For and/or/not
    Condition  *ValidatorConfig       `yaml:"condition,omitempty"`  // For ifThen
    Then       *ValidatorConfig       `yaml:"then,omitempty"`       // For ifThen
    Else       *ValidatorConfig       `yaml:"else,omitempty"`       // For ifThenElse
    Field      string                 `yaml:"field,omitempty"`      // Target field override
    Message    string                 `yaml:"message,omitempty"`
    ErrorType  string                 `yaml:"error_type,omitempty"`
}
```

#### Build Process

```go
// buildComposition recursively constructs composed validators
func (r *ValidatorRegistry) buildComposition(config ValidatorConfig) (ValidatorFunc, error) {
    switch config.Compose {
    case "and":
        return r.buildAnd(config)
    case "or":
        return r.buildOr(config)
    case "not":
        return r.buildNot(config)
    case "ifThen":
        return r.buildIfThen(config)
    case "ifThenElse":
        return r.buildIfThenElse(config)
    default:
        return nil, fmt.Errorf("unknown composition type: %s", config.Compose)
    }
}

// buildAnd - all child validators must pass
func (r *ValidatorRegistry) buildAnd(config ValidatorConfig) (ValidatorFunc, error) {
    // 1. Recursively build all child validators
    children := make([]ValidatorFunc, len(config.Validators))
    for i, childConfig := range config.Validators {
        child, err := r.Build(childConfig)
        if err != nil {
            return nil, fmt.Errorf("building child %d: %w", i, err)
        }
        children[i] = child
    }

    // 2. Return composed validator
    return func(ctx *ValidationContext) *ValidationResult {
        for _, child := range children {
            result := child(ctx)
            if !result.Valid {
                // Return first failure with composition's id
                return &ValidationResult{
                    Valid:       false,
                    ValidatorID: config.ID,
                    Category:    result.Category,
                    FieldIndex:  ctx.FieldIndex,
                    Record:      ctx.Record,
                    Schema:      ctx.Schema,
                    Group:       ctx.Group,
                    Config:      &config,
                }
            }
        }
        return &ValidationResult{Valid: true}
    }, nil
}

// buildOr - at least one child validator must pass
func (r *ValidatorRegistry) buildOr(config ValidatorConfig) (ValidatorFunc, error) {
    children := make([]ValidatorFunc, len(config.Validators))
    for i, childConfig := range config.Validators {
        child, err := r.Build(childConfig)
        if err != nil {
            return nil, err
        }
        children[i] = child
    }

    return func(ctx *ValidationContext) *ValidationResult {
        for _, child := range children {
            result := child(ctx)
            if result.Valid {
                return &ValidationResult{Valid: true}
            }
        }
        // All failed
        return &ValidationResult{
            Valid:       false,
            ValidatorID: config.ID,
            Category:    ctx.Category,
            FieldIndex:  ctx.FieldIndex,
            Record:      ctx.Record,
            Schema:      ctx.Schema,
            Group:       ctx.Group,
            Config:      &config,
        }
    }, nil
}

// buildNot - child validator must fail
func (r *ValidatorRegistry) buildNot(config ValidatorConfig) (ValidatorFunc, error) {
    if len(config.Validators) != 1 {
        return nil, fmt.Errorf("not composition requires exactly 1 child")
    }
    child, err := r.Build(config.Validators[0])
    if err != nil {
        return nil, err
    }

    return func(ctx *ValidationContext) *ValidationResult {
        result := child(ctx)
        if result.Valid {
            // Child passed, so "not" fails
            return &ValidationResult{
                Valid:       false,
                ValidatorID: config.ID,
                Config:      &config,
                Record:      ctx.Record,
                Schema:      ctx.Schema,
            }
        }
        return &ValidationResult{Valid: true}
    }, nil
}

// buildIfThen - if condition passes, then must also pass
func (r *ValidatorRegistry) buildIfThen(config ValidatorConfig) (ValidatorFunc, error) {
    if config.Condition == nil || config.Then == nil {
        return nil, fmt.Errorf("ifThen requires condition and then")
    }

    condition, err := r.Build(*config.Condition)
    if err != nil {
        return nil, fmt.Errorf("building condition: %w", err)
    }
    then, err := r.Build(*config.Then)
    if err != nil {
        return nil, fmt.Errorf("building then: %w", err)
    }

    return func(ctx *ValidationContext) *ValidationResult {
        // Save original field context
        origFieldIndex := ctx.FieldIndex

        // Apply condition's field override if specified
        if config.Condition.Field != "" {
            ctx.FieldIndex = ctx.Schema.FieldIndex[config.Condition.Field]
        }
        condResult := condition(ctx)

        if !condResult.Valid {
            // Condition failed, ifThen passes (condition not met)
            ctx.FieldIndex = origFieldIndex
            return &ValidationResult{Valid: true}
        }

        // Condition passed, check then
        if config.Then.Field != "" {
            ctx.FieldIndex = ctx.Schema.FieldIndex[config.Then.Field]
        }
        thenResult := then(ctx)

        ctx.FieldIndex = origFieldIndex

        if !thenResult.Valid {
            return &ValidationResult{
                Valid:       false,
                ValidatorID: config.ID,
                Config:      &config,
                Record:      ctx.Record,
                Schema:      ctx.Schema,
            }
        }
        return &ValidationResult{Valid: true}
    }, nil
}

// buildIfThenElse - if condition passes run then, otherwise run else
func (r *ValidatorRegistry) buildIfThenElse(config ValidatorConfig) (ValidatorFunc, error) {
    if config.Condition == nil || config.Then == nil || config.Else == nil {
        return nil, fmt.Errorf("ifThenElse requires condition, then, and else")
    }

    condition, _ := r.Build(*config.Condition)
    thenValidator, _ := r.Build(*config.Then)
    elseValidator, _ := r.Build(*config.Else)

    return func(ctx *ValidationContext) *ValidationResult {
        origFieldIndex := ctx.FieldIndex

        if config.Condition.Field != "" {
            ctx.FieldIndex = ctx.Schema.FieldIndex[config.Condition.Field]
        }
        condResult := condition(ctx)

        var result *ValidationResult
        if condResult.Valid {
            if config.Then.Field != "" {
                ctx.FieldIndex = ctx.Schema.FieldIndex[config.Then.Field]
            }
            result = thenValidator(ctx)
        } else {
            if config.Else.Field != "" {
                ctx.FieldIndex = ctx.Schema.FieldIndex[config.Else.Field]
            }
            result = elseValidator(ctx)
        }

        ctx.FieldIndex = origFieldIndex

        if !result.Valid {
            return &ValidationResult{
                Valid:       false,
                ValidatorID: config.ID,
                Config:      &config,
                Record:      ctx.Record,
                Schema:      ctx.Schema,
            }
        }
        return &ValidationResult{Valid: true}
    }, nil
}
```

#### Nested Composition Example

For this config:
```yaml
- id: complex_rule
  compose: and
  validators:
    - id: value_is_1_or_2
      compose: or
      validators:
        - id: isEqual
          params: { value: 1 }
        - id: isEqual
          params: { value: 2 }
    - id: isNotEmpty
      field: RELATED_FIELD
```

Build order:
1. `Build(complex_rule)` → calls `buildAnd()`
2. `buildAnd()` iterates children:
   - `Build(value_is_1_or_2)` → calls `buildOr()`
     - `buildOr()` iterates children:
       - `Build(isEqual{value:1})` → returns simple validator
       - `Build(isEqual{value:2})` → returns simple validator
     - Returns composed OR validator
   - `Build(isNotEmpty)` → returns simple validator
3. Returns composed AND validator

Final structure (pseudocode):
```
AND(
  OR(isEqual(1), isEqual(2)),
  isNotEmpty(field: RELATED_FIELD)
)
```

### Error Messages

```go
// MessageRegistry - error message templates
type MessageRegistry struct {
    defaults  map[string]*template.Template  // validatorID -> template
    overrides map[string]*template.Template  // "schema:field:validator" -> template
}

// Template resolution order:
// 1. Rule-level override (inline in config)
// 2. Field-level override (schema:field:validator)
// 3. Schema-level override (schema:validator)
// 4. Default template (validator)

// ErrorGenerator - lazy error creation
type ErrorGenerator struct {
    messages  *MessageRegistry
    categories map[int]CategoryConfig
}

// GenerateError - called at WRITE time, not validation time
func (g *ErrorGenerator) GenerateError(result *ValidationResult) *ParserError
```

**Template variables available:**
- `{{.RecordType}}` - T1, T2, etc.
- `{{.ItemNum}}` - Federal spec item number
- `{{.FriendlyName}}` - Human-readable field name
- `{{.Value}}` - The actual value that failed
- `{{.Params.*}}` - Validator parameters (e.g., `{{.Params.min}}`)

### Validation Flow

```
                    ┌─────────────────────┐
                    │   ParsedGroup       │
                    │ (from accumulator)  │
                    └──────────┬──────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Validation Orchestrator                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│   1. Get ValidationContext from pool                              │
│   2. Set ctx.Group = parsedGroup                                  │
│                                                                   │
│   ┌─────────────────────────────────────────────────────────────┐ │
│   │  Cat 4: Group Validation                                     │ │
│   │  - Call each Cat 4 validator with ctx                        │ │
│   │  - If ANY fail AND short_circuit=true → reject group, done   │ │
│   └─────────────────────────────────────────────────────────────┘ │
│                               │                                   │
│                               ▼                                   │
│   ┌─────────────────────────────────────────────────────────────┐ │
│   │  For each record in group:                                   │ │
│   │                                                              │ │
│   │  Set ctx.Record, ctx.Schema                                  │ │
│   │                                                              │ │
│   │  ┌─────────────────────────────────────────────────────────┐│ │
│   │  │  Cat 1: Pre-parsing validation                          ││ │
│   │  │  - Call each Cat 1 validator                            ││ │
│   │  │  - If ANY fail AND short_circuit=true → skip Cat 2,3    ││ │
│   │  └─────────────────────────────────────────────────────────┘│ │
│   │                               │                              │ │
│   │                               ▼                              │ │
│   │  ┌─────────────────────────────────────────────────────────┐│ │
│   │  │  Cat 2: Field validation (per field)                    ││ │
│   │  │  For each field with validators:                        ││ │
│   │  │    - Set ctx.FieldIndex, ctx.FieldDef                   ││ │
│   │  │    - Call each validator for this field                 ││ │
│   │  │  - Collect all failures (no short-circuit within Cat 2) ││ │
│   │  └─────────────────────────────────────────────────────────┘│ │
│   │                               │                              │ │
│   │                               ▼                              │ │
│   │  ┌─────────────────────────────────────────────────────────┐│ │
│   │  │  Cat 3: Cross-field validation                          ││ │
│   │  │  - Call each Cat 3 validator                            ││ │
│   │  │  - Collect all failures                                 ││ │
│   │  └─────────────────────────────────────────────────────────┘│ │
│   │                                                              │ │
│   │  Aggregate record results                                    │ │
│   └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│   3. Return ValidationContext to pool                             │
│   4. Return GroupResult with valid records + failures             │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
                               │
                               ▼
              ┌────────────────┴────────────────┐
              │                                 │
              ▼                                 ▼
    ┌──────────────────┐            ┌──────────────────┐
    │  Valid Records   │            │ ValidationResults │
    │  → Record Writer │            │ → Error Generator │
    └──────────────────┘            │ → Error Writer    │
                                    └──────────────────┘
```

### Configuration Structure

**Schema YAML (Cat 1, 2, 3 validators):**
```yaml
# config/schemas/tanf/t1.yaml
name: t1
record_type: T1
model: tanf_t1

# Cat 1: Record-level pre-parsing validators
# Note: Generates RECORD_PRE_CHECK errors (PRE_CHECK is header-only)
category1:
  - id: recordHasLengthBetween
    params: { min: 117, max: 156 }
  - id: caseNumberNotEmpty
    params: { start: 8, end: 19 }
    message: "Case number cannot be blank"

fields:
  - name: RPT_MONTH_YEAR
    item: "4"
    friendly_name: "Reporting Month/Year"
    type: integer
    start: 2
    end: 8
    required: true
    # Cat 2: Field validators
    category2:
      - id: dateYearIsLargerThan
        params: { year: 1998 }
        message: "Year must be after 1998, got {{.Value}}"
      - id: dateMonthIsValid

  - name: CASE_NUMBER
    item: "6"
    friendly_name: "Case Number"
    type: string
    start: 8
    end: 19
    required: true
    category2:
      - id: isNotEmpty

# Cat 3: Cross-field validators
category3:
  - id: cash_requires_months
    compose: ifThen
    condition:
      id: isGreaterThan
      params: { value: 0 }
      field: CASH_AMOUNT
    then:
      id: isGreaterThan
      params: { value: 0 }
      field: NBR_MONTHS
    message: "When cash amount is positive, months must also be positive"
```

**Header schema (PRE_CHECK errors):**
```yaml
# config/schemas/common/header.yaml
name: header
record_type: HEADER

# Cat 1 for headers generates PRE_CHECK errors (not RECORD_PRE_CHECK)
category1:
  - id: recordStartsWith
    params: { prefix: "HEADER" }
    error_type: PRE_CHECK
```

**FileSpec YAML (Cat 4 validators):**
```yaml
# config/filespecs/tanf/s1.yaml
program: TANF
section: 1
format: positional

schemas:
  - common/header
  - tanf/t1
  - tanf/t2
  - tanf/t3
  - common/trailer

accumulator:
  key_fields:
    rpt_month_year: { start: 2, end: 8 }
    case_number: { start: 8, end: 19 }
  batch_size: 10
  sorted: true

# Cat 4: Group validators
category4:
  - id: recordTypePresent
    params: { record_type: T1, required: true }
  - id: t1HasMatchingChildren
    params: { child_types: [T2, T3] }
    message: "T1 record must have at least one T2 or T3 child"
```

**Orchestrator config (short-circuit rules):**
```yaml
# config/validation/orchestrator.yaml
categories:
  - id: 1
    name: Record pre-check
    default_error_type: RECORD_PRE_CHECK  # PRE_CHECK is header-only (override in schema)
  - id: 2
    name: Field validation
    default_error_type: FIELD_VALUE
  - id: 3
    name: Cross-field
    default_error_type: VALUE_CONSISTENCY
  - id: 4
    name: Group validation
    default_error_type: CASE_CONSISTENCY

execution_order: [4, 1, 2, 3]

short_circuit:
  - on_fail: 4
    action: reject_group
    skip: [1, 2, 3]
  - on_fail: 1
    action: reject_record
    skip: [2, 3]
```

### Parallel Validation

Groups are validated in parallel via the existing worker pool:

```
┌─────────────────────────────────────────────────────────────────┐
│                        Worker Pool                               │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│   │  Worker 1   │  │  Worker 2   │  │  Worker N   │             │
│   │             │  │             │  │             │             │
│   │  Group A    │  │  Group B    │  │  Group C    │             │
│   │  → Parse    │  │  → Parse    │  │  → Parse    │  (parallel) │
│   │  → Validate │  │  → Validate │  │  → Validate │             │
│   │  → Results  │  │  → Results  │  │  → Results  │             │
│   └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

- Each worker validates its assigned `ParsedGroup` independently
- No shared state between groups during validation
- `ValidationContext` is pooled per-worker (no contention)
- Results collected and written in batches

**Default error messages:**
```yaml
# config/validation/messages.yaml
validators:
  isGreaterThan:
    template: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must be greater than {{.Params.value}}"

  isOneOf:
    template: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} is not in allowed values {{.Params.values}}"

  dateMonthIsValid:
    template: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): month {{.Value}} is not valid (must be 01-12)"
```

### Package Structure

```
internal/validation/
├── types.go           # ValidationContext, ValidationResult, ValidatorFunc
├── context.go         # Context helper methods
├── pools.go           # Object pooling
├── orchestrator.go    # Main entry point, execution flow
├── registry/
│   ├── validators.go  # ValidatorRegistry
│   └── messages.go    # MessageRegistry
├── validators/
│   ├── comparison.go  # isEqual, isGreaterThan, etc.
│   ├── string.go      # isEmpty, hasLength, etc.
│   ├── date.go        # dateYearIsLargerThan, etc.
│   ├── record.go      # recordHasLength, etc.
│   ├── crossfield.go  # ifThenAlso, sumIsGreaterThan, etc.
│   ├── group.go       # recordTypePresent, t1HasMatchingChildren, etc.
│   └── compose.go     # And, Or, Not, IfThen composition
├── errors/
│   └── generator.go   # ErrorGenerator, ParserError
└── config/
    └── loader.go      # Load validation config from YAML
```

### Key Components

#### Orchestrator (`orchestrator.go`)

Central coordinator for validation execution.

```go
type Orchestrator struct {
    config        *OrchestratorConfig
    validators    *ValidatorRegistry
    messages      *MessageRegistry
    errorGen      *ErrorGenerator
    contextPool   *sync.Pool
    resultPool    *sync.Pool
}

// Main entry point - validates a parsed group
func (o *Orchestrator) ValidateGroup(group *ParsedGroup) *GroupValidationResult

// Internal methods
func (o *Orchestrator) validateCat4(ctx *ValidationContext) []*ValidationResult
func (o *Orchestrator) validateRecord(ctx *ValidationContext) []*ValidationResult
func (o *Orchestrator) validateCat1(ctx *ValidationContext) []*ValidationResult
func (o *Orchestrator) validateCat2(ctx *ValidationContext) []*ValidationResult
func (o *Orchestrator) validateCat3(ctx *ValidationContext) []*ValidationResult
func (o *Orchestrator) shouldShortCircuit(category int, failures []*ValidationResult) (skip []int, reject bool)
```

#### GroupValidationResult

```go
type GroupValidationResult struct {
    Rejected      bool                  // True if group rejected (Cat4 failure)
    ValidRecords  []*ParsedRecord       // Records that passed validation
    Errors        []*ValidationResult   // All validation failures (for lazy error gen)
}
```

#### ValidatorRegistry (`registry/validators.go`)

```go
type ValidatorRegistry struct {
    factories map[string]ValidatorFactory
}

func NewValidatorRegistry() *ValidatorRegistry
func (r *ValidatorRegistry) Register(id string, factory ValidatorFactory)
func (r *ValidatorRegistry) Get(id string) (ValidatorFactory, bool)
func (r *ValidatorRegistry) MustGet(id string) ValidatorFactory  // Panics if not found
func (r *ValidatorRegistry) List() []string
func (r *ValidatorRegistry) Build(config ValidatorConfig) (ValidatorFunc, error)  // Build from YAML config
```

#### MessageRegistry (`registry/messages.go`)

```go
type MessageRegistry struct {
    defaults  map[string]*template.Template  // validatorID -> template
    overrides map[string]*template.Template  // "schema:field:validator" -> template
}

func NewMessageRegistry() *MessageRegistry
func (r *MessageRegistry) RegisterDefault(validatorID string, tmpl string) error
func (r *MessageRegistry) RegisterOverride(key string, tmpl string) error
func (r *MessageRegistry) GetTemplate(validatorID, schemaPath, fieldName string) *template.Template
```

#### ErrorGenerator (`errors/generator.go`)

```go
type ErrorGenerator struct {
    messages   *MessageRegistry
    categories map[int]CategoryConfig
}

// Called at WRITE time, not during validation (lazy)
// Returns []any row ready for table writer (matches parser_error table columns)
func (g *ErrorGenerator) Generate(result *ValidationResult) []any

// Columns in order (matches existing parser_error table):
// row_number, column_number, item_number, field_name, case_number,
// rpt_month_year, error_message, error_type, created_at, fields_json,
// content_type_id, file_id, object_id, deprecated, values_json

func (g *ErrorGenerator) Generate(result *ValidationResult) []any {
    // 1. Resolve message template
    template := g.resolveTemplate(result)

    // 2. Build template context from result pointers
    ctx := g.buildTemplateContext(result)

    // 3. Render message
    message := template.Execute(ctx)

    // 4. Resolve error type
    errorType := g.resolveErrorType(result)

    // 5. Build fields/values JSON
    fieldsJSON := g.buildFieldsJSON(result)
    valuesJSON := g.buildValuesJSON(result)

    // 6. Return row ready for table writer
    return []any{
        result.Record.LineNumber,           // row_number
        result.FieldDef().Item,             // column_number
        result.FieldDef().Item,             // item_number
        result.FieldDef().Name,             // field_name
        result.Record.GetString("CASE_NUMBER"), // case_number
        result.Record.GetInt("RPT_MONTH_YEAR"), // rpt_month_year
        message,                            // error_message
        errorType,                          // error_type
        time.Now(),                         // created_at
        fieldsJSON,                         // fields_json
        nil,                                // content_type_id (set by writer)
        nil,                                // file_id (set by writer)
        nil,                                // object_id (set by writer)
        result.Config.Deprecated,           // deprecated
        valuesJSON,                         // values_json
    }
}
```

#### Config Loader (`config/loader.go`)

```go
// Load orchestrator config
func LoadOrchestratorConfig(path string) (*OrchestratorConfig, error)

// Called during schema loading to attach validators
func LoadSchemaValidators(schema *CompiledSchema, registry *ValidatorRegistry) error

// Called during filespec loading to attach Cat4 validators
func LoadFileSpecValidators(filespec *FileSpec, registry *ValidatorRegistry) error

type OrchestratorConfig struct {
    Categories     []CategoryConfig
    ExecutionOrder []int
    ShortCircuit   []ShortCircuitRule
}

type CategoryConfig struct {
    ID              int
    Name            string
    DefaultErrorType string
}

type ShortCircuitRule struct {
    OnFail int
    Action string  // "reject_record", "reject_group"
    Skip   []int
}
```

#### CompiledSchema Extension

The existing `CompiledSchema` will be extended to hold compiled validators:

```go
// In schema/types.go (existing file, extended)
type CompiledSchema struct {
    // ... existing fields ...

    // Validation (added)
    Cat1Validators []CompiledValidator
    Cat2Validators map[int][]CompiledValidator  // FieldIndex -> validators
    Cat3Validators []CompiledValidator
}

type CompiledValidator struct {
    Func      ValidatorFunc
    Config    *ValidatorConfig  // For message/error_type overrides
}
```

#### FileSpec Extension

```go
// In filespec/types.go (existing file, extended)
type FileSpec struct {
    // ... existing fields ...

    // Cat4 validators (added)
    Cat4Validators []CompiledValidator
}
```

### Integration Points

1. **Schema Loader** - After loading schema YAML, call `LoadSchemaValidators()` to compile Cat1/2/3 validators
2. **FileSpec Loader** - After loading filespec YAML, call `LoadFileSpecValidators()` to compile Cat4 validators
3. **Worker Pool** - After parsing a group, call `orchestrator.ValidateGroup(parsedGroup)`
4. **Router** - Route valid records to record writer, errors to error writer

---

# Python Parser Validation Architecture Analysis

## Overview

The Python TANF parser uses a multi-category validation system with tightly coupled validators and error messages. This document captures the current architecture to inform the Go parser redesign.

---

## Validation Categories

| Category | Name | When Applied | Signature |
|----------|------|--------------|-----------|
| Cat1 | Preparsing | Before field parsing, on raw row | `(row, eargs) -> Result` |
| Cat2 | Field Validation | After parsing, per field | `(value, eargs) -> Result` |
| Cat3 | Post-parsing | After all fields, cross-field | `(record, row_schema) -> Result` |
| Cat4 | Case Consistency | After entire case cached | Custom methods |

---

## Key Files

| Component | Path |
|-----------|------|
| Base Validators | `parsers/validators/base.py` |
| Category 1 | `parsers/validators/category1.py` |
| Category 2 | `parsers/validators/category2.py` |
| Category 3 | `parsers/validators/category3.py` |
| Row Schema | `parsers/row_schema.py` |
| Error Generator | `parsers/error_generator.py` |
| Case Consistency | `parsers/case_consistency_validator.py` |
| Main Parser | `parsers/parser_classes/tdr_parser.py` |

---

## Core Patterns

### 1. Validator Creation (`make_validator`)

```python
def make_validator(validator_func, error_func):
    def validator(value, eargs):
        if validator_func(value):
            return Result()
        return Result(valid=False, error_message=error_func(eargs))
    return validator
```

- Couples validation logic with error message generation
- Error messages are lambdas receiving `ValidationErrorArgs`

### 2. Base Validators (Primitives)

```python
@base_validator
def isEqual(option, **kwargs):
    return lambda val: val == option

@base_validator
def isOneOf(options, **kwargs):
    return lambda val: val in options

@base_validator
def isBetween(min, max, inclusive=False, **kwargs):
    return lambda val: min <= val <= max if inclusive else min < val < max
```

### 3. Category Wrappers

```python
# Category 2 example
@validator(base.isOneOf)
def isOneOf(options, **kwargs):
    return lambda eargs: f"{format_error_context(eargs)} {eargs.value} is not in {options}."
```

### 4. Result Dataclass

```python
@dataclass
class Result:
    valid: bool = True
    error_message: str | None = None
    field_names: list = field(default_factory=list)  # For cross-field validators
    deprecated: bool = False
```

---

## Validation Execution Flow

```
parse_row(raw_row)
    |
    v
run_preparsing_validators(row, record)  [Cat1]
    |
    +--> If fails & quiet: return (None, True, [])  # Silent discard
    +--> If fails: return (None, False, errors)     # Early termination
    |
    v
run_field_validators(record, row_num)  [Cat2]
    |
    v
run_postparsing_validators(record, row_num)  [Cat3]
    |
    v
Return SchemaResult(record, is_valid, errors)
    |
    v
case_consistency_validator.add_record()  [Cat4 - deferred]
    |
    +--> When new case detected: validate previous case
```

---

## Error Generation

### ErrorGeneratorFactory

Creates type-specific generators:
- `PRE_CHECK` - File-level pre-check errors
- `RECORD_PRE_CHECK` - Row-level pre-check errors
- `FIELD_VALUE` - Cat2 field validation errors
- `VALUE_CONSISTENCY` - Cat3 cross-field errors
- `CASE_CONSISTENCY` - Cat4 case-level errors

### ParserError Model Fields

```python
- file: ForeignKey to DataFile
- row_number: int
- column_number, item_number: str
- field_name: str
- error_message: str (max 512)
- error_type: Category choice
- fields_json: JSON metadata
- values_json: JSON of actual values
- deprecated: bool
```

---

## Schema Definition Pattern

```python
TanfDataReportSchema(
    record_type="T1",
    model=TANF_T1,
    preparsing_validators=[           # Cat1
        category1.recordHasLength(156),
        category1.caseNumberNotEmpty(8, 19),
    ],
    postparsing_validators=[          # Cat3
        category3.ifThenAlso(...),
        category3.sumIsLarger([...], 0),
    ],
    fields=[
        Field(
            name="CASE_NUMBER",
            validators=[              # Cat2
                category2.isNotEmpty(),
            ],
        ),
    ],
)
```

---

## Identified Issues (User-Provided)

1. Code change required to add new error message/validator
2. Adding new validators/errors is complex
3. Debugging validators is difficult
4. Categories lack unified interface
5. No registry of all error messages/templates
6. No validation hierarchy/short-circuiting between categories
7. Validation is synchronous (not parallel)
8. Cannot define custom error templates for one-off cases
9. Error messages and validators tightly coupled
10. ParserErrors could use lazy evaluation
11. Would benefit from object pooling
12. Hard to add new validation categories/stages
13. Not composable/no validator pipelines

---

## Additional Issues Identified

1. **Inconsistent signatures**: Cat1/Cat2 use `(value, eargs)`, Cat3 uses `(record, schema)`
2. **Circular import issues**: Multiple files note this in comments
3. **Lambda messages non-serializable**: Can't inspect or log message templates
4. **Django model coupling**: Validators depend on ORM models
5. **Duplicated format_error_context()**: Each category file has its own
6. **Hard-coded batch sizes**: No configuration for validation behavior
7. **Confusing quiet_preparser_errors**: Inconsistent silent discard mechanism
8. **Eager error generation**: Errors created during validation, not deferred
9. **No validation result aggregation**: No summary statistics
10. **OOM protection is reactive**: Case size limits checked after accumulation
11. **No validator introspection**: Can't list all validators or their rules
12. **Error categories conflated with validation phases**: PRE_CHECK vs RECORD_PRE_CHECK confusion

---

## Short-Circuit Behaviors

| Condition | Behavior |
|-----------|----------|
| Header validation fails | Entire parsing stops |
| Multiple headers detected | Rollback and stop |
| No headers found | Rollback and stop |
| Preparsing fails (quiet=true) | Silent discard, continue |
| Preparsing fails (quiet=false) | Record rejected, errors logged |
| Cat2/Cat3 fails | Record still cached, errors logged |
| Cat4 fails | Case marked for deletion after bulk create |
| OOM case overflow | Case marked for deletion |
