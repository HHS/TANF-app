package decoder

import (
	"fmt"

	"go-parser/internal/config/filespec"
)

// KeyExtractor abstracts key extraction across file formats.
type KeyExtractor interface {
	// ExtractKey returns the composite sort key for the given row.
	// Returns an error if the row is too short or otherwise cannot produce a key.
	ExtractKey(row Row) (string, error)
}

// PositionalKeyExtractor extracts keys from fixed-width positional rows
// using the same byte positions as accumulator key_fields.
type PositionalKeyExtractor struct {
	RptMonthYear filespec.PositionDef
	CaseNumber   filespec.PositionDef
}

// ExtractKey extracts the composite key from a positional row.
func (e *PositionalKeyExtractor) ExtractKey(row Row) (string, error) {
	pr, ok := row.(*PositionalRow)
	if !ok {
		return "", fmt.Errorf("positional key extraction requires PositionalRow, got %T", row)
	}

	data := pr.Data()

	minLen := e.CaseNumber.End
	if e.RptMonthYear.End > minLen {
		minLen = e.RptMonthYear.End
	}
	if len(data) < minLen {
		return "", fmt.Errorf("line too short for key extraction: need %d bytes, got %d", minLen, len(data))
	}

	rptMonth := data[e.RptMonthYear.Start:e.RptMonthYear.End]
	caseNum := data[e.CaseNumber.Start:e.CaseNumber.End]

	return rptMonth + "|" + caseNum, nil
}

// ColumnarKeyExtractor extracts keys from CSV/XLSX rows by column index.
type ColumnarKeyExtractor struct {
	KeyColumns []int
}

// ExtractKey extracts the composite key from a columnar row.
func (e *ColumnarKeyExtractor) ExtractKey(row Row) (string, error) {
	cr, ok := row.(*ColumnarRow)
	if !ok {
		return "", fmt.Errorf("columnar key extraction requires ColumnarRow, got %T", row)
	}

	key := ""
	for i, colIdx := range e.KeyColumns {
		val := cr.Column(colIdx)
		if val == nil {
			return "", fmt.Errorf("column %d is empty or missing", colIdx)
		}
		if i > 0 {
			key += "|"
		}
		key += fmt.Sprintf("%v", val)
	}

	return key, nil
}

// NewKeyExtractor creates the appropriate KeyExtractor based on file specification.
// Returns nil if the spec has no key fields configured.
func NewKeyExtractor(spec *filespec.FileSpec) KeyExtractor {
	if !spec.Accumulator.HasKeyFields() {
		return nil
	}

	kf := spec.Accumulator.KeyFields
	return &PositionalKeyExtractor{
		RptMonthYear: kf.RptMonthYear,
		CaseNumber:   kf.CaseNumber,
	}
}
