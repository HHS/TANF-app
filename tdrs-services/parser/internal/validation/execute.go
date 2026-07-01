package validation

import (
	"fmt"

	"go-parser/internal/parser"
)

func executeOutcome(cv *CompiledValidator, state *ValidationState) (ValidationOutcome, error) {
	if cv.Executor == nil {
		return ValidationOutcome{}, fmt.Errorf("validator %s is not compiled", cv.ID)
	}
	if state == nil {
		state = &ValidationState{}
	}
	state.Scope = cv.Scope
	state.Params = cv.Params
	outcome, err := cv.Executor.Execute(state)
	if err != nil {
		return ValidationOutcome{}, fmt.Errorf("validator %s: %w", cv.ID, err)
	}
	return outcome, nil
}

// Execute runs a compiled validator against validation state.
func Execute(cv *CompiledValidator, state *ValidationState) *ValidationResult {
	outcome, err := executeOutcome(cv, state)
	if err != nil {
		return &ValidationResult{
			Valid:       false,
			ValidatorID: cv.ID,
			Error:       err,
		}
	}

	if outcome.Valid {
		return validResultSingleton
	}

	return &ValidationResult{
		Valid:       false,
		ValidatorID: cv.ID,
		Validator:   cv,
	}
}

// ExecuteGroup runs a group-scope validator and returns all resulting errors.
// For single mode (bool expressions), it delegates to Execute and returns 0 or 1 results.
// For per_record mode, it runs the expression and converts each failing record
// into a ValidationResult with LineNumber and RecordType populated.
func ExecuteGroup(cv *CompiledValidator, state *ValidationState) []*ValidationResult {
	if cv.ResultMode != "per_record" {
		if vr := Execute(cv, state); !vr.Valid {
			return []*ValidationResult{vr}
		}
		return nil
	}

	outcome, err := executeOutcome(cv, state)
	if err != nil {
		return []*ValidationResult{{
			Valid:       false,
			ValidatorID: cv.ID,
			Error:       err,
		}}
	}

	return toPerRecordResults(outcome, cv)
}

func toPerRecordResults(outcome ValidationOutcome, cv *CompiledValidator) []*ValidationResult {
	if outcome.Valid {
		return nil
	}

	if len(outcome.DuplicateMatches) > 0 {
		return resultsFromDuplicateMatches(outcome.DuplicateMatches, cv)
	}
	return resultsFromRecords(outcome.Records, cv)
}

func resultsFromRecords(records []*parser.ParsedRecord, cv *CompiledValidator) []*ValidationResult {
	if len(records) == 0 {
		return nil
	}

	results := make([]*ValidationResult, 0, len(records))
	for _, rec := range records {
		results = append(results, &ValidationResult{
			Valid:       false,
			ValidatorID: cv.ID,
			LineNumber:  rec.GetLineNumber(),
			RecordType:  rec.GetRecordType(),
			Validator:   cv,
		})
	}
	return results
}

func resultsFromDuplicateMatches(matches []*DuplicateMatch, cv *CompiledValidator) []*ValidationResult {
	if len(matches) == 0 {
		return nil
	}

	results := make([]*ValidationResult, 0, len(matches))
	for _, match := range matches {
		if match == nil || match.Record == nil {
			continue
		}

		results = append(results, &ValidationResult{
			Valid:       false,
			ValidatorID: cv.ID,
			LineNumber:  match.Record.GetLineNumber(),
			RecordType:  match.Record.GetRecordType(),
			Validator:   cv,
			TemplateData: map[string]any{
				"ExistingLineNumber": match.ExistingLineNumber,
				"DuplicatedFields":   match.DuplicatedFields,
			},
		})
	}
	return results
}
