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
// Execution order: 4 → 1 → 2 → 3
// Always run 4 and 1; skip 2 and 3 if 4 or 1 failed.
func (o *Orchestrator) ValidateGroup(group WrappedGroup, filespecKey string) *GroupValidationResult {
	result := &GroupValidationResult{
		Group: group,
	}

	// Cat 4: Group validation (always runs)
	env4 := NewGroupEnv(group)
	for _, cv := range o.registry.GetCat4Validators(filespecKey) {
		env4.Params = cv.Params // Set params for this validator
		if vr := Execute(cv, env4); !vr.Valid {
			vr.Category = Cat4
			result.Cat4Errors = append(result.Cat4Errors, vr)
		}
	}
	cat4Failed := len(result.Cat4Errors) > 0

	// Validate each record
	for _, rec := range group.GetRecords() {
		recResult := o.validateRecord(rec, cat4Failed)
		result.RecordResults = append(result.RecordResults, recResult)
	}

	return result
}

// validateRecord validates a single record.
// Called internally by ValidateGroup.
func (o *Orchestrator) validateRecord(rec Record, cat4Failed bool) *RecordValidationResult {
	result := &RecordValidationResult{Record: rec}
	recType := rec.GetRecordType()

	// Cat 1: Record pre-check (always runs)
	env1 := NewRecordEnv(rec)
	for _, cv := range o.registry.GetCat1Validators(recType) {
		env1.Params = cv.Params // Set params for this validator
		if vr := Execute(cv, env1); !vr.Valid {
			vr.Category = Cat1
			result.Cat1Errors = append(result.Cat1Errors, vr)
		}
	}
	cat1Failed := len(result.Cat1Errors) > 0

	// Short-circuit: skip Cat2 and Cat3 if Cat4 or Cat1 failed
	if cat4Failed || cat1Failed {
		result.Skipped = true
		return result
	}

	// Cat 2: Field validation
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
				vr.FieldName = fieldName
				result.Cat2Errors = append(result.Cat2Errors, vr)
			}
		}
	}

	// Cat 3: Cross-field validation
	env3 := NewRecordEnv(rec)
	for _, cv := range o.registry.GetCat3Validators(recType) {
		env3.Params = cv.Params // Set params for this validator
		if vr := Execute(cv, env3); !vr.Valid {
			vr.Category = Cat3
			result.Cat3Errors = append(result.Cat3Errors, vr)
		}
	}

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
