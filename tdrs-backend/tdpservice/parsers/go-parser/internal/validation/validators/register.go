package validators

import (
	"go-parser/internal/validation/registry"
)

// RegisterAll registers all built-in validators with the given registry.
func RegisterAll(r *registry.ValidatorRegistry) {
	RegisterComparison(r)
	RegisterString(r)
	RegisterDate(r)
	RegisterRecord(r)
	RegisterCrossField(r)
	RegisterGroup(r)
}

// RegisterWithDefaults registers all built-in validators with the default registry.
func RegisterWithDefaults() {
	RegisterAll(registry.DefaultRegistry)
}
