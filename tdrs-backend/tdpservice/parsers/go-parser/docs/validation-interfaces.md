# Go Validation Architecture - Part 2: Extensibility and Interfaces

## 8. Strategy for Configurability and Extensibility

### 8.1 Adding a New Validator (No Code Changes)

Most validators can be added purely through configuration by composing existing base validators:

```yaml
# config/validation/rules/tanf/t1.yaml
category2:
  fields:
    NEW_FIELD:
      - validator: isInRange        # Existing validator
        params:
          min: 1
          max: 99

      - validator: isNotOneOf       # Existing validator
        params:
          values: [0, 100]
```

### 8.2 Adding a New Base Validator (Code Change)

When a truly new validation function is needed:

1. **Implement the validator function** in the appropriate validators file:

```go
// internal/validation/validators/numeric.go

func init() {
    // Register at package initialization
    Register("isMultipleOf", IsMultipleOf)
}

// IsMultipleOf returns a validator that checks if value is a multiple of divisor
func IsMultipleOf(params map[string]any) ValidatorFunc {
    divisor := params["divisor"].(int)

    // Return unified ValidatorFunc signature
    return func(ctx *ValidationContext) *ValidationResult {
        // Get value from context (Cat 2 uses FieldValue())
        value := ctx.FieldValue()
        num, ok := toInt(value)
        if !ok {
            return &ValidationResult{
                Valid:       false,
                ValidatorID: "isMultipleOf",
                Category:    2,
                FieldIndex:  ctx.FieldIndex,
                FailReason:  "not_a_number",
                Record:      ctx.Record,
                Schema:      ctx.Schema,
            }
        }

        if num%divisor != 0 {
            return &ValidationResult{
                Valid:       false,
                ValidatorID: "isMultipleOf",
                Category:    2,
                FieldIndex:  ctx.FieldIndex,
                Record:      ctx.Record,
                Schema:      ctx.Schema,
            }
        }

        return &ValidationResult{Valid: true}
    }
}
```

2. **Add error message template**:

```yaml
# config/validation/messages/category2.yaml
validators:
  isMultipleOf:
    template: "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must be a multiple of {{.Divisor}}."
```

3. **Use in schema validation rules**:

```yaml
# config/validation/rules/tanf/t1.yaml
category2:
  fields:
    SOME_FIELD:
      - validator: isMultipleOf
        params:
          divisor: 5
```

### 8.3 Adding a New Validation Category (e.g., Category 5)

The architecture supports adding new categories with minimal changes:

1. **Define category in orchestrator config**:

```yaml
# config/validation/orchestrator.yaml
categories:
  - id: 5
    name: "File-Level Validation"
    scope: file                    # NEW scope type
    description: "Validates relationships across entire file"

execution_order:
  - category: 5                    # New category
    scope: file
  - category: 4
    scope: group
  - category: 1
    scope: record
  - category: 2
    scope: field
  - category: 3
    scope: record

short_circuit_rules:
  - on_category_fail: 5
    action: reject_file            # New action type
    skip_categories: [1, 2, 3, 4]
```

2. **Implement category engine** (if new scope type):

```go
// internal/validation/engines/file_engine.go

type FileLevelEngine struct {
    validators []ValidatorFunc
}

func (e *FileLevelEngine) Validate(ctx *ValidationContext, records []*schema.ParsedRecord) *CategoryResult {
    // File-level validation logic
    // e.g., total record counts, cross-section consistency
}
```

3. **Register engine with orchestrator**:

```go
// internal/validation/orchestrator.go

func (o *Orchestrator) registerEngines() {
    o.engines[1] = NewRecordEngine(CategoryPreParsing)
    o.engines[2] = NewFieldEngine()
    o.engines[3] = NewRecordEngine(CategoryCrossField)
    o.engines[4] = NewGroupEngine()
    o.engines[5] = NewFileEngine()  // NEW
}
```

4. **Add validators for new category**:

```yaml
# config/validation/rules/tanf/file.yaml
category5:
  - validator: totalRecordsMatchTrailer
    params:
      trailer_field: TOTAL_RECORDS

  - validator: sectionsAreComplete
    params:
      required_sections: [1, 2, 3, 4]
```

