package validation

import (
	"fmt"
	"os"
	"path/filepath"
	"text/template"

	"github.com/expr-lang/expr"
	"github.com/expr-lang/expr/vm"
	"gopkg.in/yaml.v3"

	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/config/validation"
)

// Category constants
const (
	Cat1 = 1 // Record pre-check (record length, format)
	Cat2 = 2 // Field validation (single field)
	Cat3 = 3 // Cross-field validation (multiple fields in same record)
	Cat4 = 4 // Group validation (cross-record, case-level)
)

// ValidatorRegistry manages compiled validators for all categories.
type ValidatorRegistry struct {
	// Deduped expressions by (category, exprString)
	// Used during loading, can be cleared after startup if needed
	expressions map[int]map[string]*CompiledExpr

	// Predefined validators from validators.yaml
	// Used during loading, can be cleared after startup if needed
	predefined map[int]map[string]*validation.ValidatorDef

	// Compiled validators per schema/filespec (populated during load)
	// These are the only maps needed at runtime
	cat1 map[string][]*CompiledValidator             // recordType -> validators
	cat2 map[string]map[string][]*CompiledValidator  // recordType -> fieldName -> validators
	cat3 map[string][]*CompiledValidator             // recordType -> validators
	cat4 map[string][]*CompiledValidator             // filespec key -> validators

	exprOpts []expr.Option
}

// NewValidatorRegistry creates a new empty validator registry.
func NewValidatorRegistry() *ValidatorRegistry {
	return &ValidatorRegistry{
		expressions: make(map[int]map[string]*CompiledExpr),
		predefined:  make(map[int]map[string]*validation.ValidatorDef),
		cat1:        make(map[string][]*CompiledValidator),
		cat2:        make(map[string]map[string][]*CompiledValidator),
		cat3:        make(map[string][]*CompiledValidator),
		cat4:        make(map[string][]*CompiledValidator),
	}
}

// Load loads all validators from configuration files.
func (r *ValidatorRegistry) Load(configPath string, schemas map[string]*schema.CompiledSchema, filespecs map[string]*filespec.FileSpec) error {
	// 1. Register custom functions
	r.exprOpts = RegisterFunctions()

	// 2. Load predefined validators from validators.yaml (if exists)
	validatorsPath := filepath.Join(configPath, "validation", "validators.yaml")
	if _, err := os.Stat(validatorsPath); err == nil {
		if err := r.loadPredefinedValidators(validatorsPath); err != nil {
			return fmt.Errorf("loading predefined validators: %w", err)
		}
	}

	// 3. Load validators from all schemas
	for path, cs := range schemas {
		if err := r.loadSchemaValidators(path, cs); err != nil {
			return fmt.Errorf("loading validators from schema %s: %w", path, err)
		}
	}

	// 4. Load validators from all filespecs
	for key, fs := range filespecs {
		if err := r.loadFileSpecValidators(key, fs); err != nil {
			return fmt.Errorf("loading validators from filespec %s: %w", key, err)
		}
	}

	return nil
}

// PredefinedValidatorsFile represents the validators.yaml file format.
type PredefinedValidatorsFile struct {
	Category1 []validation.ValidatorDef `yaml:"category1"`
	Category2 []validation.ValidatorDef `yaml:"category2"`
	Category3 []validation.ValidatorDef `yaml:"category3"`
	Category4 []validation.ValidatorDef `yaml:"category4"`
}

// loadPredefinedValidators loads predefined validators from validators.yaml.
func (r *ValidatorRegistry) loadPredefinedValidators(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("reading %s: %w", path, err)
	}

	var file PredefinedValidatorsFile
	if err := yaml.Unmarshal(data, &file); err != nil {
		return fmt.Errorf("parsing %s: %w", path, err)
	}

	// Index by category and ID
	r.predefined[Cat1] = make(map[string]*validation.ValidatorDef)
	r.predefined[Cat2] = make(map[string]*validation.ValidatorDef)
	r.predefined[Cat3] = make(map[string]*validation.ValidatorDef)
	r.predefined[Cat4] = make(map[string]*validation.ValidatorDef)

	for i := range file.Category1 {
		r.predefined[Cat1][file.Category1[i].ID] = &file.Category1[i]
	}
	for i := range file.Category2 {
		r.predefined[Cat2][file.Category2[i].ID] = &file.Category2[i]
	}
	for i := range file.Category3 {
		r.predefined[Cat3][file.Category3[i].ID] = &file.Category3[i]
	}
	for i := range file.Category4 {
		r.predefined[Cat4][file.Category4[i].ID] = &file.Category4[i]
	}

	return nil
}

