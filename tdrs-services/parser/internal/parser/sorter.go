package parser

import (
	"fmt"
	"slices"

	"go-parser/internal/config/filespec"
	"go-parser/internal/decoder"
)

// SortResult contains the sorted rows and separated non-grouped records.
type SortResult struct {
	// Header is the HEADER row if found during sorting (nil if absent or already consumed).
	Header decoder.Row

	// Trailer is the TRAILER row if found during sorting (nil if absent).
	Trailer decoder.Row

	// SortedRows contains data rows sorted by key, with each row's LineNum() preserved.
	SortedRows []decoder.Row

	// UnkeyedRows contains rows that failed key extraction (too short, unrecognized type, etc.).
	// These are processed after sorted groups to generate pre-check errors.
	UnkeyedRows []decoder.Row
}

// sortableRow pairs a row with its extracted sort key for sorting.
type sortableRow struct {
	row decoder.Row
	key string
}

// Sorter reads all rows from a decoder, separates non-grouped records,
// and stable-sorts data records by key fields.
type Sorter struct {
	detector       *decoder.RecordTypeDetector
	keyFields      []filespec.KeyFieldDef
	groupedSchemas map[string]bool
}

// NewSorter creates a Sorter for the given file specification.
// The detector is used to identify which records are grouped vs. non-grouped.
func NewSorter(spec *filespec.FileSpec, detector *decoder.RecordTypeDetector) *Sorter {
	groupedSchemas := make(map[string]bool)
	for _, name := range spec.Accumulator.GroupedSchemas {
		groupedSchemas[name] = true
	}

	return &Sorter{
		detector:       detector,
		keyFields:      spec.Accumulator.KeyFields.OrderedFields(),
		groupedSchemas: groupedSchemas,
	}
}

// Sort reads all rows from the decoder, separates header/trailer/unkeyed rows,
// and returns data rows sorted by composite key. Each row's LineNum() is preserved.
//
// The sort is stable: records within the same key retain their original
// relative order (e.g., T1 before T2 before T3 for the same case).
func (s *Sorter) Sort(dec decoder.Decoder) (*SortResult, error) {
	result := &SortResult{}

	// Collect all rows and separate by type
	var dataRows []sortableRow

	for row, err := range dec.Rows() {
		if err != nil {
			return nil, fmt.Errorf("error reading row at line %d: %w", row.LineNum(), err)
		}

		// Detect schema to determine if this is a grouped record
		sch, err := s.detector.Detect(row)
		if err != nil {
			// Unrecognized record type — collect for error reporting
			result.UnkeyedRows = append(result.UnkeyedRows, row)
			continue
		}

		// Check if this schema participates in grouping
		if !s.groupedSchemas[sch.Path] {
			// Non-grouped record: HEADER or TRAILER
			switch sch.RecordType {
			case "HEADER":
				result.Header = row
			case "TRAILER":
				result.Trailer = row
			default:
				// Other non-grouped schemas — treat as unkeyed
				result.UnkeyedRows = append(result.UnkeyedRows, row)
			}
			continue
		}

		// Extract sort key
		key, err := row.ExtractKey(s.keyFields)
		if err != nil {
			// Key extraction failed — collect for error reporting
			result.UnkeyedRows = append(result.UnkeyedRows, row)
			continue
		}

		dataRows = append(dataRows, sortableRow{row: row, key: key})
	}

	// Stable sort by key preserves relative order within same key
	slices.SortStableFunc(dataRows, func(a, b sortableRow) int {
		if a.key < b.key {
			return -1
		}
		if a.key > b.key {
			return 1
		}
		return 0
	})

	// Extract sorted rows
	result.SortedRows = make([]decoder.Row, len(dataRows))
	for i, sr := range dataRows {
		result.SortedRows[i] = sr.row
	}

	return result, nil
}