### 8.4 Category Scope Types

| Scope | Input | Parallelism | Example Validators |
|-------|-------|-------------|-------------------|
| `field` | Single field value | Per-field within record | isInRange, isOneOf |
| `record` | ParsedRecord | Per-record | recordHasLength, ifThenAlso |
| `group` | []ParsedRecord (same case) | Per-group | t1HasMatchingT2, familyAffiliation |
| `file` | All records in file | Sequential | recordCountMatchesTrailer |

---

## 9. Go Interface Definitions

### 9.1 Unified Validator Interface

```go
// internal/validation/types.go

// ValidatorFunc is the unified signature for ALL category validators.
// Validators access only what they need from the context.
type ValidatorFunc func(ctx *ValidationContext) *ValidationResult

// ValidatorFactory creates a configured ValidatorFunc from YAML parameters.
type ValidatorFactory func(params map[string]any) ValidatorFunc
```

### 9.2 Validation Context (Pooled)

The context is minimal - no redundant structs. Validators access what they need directly.
All pointers reference existing objects; no data is copied.

```go
// internal/validation/types.go

// ValidationContext provides inputs for all validator categories.
// Validators access only what's relevant to their category.
// Pooled and reused to minimize GC pressure.
type ValidationContext struct {
    // Shared across all categories (set once per file)
    DatafileID  int32
    ParseCtx    *schema.ParseContext  // Existing struct: Year, Quarter, IsEncrypted

    // Row/Field/Record categories (Cat 1, 2, 3)
    Row         decoder.Row              // Raw row data
    Schema      *schema.CompiledSchema   // Record schema (has FieldDefs)
    Record      *schema.ParsedRecord     // Parsed record (nil for Cat 1)

    // Field category only (Cat 2)
    FieldIndex  int                      // Index into Record.Fields and Schema.Fields
    FieldDef    *schema.FieldDef         // Pointer to field definition

    // Group category only (Cat 4)
    Group       *processor.RecordGroup   // Existing struct: Key, KeyFields, Lines
    FileSpec    *filespec.FileSpec       // File specification
}

// Reset clears the context for reuse from pool.
// DatafileID and ParseCtx are kept (same for entire file).
func (c *ValidationContext) Reset() {
    c.Row = nil
    c.Schema = nil
    c.Record = nil
    c.FieldIndex = 0
    c.FieldDef = nil
    c.Group = nil
    c.FileSpec = nil
}

// FieldValue returns the current field's value (Cat 2 convenience method)
func (c *ValidationContext) FieldValue() any {
    if c.Record == nil || c.FieldIndex < 0 {
        return nil
    }
    return c.Record.Fields[c.FieldIndex]
}
```

**What validators access by category:**

| Category | Context Fields Used |
|----------|---------------------|
| Cat 1 (Row) | `Row`, `Schema` |
| Cat 2 (Field) | `Record.Fields[FieldIndex]`, `FieldDef`, `Schema` |
| Cat 3 (Record) | `Record`, `Schema` |
| Cat 4 (Group) | `Group`, `FileSpec` |

### 9.3 Validation Result (Pooled, Lazy Error Generation)

ValidationResult captures failure info with pointers to existing data.
Error messages are rendered lazily at write time, not during validation.

```go
// internal/validation/types.go

// ValidationResult represents a validator outcome.
// For failures, stores pointers for lazy error rendering.
// Pooled and reused to minimize allocations.
type ValidationResult struct {
    Valid       bool

    // Populated on failure (for lazy error generation)
    ValidatorID string
    Category    int
    FieldIndex  int                      // Cat 2 only, -1 otherwise
    FailReason  string                   // Optional: multi-mode validators
    Rule        *RuleConfig              // Pointer to rule config (has params, message override)

    // Pointers to context at time of failure (for lazy rendering)
    Record      *schema.ParsedRecord     // For line number, field values
    Schema      *schema.CompiledSchema   // For field metadata
    Group       *processor.RecordGroup   // For CASE_NUMBER, RPT_MONTH_YEAR
}

// Reset clears the result for reuse from pool.
func (r *ValidationResult) Reset() {
    r.Valid = false
    r.ValidatorID = ""
    r.Category = 0
    r.FieldIndex = -1
    r.FailReason = ""
    r.Rule = nil
    r.Record = nil
    r.Schema = nil
    r.Group = nil
}

// LineNumber derives line number from the record.
func (r *ValidationResult) LineNumber() int {
    if r.Record != nil {
        return r.Record.LineNumber
    }
    return 0
}

// FieldDef returns the field definition for Cat 2 errors.
func (r *ValidationResult) FieldDef() *schema.FieldDef {
    if r.Schema != nil && r.FieldIndex >= 0 {
        return r.Schema.Fields[r.FieldIndex]
    }
    return nil
}
```

