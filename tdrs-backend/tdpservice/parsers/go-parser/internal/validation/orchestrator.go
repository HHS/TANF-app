package validation

import (
	config "go-parser/internal/config/validation"
	"go-parser/internal/parser"
	"go-parser/internal/validation/registry"
)

// Orchestrator coordinates validation execution across all categories.
// It manages the execution order, short-circuiting, and result collection.
type Orchestrator struct {
	config *config.OrchestratorDef

	// Validators by category for the current schema
	cat1Validators []registry.CompiledValidator // Record pre-check
	cat2Validators map[string][]registry.CompiledValidator // Field name -> validators
	cat3Validators []registry.CompiledValidator // Cross-field
	cat4Validators []registry.CompiledValidator // Group-level

	// File context
	parseCtx   *parser.ParseContext
}

// NewOrchestrator creates a new validation orchestrator.
func NewOrchestrator(config *config.OrchestratorDef, parseCtx *parser.ParseContext) *Orchestrator {
	if config == nil {
		config = DefaultOrchestratorDef()
	}
	return &Orchestrator{
		config:         config,
		cat2Validators: make(map[string][]registry.CompiledValidator),
		parseCtx:       parseCtx,
	}
}

// DefaultOrchestratorDef returns the default orchestrator configuration.
func DefaultOrchestratorDef() *config.OrchestratorDef {
	return &config.OrchestratorDef{
		Categories: []config.CategoryDef{
			{ID: 1, Name: "Record pre-check", DefaultErrorType: "RECORD_PRE_CHECK"},
			{ID: 2, Name: "Field validation", DefaultErrorType: "FIELD_VALUE"},
			{ID: 3, Name: "Cross-field", DefaultErrorType: "VALUE_CONSISTENCY"},
			{ID: 4, Name: "Group validation", DefaultErrorType: "CASE_CONSISTENCY"},
		},
		ExecutionOrder: []int{4, 1, 2, 3},
		ShortCircuit: []config.ShortCircuitRule{
			{OnFail: 4, Action: "reject_group", Skip: []int{1, 2, 3}},
			{OnFail: 1, Action: "reject_record", Skip: []int{2, 3}},
		},
	}
}

// SetCat1Validators sets category 1 validators for the current schema.
func (o *Orchestrator) SetCat1Validators(validators []registry.CompiledValidator) {
	o.cat1Validators = validators
}

// SetCat2Validators sets category 2 validators for a specific field.
func (o *Orchestrator) SetCat2Validators(fieldName string, validators []registry.CompiledValidator) {
	o.cat2Validators[fieldName] = validators
}

// SetCat3Validators sets category 3 validators for the current schema.
func (o *Orchestrator) SetCat3Validators(validators []registry.CompiledValidator) {
	o.cat3Validators = validators
}

// SetCat4Validators sets category 4 validators for the current file spec.
func (o *Orchestrator) SetCat4Validators(validators []registry.CompiledValidator) {
	o.cat4Validators = validators
}

// ClearValidators clears all validators.
func (o *Orchestrator) ClearValidators() {
	o.cat1Validators = nil
	o.cat2Validators = make(map[string][]registry.CompiledValidator)
	o.cat3Validators = nil
	o.cat4Validators = nil
}

// ValidateGroup validates an entire parsed group and returns the result.
// This is the main entry point for validation.
func (o *Orchestrator) ValidateGroup(group *parser.ParsedGroup) *GroupValidationResult {
	result := &GroupValidationResult{
		ValidRecords:    make([]*parser.ParsedRecord, 0, len(group.Records)),
		RejectedRecords: make([]*parser.ParsedRecord, 0),
		Errors:          make([]*registry.ValidationResult, 0),
	}

	// Acquire context from pool
	ctx := registry.AcquireContext()
	defer registry.ReleaseContext(ctx)

	// Set file-level context
	ctx.ParseCtx = o.parseCtx
	ctx.Group = group

	// Run Cat 4 (group-level) validation first
	ctx.Category = registry.CategoryGroup
	cat4Errors := o.validateCat4(ctx)
	result.Errors = append(result.Errors, cat4Errors...)

	// Check for Cat 4 short-circuit
	if len(cat4Errors) > 0 && o.shouldRejectGroup(4) {
		result.Rejected = true
		result.RejectedRecords = group.Records
		return result
	}

	// Validate each record
	for _, record := range group.Records {
		ctx.Record = record
		ctx.SegmentIndex = record.SegmentIndex

		recordErrors := o.validateRecord(ctx)
		result.Errors = append(result.Errors, recordErrors...)

		// Check if record should be rejected
		if len(recordErrors) > 0 && o.shouldRejectRecord(recordErrors) {
			result.RejectedRecords = append(result.RejectedRecords, record)
		} else {
			result.ValidRecords = append(result.ValidRecords, record)
		}
	}

	return result
}

// ValidateRecord validates a single parsed record (Cat 1, 2, 3).
func (o *Orchestrator) ValidateRecord(record *parser.ParsedRecord) []*registry.ValidationResult {
	ctx := registry.AcquireContext()
	defer registry.ReleaseContext(ctx)

	ctx.ParseCtx = o.parseCtx
	ctx.Record = record

	return o.validateRecord(ctx)
}

