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

// ExecuteReturningRecords runs a compiled validator that returns a list of failing records.
// This is used for group validators with result_mode: per_record.
// The expression should return a slice of *parser.ParsedRecord.
func ExecuteReturningRecords(cv *CompiledValidator, env any) ([]*parser.ParsedRecord, error) {
	output, err := runProgram(cv, env)
	if err != nil {
		return nil, err
	}

	if output == nil {
		return nil, nil
	}

	// Try direct type assertion
	if records, ok := output.([]*parser.ParsedRecord); ok {
		return records, nil
	}

	// Try to convert from []any (expr engine may wrap results)
	if anySlice, ok := output.([]any); ok {
		var records []*parser.ParsedRecord
		for _, item := range anySlice {
			if rec, ok := item.(*parser.ParsedRecord); ok {
				records = append(records, rec)
			}
		}
		return records, nil
	}

	return nil, fmt.Errorf("validator %s: unexpected return type %T", cv.ID, output)
}