// loadSchemaValidators compiles Cat1, Cat2, Cat3 validators from a schema.
func (r *ValidatorRegistry) loadSchemaValidators(path string, cs *schema.CompiledSchema) error {
	recordType := cs.RecordType

	// Cat1 validators
	for _, vdef := range cs.Category1 {
		cv, err := r.resolveValidator(Cat1, &vdef)
		if err != nil {
			return fmt.Errorf("cat1 validator %s: %w", vdef.ID, err)
		}
		r.cat1[recordType] = append(r.cat1[recordType], cv)
	}

	// Initialize cat2 map for this record type
	if r.cat2[recordType] == nil {
		r.cat2[recordType] = make(map[string][]*CompiledValidator)
	}

	// Cat2 validators from shared fields
	for _, field := range cs.Shared {
		for _, vdef := range field.Category2 {
			cv, err := r.resolveValidator(Cat2, &vdef)
			if err != nil {
				return fmt.Errorf("cat2 validator %s for field %s: %w", vdef.ID, field.Name, err)
			}
			r.cat2[recordType][field.Name] = append(r.cat2[recordType][field.Name], cv)
		}
	}

	// Cat2 validators from segment fields
	for _, seg := range cs.Segments {
		for _, field := range seg.Fields {
			for _, vdef := range field.Category2 {
				cv, err := r.resolveValidator(Cat2, &vdef)
				if err != nil {
					return fmt.Errorf("cat2 validator %s for field %s: %w", vdef.ID, field.Name, err)
				}
				r.cat2[recordType][field.Name] = append(r.cat2[recordType][field.Name], cv)
			}
		}
	}

	// Cat3 validators
	for _, vdef := range cs.Category3 {
		cv, err := r.resolveValidator(Cat3, &vdef)
		if err != nil {
			return fmt.Errorf("cat3 validator %s: %w", vdef.ID, err)
		}
		r.cat3[recordType] = append(r.cat3[recordType], cv)
	}

	return nil
}

// loadFileSpecValidators compiles Cat4 validators from a filespec.
func (r *ValidatorRegistry) loadFileSpecValidators(key string, fs *filespec.FileSpec) error {
	for _, vdef := range fs.Category4 {
		cv, err := r.resolveValidator(Cat4, &vdef)
		if err != nil {
			return fmt.Errorf("cat4 validator %s: %w", vdef.ID, err)
		}
		r.cat4[key] = append(r.cat4[key], cv)
	}
	return nil
}

// getOrCompileExpr returns a shared CompiledExpr, compiling if needed.
func (r *ValidatorRegistry) getOrCompileExpr(category int, exprStr string) (*CompiledExpr, error) {
	if r.expressions[category] == nil {
		r.expressions[category] = make(map[string]*CompiledExpr)
	}

	if ce, ok := r.expressions[category][exprStr]; ok {
		return ce, nil // Already compiled
	}

	// Compile new expression
	envType := r.envTypeForCategory(category)
	program, err := expr.Compile(exprStr,
		expr.Env(envType),
		expr.AsBool(),
		expr.AllowUndefinedVariables(), // For flexibility with optional fields
	)
	if err != nil {
		return nil, err
	}

	// Apply custom functions
	for _, opt := range r.exprOpts {
		program, err = expr.Compile(exprStr,
			expr.Env(envType),
			expr.AsBool(),
			expr.AllowUndefinedVariables(),
			opt,
		)
		if err != nil {
			return nil, err
		}
	}

	// Re-compile with all options at once
	opts := append([]expr.Option{
		expr.Env(envType),
		expr.AsBool(),
		expr.AllowUndefinedVariables(),
	}, r.exprOpts...)

	program, err = expr.Compile(exprStr, opts...)
	if err != nil {
		return nil, err
	}

	ce := &CompiledExpr{Expr: exprStr, Program: program}
	r.expressions[category][exprStr] = ce
	return ce, nil
}

// envTypeForCategory returns the environment type for expression compilation.
func (r *ValidatorRegistry) envTypeForCategory(category int) any {
	switch category {
	case Cat1, Cat3:
		return &RecordEnv{}
	case Cat2:
		return &FieldEnv{}
	case Cat4:
		return &GroupEnv{}
	default:
		return nil
	}
}