// validateRecord runs Cat 1, 2, 3 validation on a record.
func (o *Orchestrator) validateRecord(ctx *registry.ValidationContext) []*registry.ValidationResult {
	errors := make([]*registry.ValidationResult, 0)

	// Cat 1: Record pre-check
	ctx.Category = registry.CategoryPreCheck
	cat1Errors := o.validateCat1(ctx)
	errors = append(errors, cat1Errors...)

	// Check for Cat 1 short-circuit
	if len(cat1Errors) > 0 && o.shouldSkipCategories(1, []int{2, 3}) {
		return errors
	}

	// Cat 2: Field validation
	ctx.Category = registry.CategoryFieldValue
	cat2Errors := o.validateCat2(ctx)
	errors = append(errors, cat2Errors...)

	// Cat 3: Cross-field validation
	ctx.Category = registry.CategoryCrossField
	cat3Errors := o.validateCat3(ctx)
	errors = append(errors, cat3Errors...)

	return errors
}

// validateCat1 runs category 1 (record pre-check) validators.
func (o *Orchestrator) validateCat1(ctx *registry.ValidationContext) []*registry.ValidationResult {
	errors := make([]*registry.ValidationResult, 0)

	for _, validator := range o.cat1Validators {
		result := validator.Func(ctx)
		if !result.Valid {
			result.Category = registry.CategoryPreCheck
			result.Config = validator.Config
			errors = append(errors, result)
		}
	}

	return errors
}

// validateCat2 runs category 2 (field validation) validators.
func (o *Orchestrator) validateCat2(ctx *registry.ValidationContext) []*registry.ValidationResult {
	errors := make([]*registry.ValidationResult, 0)

	if ctx.Record == nil {
		return errors
	}

	// Iterate through all fields that have validators
	for fieldName, validators := range o.cat2Validators {
		for _, validator := range validators {
			result := validator.Func(ctx)
			if !result.Valid {
				result.Category = registry.CategoryFieldValue
				result.FieldName = fieldName
				result.Config = validator.Config
				result.Record = ctx.Record
				errors = append(errors, result)
			}
		}
	}
	return errors
}

// validateCat3 runs category 3 (cross-field) validators.
func (o *Orchestrator) validateCat3(ctx *registry.ValidationContext) []*registry.ValidationResult {
	errors := make([]*registry.ValidationResult, 0)

	for _, validator := range o.cat3Validators {
		result := validator.Func(ctx)
		if !result.Valid {
			result.Category = registry.CategoryCrossField
			result.Config = validator.Config
			result.Record = ctx.Record
			errors = append(errors, result)
		}
	}

	return errors
}

// validateCat4 runs category 4 (group-level) validators.
func (o *Orchestrator) validateCat4(ctx *registry.ValidationContext) []*registry.ValidationResult {
	errors := make([]*registry.ValidationResult, 0)

	for _, validator := range o.cat4Validators {
		result := validator.Func(ctx)
		if !result.Valid {
			result.Category = registry.CategoryGroup
			result.Config = validator.Config
			result.Group = ctx.Group
			errors = append(errors, result)
		}
	}

	return errors
}

// shouldRejectGroup checks if the group should be rejected based on short-circuit rules.
func (o *Orchestrator) shouldRejectGroup(category int) bool {
	for _, rule := range o.config.ShortCircuit {
		if rule.OnFail == category && rule.Action == "reject_group" {
			return true
		}
	}
	return false
}

// shouldRejectRecord checks if a record should be rejected based on errors.
func (o *Orchestrator) shouldRejectRecord(errors []*registry.ValidationResult) bool {
	// For now, reject if any Cat 1 error
	for _, err := range errors {
		if err.Category == registry.CategoryPreCheck {
			return true
		}
	}
	return false
}

// shouldSkipCategories checks if later categories should be skipped.
func (o *Orchestrator) shouldSkipCategories(failedCategory int, checkCategories []int) bool {
	for _, rule := range o.config.ShortCircuit {
		if rule.OnFail == failedCategory {
			for _, skip := range rule.Skip {
				for _, check := range checkCategories {
					if skip == check {
						return true
					}
				}
			}
		}
	}
	return false
}

// SchemaValidators holds compiled validators for a schema.
type SchemaValidators struct {
	Cat1 []registry.CompiledValidator
	Cat2 map[string][]registry.CompiledValidator // FieldName -> validators
	Cat3 []registry.CompiledValidator
}

// NewSchemaValidators creates empty schema validators.
func NewSchemaValidators() *SchemaValidators {
	return &SchemaValidators{
		Cat2: make(map[string][]registry.CompiledValidator),
	}
}

// LoadValidatorsForSchema loads validators from a schema into the orchestrator.
func (o *Orchestrator) LoadValidatorsForSchema(validators *SchemaValidators) {
	o.cat1Validators = validators.Cat1
	o.cat2Validators = validators.Cat2
	o.cat3Validators = validators.Cat3
}

// FileSpecValidators holds compiled validators for a file spec.
type FileSpecValidators struct {
	Cat4 []registry.CompiledValidator
}

// LoadValidatorsForFileSpec loads validators from a file spec into the orchestrator.
func (o *Orchestrator) LoadValidatorsForFileSpec(validators *FileSpecValidators) {
	o.cat4Validators = validators.Cat4
}
