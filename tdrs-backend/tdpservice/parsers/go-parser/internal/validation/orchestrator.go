package validation

import (
	"go-parser/internal/decoder"
	"go-parser/internal/parser"
	"go-parser/internal/schema"
)

// Orchestrator coordinates validation execution across all categories.
// It manages the execution order, short-circuiting, and result collection.
type Orchestrator struct {
	config *OrchestratorConfig

	// Validators by category for the current schema
	cat1Validators []CompiledValidator // Record pre-check
	cat2Validators map[int][]CompiledValidator // Field index -> validators
	cat3Validators []CompiledValidator // Cross-field
	cat4Validators []CompiledValidator // Group-level

	// File context
	datafileID int32
	parseCtx   *schema.ParseContext
}

// NewOrchestrator creates a new validation orchestrator.
func NewOrchestrator(config *OrchestratorConfig) *Orchestrator {
	if config == nil {
		config = DefaultOrchestratorConfig()
	}
	return &Orchestrator{
		config:         config,
		cat2Validators: make(map[int][]CompiledValidator),
	}
}

// DefaultOrchestratorConfig returns the default orchestrator configuration.
func DefaultOrchestratorConfig() *OrchestratorConfig {
	return &OrchestratorConfig{
		Categories: []CategoryConfig{
			{ID: 1, Name: "Record pre-check", DefaultErrorType: "RECORD_PRE_CHECK"},
			{ID: 2, Name: "Field validation", DefaultErrorType: "FIELD_VALUE"},
			{ID: 3, Name: "Cross-field", DefaultErrorType: "VALUE_CONSISTENCY"},
			{ID: 4, Name: "Group validation", DefaultErrorType: "CASE_CONSISTENCY"},
		},
		ExecutionOrder: []int{4, 1, 2, 3},
		ShortCircuit: []ShortCircuitRule{
			{OnFail: 4, Action: "reject_group", Skip: []int{1, 2, 3}},
			{OnFail: 1, Action: "reject_record", Skip: []int{2, 3}},
		},
	}
}

// SetFileContext sets file-level context for validation.
func (o *Orchestrator) SetFileContext(datafileID int32, parseCtx *schema.ParseContext) {
	o.datafileID = datafileID
	o.parseCtx = parseCtx
}

// SetCat1Validators sets category 1 validators for the current schema.
func (o *Orchestrator) SetCat1Validators(validators []CompiledValidator) {
	o.cat1Validators = validators
}

// SetCat2Validators sets category 2 validators for a specific field.
func (o *Orchestrator) SetCat2Validators(fieldIndex int, validators []CompiledValidator) {
	o.cat2Validators[fieldIndex] = validators
}

// SetCat3Validators sets category 3 validators for the current schema.
func (o *Orchestrator) SetCat3Validators(validators []CompiledValidator) {
	o.cat3Validators = validators
}

// SetCat4Validators sets category 4 validators for the current file spec.
func (o *Orchestrator) SetCat4Validators(validators []CompiledValidator) {
	o.cat4Validators = validators
}

// ClearValidators clears all validators.
func (o *Orchestrator) ClearValidators() {
	o.cat1Validators = nil
	o.cat2Validators = make(map[int][]CompiledValidator)
	o.cat3Validators = nil
	o.cat4Validators = nil
}

