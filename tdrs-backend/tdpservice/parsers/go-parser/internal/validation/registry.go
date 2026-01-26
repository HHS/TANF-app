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

// Category constants (legacy, kept for backward compatibility)
const (
	Cat1 = 1 // Record pre-check (record length, format)
	Cat2 = 2 // Field validation (single field)
	Cat3 = 3 // Cross-field validation (multiple fields in same record)
	Cat4 = 4 // Group validation (cross-record, case-level)
)

// Default error types by scope
var defaultErrorTypes = map[string]string{
	ScopeField:  ErrorTypeFieldValue,
	ScopeRecord: ErrorTypeValueConsistency,
	ScopeGroup:  ErrorTypeCaseConsistency,
}

// ValidatorRegistry manages compiled validators for all categories.
type ValidatorRegistry struct {
	// Deduped expressions by (scope, exprString)
	// Used during loading, can be cleared after startup if needed
	expressions map[string]map[string]*CompiledExpr

	// Predefined validators from validators.yaml indexed by scope then ID
	// Used during loading, can be cleared after startup if needed
	predefined map[string]map[string]*validation.ValidatorDef

	// Legacy: Compiled validators per schema/filespec (populated during load)
	// Kept for backward compatibility
	cat1 map[string][]*CompiledValidator            // recordType -> validators
	cat2 map[string]map[string][]*CompiledValidator // recordType -> fieldName -> validators
	cat3 map[string][]*CompiledValidator            // recordType -> validators
	cat4 map[string][]*CompiledValidator            // filespec key -> validators

	// New scope-based storage
	field  map[string]map[string][]*CompiledValidator // recordType -> fieldName -> validators
	record map[string][]*CompiledValidator            // recordType -> validators
	group  map[string][]*CompiledValidator            // filespec key -> validators

	exprOpts []expr.Option
}

// NewValidatorRegistry creates a new empty validator registry.
func NewValidatorRegistry() *ValidatorRegistry {
	return &ValidatorRegistry{
		expressions: make(map[string]map[string]*CompiledExpr),
		predefined:  make(map[string]map[string]*validation.ValidatorDef),
		// Legacy maps
		cat1: make(map[string][]*CompiledValidator),
		cat2: make(map[string]map[string][]*CompiledValidator),
		cat3: make(map[string][]*CompiledValidator),
		cat4: make(map[string][]*CompiledValidator),
		// New scope-based maps
		field:  make(map[string]map[string][]*CompiledValidator),
		record: make(map[string][]*CompiledValidator),
		group:  make(map[string][]*CompiledValidator),
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
// Supports both legacy category-based and new scope-based formats.
type PredefinedValidatorsFile struct {
	// Legacy category-based format
	Category1 []validation.ValidatorDef `yaml:"category1"`
	Category2 []validation.ValidatorDef `yaml:"category2"`
	Category3 []validation.ValidatorDef `yaml:"category3"`
	Category4 []validation.ValidatorDef `yaml:"category4"`

	// New scope-based format
	Field  []validation.ValidatorDef `yaml:"field"`
	Record []validation.ValidatorDef `yaml:"record"`
	Group  []validation.ValidatorDef `yaml:"group"`
}

// loadPredefinedValidators loads predefined validators from validators.yaml.
// Supports both legacy category-based and new scope-based formats.
func (r *ValidatorRegistry) loadPredefinedValidators(path string) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return fmt.Errorf("reading %s: %w", path, err)
	}

	var file PredefinedValidatorsFile
	if err := yaml.Unmarshal(data, &file); err != nil {
		return fmt.Errorf("parsing %s: %w", path, err)
	}

	// Initialize scope-based predefined maps
	r.predefined[ScopeField] = make(map[string]*validation.ValidatorDef)
	r.predefined[ScopeRecord] = make(map[string]*validation.ValidatorDef)
	r.predefined[ScopeGroup] = make(map[string]*validation.ValidatorDef)

	// Load new scope-based format
	for i := range file.Field {
		vdef := &file.Field[i]
		applyDefaultErrorType(vdef, ScopeField)
		r.predefined[ScopeField][vdef.ID] = vdef
	}
	for i := range file.Record {
		vdef := &file.Record[i]
		applyDefaultErrorType(vdef, ScopeRecord)
		r.predefined[ScopeRecord][vdef.ID] = vdef
	}
	for i := range file.Group {
		vdef := &file.Group[i]
		applyDefaultErrorType(vdef, ScopeGroup)
		r.predefined[ScopeGroup][vdef.ID] = vdef
	}

	// Also load legacy category-based format for backward compatibility
	// Map: Cat1 -> record (RECORD_PRE_CHECK), Cat2 -> field, Cat3 -> record, Cat4 -> group
	for i := range file.Category1 {
		vdef := &file.Category1[i]
		if vdef.ErrorType == "" {
			vdef.ErrorType = ErrorTypeRecordPreCheck
		}
		r.predefined[ScopeRecord][vdef.ID] = vdef
	}
	for i := range file.Category2 {
		vdef := &file.Category2[i]
		if vdef.ErrorType == "" {
			vdef.ErrorType = ErrorTypeFieldValue
		}
		r.predefined[ScopeField][vdef.ID] = vdef
	}
	for i := range file.Category3 {
		vdef := &file.Category3[i]
		if vdef.ErrorType == "" {
			vdef.ErrorType = ErrorTypeValueConsistency
		}
		r.predefined[ScopeRecord][vdef.ID] = vdef
	}
	for i := range file.Category4 {
		vdef := &file.Category4[i]
		if vdef.ErrorType == "" {
			vdef.ErrorType = ErrorTypeCaseConsistency
		}
		r.predefined[ScopeGroup][vdef.ID] = vdef
	}

	return nil
}

