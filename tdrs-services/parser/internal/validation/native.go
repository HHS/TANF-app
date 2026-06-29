package validation

type validationParams = map[string]any

type validationRule interface {
	Compile(validationParams) (ValidatorExecutor, error)
	Execute(*ValidationState) (ValidationOutcome, error)
}

// nativeExecutorFor resolves and compiles a native rule by validator scope and ID.
func nativeExecutorFor(scope string, id string, params validationParams) (ValidatorExecutor, bool, error) {
	switch scope {
	case ScopeField:
		return nativeExecutorFromMap(nativeFieldValidators, id, params)
	case ScopeRecord:
		return nativeExecutorFromMap(nativeRecordValidators, id, params)
	case ScopeGroup:
		return nativeExecutorFromMap(nativeGroupValidators, id, params)
	default:
		return nil, false, nil
	}
}

// nativeExecutorFromMap compiles a mapped validation rule with validator params.
func nativeExecutorFromMap(validators map[string]validationRule, id string, params validationParams) (ValidatorExecutor, bool, error) {
	rule, ok := validators[id]
	if !ok {
		return nil, false, nil
	}
	executor, err := rule.Compile(validationParams(params))
	return executor, true, err
}