### 9.4 Object Pools (Prewarmable)

Pools minimize GC pressure during high-throughput validation.
Modeled after the existing ParsedRecord pool.

```go
// internal/validation/pools.go

// ValidationContextPool manages reusable ValidationContext objects.
type ValidationContextPool struct {
    pool sync.Pool
}

func NewValidationContextPool() *ValidationContextPool {
    return &ValidationContextPool{
        pool: sync.Pool{
            New: func() any {
                return &ValidationContext{FieldIndex: -1}
            },
        },
    }
}

func (p *ValidationContextPool) Get() *ValidationContext {
    return p.pool.Get().(*ValidationContext)
}

func (p *ValidationContextPool) Put(ctx *ValidationContext) {
    ctx.Reset()
    p.pool.Put(ctx)
}

// Prewarm allocates n contexts upfront to avoid allocation during hot path.
func (p *ValidationContextPool) Prewarm(n int) {
    contexts := make([]*ValidationContext, n)
    for i := 0; i < n; i++ {
        contexts[i] = p.Get()
    }
    for i := 0; i < n; i++ {
        p.Put(contexts[i])
    }
}

// ValidationResultPool manages reusable ValidationResult objects.
type ValidationResultPool struct {
    pool sync.Pool
}

func NewValidationResultPool() *ValidationResultPool {
    return &ValidationResultPool{
        pool: sync.Pool{
            New: func() any {
                return &ValidationResult{FieldIndex: -1}
            },
        },
    }
}

func (p *ValidationResultPool) Get() *ValidationResult {
    return p.pool.Get().(*ValidationResult)
}

func (p *ValidationResultPool) Put(r *ValidationResult) {
    r.Reset()
    p.pool.Put(r)
}

func (p *ValidationResultPool) Prewarm(n int) {
    results := make([]*ValidationResult, n)
    for i := 0; i < n; i++ {
        results[i] = p.Get()
    }
    for i := 0; i < n; i++ {
        p.Put(results[i])
    }
}
```

### 9.5 Category Engine Interface

```go
// internal/validation/engine.go

// CategoryEngine executes validation for a specific category.
type CategoryEngine interface {
    // Category returns the category ID (1, 2, 3, 4, ...)
    Category() int

    // Validate runs all validators for this category.
    // Returns failed ValidationResults (valid results are not returned).
    Validate(ctx *ValidationContext) []*ValidationResult
}
```

### 9.6 Orchestrator

```go
// internal/validation/orchestrator.go

// Orchestrator coordinates validation across categories.
type Orchestrator struct {
    config       *OrchestratorConfig
    engines      map[int]CategoryEngine
    validatorReg *ValidatorRegistry
    messageReg   *MessageRegistry

    // Pools for reuse
    ctxPool      *ValidationContextPool
    resultPool   *ValidationResultPool
}

// OrchestratorConfig defines category ordering, short-circuit rules, and defaults.
type OrchestratorConfig struct {
    Categories        []CategoryConfig
    ExecutionOrder    []int              // e.g., [4, 1, 2, 3]
    ShortCircuitRules []ShortCircuitRule
}

// CategoryConfig defines a validation category and its defaults.
type CategoryConfig struct {
    ID               int       `yaml:"id"`
    Name             string    `yaml:"name"`
    DefaultErrorType ErrorType `yaml:"default_error_type"`
    Description      string    `yaml:"description,omitempty"`
}

type ShortCircuitRule struct {
    OnCategoryFail  int
    Action          ShortCircuitAction
    SkipCategories  []int
}

type ShortCircuitAction int

const (
    ActionContinue ShortCircuitAction = iota
    ActionRejectRecord
    ActionRejectGroup
    ActionRejectFile
)

// ValidateGroup is the main entry point for validation
func (o *Orchestrator) ValidateGroup(ctx context.Context, group *processor.RecordGroup) *GroupResult

// ValidateBatch validates multiple groups (called from worker pool)
func (o *Orchestrator) ValidateBatch(ctx context.Context, batch *processor.Batch) *BatchResult
```

