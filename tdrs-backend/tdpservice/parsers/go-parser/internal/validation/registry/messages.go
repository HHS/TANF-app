package registry

import (
	"bytes"
	"fmt"
	"sort"
	"strings"
	"sync"
	"text/template"
)

// MessageRegistry holds error message templates for validators.
// Templates are resolved in priority order:
// 1. Rule-level override (inline in validator config)
// 2. Field-level override (schema:field:validator)
// 3. Schema-level override (schema:validator)
// 4. Default template (validator)
type MessageRegistry struct {
	// TODO: probably don't need the mutex
	mu        sync.RWMutex
	defaults  map[string]*template.Template // validatorID -> template
	overrides map[string]*template.Template // "schema:field:validator" or "schema:validator" -> template
	funcMap   template.FuncMap              // Custom template functions
}

// NewMessageRegistry creates a new message registry with default template functions.
func NewMessageRegistry() *MessageRegistry {
	return &MessageRegistry{
		defaults:  make(map[string]*template.Template),
		overrides: make(map[string]*template.Template),
		funcMap:   defaultFuncMap(),
	}
}

// defaultFuncMap returns the default template function map.
func defaultFuncMap() template.FuncMap {
	return template.FuncMap{
		// join concatenates slice elements with a separator
		"join": func(sep string, items any) string {
			switch v := items.(type) {
			case []string:
				return strings.Join(v, sep)
			case []int:
				strs := make([]string, len(v))
				for i, val := range v {
					strs[i] = fmt.Sprintf("%d", val)
				}
				return strings.Join(strs, sep)
			case []any:
				strs := make([]string, len(v))
				for i, val := range v {
					strs[i] = fmt.Sprintf("%v", val)
				}
				return strings.Join(strs, sep)
			default:
				return fmt.Sprintf("%v", items)
			}
		},
		// quote wraps a string in quotes
		"quote": func(s any) string {
			return fmt.Sprintf("%q", s)
		},
		// default returns a default value if the input is empty/nil
		"default": func(defaultVal, val any) any {
			if val == nil {
				return defaultVal
			}
			if s, ok := val.(string); ok && s == "" {
				return defaultVal
			}
			return val
		},
	}
}

// RegisterDefault adds a default message template for a validator.
// This is used when no more specific override is found.
func (r *MessageRegistry) RegisterDefault(validatorID, tmpl string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	t, err := template.New(validatorID).Funcs(r.funcMap).Parse(tmpl)
	if err != nil {
		return fmt.Errorf("parsing template for %q: %w", validatorID, err)
	}
	r.defaults[validatorID] = t
	return nil
}

// MustRegisterDefault is like RegisterDefault but panics on error.
func (r *MessageRegistry) MustRegisterDefault(validatorID, tmpl string) {
	if err := r.RegisterDefault(validatorID, tmpl); err != nil {
		panic(err)
	}
}

// RegisterOverride adds an override message template.
// Key formats:
//   - "schema:field:validator" - field-level override
//   - "schema:validator" - schema-level override
func (r *MessageRegistry) RegisterOverride(key, tmpl string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	t, err := template.New(key).Funcs(r.funcMap).Parse(tmpl)
	if err != nil {
		return fmt.Errorf("parsing override template for %q: %w", key, err)
	}
	r.overrides[key] = t
	return nil
}

// GetTemplate retrieves the best matching template for a validator.
// Resolution order: field-level > schema-level > default
// Returns nil if no template is found.
func (r *MessageRegistry) GetTemplate(validatorID, schemaPath, fieldName string) *template.Template {
	r.mu.RLock()
	defer r.mu.RUnlock()

	// 1. Try field-level override: "schema:field:validator"
	if schemaPath != "" && fieldName != "" {
		key := fmt.Sprintf("%s:%s:%s", schemaPath, fieldName, validatorID)
		if t, ok := r.overrides[key]; ok {
			return t
		}
	}

	// 2. Try schema-level override: "schema:validator"
	if schemaPath != "" {
		key := fmt.Sprintf("%s:%s", schemaPath, validatorID)
		if t, ok := r.overrides[key]; ok {
			return t
		}
	}

	// 3. Fall back to default
	return r.defaults[validatorID]
}

// ParseInline parses an inline message template.
// Used for rule-level message overrides in validator config.
func (r *MessageRegistry) ParseInline(name, tmpl string) (*template.Template, error) {
	r.mu.RLock()
	funcMap := r.funcMap
	r.mu.RUnlock()
	return template.New(name).Funcs(funcMap).Parse(tmpl)
}

// MustParseInline is like ParseInline but panics on error.
func (r *MessageRegistry) MustParseInline(name, tmpl string) *template.Template {
	t, err := r.ParseInline(name, tmpl)
	if err != nil {
		panic(fmt.Sprintf("parsing inline template %q: %v", name, err))
	}
	return t
}

// ListDefaults returns all registered default validator IDs.
func (r *MessageRegistry) ListDefaults() []string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	ids := make([]string, 0, len(r.defaults))
	for id := range r.defaults {
		ids = append(ids, id)
	}
	sort.Strings(ids)
	return ids
}