// resolveValidator resolves a validator definition to a compiled validator.
// It handles both predefined references and inline definitions.
func (r *ValidatorRegistry) resolveValidator(category int, vdef *validation.ValidatorDef) (*CompiledValidator, error) {
	id := vdef.ID
	exprStr := vdef.Expr
	message := vdef.Message
	params := vdef.Params
	fields := vdef.Fields

	// If no expression, try to find predefined validator
	if exprStr == "" && r.predefined[category] != nil {
		if predef, ok := r.predefined[category][id]; ok {
			exprStr = predef.Expr
			if message == "" {
				message = predef.Message
			}
			// Merge params: use-site params take precedence over predefined
			if len(predef.Params) > 0 || len(params) > 0 {
				params = mergeParams(predef.Params, params)
			}
			// Use predefined fields if not specified at use-site
			if len(fields) == 0 {
				fields = predef.Fields
			}
		}
	}

	if exprStr == "" {
		return nil, fmt.Errorf("no expression for validator %s", id)
	}

	ce, err := r.getOrCompileExpr(category, exprStr)
	if err != nil {
		return nil, fmt.Errorf("compiling expression: %w", err)
	}

	var msgTmpl *template.Template
	if message != "" {
		msgTmpl, err = template.New(id).Parse(message)
		if err != nil {
			return nil, fmt.Errorf("parsing message template: %w", err)
		}
	}

	return &CompiledValidator{
		ID:       id,
		Category: category,
		Expr:     ce,
		Message:  msgTmpl,
		Fields:   fields,
		Params:   params,
	}, nil
}

// mergeParams merges predefined params with use-site params.
// Use-site params take precedence over predefined params.
func mergeParams(predefined, useSite map[string]any) map[string]any {
	if len(predefined) == 0 {
		return useSite
	}
	if len(useSite) == 0 {
		return predefined
	}
	// Copy predefined first, then override with use-site
	merged := make(map[string]any, len(predefined)+len(useSite))
	for k, v := range predefined {
		merged[k] = v
	}
	for k, v := range useSite {
		merged[k] = v
	}
	return merged
}

// GetCat1Validators returns Cat1 validators for a record type.
func (r *ValidatorRegistry) GetCat1Validators(recordType string) []*CompiledValidator {
	return r.cat1[recordType]
}

// GetCat2Validators returns Cat2 validators for a specific field.
func (r *ValidatorRegistry) GetCat2Validators(recordType, fieldName string) []*CompiledValidator {
	if fields, ok := r.cat2[recordType]; ok {
		return fields[fieldName]
	}
	return nil
}

// GetCat2FieldsForRecord returns all fields with Cat2 validators for a record type.
func (r *ValidatorRegistry) GetCat2FieldsForRecord(recordType string) map[string][]*CompiledValidator {
	return r.cat2[recordType]
}

// GetCat3Validators returns Cat3 validators for a record type.
func (r *ValidatorRegistry) GetCat3Validators(recordType string) []*CompiledValidator {
	return r.cat3[recordType]
}

// GetCat4Validators returns Cat4 validators for a filespec.
func (r *ValidatorRegistry) GetCat4Validators(filespecKey string) []*CompiledValidator {
	return r.cat4[filespecKey]
}

// Stats returns statistics about compiled validators.
type RegistryStats struct {
	TotalExpressions  int
	Cat1Validators    int
	Cat2Validators    int
	Cat3Validators    int
	Cat4Validators    int
	RecordTypesWithCat1 int
	RecordTypesWithCat2 int
	RecordTypesWithCat3 int
	FileSpecsWithCat4   int
}

// Stats returns statistics about the registry.
func (r *ValidatorRegistry) Stats() RegistryStats {
	stats := RegistryStats{
		RecordTypesWithCat1: len(r.cat1),
		RecordTypesWithCat2: len(r.cat2),
		RecordTypesWithCat3: len(r.cat3),
		FileSpecsWithCat4:   len(r.cat4),
	}

	// Count total expressions
	for _, m := range r.expressions {
		stats.TotalExpressions += len(m)
	}

	// Count validators
	for _, validators := range r.cat1 {
		stats.Cat1Validators += len(validators)
	}
	for _, fields := range r.cat2 {
		for _, validators := range fields {
			stats.Cat2Validators += len(validators)
		}
	}
	for _, validators := range r.cat3 {
		stats.Cat3Validators += len(validators)
	}
	for _, validators := range r.cat4 {
		stats.Cat4Validators += len(validators)
	}

	return stats
}

// Execute runs a compiled validator against an environment.
func Execute(cv *CompiledValidator, env any) *ValidationResult {
	program, ok := cv.Expr.Program.(*vm.Program)
	if !ok {
		return &ValidationResult{
			Valid:       false,
			ValidatorID: cv.ID,
			Error:       fmt.Errorf("invalid program type"),
		}
	}

	output, err := vm.Run(program, env)
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

// ClearCompileTimeData clears data that's only needed during loading.
// Call this after startup to free memory.
func (r *ValidatorRegistry) ClearCompileTimeData() {
	r.expressions = nil
	r.predefined = nil
}
