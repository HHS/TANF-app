package processor

import (
	"go-parser/internal/decoder"
	"go-parser/internal/schema"
)

// RawLine holds a raw row along with its detected schema.
type RawLine struct {
	Row    decoder.Row
	Schema *schema.CompiledSchema
}

// RecordGroup holds all raw lines belonging to a logical group.
// For key-based grouping: all records with the same (RPT_MONTH_YEAR, CASE_NUMBER).
// For non-keyed: each record is its own group (Key is empty).
type RecordGroup struct {
	// Key is the composite grouping key: "YYYYMM|CASE_NUMBER"
	// Empty string if no key_fields are configured (each record is its own group).
	Key string

	// RptMonthYear is extracted from the key for convenience (empty if no key_fields)
	RptMonthYear string

	// CaseNumber is extracted from the key for convenience (empty if no key_fields)
	CaseNumber string

	// Lines contains all rows for this group
	Lines []RawLine
}

// TotalRecords returns the total number of records in this group.
func (g *RecordGroup) TotalRecords() int {
	return len(g.Lines)
}

// Batch is the unit of work dispatched to workers.
// Contains one or more RecordGroups depending on batch_size configuration.
type Batch struct {
	// BatchID is a sequential identifier for this batch
	BatchID int

	// Groups contains the record groups in this batch.
	// - If key_fields set + batch_size=0: 1 group with N records (a case)
	// - If key_fields set + batch_size=M: M groups, each with N records
	// - If no key_fields + batch_size=N: N groups, each with 1 record
	// - If no key_fields + batch_size=0: 1 group with 1 record
	Groups []*RecordGroup
}

// TotalGroups returns the number of groups in this batch.
func (b *Batch) TotalGroups() int {
	return len(b.Groups)
}

// TotalRecords returns the total number of records across all groups.
func (b *Batch) TotalRecords() int {
	total := 0
	for _, g := range b.Groups {
		total += len(g.Lines)
	}
	return total
}
