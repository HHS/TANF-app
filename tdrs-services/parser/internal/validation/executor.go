package validation

import (
	"fmt"

	"github.com/expr-lang/expr/vm"

	"go-parser/internal/parser"
)

// ValidatorExecutor is the runtime interface shared by expr and native validators.
type ValidatorExecutor interface {
	Execute(*ValidationState) (ValidationOutcome, error)
}

type ValidatorExecutorFunc func(*ValidationState) (ValidationOutcome, error)

func (fn ValidatorExecutorFunc) Execute(state *ValidationState) (ValidationOutcome, error) {
	return fn(state)
}

// ValidationOutcome is the normalized result from one validator execution.
type ValidationOutcome struct {
	Valid            bool
	Records          []*parser.ParsedRecord
	DuplicateMatches []*DuplicateMatch
}

func boolOutcome(valid bool) ValidationOutcome {
	return ValidationOutcome{Valid: valid}
}

func recordsOutcome(records []*parser.ParsedRecord) ValidationOutcome {
	return ValidationOutcome{Valid: len(records) == 0, Records: records}
}

func duplicateMatchesOutcome(matches []*DuplicateMatch) ValidationOutcome {
	return ValidationOutcome{Valid: len(matches) == 0, DuplicateMatches: matches}
}

type exprExecutor struct {
	program    *vm.Program
	makeEnv    func(*ValidationState) any
	resultMode string
}

func newExprExecutor(ce *CompiledExpr, scope string, resultMode string) (ValidatorExecutor, error) {
	if ce == nil {
		return nil, fmt.Errorf("missing compiled expression")
	}
	program, ok := ce.Program.(*vm.Program)
	if !ok {
		return nil, fmt.Errorf("invalid program type")
	}
	return exprExecutor{
		program:    program,
		makeEnv:    exprEnvFactory(scope),
		resultMode: resultMode,
	}, nil
}

func exprEnvFactory(scope string) func(*ValidationState) any {
	return func(state *ValidationState) any {
		if state == nil {
			state = &ValidationState{Scope: scope}
		}
		state.Scope = scope
		return state.exprEnv()
	}
}

func (e exprExecutor) Execute(state *ValidationState) (ValidationOutcome, error) {
	output, err := vm.Run(e.program, e.makeEnv(state))
	if err != nil {
		return ValidationOutcome{}, err
	}
	return outcomeFromOutput(output, e.resultMode)
}

func outcomeFromOutput(output any, resultMode string) (ValidationOutcome, error) {
	if resultMode == "per_record" {
		return perRecordOutcomeFromOutput(output), nil
	}

	valid, ok := output.(bool)
	if !ok {
		return ValidationOutcome{}, fmt.Errorf("expression did not return bool")
	}
	return boolOutcome(valid), nil
}

func perRecordOutcomeFromOutput(output any) ValidationOutcome {
	if output == nil {
		return ValidationOutcome{Valid: true}
	}

	if records, ok := output.([]*parser.ParsedRecord); ok {
		return recordsOutcome(records)
	}

	if matches, ok := output.([]*DuplicateMatch); ok {
		return duplicateMatchesOutcome(matches)
	}

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
			return duplicateMatchesOutcome(matches)
		}
		return recordsOutcome(records)
	}

	return ValidationOutcome{Valid: true}
}
