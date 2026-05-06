package validation

import (
	"text/template"

	"go-parser/internal/parser"
)

var noRecordsCreatedMessage = template.Must(
	template.New("no_records_created").Parse("No records created."),
)

var fieldRequiredMessage = template.Must(
	template.New("field_required").Parse("{{.RecordType}} Item {{.Item}} ({{.FriendlyName}}): field is required but a value was not provided."),
)

// ValidationOrchestrator coordinates validation across all scopes.
// Execution order: group → record (precheck) → field → record (consistency)
// Always run group and record precheck; skip field and record consistency if blocked.
type ValidationOrchestrator struct {
	registry     *ValidatorRegistry
	shortCircuit bool
}

// NewValidationOrchestrator creates a new validation orchestrator.
// When shortCircuit is true, field and record consistency validators are skipped
// if precheck or group validators fail (default production behavior).
func NewValidationOrchestrator(registry *ValidatorRegistry, shortCircuit bool) *ValidationOrchestrator {
	return &ValidationOrchestrator{
		registry:     registry,
		shortCircuit: shortCircuit,
	}
}

// ValidateGroup validates a single group.
// Execution order: group → record (precheck) → field → record (consistency)
// Always run group and record precheck; skip field and record consistency if blocked.
func (o *ValidationOrchestrator) ValidateGroup(group *parser.ParsedGroup, filespecKey string, dfCtx *DataFileContext) *GroupValidationResult {
	result := &GroupValidationResult{
		Group: group,
	}

	// Initialize record results for all records in the group
	// This is needed for per-record error attribution from group validators
	for _, rec := range group.Records {
		result.RecordResults = append(result.RecordResults, &RecordValidationResult{Record: rec})
	}

	// Phase 1: Group validation (always runs)
	groupEnv := NewGroupEnv(group)
	groupEnv.DataFileContext = dfCtx
	for _, validator := range o.registry.GetGroupValidators(filespecKey) {
		groupEnv.Params = validator.Params // Set params for this validator

		for _, vr := range ExecuteGroup(validator, groupEnv) {
			vr.DataFileContext = dfCtx
			vr.ErrorType = validator.ErrorType
			if validator.ResultMode == "per_record" {
				result.AppendResultToRecordErrors(vr)
			} else {
				result.GroupErrors = append(result.GroupErrors, vr)
			}
		}
	}

	// Check if blocked by group-level errors
	groupBlocked := result.HasBlockingGroupErrors()

	// Phase 2: Validate each record
	for i, rec := range group.Records {
		o.validateRecord(result.RecordResults[i], rec, groupBlocked, dfCtx)
	}

	return result
}

// CreateNoRecordsCreatedError builds a synthetic validation result for the
// pipeline case where processing completes without writing any records.
func (o *ValidationOrchestrator) CreateNoRecordsCreatedError() *ValidationResult {
	return &ValidationResult{
		Valid:       false,
		ErrorType:   ErrorTypePreCheck,
		ValidatorID: "no_records_created",
		Validator: &CompiledValidator{
			ID:         "no_records_created",
			Scope:      ScopeGroup,
			ErrorType:  ErrorTypePreCheck,
			ResultMode: "single",
			Message:    noRecordsCreatedMessage,
		},
	}
}

// ValidateHeader validates a single header record with DataFileContext injected
// into the validation environments. This runs the same phases as validateRecord
// (record precheck → field → record consistency) but with DataFileContext available
// to expressions for cross-validation against submission metadata.
func (o *ValidationOrchestrator) ValidateHeader(headerRec *parser.ParsedRecord, dfCtx *DataFileContext) *RecordValidationResult {
	result := &RecordValidationResult{Record: headerRec}
	recType := headerRec.GetRecordType()
	recordEnv := NewRecordEnv(headerRec)
	recordEnv.DataFileContext = dfCtx

	// Phase 1: Run PRE_CHECK and RECORD_PRE_CHECK validators
	recordBlocked := false
	for _, validator := range o.registry.GetRecordValidators(recType) {
		if validator.ErrorType != ErrorTypeRecordPreCheck && validator.ErrorType != ErrorTypePreCheck {
			continue
		}
		recordEnv.Params = validator.Params
		if vr := Execute(validator, recordEnv); !vr.Valid {
			vr.DataFileContext = dfCtx
			vr.ErrorType = validator.ErrorType
			result.RecordErrors = append(result.RecordErrors, vr)
			recordBlocked = true
		}
	}

	if o.shortCircuit && recordBlocked {
		result.Skipped = true
		return result
	}

	// Phase 2: Field validation
	fieldEnv := &FieldEnv{DataFileContext: dfCtx}
	for fieldName, validators := range o.registry.GetFieldValidatorsForRecord(recType) {
		value := headerRec.Get(fieldName)
		required := headerRec.IsFieldRequired(fieldName)

		if value == nil {
			if required {
				result.FieldErrors = append(result.FieldErrors, &ValidationResult{
					Valid:       false,
					ValidatorID: "field_required",
					ErrorType:   ErrorTypeFieldValue,
					FieldName:   fieldName,
					Validator: &CompiledValidator{
						ID:         "field_required",
						Scope:      ScopeField,
						ErrorType:  ErrorTypeFieldValue,
						ResultMode: "single",
						Message:    fieldRequiredMessage,
					},
				})
			}
			continue
		}

		// Preserve Python parser parity: field validators only run for required fields.
		if !required {
			continue
		}

		fieldEnv.Value = value
		for _, cv := range validators {
			fieldEnv.Params = cv.Params
			if vr := Execute(cv, fieldEnv); !vr.Valid {
				vr.DataFileContext = dfCtx
				vr.ErrorType = cv.ErrorType
				vr.FieldName = fieldName
				result.FieldErrors = append(result.FieldErrors, vr)
			}
		}
	}

	// Phase 3: Non-precheck record validators (consistency checks)
	for _, cv := range o.registry.GetRecordValidators(recType) {
		if cv.ErrorType == ErrorTypeRecordPreCheck || cv.ErrorType == ErrorTypePreCheck {
			continue
		}
		recordEnv.Params = cv.Params
		if vr := Execute(cv, recordEnv); !vr.Valid {
			vr.DataFileContext = dfCtx
			vr.ErrorType = cv.ErrorType
			result.RecordErrors = append(result.RecordErrors, vr)
		}
	}

	return result
}