// ValidateGroup validates an entire parsed group and returns the result.
// This is the main entry point for validation.
func (o *Orchestrator) ValidateGroup(group *parser.ParsedGroup) *GroupValidationResult {
	result := &GroupValidationResult{
		ValidRecords:    make([]*schema.ParsedRecord, 0, len(group.Records)),
		RejectedRecords: make([]*schema.ParsedRecord, 0),
		Errors:          make([]*ValidationResult, 0),
	}

	// Acquire context from pool
	ctx := AcquireContext()
	defer ReleaseContext(ctx)

	// Set file-level context
	ctx.DatafileID = o.datafileID
	ctx.ParseCtx = o.parseCtx
	ctx.Group = group

	// Run Cat 4 (group-level) validation first
	ctx.Category = CategoryGroup
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
		ctx.Schema = record.Schema

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

// ValidateRow validates a single row before parsing (Cat 1 only).
// Used for pre-parsing validation.
func (o *Orchestrator) ValidateRow(row decoder.Row, compiledSchema *schema.CompiledSchema) []*ValidationResult {
	ctx := AcquireContext()
	defer ReleaseContext(ctx)

	ctx.DatafileID = o.datafileID
	ctx.ParseCtx = o.parseCtx
	ctx.Row = row
	ctx.Schema = compiledSchema
	ctx.Category = CategoryPreCheck

	return o.validateCat1(ctx)
}

// ValidateRecord validates a single parsed record (Cat 1, 2, 3).
func (o *Orchestrator) ValidateRecord(record *schema.ParsedRecord) []*ValidationResult {
	ctx := AcquireContext()
	defer ReleaseContext(ctx)

	ctx.DatafileID = o.datafileID
	ctx.ParseCtx = o.parseCtx
	ctx.Record = record
	ctx.Schema = record.Schema

	return o.validateRecord(ctx)
}

// validateRecord runs Cat 1, 2, 3 validation on a record.
func (o *Orchestrator) validateRecord(ctx *ValidationContext) []*ValidationResult {
	errors := make([]*ValidationResult, 0)

	// Cat 1: Record pre-check
	ctx.Category = CategoryPreCheck
	cat1Errors := o.validateCat1(ctx)
	errors = append(errors, cat1Errors...)

	// Check for Cat 1 short-circuit
	if len(cat1Errors) > 0 && o.shouldSkipCategories(1, []int{2, 3}) {
		return errors
	}

	// Cat 2: Field validation
	ctx.Category = CategoryFieldValue
	cat2Errors := o.validateCat2(ctx)
	errors = append(errors, cat2Errors...)

	// Cat 3: Cross-field validation
	ctx.Category = CategoryCrossField
	cat3Errors := o.validateCat3(ctx)
	errors = append(errors, cat3Errors...)

	return errors
}

// validateCat1 runs category 1 (record pre-check) validators.
func (o *Orchestrator) validateCat1(ctx *ValidationContext) []*ValidationResult {
	errors := make([]*ValidationResult, 0)

	for _, validator := range o.cat1Validators {
		result := validator.Func(ctx)
		if !result.Valid {
			result.Category = CategoryPreCheck
			result.Config = validator.Config
			errors = append(errors, result)
		}
	}

	return errors
}

// validateCat2 runs category 2 (field validation) validators.
func (o *Orchestrator) validateCat2(ctx *ValidationContext) []*ValidationResult {
	errors := make([]*ValidationResult, 0)

	if ctx.Record == nil || ctx.Schema == nil {
		return errors
	}

	// Iterate through all fields that have validators
	for fieldIndex, validators := range o.cat2Validators {
		ctx.FieldIndex = fieldIndex

		for _, validator := range validators {
			result := validator.Func(ctx)
			if !result.Valid {
				result.Category = CategoryFieldValue
				result.FieldIndex = fieldIndex
				result.Config = validator.Config
				result.Record = ctx.Record
				result.Schema = ctx.Schema

				// Set field name from schema if not already set
				if result.FieldName == "" {
					if fieldDef := ctx.FieldDef(); fieldDef != nil {
						result.FieldName = fieldDef.Name
					}
				}

				errors = append(errors, result)
			}
		}
	}

	ctx.FieldIndex = -1
	return errors
}

// validateCat3 runs category 3 (cross-field) validators.
func (o *Orchestrator) validateCat3(ctx *ValidationContext) []*ValidationResult {
	errors := make([]*ValidationResult, 0)

	for _, validator := range o.cat3Validators {
		result := validator.Func(ctx)
		if !result.Valid {
			result.Category = CategoryCrossField
			result.Config = validator.Config
			result.Record = ctx.Record
			result.Schema = ctx.Schema
			errors = append(errors, result)
		}
	}

	return errors
}

// validateCat4 runs category 4 (group-level) validators.
func (o *Orchestrator) validateCat4(ctx *ValidationContext) []*ValidationResult {
	errors := make([]*ValidationResult, 0)

	for _, validator := range o.cat4Validators {
		result := validator.Func(ctx)
		if !result.Valid {
			result.Category = CategoryGroup
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
func (o *Orchestrator) shouldRejectRecord(errors []*ValidationResult) bool {
	// For now, reject if any Cat 1 error
	for _, err := range errors {
		if err.Category == CategoryPreCheck {
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
	Cat1 []CompiledValidator
	Cat2 map[int][]CompiledValidator // FieldIndex -> validators
	Cat3 []CompiledValidator
}

// NewSchemaValidators creates empty schema validators.
func NewSchemaValidators() *SchemaValidators {
	return &SchemaValidators{
		Cat2: make(map[int][]CompiledValidator),
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
	Cat4 []CompiledValidator
}

// LoadValidatorsForFileSpec loads validators from a file spec into the orchestrator.
func (o *Orchestrator) LoadValidatorsForFileSpec(validators *FileSpecValidators) {
	o.cat4Validators = validators.Cat4
}
