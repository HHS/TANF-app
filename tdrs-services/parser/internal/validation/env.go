package validation

import "go-parser/internal/parser"

// DataFileContext contains DataFile submission metadata used by header
// validation expressions. Defined here (rather than in the pipeline package)
// to avoid circular imports.
type DataFileContext struct {
	FiscalYear    int
	FiscalQuarter string
	SectionName   string
	Program       string
}

// GroupStats contains per-group aggregates shared by native and expr validators.
type GroupStats struct {
	TotalRecords int
	RecordCounts map[string]int
	HasType      map[string]bool
}

// NewGroupStats builds group-level aggregates once for a validation pass.
func NewGroupStats(group *parser.ParsedGroup) *GroupStats {
	stats := &GroupStats{
		RecordCounts: make(map[string]int),
		HasType:      make(map[string]bool),
	}
	if group == nil {
		return stats
	}
	stats.TotalRecords = len(group.Records)
	for _, rec := range group.Records {
		recType := rec.GetRecordType()
		stats.RecordCounts[recType]++
		stats.HasType[recType] = true
	}
	return stats
}

// ValidationState is the parser-owned runtime input for all validators.
// Expr-specific environments are built from this state inside the expr executor.
type ValidationState struct {
	Scope           string
	FieldName       string
	Value           any
	Record          *parser.ParsedRecord
	Group           *parser.ParsedGroup
	GroupStats      *GroupStats
	Params          map[string]any
	DataFileContext *DataFileContext
}

// NewGroupValidationState creates reusable group-scope validation state.
func NewGroupValidationState(group *parser.ParsedGroup, dfCtx *DataFileContext) *ValidationState {
	return &ValidationState{
		Scope:           ScopeGroup,
		Group:           group,
		GroupStats:      NewGroupStats(group),
		DataFileContext: dfCtx,
	}
}

// NewRecordValidationState creates reusable record-scope validation state.
func NewRecordValidationState(rec *parser.ParsedRecord, dfCtx *DataFileContext) *ValidationState {
	return &ValidationState{
		Scope:           ScopeRecord,
		Record:          rec,
		DataFileContext: dfCtx,
	}
}

// NewFieldValidationState creates reusable field-scope validation state.
func NewFieldValidationState(rec *parser.ParsedRecord, fieldName string, value any, dfCtx *DataFileContext) *ValidationState {
	return &ValidationState{
		Scope:           ScopeField,
		FieldName:       fieldName,
		Value:           value,
		Record:          rec,
		DataFileContext: dfCtx,
	}
}

// SetField updates reusable field-scope state for the next field validator.
func (s *ValidationState) SetField(fieldName string, value any) {
	s.Scope = ScopeField
	s.FieldName = fieldName
	s.Value = value
}

func (s *ValidationState) Get(fieldName string) any {
	if s == nil || s.Record == nil {
		return nil
	}
	return s.Record.Get(fieldName)
}

func (s *ValidationState) GetString(fieldName string) string {
	if s == nil || s.Record == nil {
		return ""
	}
	return s.Record.GetString(fieldName)
}

func (s *ValidationState) GetInt(fieldName string) int {
	if s == nil || s.Record == nil {
		return 0
	}
	return s.Record.GetInt(fieldName)
}

func (s *ValidationState) SumFields(fieldNames []any) int {
	if s == nil || s.Record == nil {
		return 0
	}
	return s.Record.SumFields(fieldNames)
}

func (s *ValidationState) RecordLength() int {
	if s == nil || s.Record == nil {
		return 0
	}
	return s.Record.GetDecodedSize()
}

func (s *ValidationState) RecordType() string {
	if s == nil || s.Record == nil {
		return ""
	}
	return s.Record.GetRecordType()
}

func (s *ValidationState) LineNumber() int {
	if s == nil || s.Record == nil {
		return 0
	}
	return s.Record.GetLineNumber()
}

func (s *ValidationState) RecordsOfType(recordType string) []*parser.ParsedRecord {
	if s == nil || s.Group == nil {
		return nil
	}
	return getRecordsOfType(s.Group, recordType)
}

func (s *ValidationState) HasAnyRecordOfTypeWithInt(recordType string, fieldName string, expectedValue int) bool {
	if s == nil || s.Group == nil {
		return false
	}
	return hasAnyRecordOfTypeWithInt(s.Group, recordType, fieldName, expectedValue)
}

func (s *ValidationState) HasRelatedRecordWithInt(relatedRecordTypes []string, fieldName string, expectedValue int) bool {
	if s == nil || s.Group == nil {
		return false
	}
	return groupHasRelatedRecordWithInt(s.Group, relatedRecordTypes, fieldName, expectedValue)
}

