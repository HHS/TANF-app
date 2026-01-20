package validation

// ValidatorConfig is the unified config schema for all validators.
// It supports both simple validators and compositions.
type ValidatorDef struct {
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
	Validators []ValidatorDef `yaml:"validators,omitempty"`

	// Condition is the condition validator for "ifThen" and "ifThenElse".
	Condition *ValidatorDef `yaml:"condition,omitempty"`

	// Then is the then-branch validator for "ifThen" and "ifThenElse".
	Then *ValidatorDef `yaml:"then,omitempty"`

	// Else is the else-branch validator for "ifThenElse".
	Else *ValidatorDef `yaml:"else,omitempty"`

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

// CategoryDef defines configuration for a validation category.
type CategoryDef struct {
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

// OrchestratorDef defines the validation execution order and behavior.
type OrchestratorDef struct {
	Categories     []CategoryDef   `yaml:"categories"`
	ExecutionOrder []int              `yaml:"execution_order"`
	ShortCircuit   []ShortCircuitRule `yaml:"short_circuit"`
}

// OrchestratorDefFile represents the orchestrator config file format.
type OrchestratorDefFile struct {
	Categories     []CategoryDef   `yaml:"categories"`
	ExecutionOrder []int                         `yaml:"execution_order"`
	ShortCircuit   []ShortCircuitRule `yaml:"short_circuit"`
}

// MessagesDefFile represents the messages config file format.
type DefaultValidatorMessageTemplate struct {
	ID string `yaml:"id"`
	Template string `yaml:"template"`
}
type DefaultMessageTemplates struct {
	Validators []DefaultValidatorMessageTemplate `yaml:"validators"`
}
