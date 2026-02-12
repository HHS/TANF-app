package validation

import (
	"sync"

	"github.com/expr-lang/expr/vm"

	"go-parser/internal/parser"
)

// OrchestratorConfig configures the validation orchestrator.
type OrchestratorConfig struct {
	// Workers is the number of parallel workers for group validation.
	// If 0, uses sequential validation.
	Workers int
}

// Orchestrator coordinates validation across all scopes.
// Execution order: group → record (precheck) → field → record (consistency)
// Always run group and record precheck; skip field and record consistency if blocked.
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
func (o *Orchestrator) ValidateGroup(group *parser.ParsedGroup, filespecKey string) *GroupValidationResult {
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
	for _, cv := range o.registry.GetGroupValidators(filespecKey) {
		groupEnv.Params = cv.Params // Set params for this validator

		if cv.ResultMode == "per_record" {
			// Per-record mode: expression returns list of failing records
			failedRecords := ExecuteReturningRecords(cv, groupEnv)
			for _, rec := range failedRecords {
				result.AddRecordError(rec, cv, nil)
			}
		} else {
			// Single mode: expression returns bool
			if vr := Execute(cv, groupEnv); !vr.Valid {
				vr.ErrorType = cv.ErrorType
				result.GroupErrors = append(result.GroupErrors, vr)
			}
		}
	}

	// Check if blocked by group-level errors
	groupBlocked := result.HasBlockingGroupErrors()

	// Phase 2: Validate each record
	for i, rec := range group.Records {
		o.validateRecordInPlace(result.RecordResults[i], rec, groupBlocked)
	}

	return result
}

// validateRecordInPlace validates a single record, updating the provided result.
// Called internally by ValidateGroup.
func (o *Orchestrator) validateRecordInPlace(result *RecordValidationResult, rec *parser.ParsedRecord, groupBlocked bool) {
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
	if groupBlocked || recordBlocked {
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

// ValidateGroups validates multiple groups in parallel.
func (o *Orchestrator) ValidateGroups(groups []*parser.ParsedGroup, filespecKey string) []*GroupValidationResult {
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

		go func(idx int, g *parser.ParsedGroup) {
			defer wg.Done()
			defer func() { <-sem }() // Release

			results[idx] = o.ValidateGroup(g, filespecKey)
		}(i, group)
	}

	wg.Wait()
	return results
}

// ExecuteReturningRecords runs a compiled validator that returns a list of failing records.
// This is used for group validators with result_mode: per_record.
// The expression should return a slice of *parser.ParsedRecord.
func ExecuteReturningRecords(cv *CompiledValidator, env any) []*parser.ParsedRecord {
	program, ok := cv.Expr.Program.(*vm.Program)
	if !ok {
		return nil
	}

	output, err := vm.Run(program, env)
	if err != nil {
		return nil
	}

	// Handle nil result (no failures)
	if output == nil {
		return nil
	}

	// Try direct type assertion
	if records, ok := output.([]*parser.ParsedRecord); ok {
		return records
	}

	// Try to convert from []any (expr engine may wrap results)
	if anySlice, ok := output.([]any); ok {
		var records []*parser.ParsedRecord
		for _, item := range anySlice {
			if rec, ok := item.(*parser.ParsedRecord); ok {
				records = append(records, rec)
			}
		}
		return records
	}

	return nil
}