### 9.7 Validator Registry

```go
// internal/validation/registry/validators.go

// ValidatorRegistry manages validator registration and lookup
type ValidatorRegistry struct {
    factories map[string]ValidatorFactory
}

// Register adds a validator factory to the registry
func (r *ValidatorRegistry) Register(id string, factory ValidatorFactory)

// Get retrieves a validator factory by ID
func (r *ValidatorRegistry) Get(id string) (ValidatorFactory, bool)

// CreateValidator creates a configured validator from a rule config
func (r *ValidatorRegistry) CreateValidator(rule *RuleConfig) (ValidatorFunc, error)

// RuleConfig represents a validation rule from YAML
type RuleConfig struct {
    Validator       string         `yaml:"validator"`
    Params          map[string]any `yaml:"params"`

    // Inline overrides - highest priority
    Message         string         `yaml:"message,omitempty"`          // Single-line message template
    MessageTemplate string         `yaml:"message_template,omitempty"` // Multi-line message template
    ErrorType       ErrorType      `yaml:"error_type,omitempty"`       // Override category default

    // Metadata
    Deprecated      bool           `yaml:"deprecated,omitempty"`
}

// HasMessageOverride returns true if this rule has an inline message override
func (r *RuleConfig) HasMessageOverride() bool {
    return r.Message != "" || r.MessageTemplate != ""
}

// GetMessageTemplate returns the message template, preferring MessageTemplate over Message
func (r *RuleConfig) GetMessageTemplate() string {
    if r.MessageTemplate != "" {
        return r.MessageTemplate
    }
    return r.Message
}

// HasErrorTypeOverride returns true if this rule overrides the category error type
func (r *RuleConfig) HasErrorTypeOverride() bool {
    return r.ErrorType != ""
}
```

### 9.8 Message Registry and Error Engine (Lazy Rendering)

