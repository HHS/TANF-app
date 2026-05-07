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

// FieldEnv is the environment for Category 2 (field) validation.
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

// RecordEnv is the environment for Category 1 and Category 3 validation.
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
	return &RecordEnv{
		ParsedRecord: rec,
		RecordType:   rec.GetRecordType(),
		LineNumber:   rec.GetLineNumber(),
		RecordLength: rec.GetDecodedSize(),
		Params:       params,
	}
}

// GroupEnv is the environment for Category 4 (group/case) validation.
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
	records := group.Records
	env := &GroupEnv{
		Group:        group,
		TotalRecords: len(records),
		RecordCounts: make(map[string]int),
		HasType:      make(map[string]bool),
	}
	for _, rec := range records {
		recType := rec.GetRecordType()
		env.RecordCounts[recType]++
		env.HasType[recType] = true
	}
	return env
}

// NewGroupEnvWithParams creates a new group validation environment with params.
func NewGroupEnvWithParams(group *parser.ParsedGroup, params map[string]any) *GroupEnv {
	env := NewGroupEnv(group)
	env.Params = params
	return env
}
