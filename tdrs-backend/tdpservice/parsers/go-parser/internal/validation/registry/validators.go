// Package registry provides validator and message registries for the validation system.
package registry

import (
	"fmt"
	"sort"
	"sync"

	"go-parser/internal/validation"
)

// ValidatorRegistry holds all available validators and builds composed validators.
type ValidatorRegistry struct {
	mu        sync.RWMutex
	factories map[string]validation.ValidatorFactory
}

// NewValidatorRegistry creates a new empty validator registry.
func NewValidatorRegistry() *ValidatorRegistry {
	return &ValidatorRegistry{
		factories: make(map[string]validation.ValidatorFactory),
	}
}

// Register adds a validator factory to the registry.
// The id should be the validator name (e.g., "isGreaterThan").
// Panics if a validator with the same id is already registered.
func (r *ValidatorRegistry) Register(id string, factory validation.ValidatorFactory) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, exists := r.factories[id]; exists {
		panic(fmt.Sprintf("validator %q already registered", id))
	}
	r.factories[id] = factory
}

// RegisterFunc is a convenience method for registering simple validators
// that don't need parameters.
func (r *ValidatorRegistry) RegisterFunc(id string, fn validation.ValidatorFunc) {
	r.Register(id, func(params map[string]any) (validation.ValidatorFunc, error) {
		return fn, nil
	})
}

// Get retrieves a validator factory by id.
// Returns nil and false if the validator is not found.
func (r *ValidatorRegistry) Get(id string) (validation.ValidatorFactory, bool) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	factory, ok := r.factories[id]
	return factory, ok
}

// MustGet retrieves a validator factory by id.
// Panics if the validator is not found.
func (r *ValidatorRegistry) MustGet(id string) validation.ValidatorFactory {
	factory, ok := r.Get(id)
	if !ok {
		panic(fmt.Sprintf("validator %q not found", id))
	}
	return factory
}

// Has checks if a validator is registered.
func (r *ValidatorRegistry) Has(id string) bool {
	r.mu.RLock()
	defer r.mu.RUnlock()
	_, ok := r.factories[id]
	return ok
}

// List returns all registered validator ids in sorted order.
func (r *ValidatorRegistry) List() []string {
	r.mu.RLock()
	defer r.mu.RUnlock()
	ids := make([]string, 0, len(r.factories))
	for id := range r.factories {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	return ids
}

// Count returns the number of registered validators.
func (r *ValidatorRegistry) Count() int {
	r.mu.RLock()
	defer r.mu.RUnlock()
	return len(r.factories)
}

// Build creates a ValidatorFunc from a ValidatorConfig.
// For simple validators (no Compose), the ID is looked up in the registry.
// For composed validators, the appropriate composition is built recursively.
func (r *ValidatorRegistry) Build(config validation.ValidatorConfig) (validation.ValidatorFunc, error) {
	if config.Compose != "" {
		return r.buildComposition(config)
	}
	return r.buildSimple(config)
}

// MustBuild is like Build but panics on error.
func (r *ValidatorRegistry) MustBuild(config validation.ValidatorConfig) validation.ValidatorFunc {
	fn, err := r.Build(config)
	if err != nil {
		panic(fmt.Sprintf("failed to build validator %q: %v", config.ID, err))
	}
	return fn
}

// buildSimple builds a simple (non-composed) validator.
func (r *ValidatorRegistry) buildSimple(config validation.ValidatorConfig) (validation.ValidatorFunc, error) {
	factory, ok := r.Get(config.ID)
	if !ok {
		return nil, fmt.Errorf("validator %q not found in registry", config.ID)
	}
	fn, err := factory(config.Params)
	if err != nil {
		return nil, fmt.Errorf("building validator %q: %w", config.ID, err)
	}

	// If field override is specified, wrap the validator to use that field
	if config.Field != "" {
		fn = r.wrapWithFieldOverride(fn, config.Field, &config)
	}

	return fn, nil
}

// wrapWithFieldOverride wraps a validator to operate on a different field.
func (r *ValidatorRegistry) wrapWithFieldOverride(fn validation.ValidatorFunc, fieldName string, config *validation.ValidatorConfig) validation.ValidatorFunc {
	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		// Set field by name
		fieldIdx := ctx.GetFieldIndex(fieldName)
		if fieldIdx < 0 {
			result := validation.NewInvalidResult(config.ID, ctx.Category, config)
			result.Record = ctx.Record
			result.FieldName = fieldName
			return result
		}

		// Run validator
		result := fn(ctx)

		// Update result with field info if invalid
		if !result.Valid {
			result.FieldName = fieldName
		}

		return result
	}
}

