package parser

import (
	"fmt"
	"slices"
	"strconv"

	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
)

// DecodedRecord holds a decoded row along with its detected schema.
type DecodedRecord struct {
	Row    decoder.Row
	Schema *schema.CompiledSchema
}

// DecodedGroup holds all decoded records belonging to a logical group.
// For key-based grouping: all records with the same (RPT_MONTH_YEAR, CASE_NUMBER).
// For non-keyed: each record is its own group (Key is empty).
type DecodedGroup struct {
	// Key is the composite grouping key: "YYYYMM|CASE_NUMBER"
	// Empty string if no key_fields are configured (each record is its own group).
	Key string

	// RptMonthYear is extracted from the key for convenience (empty if no key_fields)
	RptMonthYear string

	// CaseNumber is extracted from the key for convenience (empty if no key_fields)
	CaseNumber string

	// DecodedRecords contains all rows for this group
	DecodedRecords []DecodedRecord
}

// TotalRecords returns the total number of records in this group.
func (g *DecodedGroup) TotalRecords() int {
	return len(g.DecodedRecords)
}

// DecodedBatch is the unit of work dispatched to workers.
// Contains one or more RecordGroups depending on batch_size configuration.
type DecodedBatch struct {
	// BatchID is a sequential identifier for this batch
	BatchID int

	// DecodedGroups contains the record groups in this batch.
	// - If key_fields set + batch_size=0: 1 group with N records (a case)
	// - If key_fields set + batch_size=M: M groups, each with N records
	// - If no key_fields + batch_size=N: N groups, each with 1 record
	// - If no key_fields + batch_size=0: 1 group with 1 record
	DecodedGroups []*DecodedGroup
}

// TotalGroups returns the number of groups in this batch.
func (b *DecodedBatch) TotalGroups() int {
	return len(b.DecodedGroups)
}

// TotalRecords returns the total number of records across all groups.
func (b *DecodedBatch) TotalRecords() int {
	total := 0
	for _, g := range b.DecodedGroups {
		total += len(g.DecodedRecords)
	}
	return total
}

// ParsedField combines a field definition pointer with its parsed value.
type ParsedField struct {
	Def   *schema.FieldDef // Pointer to schema FieldDef (nil if not set)
	Value any              // Parsed value (nil if empty/missing)
}

// ParsedRecord represents a successfully parsed record.
// For multi-segment schemas (T3, T6, T7), one input line produces multiple ParsedRecords.
// This type is used for all record types including HEADER.
//
// Fields is a slice indexed by the schema's FieldIndex map. Use Get/Set methods
// for field access, or access Fields directly by index for performance-critical code.
type ParsedRecord struct {
	Schema       *schema.CompiledSchema
	DecodedSize  int
	LineNumber   int
	SegmentIndex int           // Which segment this record came from (0-indexed)
	Fields       []ParsedField // Indexed by schema's FieldIndex map
}

// Reset implements the PooledRecord interface in the schema package for ParsedRecord
func (pr *ParsedRecord) Reset() {
	pr.LineNumber = 0
	pr.SegmentIndex = 0
	for i := range pr.Fields {
		pr.Fields[i].Def = nil
		pr.Fields[i].Value = nil
	}
}

// Get retrieves a field value by name.
// Returns nil if the field doesn't exist or has no value.
func (pr *ParsedRecord) Get(fieldName string) any {
	idx, ok := pr.Schema.FieldIndex[fieldName]
	if !ok {
		return nil
	}
	return pr.Fields[idx].Value
}

// GetField implements the FieldGetter interface for use with extractors.
// This allows ParsedRecord to be passed directly to Extract() for source field lookups.
func (pr *ParsedRecord) GetField(fieldName string) any {
	return pr.Get(fieldName)
}

// Set stores a field value by name.
// No-op if the field name is not in the schema.
// Note: This only sets the Value, not the Def. Use SetField() to set both.
func (pr *ParsedRecord) Set(fieldName string, value any) {
	idx, ok := pr.Schema.FieldIndex[fieldName]
	if ok {
		pr.Fields[idx].Value = value
	}
}

// SetField stores both a field definition and value by field index.
// This is the preferred method during parsing when the *FieldDef is already available.
func (pr *ParsedRecord) SetField(def *schema.FieldDef, value any) {
	idx, ok := pr.Schema.FieldIndex[def.Name]
	if ok {
		pr.Fields[idx].Def = def
		pr.Fields[idx].Value = value
	}
}