```go
// internal/validation/registry/messages.go

// MessageRegistry manages error message templates with hierarchical lookup
type MessageRegistry struct {
    // Default templates by validator ID
    defaults map[string]*template.Template

    // Schema-level overrides: "schemaPath:validatorID" -> template
    schemaOverrides map[string]*template.Template

    // Field-level overrides: "schemaPath:fieldName:validatorID" -> template
    fieldOverrides map[string]*template.Template
}

// GetTemplate retrieves the most specific template for a validation failure.
// Lookup priority (highest to lowest):
//   1. Field-level override: overrides[schema][field][validator]
//   2. Schema-level override: overrides[schema][validator]
//   3. Default validator template: validators[validatorID]
func (r *MessageRegistry) GetTemplate(validatorID, schemaPath, fieldName string) *template.Template {
    // Priority 1: Field-level override
    fieldKey := fmt.Sprintf("%s:%s:%s", schemaPath, fieldName, validatorID)
    if tmpl, ok := r.fieldOverrides[fieldKey]; ok {
        return tmpl
    }

    // Priority 2: Schema-level override
    schemaKey := fmt.Sprintf("%s:%s", schemaPath, validatorID)
    if tmpl, ok := r.schemaOverrides[schemaKey]; ok {
        return tmpl
    }

    // Priority 3: Default template
    return r.defaults[validatorID]
}

// internal/validation/errors/engine.go

// ErrorEngine generates ParserError objects from ValidationResults.
// All data is derived from the pointers stored in ValidationResult (lazy rendering).
type ErrorEngine struct {
    messageReg      *MessageRegistry
    categoryConfigs map[int]*CategoryConfig  // For default error types
}

// GenerateError creates a ParserError from a ValidationResult.
// Called at write time, NOT during validation (lazy rendering).
// All context is derived from pointers stored in the ValidationResult.
//
// Resolution order for message template:
//   1. result.Rule.Message or result.Rule.MessageTemplate (inline override)
//   2. MessageRegistry lookup (schema/field/validator hierarchy)
// Resolution order for error type:
//   1. result.Rule.ErrorType (inline override)
//   2. CategoryConfig.DefaultErrorType
//   3. Built-in default for category
func (e *ErrorEngine) GenerateError(result *ValidationResult) *ParserError {
    rule := result.Rule

    // Derive field info from result pointers (lazy)
    var fieldDef *schema.FieldDef
    var fieldName, itemNumber string
    if result.FieldIndex >= 0 && result.Schema != nil {
        fieldDef = result.Schema.Fields[result.FieldIndex]
        fieldName = fieldDef.Name
        itemNumber = fieldDef.ItemNumber
    }

    // Derive schema path from result pointer
    var schemaPath string
    if result.Schema != nil {
        schemaPath = result.Schema.Path
    }

    // Resolve message template
    var tmpl *template.Template
    if rule != nil && rule.HasMessageOverride() {
        tmpl = template.Must(template.New("inline").Parse(rule.GetMessageTemplate()))
    } else {
        tmpl = e.messageReg.GetTemplate(result.ValidatorID, schemaPath, fieldName)
    }

    // Resolve error type
    errorType := e.resolveErrorType(result.Category, rule)

    // Build template context from result pointers and render message
    message := e.renderTemplate(tmpl, result, fieldDef)

    // Derive line number from record pointer
    var rowNumber int
    if result.Record != nil {
        rowNumber = result.Record.LineNumber
    }

    // Derive group key fields from group pointer
    var rptMonthYear, caseNumber string
    if result.Group != nil {
        rptMonthYear = result.Group.KeyFields["RPT_MONTH_YEAR"]
        caseNumber = result.Group.KeyFields["CASE_NUMBER"]
    }

    pe := &ParserError{
        RowNumber:    rowNumber,
        ColumnNumber: itemNumber,
        ItemNumber:   itemNumber,
        FieldName:    fieldName,
        RptMonthYear: rptMonthYear,
        CaseNumber:   caseNumber,
        ErrorMessage: message,
        ErrorType:    errorType,
        Category:     result.Category,
        ValidatorID:  result.ValidatorID,
        SchemaPath:   schemaPath,
        FieldsJSON:   e.buildFieldsJSON(result),
        ValuesJSON:   e.buildValuesJSON(result),
    }

    if rule != nil {
        pe.Deprecated = rule.Deprecated
    }

    return pe
}

// resolveErrorType determines the error type using the override hierarchy
func (e *ErrorEngine) resolveErrorType(category int, rule *RuleConfig) ErrorType {
    // Priority 1: Rule-level override
    if rule.HasErrorTypeOverride() {
        return rule.ErrorType
    }

    // Priority 2: Category default
    if cfg, ok := e.categoryConfigs[category]; ok && cfg.DefaultErrorType != "" {
        return cfg.DefaultErrorType
    }

    // Priority 3: Built-in defaults
    switch category {
    case 1:
        return ErrorTypePreCheck
    case 2:
        return ErrorTypeFieldValue
    case 3:
        return ErrorTypeValueConsistency
    case 4:
        return ErrorTypeCaseConsistency
    default:
        return ErrorType(fmt.Sprintf("CATEGORY_%d", category))
    }
}

// ParserError represents a validation error to be persisted
type ParserError struct {
    RowNumber     int
    ColumnNumber  string
    ItemNumber    string
    FieldName     string
    RptMonthYear  string
    CaseNumber    string
    ErrorMessage  string
    ErrorType     ErrorType  // Resolved from rule -> category -> default
    Category      int
    ValidatorID   string     // Use this for debugging (lookup rule config by validator ID)
    SchemaPath    string
    FieldsJSON    map[string]any
    ValuesJSON    map[string]any
    Deprecated    bool
}

// ErrorType represents the classification of a validation error
type ErrorType string

const (
    ErrorTypePreCheck         ErrorType = "PRE_CHECK"
    ErrorTypeFieldValue       ErrorType = "FIELD_VALUE"
    ErrorTypeValueConsistency ErrorType = "VALUE_CONSISTENCY"
    ErrorTypeCaseConsistency  ErrorType = "CASE_CONSISTENCY"
    // Custom error types can be defined in config
)
```

