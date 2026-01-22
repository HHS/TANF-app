package validation

// Record is the interface for parsed records used in validation.
// This interface allows the validation package to work with parser types
// without creating an import cycle.
type Record interface {
	Get(fieldName string) any
	GetString(fieldName string) string
	GetInt(fieldName string) int
	GetRecordType() string
	GetLineNumber() int
	GetDecodedSize() int
}

// Group is the interface for parsed groups used in validation.
type Group interface {
	GetKey() string
	GetRptMonthYear() string
	GetCaseNumber() string
}

// GroupWrapper wraps a Group and its records for validation.
// This avoids the slice conversion issue ([]T doesn't satisfy []I).
type GroupWrapper struct {
	group   Group
	records []Record
}

// WrapGroup creates a GroupWrapper from a Group and records.
// Use this when you have a ParsedGroup and need to pass it to validation.
func WrapGroup(group Group, records []Record) *GroupWrapper {
	return &GroupWrapper{
		group:   group,
		records: records,
	}
}

// GetKey returns the grouping key.
func (gw *GroupWrapper) GetKey() string {
	return gw.group.GetKey()
}

// GetRptMonthYear returns the reporting month/year.
func (gw *GroupWrapper) GetRptMonthYear() string {
	return gw.group.GetRptMonthYear()
}

// GetCaseNumber returns the case number.
func (gw *GroupWrapper) GetCaseNumber() string {
	return gw.group.GetCaseNumber()
}

// GetRecords returns the records in this group.
func (gw *GroupWrapper) GetRecords() []Record {
	return gw.records
}

// WrappedGroup is the interface used internally by validation.
// It extends Group with GetRecords().
type WrappedGroup interface {
	Group
	GetRecords() []Record
}

// FieldEnv is the environment for Category 2 (field) validation.
// It contains only the field's value - no other metadata needed.
type FieldEnv struct {
	Value any
}

// NewFieldEnv creates a new field validation environment.
func NewFieldEnv(value any) *FieldEnv {
	return &FieldEnv{Value: value}
}

// RecordEnv is the environment for Category 1 and Category 3 validation.
// It wraps a Record and provides convenience fields for expressions.
type RecordEnv struct {
	Record

	// Convenience fields for expressions
	RecordType   string
	LineNumber   int
	RecordLength int
}

// NewRecordEnv creates a new record validation environment.
func NewRecordEnv(rec Record) *RecordEnv {
	return &RecordEnv{
		Record:       rec,
		RecordType:   rec.GetRecordType(),
		LineNumber:   rec.GetLineNumber(),
		RecordLength: rec.GetDecodedSize(),
	}
}

// GroupEnv is the environment for Category 4 (group/case) validation.
// It wraps a WrappedGroup and provides pre-computed aggregates for expressions.
type GroupEnv struct {
	Group WrappedGroup

	// Pre-computed aggregates for fast expression evaluation
	TotalRecords int
	RecordCounts map[string]int  // "T1" -> count
	HasType      map[string]bool // "T1" -> true
}

// NewGroupEnv creates a new group validation environment with pre-computed aggregates.
func NewGroupEnv(group WrappedGroup) *GroupEnv {
	records := group.GetRecords()
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
