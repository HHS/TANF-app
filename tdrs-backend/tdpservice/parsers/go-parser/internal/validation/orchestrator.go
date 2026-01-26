package validation

import (
	"sync"
)

// OrchestratorConfig configures the validation orchestrator.
type OrchestratorConfig struct {
	// Workers is the number of parallel workers for group validation.
	// If 0, uses sequential validation.
	Workers int
}

// Orchestrator coordinates validation across all categories.
// Execution order: 4 → 1 → 2 → 3
// Always run 4 and 1; skip 2 and 3 if 4 or 1 failed.
type Orchestrator struct {
	registry *ValidatorRegistry
	config   *OrchestratorConfig
}

// NewOrchestrator creates a new validation orchestrator.
func NewOrchestrator(registry *ValidatorRegistry, workers int) *Orchestrator {
	return &Orchestrator{
		registry: registry,
		config: &OrchestratorConfig{
			Workers: workers,
		},
	}
}

// ValidateGroup validates a single group.
// Execution order: group → record (precheck) → field → record (consistency)
// Always run group and record precheck; skip field and record consistency if blocked.
func (o *Orchestrator) ValidateGroup(group WrappedGroup, filespecKey string) *GroupValidationResult {
	result := &GroupValidationResult{
		Group: group,
	}

	// Initialize record results for all records in the group
	// This is needed for per-record error attribution from group validators
	for _, rec := range group.GetRecords() {
		result.RecordResults = append(result.RecordResults, &RecordValidationResult{Record: rec})
	}

	// Phase 1: Group validation (always runs)
	env4 := NewGroupEnv(group)
	for _, cv := range o.registry.GetCat4Validators(filespecKey) {
		env4.Params = cv.Params // Set params for this validator

		if cv.ResultMode == "per_record" {
			// Per-record mode: expression returns list of failing records
			failedRecords := ExecuteReturningRecords(cv, env4)
			for _, rec := range failedRecords {
				result.AddRecordError(rec, cv, nil)
			}
		} else {
			// Single mode: expression returns bool
			if vr := Execute(cv, env4); !vr.Valid {
				vr.Category = Cat4
				vr.ErrorType = cv.ErrorType
				result.Cat4Errors = append(result.Cat4Errors, vr)
			}
		}
	}

	// Check if blocked by group-level errors
	groupBlocked := result.HasBlockingGroupErrors()

	// Phase 2: Validate each record
	for i, rec := range group.GetRecords() {
		o.validateRecordInPlace(result.RecordResults[i], rec, groupBlocked)
	}

	return result
}

// validateRecordInPlace validates a single record, updating the provided result.
// Called internally by ValidateGroup.
func (o *Orchestrator) validateRecordInPlace(result *RecordValidationResult, rec Record, groupBlocked bool) {
	recType := rec.GetRecordType()

	// Cat 1 / Record precheck: Record pre-check (always runs)
	env1 := NewRecordEnv(rec)
	for _, cv := range o.registry.GetCat1Validators(recType) {
		env1.Params = cv.Params // Set params for this validator
		if vr := Execute(cv, env1); !vr.Valid {
			vr.Category = Cat1
			vr.ErrorType = cv.ErrorType
			result.Cat1Errors = append(result.Cat1Errors, vr)
		}
	}

	// Check if blocked by record-level errors
	recordBlocked := result.HasBlockingErrors()

	// Short-circuit: skip Cat2 and Cat3 if group or record is blocked
	if groupBlocked || recordBlocked {
		result.Skipped = true
		return
	}

	// Cat 2 / Field: Field validation
	env2 := &FieldEnv{} // Reuse env for efficiency
	for fieldName, validators := range o.registry.GetCat2FieldsForRecord(recType) {
		value := rec.Get(fieldName)

		// Handle nil values
		if value == nil {
			if rec.IsFieldRequired(fieldName) {
				// Required field is nil - generate error
				result.Cat2Errors = append(result.Cat2Errors, &ValidationResult{
					Valid:       false,
					ValidatorID: "field_required",
					Category:    Cat2,
					ErrorType:   ErrorTypeFieldValue,
					FieldName:   fieldName,
				})
			}
			// Skip validators for nil fields (both required and optional)
			continue
		}

		env2.Value = value
		for _, cv := range validators {
			env2.Params = cv.Params // Set params for this validator
			if vr := Execute(cv, env2); !vr.Valid {
				vr.Category = Cat2
				vr.ErrorType = cv.ErrorType
				vr.FieldName = fieldName
				result.Cat2Errors = append(result.Cat2Errors, vr)
			}
		}
	}

	// Cat 3 / Record consistency: Cross-field validation
	env3 := NewRecordEnv(rec)
	for _, cv := range o.registry.GetCat3Validators(recType) {
		env3.Params = cv.Params // Set params for this validator
		if vr := Execute(cv, env3); !vr.Valid {
			vr.Category = Cat3
			vr.ErrorType = cv.ErrorType
			result.Cat3Errors = append(result.Cat3Errors, vr)
		}
	}
}

// validateRecord validates a single record.
// Deprecated: Use validateRecordInPlace instead.
func (o *Orchestrator) validateRecord(rec Record, cat4Failed bool) *RecordValidationResult {
	result := &RecordValidationResult{Record: rec}
	o.validateRecordInPlace(result, rec, cat4Failed)
	return result
}

// ValidateGroups validates multiple groups in parallel.
func (o *Orchestrator) ValidateGroups(groups []WrappedGroup, filespecKey string) []*GroupValidationResult {
	if len(groups) == 0 {
		return nil
	}

	results := make([]*GroupValidationResult, len(groups))

	// Sequential validation if no workers configured
	if o.config.Workers <= 0 {
		for i, group := range groups {
			results[i] = o.ValidateGroup(group, filespecKey)
		}
		return results
	}

	// Parallel validation with worker pool
	var wg sync.WaitGroup
	sem := make(chan struct{}, o.config.Workers)

	for i, group := range groups {
		wg.Add(1)
		sem <- struct{}{} // Acquire

		go func(idx int, g WrappedGroup) {
			defer wg.Done()
			defer func() { <-sem }() // Release

			results[idx] = o.ValidateGroup(g, filespecKey)
		}(i, group)
	}

	wg.Wait()
	return results
}
