package parser

import (
	"go-parser/internal/decoder"
	"go-parser/internal/schema"
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
	SegmentIndex int   // Which segment this record came from (0-indexed)
	Fields       []any // Indexed by schema's FieldIndex map
}

// Reset implements the PooledRecord interface in the schema package for ParsedRecord
func (pr *ParsedRecord) Reset() {
	pr.LineNumber = 0
	pr.SegmentIndex = 0
	for i := range pr.Fields {
		pr.Fields[i] = nil
	}
}

// Get retrieves a field value by name.
// Returns nil if the field doesn't exist or has no value.
func (pr *ParsedRecord) Get(fieldName string) any {
	idx, ok := pr.Schema.FieldIndex[fieldName]
	if !ok {
		return nil
	}
	return pr.Fields[idx]
}

// GetField implements the FieldGetter interface for use with extractors.
// This allows ParsedRecord to be passed directly to Extract() for source field lookups.
func (pr *ParsedRecord) GetField(fieldName string) any {
	return pr.Get(fieldName)
}

// Set stores a field value by name.
// No-op if the field name is not in the schema.
func (pr *ParsedRecord) Set(fieldName string, value any) {
	idx, ok := pr.Schema.FieldIndex[fieldName]
	if ok {
		pr.Fields[idx] = value
	}
}

// GetString retrieves a field as a string.
// Returns empty string if field is nil or not a string.
func (pr *ParsedRecord) GetString(fieldName string) string {
	v := pr.Get(fieldName)
	if s, ok := v.(string); ok {
		return s
	}
	return ""
}

// GetInt retrieves a field as an int.
// Returns 0 if field is nil or not an int.
func (pr *ParsedRecord) GetInt(fieldName string) int {
	v := pr.Get(fieldName)
	if i, ok := v.(int); ok {
		return i
	}
	return 0
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