// applyDefaultErrorType sets the default error type based on scope if not specified.
func applyDefaultErrorType(vdef *validation.ValidatorDef, scope string) {
	if vdef.ErrorType == "" {
		vdef.ErrorType = defaultErrorTypes[scope]
	}
}

// loadSchemaValidators compiles field and record validators from a schema.
// Supports both legacy category-based (category1/2/3) and new scope-based (field/record) formats.
func (r *ValidatorRegistry) loadSchemaValidators(path string, cs *schema.CompiledSchema) error {
	recordType := cs.RecordType

	// Initialize maps for this record type
	if r.cat2[recordType] == nil {
		r.cat2[recordType] = make(map[string][]*CompiledValidator)
	}
	if r.field[recordType] == nil {
		r.field[recordType] = make(map[string][]*CompiledValidator)
	}

	// Load legacy Category1 validators (record scope, RECORD_PRE_CHECK)
	for _, vdef := range cs.Category1 {
		cv, err := r.resolveValidatorByScope(ScopeRecord, &vdef, ErrorTypeRecordPreCheck)
		if err != nil {
			return fmt.Errorf("cat1 validator %s: %w", vdef.ID, err)
		}
		cv.Category = Cat1 // Set legacy category for backward compatibility
		r.cat1[recordType] = append(r.cat1[recordType], cv)
		r.record[recordType] = append(r.record[recordType], cv)
	}

	// Load legacy Category2 validators from shared fields (field scope)
	for _, field := range cs.Shared {
		for _, vdef := range field.Category2 {
			cv, err := r.resolveValidatorByScope(ScopeField, &vdef, "")
			if err != nil {
				return fmt.Errorf("cat2 validator %s for field %s: %w", vdef.ID, field.Name, err)
			}
			cv.Category = Cat2
			r.cat2[recordType][field.Name] = append(r.cat2[recordType][field.Name], cv)
			r.field[recordType][field.Name] = append(r.field[recordType][field.Name], cv)
		}
	}

	// Load legacy Category2 validators from segment fields (field scope)
	for _, seg := range cs.Segments {
		for _, field := range seg.Fields {
			for _, vdef := range field.Category2 {
				cv, err := r.resolveValidatorByScope(ScopeField, &vdef, "")
				if err != nil {
					return fmt.Errorf("cat2 validator %s for field %s: %w", vdef.ID, field.Name, err)
				}
				cv.Category = Cat2
				r.cat2[recordType][field.Name] = append(r.cat2[recordType][field.Name], cv)
				r.field[recordType][field.Name] = append(r.field[recordType][field.Name], cv)
			}
		}
	}

	// Load legacy Category3 validators (record scope, VALUE_CONSISTENCY)
	for _, vdef := range cs.Category3 {
		cv, err := r.resolveValidatorByScope(ScopeRecord, &vdef, "")
		if err != nil {
			return fmt.Errorf("cat3 validator %s: %w", vdef.ID, err)
		}
		cv.Category = Cat3
		r.cat3[recordType] = append(r.cat3[recordType], cv)
		r.record[recordType] = append(r.record[recordType], cv)
	}

	// Load new scope-based validators if present
	for _, vdef := range cs.Record {
		cv, err := r.resolveValidatorByScope(ScopeRecord, &vdef, "")
		if err != nil {
			return fmt.Errorf("record validator %s: %w", vdef.ID, err)
		}
		// Set legacy category based on error type
		if cv.ErrorType == ErrorTypeRecordPreCheck {
			cv.Category = Cat1
			r.cat1[recordType] = append(r.cat1[recordType], cv)
		} else {
			cv.Category = Cat3
			r.cat3[recordType] = append(r.cat3[recordType], cv)
		}
		r.record[recordType] = append(r.record[recordType], cv)
	}

	// Load new scope-based field validators from shared fields
	for _, field := range cs.Shared {
		for _, vdef := range field.Field {
			cv, err := r.resolveValidatorByScope(ScopeField, &vdef, "")
			if err != nil {
				return fmt.Errorf("field validator %s for field %s: %w", vdef.ID, field.Name, err)
			}
			cv.Category = Cat2
			r.cat2[recordType][field.Name] = append(r.cat2[recordType][field.Name], cv)
			r.field[recordType][field.Name] = append(r.field[recordType][field.Name], cv)
		}
	}

	// Load new scope-based field validators from segment fields
	for _, seg := range cs.Segments {
		for _, field := range seg.Fields {
			for _, vdef := range field.Field {
				cv, err := r.resolveValidatorByScope(ScopeField, &vdef, "")
				if err != nil {
					return fmt.Errorf("field validator %s for field %s: %w", vdef.ID, field.Name, err)
				}
				cv.Category = Cat2
				r.cat2[recordType][field.Name] = append(r.cat2[recordType][field.Name], cv)
				r.field[recordType][field.Name] = append(r.field[recordType][field.Name], cv)
			}
		}
	}

	return nil
}