// buildComposition builds a composed validator based on the Compose type.
func (r *ValidatorRegistry) buildComposition(config validation.ValidatorConfig) (validation.ValidatorFunc, error) {
	switch config.Compose {
	case "and":
		return r.buildAnd(config)
	case "or":
		return r.buildOr(config)
	case "not":
		return r.buildNot(config)
	case "ifThen":
		return r.buildIfThen(config)
	case "ifThenElse":
		return r.buildIfThenElse(config)
	default:
		return nil, fmt.Errorf("unknown composition type: %q", config.Compose)
	}
}

// buildAnd creates an AND composition - all validators must pass.
func (r *ValidatorRegistry) buildAnd(config validation.ValidatorConfig) (validation.ValidatorFunc, error) {
	if len(config.Validators) == 0 {
		return nil, fmt.Errorf("and composition %q requires at least one validator", config.ID)
	}

	// Recursively build all child validators
	children := make([]validation.ValidatorFunc, len(config.Validators))
	for i, childConfig := range config.Validators {
		child, err := r.Build(childConfig)
		if err != nil {
			return nil, fmt.Errorf("building and child %d: %w", i, err)
		}
		children[i] = child
	}

	// Create a copy of config for the closure
	configCopy := config

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		for _, child := range children {
			result := child(ctx)
			if !result.Valid {
				// Return first failure with this composition's id
				return &validation.ValidationResult{
					Valid:       false,
					ValidatorID: configCopy.ID,
					Category:    ctx.Category,
					FieldName:   result.FieldName,
					Record:      ctx.Record,
					Group:       ctx.Group,
					Config:      &configCopy,
				}
			}
		}
		return validation.ValidResult()
	}, nil
}

// buildOr creates an OR composition - at least one validator must pass.
func (r *ValidatorRegistry) buildOr(config validation.ValidatorConfig) (validation.ValidatorFunc, error) {
	if len(config.Validators) == 0 {
		return nil, fmt.Errorf("or composition %q requires at least one validator", config.ID)
	}

	children := make([]validation.ValidatorFunc, len(config.Validators))
	for i, childConfig := range config.Validators {
		child, err := r.Build(childConfig)
		if err != nil {
			return nil, fmt.Errorf("building or child %d: %w", i, err)
		}
		children[i] = child
	}

	configCopy := config

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		for _, child := range children {
			result := child(ctx)
			if result.Valid {
				return validation.ValidResult()
			}
		}
		// All failed
		return &validation.ValidationResult{
			Valid:       false,
			ValidatorID: configCopy.ID,
			Category:    ctx.Category,
			Record:      ctx.Record,
			Group:       ctx.Group,
			Config:      &configCopy,
		}
	}, nil
}

// buildNot creates a NOT composition - the child validator must fail.
func (r *ValidatorRegistry) buildNot(config validation.ValidatorConfig) (validation.ValidatorFunc, error) {
	if len(config.Validators) != 1 {
		return nil, fmt.Errorf("not composition %q requires exactly 1 validator, got %d", config.ID, len(config.Validators))
	}

	child, err := r.Build(config.Validators[0])
	if err != nil {
		return nil, fmt.Errorf("building not child: %w", err)
	}

	configCopy := config

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		result := child(ctx)
		if result.Valid {
			// Child passed, so NOT fails
			return &validation.ValidationResult{
				Valid:       false,
				ValidatorID: configCopy.ID,
				Category:    ctx.Category,
				Record:      ctx.Record,
				Group:       ctx.Group,
				Config:      &configCopy,
			}
		}
		return validation.ValidResult()
	}, nil
}