// ListOverrides returns all registered override keys.
func (r *MessageRegistry) ListOverrides() []string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	keys := make([]string, 0, len(r.overrides))
	for key := range r.overrides {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	return keys
}

// TemplateContext provides data for message template execution.
type TemplateContext struct {
	// RecordType is the record type (e.g., "T1", "T2")
	RecordType string

	// ItemNum is the federal specification item number
	ItemNum string

	// FriendlyName is the human-readable field name
	FriendlyName string

	// FieldName is the internal field name
	FieldName string

	// Value is the actual value that failed validation
	Value any

	// Params contains validator parameters (e.g., min, max, values)
	Params map[string]any

	// Row is the row/line number
	Row int

	// Extra allows validators to pass additional context
	Extra map[string]any
}

// Execute executes a template with the given context.
func Execute(t *template.Template, ctx *TemplateContext) (string, error) {
	if t == nil {
		return "", nil
	}
	var buf bytes.Buffer
	if err := t.Execute(&buf, ctx); err != nil {
		return "", err
	}
	return buf.String(), nil
}

// ExecuteString is like Execute but returns empty string on error.
func ExecuteString(t *template.Template, ctx *TemplateContext) string {
	s, _ := Execute(t, ctx)
	return s
}

// DefaultMessages is the global default message registry.
var DefaultMessages = NewMessageRegistry()

// RegisterBuiltinMessages registers default messages for all built-in validators.
func RegisterBuiltinMessages(r *MessageRegistry) {
	// Comparison validators
	r.MustRegisterDefault("isEqual", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must equal {{.Params.value}}")
	r.MustRegisterDefault("isNotEqual", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must not equal {{.Params.value}}")
	r.MustRegisterDefault("isGreaterThan", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must be greater than {{.Params.value}}")
	r.MustRegisterDefault("isGreaterThanOrEqual", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must be greater than or equal to {{.Params.value}}")
	r.MustRegisterDefault("isLessThan", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must be less than {{.Params.value}}")
	r.MustRegisterDefault("isLessThanOrEqual", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must be less than or equal to {{.Params.value}}")
	r.MustRegisterDefault("isBetween", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must be between {{.Params.min}} and {{.Params.max}}")
	r.MustRegisterDefault("isOneOf", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} is not in allowed values {{.Params.values | join \", \"}}")

	// String validators
	r.MustRegisterDefault("isEmpty", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): value must be empty")
	r.MustRegisterDefault("isNotEmpty", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): value is required and cannot be empty")
	r.MustRegisterDefault("hasLength", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): value must have length {{.Params.length}}")
	r.MustRegisterDefault("hasMinLength", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): value must have at least {{.Params.min}} characters")
	r.MustRegisterDefault("hasMaxLength", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): value must have at most {{.Params.max}} characters")
	r.MustRegisterDefault("matchesPattern", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} does not match pattern {{.Params.pattern}}")
	r.MustRegisterDefault("startsWith", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must start with {{.Params.prefix}}")
	r.MustRegisterDefault("endsWith", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} must end with {{.Params.suffix}}")

	// Date validators
	r.MustRegisterDefault("dateYearIsLargerThan", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): year must be larger than {{.Params.year}}, got {{.Value}}")
	r.MustRegisterDefault("dateYearIsLessThan", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): year must be less than {{.Params.year}}, got {{.Value}}")
	r.MustRegisterDefault("dateMonthIsValid", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): month {{.Value}} is not valid (must be 01-12)")
	r.MustRegisterDefault("dateIsValid", "{{.RecordType}} Item {{.ItemNum}} ({{.FriendlyName}}): {{.Value}} is not a valid date")

	// Record validators
	r.MustRegisterDefault("recordHasLength", "{{.RecordType}}: record must have exactly {{.Params.length}} characters")
	r.MustRegisterDefault("recordHasLengthBetween", "{{.RecordType}}: record must have between {{.Params.min}} and {{.Params.max}} characters")
	r.MustRegisterDefault("recordStartsWith", "{{.RecordType}}: record must start with {{.Params.prefix}}")
	r.MustRegisterDefault("caseNumberNotEmpty", "{{.RecordType}}: case number cannot be blank")

	// Cross-field validators
	r.MustRegisterDefault("ifThenAlso", "{{.RecordType}}: when {{.Params.conditionField}} is {{.Params.conditionValue}}, {{.Params.thenField}} must satisfy the constraint")
	r.MustRegisterDefault("sumIsGreaterThan", "{{.RecordType}}: sum of {{.Params.fields | join \", \"}} must be greater than {{.Params.value}}")
	r.MustRegisterDefault("atLeastOneOf", "{{.RecordType}}: at least one of {{.Params.fields | join \", \"}} must have a value")

	// Group validators
	r.MustRegisterDefault("recordTypePresent", "{{.RecordType}}: record type {{.Params.record_type}} is required but not present in case")
	r.MustRegisterDefault("recordCountInRange", "{{.RecordType}}: expected {{.Params.min}} to {{.Params.max}} records of type {{.Params.record_type}}, found {{.Value}}")
	r.MustRegisterDefault("t1HasMatchingChildren", "{{.RecordType}}: T1 record must have at least one T2 or T3 child record")
}