---

## 10. Built-in Validator Signatures

### 10.1 Comparison Validators

```go
// internal/validation/validators/comparison.go

// IsEqual checks if value equals expected
func IsEqual(params map[string]any) ValidatorFunc
// params: {"value": any}

// IsNotEqual checks if value does not equal expected
func IsNotEqual(params map[string]any) ValidatorFunc
// params: {"value": any}

// IsGreaterThan checks if value > threshold
func IsGreaterThan(params map[string]any) ValidatorFunc
// params: {"value": int|float, "inclusive": bool}

// IsLessThan checks if value < threshold
func IsLessThan(params map[string]any) ValidatorFunc
// params: {"value": int|float, "inclusive": bool}

// IsBetween checks if value is within range
func IsBetween(params map[string]any) ValidatorFunc
// params: {"min": int|float, "max": int|float, "inclusive": bool}

// IsOneOf checks if value is in allowed set
func IsOneOf(params map[string]any) ValidatorFunc
// params: {"values": []any}

// IsNotOneOf checks if value is not in forbidden set
func IsNotOneOf(params map[string]any) ValidatorFunc
// params: {"values": []any}
```

### 10.2 String Validators

```go
// internal/validation/validators/string.go

// HasLength checks exact string length
func HasLength(params map[string]any) ValidatorFunc
// params: {"length": int}

// HasLengthBetween checks string length in range
func HasLengthBetween(params map[string]any) ValidatorFunc
// params: {"min": int, "max": int}

// StartsWith checks string prefix
func StartsWith(params map[string]any) ValidatorFunc
// params: {"prefix": string}

// EndsWith checks string suffix
func EndsWith(params map[string]any) ValidatorFunc
// params: {"suffix": string}

// MatchesPattern checks regex match
func MatchesPattern(params map[string]any) ValidatorFunc
// params: {"pattern": string}

// IsEmpty checks if value is empty or blank
func IsEmpty(params map[string]any) ValidatorFunc
// params: {}

// IsNotEmpty checks if value is not empty
func IsNotEmpty(params map[string]any) ValidatorFunc
// params: {}
```

### 10.3 Type Validators

```go
// internal/validation/validators/type.go

// IsNumeric checks if value is a valid number
func IsNumeric(params map[string]any) ValidatorFunc
// params: {}

// IsAlphanumeric checks if value contains only alphanumeric chars
func IsAlphanumeric(params map[string]any) ValidatorFunc
// params: {}

// IsAlpha checks if value contains only letters
func IsAlpha(params map[string]any) ValidatorFunc
// params: {}
```

### 10.4 Date Validators

```go
// internal/validation/validators/date.go

// DateYearIsLargerThan checks year component > threshold
func DateYearIsLargerThan(params map[string]any) ValidatorFunc
// params: {"year": int}

// DateMonthIsValid checks month is 01-12
func DateMonthIsValid(params map[string]any) ValidatorFunc
// params: {}

// DateDayIsValid checks day is valid for month
func DateDayIsValid(params map[string]any) ValidatorFunc
// params: {}

// QuarterIsValid checks quarter is 1-4
func QuarterIsValid(params map[string]any) ValidatorFunc
// params: {}

// IsValidDate checks full date validity
func IsValidDate(params map[string]any) ValidatorFunc
// params: {"format": string}  // e.g., "YYYYMMDD"
```

### 10.5 Category 1 Validators (Pre-Parsing)

```go
// internal/validation/validators/category1.go

// RecordHasLength checks exact record length
func RecordHasLength(params map[string]any) ValidatorFunc
// params: {"length": int}

// RecordHasLengthBetween checks record length in range
func RecordHasLengthBetween(params map[string]any) ValidatorFunc
// params: {"min": int, "max": int}

// CaseNumberNotEmpty checks case number field is not blank
func CaseNumberNotEmpty(params map[string]any) ValidatorFunc
// params: {"start": int, "end": int}

// RecordStartsWith checks record type prefix
func RecordStartsWith(params map[string]any) ValidatorFunc
// params: {"prefix": string}

// ValidateRptMonthYear checks RPT_MONTH_YEAR format and value
func ValidateRptMonthYear(params map[string]any) ValidatorFunc
// params: {"start": int, "end": int}
```

