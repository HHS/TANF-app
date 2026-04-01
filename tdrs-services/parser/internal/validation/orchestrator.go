package validation

import (
	"go-parser/internal/parser"
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
func (o *ValidationOrchestrator) ValidateGroup(group *parser.ParsedGroup, filespecKey string) *GroupValidationResult {
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
	for _, validator := range o.registry.GetGroupValidators(filespecKey) {
		groupEnv.Params = validator.Params // Set params for this validator

		if validator.ResultMode == "per_record" {
			// Per-record mode: expression returns list of failing records instead of a boolean pass fail.
			failedRecords, err := ExecuteReturningRecords(validator, groupEnv)
			if err != nil {
				result.GroupErrors = append(result.GroupErrors, &ValidationResult{
					Valid:       false,
					ValidatorID: validator.ID,
					ErrorType:   validator.ErrorType,
					Error:       err,
				})
			}
			for _, rec := range failedRecords {
				result.AddRecordError(rec, validator, nil)
			}
		} else {
			// Single mode: expression returns bool
			if validationResult := Execute(validator, groupEnv); !validationResult.Valid {
				validationResult.ErrorType = validator.ErrorType
				result.GroupErrors = append(result.GroupErrors, validationResult)
			}
		}
	}

	// Check if blocked by group-level errors
	groupBlocked := result.HasBlockingGroupErrors()

	// Phase 2: Validate each record
	for i, rec := range group.Records {
		o.validateRecord(result.RecordResults[i], rec, groupBlocked)
	}

	return result
}

// validateRecord validates a single record, updating the provided result.
// Called internally by ValidateGroup.
func (o *ValidationOrchestrator) validateRecord(result *RecordValidationResult, rec *parser.ParsedRecord, groupBlocked bool) {
	recType := rec.GetRecordType()
	recordEnv := NewRecordEnv(rec)

	// Phase 1: Run RECORD_PRE_CHECK validators (always runs, can block)
	for _, cv := range o.registry.GetRecordValidators(recType) {
		if cv.ErrorType != ErrorTypeRecordPreCheck {
			continue // Skip non-precheck validators in this phase
		}
		recordEnv.Params = cv.Params
		if vr := Execute(cv, recordEnv); !vr.Valid {
			vr.ErrorType = cv.ErrorType
			result.RecordErrors = append(result.RecordErrors, vr)
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
	fieldEnv := &FieldEnv{} // Reuse env for efficiency
	for fieldName, validators := range o.registry.GetFieldValidatorsForRecord(recType) {
		value := rec.Get(fieldName)

		// Handle nil values
		if value == nil {
			if rec.IsFieldRequired(fieldName) {
				// Required field is nil - generate error
				result.FieldErrors = append(result.FieldErrors, &ValidationResult{
					Valid:       false,
					ValidatorID: "field_required",
					ErrorType:   ErrorTypeFieldValue,
					FieldName:   fieldName,
				})
			}
			// Skip validators for nil fields (both required and optional)
			continue
		}

		fieldEnv.Value = value
		for _, cv := range validators {
			fieldEnv.Params = cv.Params
			if vr := Execute(cv, fieldEnv); !vr.Valid {
				vr.ErrorType = cv.ErrorType
				vr.FieldName = fieldName
				result.FieldErrors = append(result.FieldErrors, vr)
			}
		}
	}

	// Phase 3: Non-precheck record validators (consistency checks)
	for _, cv := range o.registry.GetRecordValidators(recType) {
		if cv.ErrorType == ErrorTypeRecordPreCheck {
			continue // Already ran in phase 1
		}
		recordEnv.Params = cv.Params
		if vr := Execute(cv, recordEnv); !vr.Valid {
			vr.ErrorType = cv.ErrorType
			result.RecordErrors = append(result.RecordErrors, vr)
		}
	}
}
