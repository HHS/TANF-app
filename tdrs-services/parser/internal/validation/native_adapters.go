package validation

import "go-parser/internal/parser"

// fieldPredicate adapts a field-value predicate into a native validator factory.
func fieldPredicate(fn func(value any) bool) nativeFactory {
	return func(map[string]any) (ValidatorExecutor, error) {
		return fieldPredicateExecutor(fn), nil
	}
}

// fieldPredicateExecutor runs a field predicate against ValidationState.Value.
func fieldPredicateExecutor(fn func(value any) bool) ValidatorExecutor {
	return fieldPredicateValidator{predicate: fn}
}

type fieldPredicateValidator struct {
	predicate func(value any) bool
}

func (v fieldPredicateValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(v.predicate(fieldValueFromState(state))), nil
}

// recordPredicate adapts a record-state predicate into a native validator factory.
func recordPredicate(fn func(state *ValidationState) bool) nativeFactory {
	return func(map[string]any) (ValidatorExecutor, error) {
		return recordPredicateExecutor(fn), nil
	}
}

// recordPredicateExecutor normalizes a record predicate into a bool outcome.
func recordPredicateExecutor(fn func(state *ValidationState) bool) ValidatorExecutor {
	return recordPredicateValidator{predicate: fn}
}

type recordPredicateValidator struct {
	predicate func(state *ValidationState) bool
}

func (v recordPredicateValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(v.predicate(state)), nil
}

// groupPredicateExecutor normalizes a group predicate into a bool outcome.
func groupPredicateExecutor(fn func(state *ValidationState) bool) ValidatorExecutor {
	return groupPredicateValidator{predicate: fn}
}

type groupPredicateValidator struct {
	predicate func(state *ValidationState) bool
}

func (v groupPredicateValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return boolOutcome(v.predicate(state)), nil
}

// groupRecordsExecutor converts invalid records into a per-record outcome.
func groupRecordsExecutor(fn func(state *ValidationState) []*parser.ParsedRecord) ValidatorExecutor {
	return groupRecordsValidator{records: fn}
}

type groupRecordsValidator struct {
	records func(state *ValidationState) []*parser.ParsedRecord
}

func (v groupRecordsValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return recordsOutcome(v.records(state)), nil
}

// groupDuplicateMatchesExecutor converts duplicate matches into a per-record outcome.
func groupDuplicateMatchesExecutor(fn func(state *ValidationState) []*DuplicateMatch) ValidatorExecutor {
	return groupDuplicateMatchesValidator{matches: fn}
}

type groupDuplicateMatchesValidator struct {
	matches func(state *ValidationState) []*DuplicateMatch
}

func (v groupDuplicateMatchesValidator) Execute(state *ValidationState) (ValidationOutcome, error) {
	return duplicateMatchesOutcome(v.matches(state)), nil
}