// loadFileSpecValidators compiles group validators from a filespec.
// Supports both legacy category-based (category4) and new scope-based (group) formats.
func (r *ValidatorRegistry) loadFileSpecValidators(key string, fs *filespec.FileSpec) error {
	// Load legacy Category4 validators (group scope)
	for _, vdef := range fs.Category4 {
		cv, err := r.resolveValidatorByScope(ScopeGroup, &vdef, "")
		if err != nil {
			return fmt.Errorf("cat4 validator %s: %w", vdef.ID, err)
		}
		cv.Category = Cat4
		r.cat4[key] = append(r.cat4[key], cv)
		r.group[key] = append(r.group[key], cv)
	}

	// Load new scope-based group validators
	for _, vdef := range fs.Group {
		cv, err := r.resolveValidatorByScope(ScopeGroup, &vdef, "")
		if err != nil {
			return fmt.Errorf("group validator %s: %w", vdef.ID, err)
		}
		cv.Category = Cat4
		r.cat4[key] = append(r.cat4[key], cv)
		r.group[key] = append(r.group[key], cv)
	}

	return nil
}

// getOrCompileExpr returns a shared CompiledExpr, compiling if needed.
// Uses scope to determine the environment type.
func (r *ValidatorRegistry) getOrCompileExpr(scope string, exprStr string, resultMode string) (*CompiledExpr, error) {
	if r.expressions[scope] == nil {
		r.expressions[scope] = make(map[string]*CompiledExpr)
	}

	if ce, ok := r.expressions[scope][exprStr]; ok {
		return ce, nil // Already compiled
	}

	// Compile new expression
	envType := r.envTypeForScope(scope)

	// Determine return type based on result mode
	var returnTypeOpt expr.Option
	if resultMode == "per_record" {
		// For per_record mode, expression returns a list of records
		returnTypeOpt = expr.AsKind(0) // Allow any return type
	} else {
		returnTypeOpt = expr.AsBool()
	}

	// Compile with all options at once
	opts := append([]expr.Option{
		expr.Env(envType),
		returnTypeOpt,
		expr.AllowUndefinedVariables(), // For flexibility with optional fields
	}, r.exprOpts...)

	program, err := expr.Compile(exprStr, opts...)
	if err != nil {
		return nil, err
	}

	ce := &CompiledExpr{Expr: exprStr, Program: program}
	r.expressions[scope][exprStr] = ce
	return ce, nil
}

// envTypeForScope returns the environment type for expression compilation.
func (r *ValidatorRegistry) envTypeForScope(scope string) any {
	switch scope {
	case ScopeRecord:
		return &RecordEnv{}
	case ScopeField:
		return &FieldEnv{}
	case ScopeGroup:
		return &GroupEnv{}
	default:
		return nil
	}
}

// Legacy: envTypeForCategory returns the environment type for expression compilation.
// Deprecated: Use envTypeForScope instead.
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