### 10.6 Category 3 Validators (Cross-Field)

```go
// internal/validation/validators/category3.go

// IfThenAlso checks conditional field relationships
func IfThenAlso(params map[string]any) ValidatorFunc
// params: {
//   "condition_field": string,
//   "condition": string,        // validator name
//   "condition_value": any,
//   "result_field": string,
//   "result": string,           // validator name
//   "result_value": any
// }

// SumIsGreaterThan checks sum of fields exceeds threshold
func SumIsGreaterThan(params map[string]any) ValidatorFunc
// params: {"fields": []string, "threshold": int|float}

// AtLeastOneOf checks at least one field has value
func AtLeastOneOf(params map[string]any) ValidatorFunc
// params: {"fields": []string}

// MutuallyExclusive checks only one field has value
func MutuallyExclusive(params map[string]any) ValidatorFunc
// params: {"fields": []string}
```

### 10.7 Category 4 Validators (Group-Level)

```go
// internal/validation/validators/category4.go

// T1HasMatchingChildren checks T1 has related T2 or T3
func T1HasMatchingChildren(params map[string]any) ValidatorFunc
// params: {"child_types": []string}

// ChildHasParent checks T2/T3 has related T1
func ChildHasParent(params map[string]any) ValidatorFunc
// params: {"parent_type": string}

// FamilyAffiliationRequired checks family affiliation rules
func FamilyAffiliationRequired(params map[string]any) ValidatorFunc
// params: {"affiliation_field": string, "required_value": int}

// RecordCountInRange checks group has expected record count
func RecordCountInRange(params map[string]any) ValidatorFunc
// params: {"record_type": string, "min": int, "max": int}
```

---

## 11. Observability and Debugging

### 11.1 Structured Logging

Logging derives context from ValidationResult pointers (consistent with lazy rendering).

```go
// internal/validation/logging.go

type ValidationLogger struct {
    logger *slog.Logger
}

// LogValidatorFailure logs validation failure with context derived from result pointers
func (l *ValidationLogger) LogValidatorFailure(result *ValidationResult, err *ParserError) {
    // Derive schema path
    var schemaPath string
    if result.Schema != nil {
        schemaPath = result.Schema.Path
    }

    // Derive field name for Cat 2
    var fieldName string
    if result.FieldIndex >= 0 && result.Schema != nil {
        fieldName = result.Schema.Fields[result.FieldIndex].Name
    }

    l.logger.Info("validation failed",
        "validator_id", result.ValidatorID,
        "category", result.Category,
        "line_number", result.LineNumber(),  // Helper method on ValidationResult
        "schema_path", schemaPath,
        "field_name", fieldName,
        "error_message", err.ErrorMessage,
    )
}
```

### 11.2 Debugging with ValidatorID

When debugging validation failures, use the `ValidatorID` field to look up the rule configuration:

```go
// Given an error with ValidatorID = "isInRange"
// Look up in: config/validation/rules/{program}/{schema}.yaml
// Search for: "validator: isInRange"

// The validator ID uniquely identifies:
// - The validation logic (in validators/*.go)
// - The default message template (in config/validation/messages/*.yaml)
// - All usages in rule configs (searchable by validator ID)
```

### 11.3 Validation Trace

For debugging complex validation flows, enable tracing:

```go
// Enable trace mode via config
config:
  validation:
    trace_enabled: true
    trace_sample_rate: 0.01  # Sample 1% of records

// Trace output
{
    "trace_id": "abc123",
    "line_number": 42,
    "schema_path": "tanf/t1",
    "stages": [
        {"category": 4, "validators_run": ["t1HasMatchingChildren"], "passed": true, "duration_us": 150},
        {"category": 1, "validators_run": ["recordHasLength"], "passed": true, "duration_us": 12},
        {"category": 2, "validators_run": ["isInRange", "dateMonthIsValid", ...], "passed": false, "failures": ["isInRange"], "duration_us": 89},
        {"category": 3, "validators_run": ["ifThenAlso"], "passed": true, "duration_us": 23}
    ],
    "total_duration_us": 274,
    "result": "invalid",
    "error_count": 1
}
```

