// Package validation provides a config-driven validation system for parsed records.
// It supports multiple validation categories (Cat 1-4), composable validators,
// and lazy error message generation.
package validation

import (
	"go-parser/internal/decoder"
	"go-parser/internal/parser"
	"go-parser/internal/schema"
)

// Category represents a validation category (1-4).
type Category int

const (
	CategoryPreCheck   Category = 1 // Record-level pre-parsing validation
	CategoryFieldValue Category = 2 // Field-level validation
	CategoryCrossField Category = 3 // Cross-field validation within a record
	CategoryGroup      Category = 4 // Group-level validation (case consistency)
)

// String returns the category name.
func (c Category) String() string {
	switch c {
	case CategoryPreCheck:
		return "RECORD_PRE_CHECK"
	case CategoryFieldValue:
		return "FIELD_VALUE"
	case CategoryCrossField:
		return "VALUE_CONSISTENCY"
	case CategoryGroup:
		return "CASE_CONSISTENCY"
	default:
		return "UNKNOWN"
	}
}

// ValidatorFunc is the unified signature for ALL validators.
// It takes a ValidationContext and returns a ValidationResult.
// Validators should be stateless and reusable.
type ValidatorFunc func(ctx *ValidationContext) *ValidationResult

// ValidatorFactory creates parameterized validators from config parameters.
// It's called once at startup when building validators from YAML config.
type ValidatorFactory func(params map[string]any) (ValidatorFunc, error)

// ValidationContext provides unified context for all validators.
// It is pooled and reused across validations for performance.
type ValidationContext struct {
	// File-level context (set once per file)
	DatafileID int32
	ParseCtx   *parser.ParseContext

	// Record-level context (Cat 1, 2, 3)
	Record *parser.ParsedRecord
	Schema *schema.CompiledSchema
	Row    decoder.Row // Raw row for Cat 1 validators

	// Field-level context (Cat 2)
	FieldIndex int // Index into Record.Fields and Schema.Fields

	// Group-level context (Cat 4)
	Group *parser.ParsedGroup

	// Category being validated
	Category Category
}

// ValidationResult represents the outcome of a validator.
// Results are pooled and reused for performance.
type ValidationResult struct {
	Valid       bool
	ValidatorID string   // e.g., "isGreaterThan", "cash_requires_months"
	Category    Category // Which category this result is from

	// Context pointers for lazy error generation (not copied, just referenced)
	FieldIndex int
	FieldName  string // For Cat 2 and cross-field, which field(s) failed
	Record     *parser.ParsedRecord
	Schema     *schema.CompiledSchema
	Group      *parser.ParsedGroup
	Row        decoder.Row

	// Config that triggered this validation (for message/error_type overrides)
	// TODO: This is a heavy object. Might need to extract only what we need from it
	Config *ValidatorConfig
}

// ValidatorConfig is the unified config schema for all validators.
// It supports both simple validators and compositions.
type ValidatorConfig struct {
	// ID is the validator identifier.
	// For simple validators, this IS the validator type (e.g., "isGreaterThan").
	// For compositions, this is a custom name for message lookup.
	ID string `yaml:"id"`

	// Compose specifies the composition type: "and", "or", "not", "ifThen", "ifThenElse".
	// If empty, ID is looked up as a simple validator in the registry.
	Compose string `yaml:"compose,omitempty"`

	// Params are parameters for simple validators (e.g., {"value": 0, "min": 1}).
	Params map[string]any `yaml:"params,omitempty"`

	// Validators are child validators for "and", "or", "not" compositions.
	Validators []ValidatorConfig `yaml:"validators,omitempty"`

	// Condition is the condition validator for "ifThen" and "ifThenElse".
	Condition *ValidatorConfig `yaml:"condition,omitempty"`

	// Then is the then-branch validator for "ifThen" and "ifThenElse".
	Then *ValidatorConfig `yaml:"then,omitempty"`

	// Else is the else-branch validator for "ifThenElse".
	Else *ValidatorConfig `yaml:"else,omitempty"`

	// Field specifies a target field for cross-field access in compositions.
	// When set, the validator operates on this field instead of the current context field.
	Field string `yaml:"field,omitempty"`

	// Message is an optional override error message (template or static string).
	// If empty, the default message for the validator ID is used.
	Message string `yaml:"message,omitempty"`

	// ErrorType is an optional override error type.
	// If empty, the category's default error type is used.
	ErrorType string `yaml:"error_type,omitempty"`

	// Deprecated marks this validation as deprecated (for compatibility).
	Deprecated bool `yaml:"deprecated,omitempty"`
}

// CompiledValidator holds a compiled validator function with its config.
type CompiledValidator struct {
	Func   ValidatorFunc
	Config *ValidatorConfig
}

// GroupValidationResult holds the results of validating an entire group.
type GroupValidationResult struct {
	// Rejected is true if the entire group was rejected (e.g., Cat 4 failure).
	Rejected bool

	// ValidRecords are records that passed all validations.
	ValidRecords []*parser.ParsedRecord

	// RejectedRecords are records that failed validation (for error logging).
	RejectedRecords []*parser.ParsedRecord

	// Errors are all validation failures, used for lazy error generation.
	Errors []*ValidationResult
}

// CategoryConfig defines configuration for a validation category.
type CategoryConfig struct {
	ID               int    `yaml:"id"`
	Name             string `yaml:"name"`
	DefaultErrorType string `yaml:"default_error_type"`
}

// ShortCircuitRule defines when to skip later categories.
type ShortCircuitRule struct {
	OnFail int    `yaml:"on_fail"` // Category that failed
	Action string `yaml:"action"`  // "reject_record", "reject_group"
	Skip   []int  `yaml:"skip"`    // Categories to skip
}

// OrchestratorConfig defines the validation execution order and behavior.
type OrchestratorConfig struct {
	Categories     []CategoryConfig   `yaml:"categories"`
	ExecutionOrder []int              `yaml:"execution_order"`
	ShortCircuit   []ShortCircuitRule `yaml:"short_circuit"`
}