// resolveValidatorByScope resolves a validator definition to a compiled validator using scope-based lookup.
// If defaultErrorType is provided and vdef.ErrorType is empty, it will be used.
func (r *ValidatorRegistry) resolveValidatorByScope(scope string, vdef *validation.ValidatorDef, defaultErrorType string) (*CompiledValidator, error) {
	id := vdef.ID
	exprStr := vdef.Expr
	message := vdef.Message
	params := vdef.Params
	fields := vdef.Fields
	errorType := vdef.ErrorType
	resultMode := vdef.ResultMode

	// Check if this ID matches a predefined validator
	var predef *validation.ValidatorDef
	if r.predefined[scope] != nil {
		predef = r.predefined[scope][id]
	}

	if predef != nil {
		// Using a predefined validator - cannot override the expression
		if exprStr != "" {
			return nil, fmt.Errorf("validator %q is predefined; cannot override expression (remove 'expr' from schema)", id)
		}
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
		// Use predefined error type if not specified at use-site
		if errorType == "" {
			errorType = predef.ErrorType
		}
		// Use predefined result mode if not specified at use-site
		if resultMode == "" {
			resultMode = predef.ResultMode
		}
	}

	if exprStr == "" {
		return nil, fmt.Errorf("no expression for validator %s (not predefined and no inline expr)", id)
	}

	// Apply error type defaults
	if errorType == "" {
		if defaultErrorType != "" {
			errorType = defaultErrorType
		} else {
			errorType = defaultErrorTypes[scope]
		}
	}

	// Default result mode is "single"
	if resultMode == "" {
		resultMode = "single"
	}

	// Auto-derive fields from params if not specified
	if len(fields) == 0 && len(params) > 0 {
		fields = deriveFieldsFromParams(params)
	}

	ce, err := r.getOrCompileExpr(scope, exprStr, resultMode)
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
		ID:         id,
		Scope:      scope,
		ErrorType:  errorType,
		ResultMode: resultMode,
		Expr:       ce,
		Message:    msgTmpl,
		Fields:     fields,
		Params:     params,
	}, nil
}

// deriveFieldsFromParams extracts field names from common param keys.
// This allows schemas to omit the `fields` array when using parametrized validators.
// TODO: This feels a little clunky. Can we do better?
func deriveFieldsFromParams(params map[string]any) []string {
	var fields []string
	// Look for common field param names
	fieldParamNames := []string{"condition_field", "target_field", "amount_field", "required_field"}
	for _, name := range fieldParamNames {
		if v, ok := params[name]; ok {
			if s, ok := v.(string); ok && s != "" {
				fields = append(fields, s)
			}
		}
	}
	return fields
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

// GetFieldValidators returns field-scope validators for a specific field.
func (r *ValidatorRegistry) GetFieldValidators(recordType, fieldName string) []*CompiledValidator {
	if fields, ok := r.field[recordType]; ok {
		return fields[fieldName]
	}
	return nil
}

// GetFieldValidatorsForRecord returns all fields with field-scope validators for a record type.
func (r *ValidatorRegistry) GetFieldValidatorsForRecord(recordType string) map[string][]*CompiledValidator {
	return r.field[recordType]
}

// GetRecordValidators returns record-scope validators for a record type.
func (r *ValidatorRegistry) GetRecordValidators(recordType string) []*CompiledValidator {
	return r.record[recordType]
}

// GetGroupValidators returns group-scope validators for a filespec.
func (r *ValidatorRegistry) GetGroupValidators(filespecKey string) []*CompiledValidator {
	return r.group[filespecKey]
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

// ExecuteReturningRecords runs a compiled validator that returns a list of failing records.
// This is used for group validators with result_mode: per_record.
// The expression should return a slice of Record (or types that satisfy the Record interface).
func ExecuteReturningRecords(cv *CompiledValidator, env any) []Record {
	program, ok := cv.Expr.Program.(*vm.Program)
	if !ok {
		return nil
	}

	output, err := vm.Run(program, env)
	if err != nil {
		return nil
	}

	// Handle nil result (no failures)
	if output == nil {
		return nil
	}

	// Try to convert to []Record
	if records, ok := output.([]Record); ok {
		return records
	}

	// Try to convert from []any
	if anySlice, ok := output.([]any); ok {
		var records []Record
		for _, item := range anySlice {
			if rec, ok := item.(Record); ok {
				records = append(records, rec)
			}
		}
		return records
	}

	return nil
}

// ClearCompileTimeData clears data that's only needed during loading.
// Call this after startup to free memory.
func (r *ValidatorRegistry) ClearCompileTimeData() {
	r.expressions = nil
	r.predefined = nil
}