// validateRecord validates a single record, updating the provided result.
// Called internally by ValidateGroup.
func (o *ValidationOrchestrator) validateRecord(result *RecordValidationResult, rec *parser.ParsedRecord, groupBlocked bool, dfCtx *DataFileContext) {
	recType := rec.GetRecordType()
	recordEnv := NewRecordEnv(rec)
	recordEnv.DataFileContext = dfCtx

	// Phase 1: Run RECORD_PRE_CHECK and PRE_CHECK validators (always runs, can block)
	for _, cv := range o.registry.GetRecordValidators(recType) {
		// Skip non-precheck validators in this phase
		if cv.ErrorType == ErrorTypeRecordPreCheck || cv.ErrorType == ErrorTypePreCheck {
			recordEnv.Params = cv.Params
			if vr := Execute(cv, recordEnv); !vr.Valid {
				vr.DataFileContext = dfCtx
				vr.ErrorType = cv.ErrorType
				result.RecordErrors = append(result.RecordErrors, vr)
			}
		}
	}

	// Check if blocked by record-level errors
	recordBlocked := result.HasBlockingErrors()

	// Short-circuit: skip field and non-precheck record validators if group or record is blocked
	if o.shortCircuit && (groupBlocked || recordBlocked) {
		result.Skipped = true
		return
	}

	// Phase 2: Field validation
	fieldEnv := &FieldEnv{DataFileContext: dfCtx} // Reuse env for efficiency
	for fieldName, validators := range o.registry.GetFieldValidatorsForRecord(recType) {
		value := rec.Get(fieldName)
		required := rec.IsFieldRequired(fieldName)

		// Handle nil values
		if value == nil {
			if required {
				// Required field is nil - generate error
				result.FieldErrors = append(result.FieldErrors, &ValidationResult{
					Valid:       false,
					ValidatorID: "field_required",
					ErrorType:   ErrorTypeFieldValue,
					FieldName:   fieldName,
					Validator: &CompiledValidator{
						ID:         "field_required",
						Scope:      ScopeField,
						ErrorType:  ErrorTypeFieldValue,
						ResultMode: "single",
						Message:    fieldRequiredMessage,
					},
				})
			}
			// Skip validators for nil fields (both required and optional)
			continue
		}

		// Preserve Python parser parity: field validators only run for required fields.
		if !required {
			continue
		}

		fieldEnv.Value = value
		for _, cv := range validators {
			fieldEnv.Params = cv.Params
			if vr := Execute(cv, fieldEnv); !vr.Valid {
				vr.DataFileContext = dfCtx
				vr.ErrorType = cv.ErrorType
				vr.FieldName = fieldName
				result.FieldErrors = append(result.FieldErrors, vr)
			}
		}
	}

	// Phase 3: Non-precheck record validators (consistency checks)
	for _, cv := range o.registry.GetRecordValidators(recType) {
		if cv.ErrorType == ErrorTypeRecordPreCheck || cv.ErrorType == ErrorTypePreCheck {
			continue // Already ran in phase 1
		}
		recordEnv.Params = cv.Params
		if vr := Execute(cv, recordEnv); !vr.Valid {
			vr.DataFileContext = dfCtx
			vr.ErrorType = cv.ErrorType
			result.RecordErrors = append(result.RecordErrors, vr)
		}
	}
}