// GetParsedField returns the full ParsedField (Def + Value) by name.
// Returns nil if the field doesn't exist.
func (pr *ParsedRecord) GetParsedField(fieldName string) *ParsedField {
	idx, ok := pr.Schema.FieldIndex[fieldName]
	if !ok {
		return nil
	}
	return &pr.Fields[idx]
}

// GetString retrieves a field as a string.
// Coerces int values to string if needed.
// Returns empty string if field is nil.
func (pr *ParsedRecord) GetString(fieldName string) string {
	v := pr.Get(fieldName)
	if v == nil {
		return ""
	}
	switch val := v.(type) {
	case string:
		return val
	case int:
		return strconv.Itoa(val)
	default:
		return fmt.Sprintf("%v", val)
	}
}

// GetInt retrieves a field as an int.
// Coerces string values to int if they contain numeric data.
// Returns 0 if field is nil, not convertible, or empty.
func (pr *ParsedRecord) GetInt(fieldName string) int {
	v := pr.Get(fieldName)
	if v == nil {
		return 0
	}
	switch val := v.(type) {
	case int:
		return val
	case string:
		if val == "" {
			return 0
		}
		// Parse string as int, return 0 on failure
		i, err := strconv.Atoi(val)
		if err != nil {
			return 0
		}
		return i
	default:
		return 0
	}
}

// SumFields returns the sum of integer-coercible values for the given field names.
// Missing fields, blank strings, non-numeric values, and non-string field names
// contribute 0 so validator expressions can stay concise.
func (pr *ParsedRecord) SumFields(fieldNames []any) int {
	total := 0
	for _, fieldName := range fieldNames {
		name, ok := fieldName.(string)
		if !ok || name == "" {
			continue
		}
		total += pr.GetInt(name)
	}
	return total
}

// GetRecordType returns the record type from the schema.
func (pr *ParsedRecord) GetRecordType() string {
	return pr.Schema.RecordType
}

// GetLineNumber returns the line number of this record.
func (pr *ParsedRecord) GetLineNumber() int {
	return pr.LineNumber
}

// GetDecodedSize returns the decoded size of this record.
func (pr *ParsedRecord) GetDecodedSize() int {
	return pr.DecodedSize
}

// IsFieldRequired returns true if the field is marked as required in the schema.
// Returns false if the field doesn't exist or has no definition.
func (pr *ParsedRecord) IsFieldRequired(fieldName string) bool {
	pf := pr.GetParsedField(fieldName)
	if pf == nil || pf.Def == nil {
		return false
	}
	return pf.Def.Required
}

// EqualFields returns true if this record has identical field values to another record.
// Uses slices.Equal on the Fields slices — works because ParsedField is comparable
// (pointer Def and interface Value are both comparable types).
// Two records of the same schema type have Fields in the same order with the same
// Def pointers, so this gives correct exact-match comparison.
func (pr *ParsedRecord) EqualFields(other *ParsedRecord) bool {
	return slices.Equal(pr.Fields, other.Fields)
}

// ParseContext carries runtime information extracted from header
// that affects how subsequent records are parsed.
type ParseContext struct {
	DatafileID int32

	// Header contains the fully parsed header record.
	// All header fields are available via Header.Fields.
	Header *ParsedRecord

	// Convenience fields extracted from Header for common use cases:

	// IsEncrypted indicates whether SSN fields need decryption.
	// Determined by header item 9 (encryption indicator = "E").
	IsEncrypted bool

	// Year is the calendar year from the header (item 2).
	Year int

	// Quarter is the calendar quarter from the header (item 3).
	Quarter string
}

// ParsedGroup contains parsing results for a single RecordGroup.
type ParsedGroup struct {
	// Key is the grouping key (empty for non-keyed records)
	Key          string
	RptMonthYear string
	CaseNumber   string

	// Records contains all successfully parsed records in this group
	Records []*ParsedRecord
}

// GetKey returns the grouping key.
func (pg *ParsedGroup) GetKey() string {
	return pg.Key
}

// GetRptMonthYear returns the reporting month/year.
func (pg *ParsedGroup) GetRptMonthYear() string {
	return pg.RptMonthYear
}

// GetCaseNumber returns the case number.
func (pg *ParsedGroup) GetCaseNumber() string {
	return pg.CaseNumber
}

// ParsedBatch contains parsing results for a Batch (one or more groups).
type ParsedBatch struct {
	BatchID int
	Groups  []*ParsedGroup
}

// TotalRecords returns the total number of successfully parsed records.
func (pb *ParsedBatch) TotalRecords() int {
	total := 0
	for _, g := range pb.Groups {
		total += len(g.Records)
	}
	return total
}
