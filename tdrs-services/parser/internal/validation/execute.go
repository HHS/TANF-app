package validation

import (
	"fmt"

	"github.com/expr-lang/expr/vm"

	"go-parser/internal/parser"
)

// runProgram extracts the vm.Program from a CompiledValidator and runs it.
// Returns the raw output and any error from program extraction or execution.
func runProgram(cv *CompiledValidator, env any) (any, error) {
	program, ok := cv.Expr.Program.(*vm.Program)
	if !ok {
		return nil, fmt.Errorf("invalid program type for validator %s", cv.ID)
	}

	output, err := vm.Run(program, env)
	if err != nil {
		return nil, fmt.Errorf("validator %s: %w", cv.ID, err)
	}

	return output, nil
}

// Execute runs a compiled validator against an environment.
// The expression must return a bool.
func Execute(cv *CompiledValidator, env any) *ValidationResult {
	output, err := runProgram(cv, env)
	if err != nil {
		return &ValidationResult{
			Valid:       false,
			ValidatorID: cv.ID,
			Error:       err,
		}
	}

	valid, ok := output.(bool)
	if !ok {
		return &ValidationResult{
			Valid:       false,
			ValidatorID: cv.ID,
			Error:       fmt.Errorf("expression did not return bool"),
		}
	}

	if valid {
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
func ExecuteGroup(cv *CompiledValidator, env any) []*ValidationResult {
	if cv.ResultMode != "per_record" {
		if vr := Execute(cv, env); !vr.Valid {
			return []*ValidationResult{vr}
		}
		return nil
	}

	// Per-record mode: expression returns a list of failing records
	output, err := runProgram(cv, env)
	if err != nil {
		return []*ValidationResult{{
			Valid:       false,
			ValidatorID: cv.ID,
			Error:       err,
		}}
	}

	return toPerRecordResults(output, cv)
}

func toPerRecordResults(output any, cv *CompiledValidator) []*ValidationResult {
	if output == nil {
		return nil
	}

	if records, ok := output.([]*parser.ParsedRecord); ok {
		return resultsFromRecords(records, cv)
	}

	if matches, ok := output.([]*DuplicateMatch); ok {
		return resultsFromDuplicateMatches(matches, cv)
	}

	// The expr engine may wrap results as []any
	if anySlice, ok := output.([]any); ok {
		var records []*parser.ParsedRecord
		var matches []*DuplicateMatch
		for _, item := range anySlice {
			if rec, ok := item.(*parser.ParsedRecord); ok {
				records = append(records, rec)
				continue
			}
			if match, ok := item.(*DuplicateMatch); ok {
				matches = append(matches, match)
			}
		}
		if len(matches) > 0 {
			return resultsFromDuplicateMatches(matches, cv)
		}
		return resultsFromRecords(records, cv)
	}

	return nil
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
