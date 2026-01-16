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

    return func(ctx *ValidationContext, value any) *ValidationResult {
        num, ok := toInt(value)
        if !ok {
            return &ValidationResult{
                Valid:       false,
                ValidatorID: "isMultipleOf",
                FailReason:  "not_a_number",
            }
        }

        if num%divisor != 0 {
            return &ValidationResult{
                Valid:       false,
                ValidatorID: "isMultipleOf",
                Params:      params,
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
  - category: 4
    scope: group
  - category: 5                    # New category
    scope: file
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

### 9.1 Core Validator Interface

```go
// internal/validation/types.go

// ValidatorFunc is the core validator function signature.
// It receives a context with all metadata and the value(s) to validate.
// Returns a result indicating validity and any failure details.
type ValidatorFunc func(ctx *ValidationContext, value any) *ValidationResult

// ValidatorFactory creates a ValidatorFunc from configuration parameters.
// This allows validators to be configured at load time with specific params.
type ValidatorFactory func(params map[string]any) ValidatorFunc

// Validator is the interface for named, configurable validators.
type Validator interface {
    // ID returns the unique identifier for this validator (e.g., "isInRange")
    ID() string

    // Category returns which category this validator belongs to (1-4+)
    Category() int

    // Validate performs the validation
    Validate(ctx *ValidationContext, value any) *ValidationResult
}
```

### 9.2 Validation Context

```go
// internal/validation/context.go

// ValidationContext provides all metadata needed by validators.
// It is passed through the validation pipeline and enriched at each stage.
type ValidationContext struct {
    // Record-level context
    Record       *schema.ParsedRecord
    RawRow       decoder.Row
    Schema       *schema.CompiledSchema
    SchemaPath   string
    LineNumber   int
    SegmentIndex int

    // Field-level context (populated for Cat 2)
    Field        *FieldContext

    // Group-level context (populated for Cat 4)
    Group        *GroupContext

    // File-level context
    File         *FileContext

    // Parse context from header
    ParseCtx     *schema.ParseContext

    // For tracing/debugging
    TraceID      string
}

// FieldContext contains field-specific metadata
type FieldContext struct {
    Name         string
    FriendlyName string
    ItemNumber   string
    Position     Position
    FieldDef     *schema.FieldDef
    Value        any
    RawValue     string
}

// GroupContext contains case/group metadata
type GroupContext struct {
    Key          string            // e.g., "202001-CASE12345"
    KeyFields    map[string]string // e.g., {"RPT_MONTH_YEAR": "202001", "CASE_NUMBER": "CASE12345"}
    Records      []*schema.ParsedRecord
    RecordTypes  map[string]int    // Count by record type
}

// FileContext contains file-level metadata
type FileContext struct {
    DatafileID   int32
    Program      string
    Section      int
    TotalLines   int
    Header       *schema.ParsedRecord
    Trailer      *schema.ParsedRecord
}

// Position represents a field's location in the raw row
type Position struct {
    Start   int
    End     int
    Column  int  // For columnar formats
}
```

### 9.3 Validation Result Types

```go
// internal/validation/result.go

// ValidationResult represents the outcome of a single validator execution
type ValidationResult struct {
    Valid       bool
    ValidatorID string
    Category    int

    // For error message generation
    Params      map[string]any  // Original validator params
    FailReason  string          // Optional reason code for complex validators

    // For debugging
    Deprecated  bool
}

// RecordResult aggregates validation results for a single record
type RecordResult struct {
    Record      *schema.ParsedRecord
    LineNumber  int
    SchemaPath  string

    Valid       bool
    Rejected    bool            // True if short-circuited (Cat 1 or Cat 4 failure)

    Results     []*ValidationResult
    Errors      []*ParserError  // Generated errors
}

// GroupResult aggregates validation results for a case/group
type GroupResult struct {
    Key         string
    KeyFields   map[string]string

    Valid       bool
    Rejected    bool            // True if Cat 4 failed

    GroupResults []*ValidationResult  // Cat 4 results
    RecordResults []*RecordResult     // Per-record results
}

// BatchResult aggregates results for a batch of groups
type BatchResult struct {
    Groups      []*GroupResult
    Stats       *ValidationStats
}

// ValidationStats tracks validation metrics
type ValidationStats struct {
    TotalRecords    int64
    ValidRecords    int64
    InvalidRecords  int64
    RejectedRecords int64  // Short-circuited

    TotalGroups     int64
    ValidGroups     int64
    RejectedGroups  int64

    ErrorsByCategory map[int]int64
    ErrorsByValidator map[string]int64
}
```

### 9.4 Category Engine Interface

```go
// internal/validation/engine.go

// CategoryEngine executes validation for a specific category
type CategoryEngine interface {
    // Category returns the category ID (1, 2, 3, 4, ...)
    Category() int

    // Scope returns the validation scope (field, record, group, file)
    Scope() Scope

    // ValidateRecord validates a single record (for Cat 1, 2, 3)
    ValidateRecord(ctx *ValidationContext) []*ValidationResult

    // ValidateGroup validates a group of records (for Cat 4)
    ValidateGroup(ctx *ValidationContext, records []*schema.ParsedRecord) []*ValidationResult
}

// Scope defines the validation scope
type Scope int

const (
    ScopeField  Scope = iota
    ScopeRecord
    ScopeGroup
    ScopeFile
)
```

### 9.5 Orchestrator Interface

```go
// internal/validation/orchestrator.go

// Orchestrator coordinates validation across categories
type Orchestrator struct {
    config          *OrchestratorConfig
    engines         map[int]CategoryEngine
    validatorReg    *ValidatorRegistry
    messageReg      *MessageRegistry
    errorEngine     *ErrorEngine
}

// OrchestratorConfig defines category ordering, short-circuit rules, and defaults
type OrchestratorConfig struct {
    Categories        []CategoryConfig
    ExecutionOrder    []CategoryExecution
    ShortCircuitRules []ShortCircuitRule
}

// CategoryConfig defines a validation category and its defaults
type CategoryConfig struct {
    ID               int       `yaml:"id"`
    Name             string    `yaml:"name"`
    Scope            Scope     `yaml:"scope"`
    DefaultErrorType ErrorType `yaml:"default_error_type"`
    Description      string    `yaml:"description,omitempty"`
}

type CategoryExecution struct {
    Category int
    Scope    Scope
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

### 9.6 Validator Registry

```go
// internal/validation/registry/validators.go

// ValidatorRegistry manages validator registration and lookup
type ValidatorRegistry struct {
    factories map[string]ValidatorFactory
    mu        sync.RWMutex
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

    // Source tracking (populated by config loader)
    SourceFile      string         `yaml:"-"`
    SourceLine      int            `yaml:"-"`
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

### 9.7 Message Registry and Error Engine

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

    mu sync.RWMutex
}

// GetTemplate retrieves the most specific template for a validation failure.
// Lookup priority (highest to lowest):
//   1. Field-level override: overrides[schema][field][validator]
//   2. Schema-level override: overrides[schema][validator]
//   3. Default validator template: validators[validatorID]
func (r *MessageRegistry) GetTemplate(validatorID, schemaPath, fieldName string) *template.Template {
    r.mu.RLock()
    defer r.mu.RUnlock()

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

// ErrorEngine generates ParserError objects from validation failures
type ErrorEngine struct {
    messageReg      *MessageRegistry
    categoryConfigs map[int]*CategoryConfig  // For default error types
}

// GenerateError creates a ParserError from a ValidationResult, context, and rule config.
// Resolution order for message template:
//   1. rule.Message or rule.MessageTemplate (inline override)
//   2. MessageRegistry lookup (schema/field/validator hierarchy)
// Resolution order for error type:
//   1. rule.ErrorType (inline override)
//   2. CategoryConfig.DefaultErrorType
//   3. Built-in default for category
func (e *ErrorEngine) GenerateError(
    result *ValidationResult,
    ctx *ValidationContext,
    rule *RuleConfig,
) *ParserError {
    // Resolve message template
    var tmpl *template.Template
    if rule.HasMessageOverride() {
        tmpl = template.Must(template.New("inline").Parse(rule.GetMessageTemplate()))
    } else {
        tmpl = e.messageReg.GetTemplate(
            result.ValidatorID,
            ctx.SchemaPath,
            ctx.Field.Name,
        )
    }

    // Resolve error type
    errorType := e.resolveErrorType(result.Category, rule)

    // Build template context and render message
    message := e.renderTemplate(tmpl, result, ctx)

    return &ParserError{
        RowNumber:    ctx.LineNumber,
        ColumnNumber: ctx.Field.ItemNumber,
        ItemNumber:   ctx.Field.ItemNumber,
        FieldName:    ctx.Field.Name,
        RptMonthYear: ctx.Group.KeyFields["RPT_MONTH_YEAR"],
        CaseNumber:   ctx.Group.KeyFields["CASE_NUMBER"],
        ErrorMessage: message,
        ErrorType:    errorType,
        Category:     result.Category,
        ValidatorID:  result.ValidatorID,
        SchemaPath:   ctx.SchemaPath,
        FieldsJSON:   e.buildFieldsJSON(ctx),
        ValuesJSON:   e.buildValuesJSON(ctx),
        Deprecated:   rule.Deprecated,
        ConfigSource: fmt.Sprintf("%s:%d", rule.SourceFile, rule.SourceLine),
    }
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
    ValidatorID   string
    SchemaPath    string
    FieldsJSON    map[string]any
    ValuesJSON    map[string]any
    Deprecated    bool

    // For tracing
    ConfigSource  string  // e.g., "config/validation/rules/tanf/t1.yaml:42"
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

```go
// internal/validation/logging.go

type ValidationLogger struct {
    logger *slog.Logger
}

// LogValidatorRun logs when a validator is executed
func (l *ValidationLogger) LogValidatorRun(ctx *ValidationContext, validatorID string, result *ValidationResult) {
    l.logger.Debug("validator executed",
        "validator_id", validatorID,
        "category", result.Category,
        "valid", result.Valid,
        "line_number", ctx.LineNumber,
        "schema_path", ctx.SchemaPath,
        "field_name", ctx.Field.Name,
        "trace_id", ctx.TraceID,
    )
}

// LogValidatorFailure logs validation failure with full context
func (l *ValidationLogger) LogValidatorFailure(ctx *ValidationContext, result *ValidationResult, err *ParserError) {
    l.logger.Info("validation failed",
        "validator_id", result.ValidatorID,
        "category", result.Category,
        "line_number", ctx.LineNumber,
        "schema_path", ctx.SchemaPath,
        "field_name", ctx.Field.Name,
        "field_value", ctx.Field.Value,
        "error_message", err.ErrorMessage,
        "config_source", err.ConfigSource,
        "trace_id", ctx.TraceID,
    )
}
```

### 11.2 Config Source Tracking

Every validation rule carries its source location for debugging:

```go
type RuleConfig struct {
    Validator    string
    Params       map[string]any

    // Populated by config loader
    SourceFile   string  // e.g., "config/validation/rules/tanf/t1.yaml"
    SourceLine   int     // e.g., 42
}
```

When an error is generated, this source is included:

```go
err := &ParserError{
    // ...
    ConfigSource: fmt.Sprintf("%s:%d", rule.SourceFile, rule.SourceLine),
}
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