func (s *ValidationState) exprEnv() any {
	switch s.Scope {
	case ScopeField:
		return fieldExprEnv(s)
	case ScopeRecord:
		return recordExprEnv(s)
	case ScopeGroup:
		return groupExprEnv(s)
	default:
		return s
	}
}

// FieldEnv is the expr environment for Category 2 (field) validation.
// It contains only the field's value - no other metadata needed.
type FieldEnv struct {
	Value           any
	Params          map[string]any   // Runtime params from validator definition
	DataFileContext *DataFileContext // Set when validation needs file submission metadata
}

// NewFieldEnv creates a new field validation environment.
func NewFieldEnv(value any) *FieldEnv {
	return &FieldEnv{Value: value}
}

// NewFieldEnvWithParams creates a new field validation environment with params.
func NewFieldEnvWithParams(value any, params map[string]any) *FieldEnv {
	return &FieldEnv{Value: value, Params: params}
}

func fieldExprEnv(state *ValidationState) *FieldEnv {
	if state == nil {
		return &FieldEnv{}
	}
	return &FieldEnv{
		Value:           state.Value,
		Params:          state.Params,
		DataFileContext: state.DataFileContext,
	}
}

// RecordEnv is the expr environment for Category 1 and Category 3 validation.
// It embeds a *ParsedRecord to promote Get/GetString/GetInt for expressions,
// and adds convenience fields for direct access in expressions.
type RecordEnv struct {
	*parser.ParsedRecord

	// Convenience fields for expressions
	RecordType      string
	LineNumber      int
	RecordLength    int
	Params          map[string]any   // Runtime params from validator definition
	DataFileContext *DataFileContext // Set when validation needs file submission metadata
}

// NewRecordEnv creates a new record validation environment.
func NewRecordEnv(rec *parser.ParsedRecord) *RecordEnv {
	return &RecordEnv{
		ParsedRecord: rec,
		RecordType:   rec.GetRecordType(),
		LineNumber:   rec.GetLineNumber(),
		RecordLength: rec.GetDecodedSize(),
	}
}

// NewRecordEnvWithParams creates a new record validation environment with params.
func NewRecordEnvWithParams(rec *parser.ParsedRecord, params map[string]any) *RecordEnv {
	env := NewRecordEnv(rec)
	env.Params = params
	return env
}

func recordExprEnv(state *ValidationState) *RecordEnv {
	if state == nil || state.Record == nil {
		return &RecordEnv{
			Params:          state.Params,
			DataFileContext: state.DataFileContext,
		}
	}
	return &RecordEnv{
		ParsedRecord:    state.Record,
		RecordType:      state.Record.GetRecordType(),
		LineNumber:      state.Record.GetLineNumber(),
		RecordLength:    state.Record.GetDecodedSize(),
		Params:          state.Params,
		DataFileContext: state.DataFileContext,
	}
}

// GroupEnv is the expr environment for Category 4 (group/case) validation.
// It wraps a *ParsedGroup and provides pre-computed aggregates for expressions.
type GroupEnv struct {
	Group *parser.ParsedGroup

	// Pre-computed aggregates for fast expression evaluation
	TotalRecords    int
	RecordCounts    map[string]int  // "T1" -> count
	HasType         map[string]bool // "T1" -> true
	Params          map[string]any  // Runtime params from validator definition
	DataFileContext *DataFileContext
}

// NewGroupEnv creates a new group validation environment with pre-computed aggregates.
func NewGroupEnv(group *parser.ParsedGroup) *GroupEnv {
	return groupExprEnv(NewGroupValidationState(group, nil))
}

// NewGroupEnvWithParams creates a new group validation environment with params.
func NewGroupEnvWithParams(group *parser.ParsedGroup, params map[string]any) *GroupEnv {
	env := NewGroupEnv(group)
	env.Params = params
	return env
}

func groupExprEnv(state *ValidationState) *GroupEnv {
	stats := groupStatsFromState(state)
	return &GroupEnv{
		Group:           state.Group,
		TotalRecords:    stats.TotalRecords,
		RecordCounts:    stats.RecordCounts,
		HasType:         stats.HasType,
		Params:          state.Params,
		DataFileContext: state.DataFileContext,
	}
}

func groupStatsFromState(state *ValidationState) *GroupStats {
	if state == nil {
		return NewGroupStats(nil)
	}
	if state.GroupStats != nil {
		return state.GroupStats
	}
	return NewGroupStats(state.Group)
}
