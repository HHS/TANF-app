package validation

// ValidatorDef is the unified config schema for all validators.
// It supports both simple validators and compositions.
type ValidatorDef struct {
	// ID is the validator identifier.
	// For simple validators, this IS the validator type (e.g., "isGreaterThan").
	// For compositions, this is a custom name for message lookup.
	ID string `yaml:"id"`

	// Expr is the expression that defines the validation.
	Expr string `yaml:"expr"`

	// Params provides runtime parameters accessible in expressions via Params.key.
	// Use this for parameterized validators (e.g., length: {n: 9}).
	Params map[string]any `yaml:"params,omitempty"`

	// Fields lists all fields involved in this validation.
	// Used for dependency tracking, error attribution, and cross-field access.
	// For single-field validators, use a single-element slice.
	Fields []string `yaml:"fields,omitempty"`

	// Message is an optional override error message (template or static string).
	// If empty, the default message for the validator ID is used.
	Message string `yaml:"message,omitempty"`

	// ErrorType declares the error category this validator produces.
	// Valid values: RECORD_PRE_CHECK, FIELD_VALUE, VALUE_CONSISTENCY, CASE_CONSISTENCY
	// If empty, defaults based on scope: group->CASE_CONSISTENCY, record->VALUE_CONSISTENCY, field->FIELD_VALUE
	ErrorType string `yaml:"error_type,omitempty"`

	// ResultMode specifies how group validators produce errors.
	// "single" (default): One error for the whole group
	// "per_record": Expression returns list of failing records, each gets its own error
	ResultMode string `yaml:"result_mode,omitempty"`

	// Deprecated marks this validation as deprecated (for compatibility).
	Deprecated bool `yaml:"deprecated,omitempty"`
}

// CategoryDef defines configuration for a validation category.
type CategoryDef struct {
	ID               int    `yaml:"id"`
	Name             string `yaml:"name"`
	DefaultErrorType string `yaml:"default_error_type"`
}

// OrchestratorDef defines the validation execution order and behavior.
type OrchestratorDef struct {
	Categories     []CategoryDef   `yaml:"categories"`
}

// OrchestratorDefFile represents the orchestrator config file format.
type OrchestratorDefFile struct {
	Categories     []CategoryDef   `yaml:"categories"`
}

// MessagesDefFile represents the messages config file format.
type DefaultValidatorMessageTemplate struct {
	ID string `yaml:"id"`
	Template string `yaml:"template"`
}
type DefaultMessageTemplates struct {
	Validators []DefaultValidatorMessageTemplate `yaml:"validators"`
}