---

## 12. Integration with Existing Pipeline

### 12.1 Modified Pipeline Flow

```go
// internal/pipeline/pipeline.go

func (p *Pipeline) ProcessFile(ctx context.Context, params ProcessParams) (*ProcessResult, error) {
    // 1. Load filespec and schemas (existing)
    filespec := p.registry.GetFileSpec(params.Program, params.Section)

    // 2. Create decoder (existing)
    decoder := p.createDecoder(filespec, params.FilePath)

    // 3. Create accumulator (existing)
    accumulator := processor.NewAccumulator(filespec.Accumulator)

    // 4. Create validation orchestrator (NEW)
    orchestrator := validation.NewOrchestrator(
        p.validationConfig,
        p.validatorRegistry,
        p.messageRegistry,
    )

    // 5. Create worker pool with validation (MODIFIED)
    pool := worker.NewPool(worker.Config{
        NumWorkers: p.config.NumWorkers,
        WorkQueue:  p.config.WorkQueueSize,
        ResultQueue: p.config.ResultQueueSize,

        // NEW: Pass orchestrator to workers
        Orchestrator: orchestrator,
    })

    // 6. Create writers (existing + error writer)
    router := writer.NewRouter(p.db, p.registry)
    errorWriter := writer.NewErrorWriter(p.db, params.DatafileID)

    // 7. Process file (existing flow, validation integrated in workers)
    // ...
}
```

### 12.2 Modified Worker

```go
// internal/worker/pool.go

func (w *Worker) processGroup(group *processor.RecordGroup) *worker.ParsedBatch {
    // 1. Parse all records in group (existing)
    parsedRecords := w.parseRecords(group)

    // 2. Validate group (NEW)
    validationResult := w.orchestrator.ValidateGroup(w.ctx, group, parsedRecords)

    // 3. Separate valid and invalid records
    var validRecords []*schema.ParsedRecord
    var errors []*validation.ParserError

    if validationResult.Rejected {
        // Entire group rejected (Cat 4 failure)
        errors = append(errors, validationResult.GroupErrors()...)
    } else {
        for _, recordResult := range validationResult.RecordResults {
            if recordResult.Valid {
                validRecords = append(validRecords, recordResult.Record)
            }
            errors = append(errors, recordResult.Errors...)
        }
    }

    return &worker.ParsedBatch{
        Records: validRecords,
        Errors:  errors,
    }
}
```

---

## 13. Summary

This architecture provides:

| Requirement | Solution |
|-------------|----------|
| 4+ validation categories | First-class category concept with configurable ordering |
| Hierarchical short-circuiting | Orchestrator config with explicit short-circuit rules |
| Parallel processing | Worker pool per-group + optional per-field parallelism |
| Config-driven validators | YAML rules + factory pattern + message registry |
| Extensible categories | New category = new engine + config changes |
| Separation of concerns | Registry (config) → Engine (execution) → Error Engine (output) |
| Observability | Structured logging, config source tracking, validation traces |
| Python pain points addressed | No decorator magic, explicit flow, debuggable config |
| **Error type overrides** | Rule-level → Category-level → Built-in defaults |
| **Message template overrides** | Inline rule → Field override → Schema override → Default |

### Override Hierarchy Summary

**Error Type Resolution:**
```
1. rule.error_type        (inline in rules YAML)
2. category.default_error_type  (in orchestrator.yaml)
3. Built-in default       (PRE_CHECK, FIELD_VALUE, etc.)
```

**Message Template Resolution:**
```
1. rule.message / rule.message_template  (inline in rules YAML)
2. overrides[schema][field][validator]   (in messages YAML)
3. overrides[schema][validator]          (in messages YAML)
4. validators[validatorID].template      (in messages YAML)
```

The key insight is treating validation as a **configurable pipeline** rather than hard-coded logic, enabling most changes through YAML while providing clear extension points for new functionality.
