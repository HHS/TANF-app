package validation

type nativeFactory func(params map[string]any) (ValidatorExecutor, error)

// nativeExecutorFor resolves a native executor factory by validator scope and ID.
func nativeExecutorFor(scope string, id string, params map[string]any) (ValidatorExecutor, bool, error) {
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

// nativeExecutorFromMap compiles a mapped native factory with validator params.
func nativeExecutorFromMap(validators map[string]nativeFactory, id string, params map[string]any) (ValidatorExecutor, bool, error) {
	factory, ok := validators[id]
	if !ok {
		return nil, false, nil
	}
	executor, err := factory(params)
	return executor, true, err
}
