package decoder

import (
	"fmt"
	"strings"

	"go-parser/internal/config/filespec"
)

// Row is the interface that all row types implement.
// This allows the parser to work with any row format.
type Row interface {
	// LineNum returns the 1-indexed line number in the source file
	LineNum() int

	// RecordType returns the detected record type (e.g., "T1", "TE1")
	RecordType() string

	// RawData returns the underlying data for debugging/error messages
	RawData() any

	// DecodedLength returns the length of the decoded row
	DecodedLength() int

	// ExtractKey returns the composite key for the configured key fields.
	ExtractKey(fields []filespec.KeyFieldDef) (string, error)
}

// PositionalRow represents a row from a positional (fixed-width) file.
// The data is a string, and fields are accessed by byte positions.
type PositionalRow struct {
	lineNum       int
	recordType    string
	decodedLength int
	data          string
}

// NewPositionalRow creates a new PositionalRow.
func NewPositionalRow(lineNum int, recordType string, decodedLength int, data string) *PositionalRow {
	return &PositionalRow{
		lineNum:       lineNum,
		recordType:    recordType,
		decodedLength: decodedLength,
		data:          data,
	}
}

func (r *PositionalRow) LineNum() int       { return r.lineNum }
func (r *PositionalRow) RecordType() string { return r.recordType }
func (r *PositionalRow) RawData() any       { return r.data }
func (r *PositionalRow) DecodedLength() int { return r.decodedLength }

// Slice extracts a substring from the row data.
// start is inclusive, end is exclusive (Python slice convention).
// Returns empty string if positions are out of bounds.
func (r *PositionalRow) Slice(start, end int) string {
	if start < 0 || end > len(r.data) || start >= end {
		return ""
	}
	return r.data[start:end]
}

// Data returns the full row data as a string.
func (r *PositionalRow) Data() string {
	return r.data
}

func (r *PositionalRow) ExtractKey(fields []filespec.KeyFieldDef) (string, error) {
	// Fields are assumed to be ordered by position
	minLen := fields[len(fields)-1].End
	if len(r.data) < minLen {
		return "", fmt.Errorf("line too short for key extraction: need %d bytes, got %d", minLen, len(r.data))
	}

	parts := make([]string, 0, len(fields))
	for _, field := range fields {
		parts = append(parts, r.data[field.Start:field.End])
	}
	return strings.Join(parts, "|"), nil
}

// ColumnarRow represents a row from a columnar (CSV/XLSX) file.
// The data is a slice of values, and fields are accessed by column index.
type ColumnarRow struct {
	lineNum       int
	recordType    string
	decodedLength int
	columns       []any // Can be string, int, float64, etc. (especially from XLSX)
}

// NewColumnarRow creates a new ColumnarRow.
func NewColumnarRow(lineNum int, recordType string, decodedLength int, columns []any) *ColumnarRow {
	return &ColumnarRow{
		lineNum:       lineNum,
		recordType:    recordType,
		decodedLength: decodedLength,
		columns:       columns,
	}
}

func (r *ColumnarRow) LineNum() int       { return r.lineNum }
func (r *ColumnarRow) RecordType() string { return r.recordType }
func (r *ColumnarRow) RawData() any       { return r.columns }
func (r *ColumnarRow) DecodedLength() int { return r.decodedLength }

// Column returns the value at the specified column index.
// Returns nil if the index is out of bounds.
func (r *ColumnarRow) Column(index int) any {
	if index < 0 || index >= len(r.columns) {
		return nil
	}
	return r.columns[index]
}

// ColumnCount returns the number of columns in the row.
func (r *ColumnarRow) ColumnCount() int {
	return len(r.columns)
}

func (r *ColumnarRow) ExtractKey(fields []filespec.KeyFieldDef) (string, error) {
	parts := make([]string, 0, len(fields))
	for _, field := range fields {
		value := r.Column(field.Start)
		if value == nil {
			return "", fmt.Errorf("column %d is empty or missing", field.Start)
		}
		parts = append(parts, strings.TrimSpace(fmt.Sprintf("%v", value)))
	}
	return strings.Join(parts, "|"), nil
}