// buildIfThen creates an IF-THEN composition.
// If the condition passes, the then validator must also pass.
// If the condition fails, the whole composition passes (condition not met).
func (r *ValidatorRegistry) buildIfThen(config validation.ValidatorConfig) (validation.ValidatorFunc, error) {
	if config.Condition == nil {
		return nil, fmt.Errorf("ifThen composition %q requires a condition", config.ID)
	}
	if config.Then == nil {
		return nil, fmt.Errorf("ifThen composition %q requires a then validator", config.ID)
	}

	condition, err := r.Build(*config.Condition)
	if err != nil {
		return nil, fmt.Errorf("building ifThen condition: %w", err)
	}
	thenValidator, err := r.Build(*config.Then)
	if err != nil {
		return nil, fmt.Errorf("building ifThen then: %w", err)
	}

	configCopy := config

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		condResult := condition(ctx)

		if !condResult.Valid {
			// Condition failed, ifThen passes (condition not met)
			return validation.ValidResult()
		}

		thenResult := thenValidator(ctx)

		if !thenResult.Valid {
			return &validation.ValidationResult{
				Valid:       false,
				ValidatorID: configCopy.ID,
				Category:    ctx.Category,
				FieldName:   thenResult.FieldName,
				Record:      ctx.Record,
				Group:       ctx.Group,
				Config:      &configCopy,
			}
		}
		return validation.ValidResult()
	}, nil
}

// buildIfThenElse creates an IF-THEN-ELSE composition.
// If the condition passes, run the then validator.
// If the condition fails, run the else validator.
func (r *ValidatorRegistry) buildIfThenElse(config validation.ValidatorConfig) (validation.ValidatorFunc, error) {
	if config.Condition == nil {
		return nil, fmt.Errorf("ifThenElse composition %q requires a condition", config.ID)
	}
	if config.Then == nil {
		return nil, fmt.Errorf("ifThenElse composition %q requires a then validator", config.ID)
	}
	if config.Else == nil {
		return nil, fmt.Errorf("ifThenElse composition %q requires an else validator", config.ID)
	}

	condition, err := r.Build(*config.Condition)
	if err != nil {
		return nil, fmt.Errorf("building ifThenElse condition: %w", err)
	}
	thenValidator, err := r.Build(*config.Then)
	if err != nil {
		return nil, fmt.Errorf("building ifThenElse then: %w", err)
	}
	elseValidator, err := r.Build(*config.Else)
	if err != nil {
		return nil, fmt.Errorf("building ifThenElse else: %w", err)
	}

	configCopy := config

	return func(ctx *validation.ValidationContext) *validation.ValidationResult {
		// Apply condition's field override
		condResult := condition(ctx)

		var result *validation.ValidationResult
		if condResult.Valid {
			// Condition passed, run then
			result = thenValidator(ctx)
		} else {
			// Condition failed, run else
			result = elseValidator(ctx)
		}

		if !result.Valid {
			return &validation.ValidationResult{
				Valid:       false,
				ValidatorID: configCopy.ID,
				Category:    ctx.Category,
				FieldName:   result.FieldName,
				Record:      ctx.Record,
				Group:       ctx.Group,
				Config:      &configCopy,
			}
		}
		return validation.ValidResult()
	}, nil
}

// BuildAll builds multiple validators from configs.
func (r *ValidatorRegistry) BuildAll(configs []validation.ValidatorConfig) ([]validation.CompiledValidator, error) {
	validators := make([]validation.CompiledValidator, len(configs))
	for i, config := range configs {
		fn, err := r.Build(config)
		if err != nil {
			return nil, fmt.Errorf("building validator %d (%s): %w", i, config.ID, err)
		}
		configCopy := config
		validators[i] = validation.CompiledValidator{
			Func:   fn,
			Config: &configCopy,
		}
	}
	return validators, nil
}

// DefaultRegistry is the global default validator registry.
// Validators should be registered at init time.
var DefaultRegistry = NewValidatorRegistry()
