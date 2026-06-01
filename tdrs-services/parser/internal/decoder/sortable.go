package decoder

import (
	"fmt"
	"iter"
	"log"
	"slices"

	"go-parser/internal/config/filespec"
)

// Sortable provides shared sorting logic for embedding in decoder implementations.
// After DoSort is called, IsSorted returns true and SortedRows yields sorted output.
type Sortable struct {
	sorted      bool
	sortedRows  []Row
	unkeyedRows []Row
	trailer     Row
}

// IsSorted returns true if DoSort has been called.
func (s *Sortable) IsSorted() bool { return s.sorted }

// DoSort reads all rows from the given iterator, classifies and stable-sorts them by key.
// After calling this, IsSorted() returns true and SortedRows() yields sorted output.
func (s *Sortable) DoSort(
	rows iter.Seq2[Row, error],
	detector *RecordTypeDetector,
	keyFields []filespec.KeyFieldDef,
	groupedSchemas []string,
) error {
	groupedSet := make(map[string]bool, len(groupedSchemas))
	for _, name := range groupedSchemas {
		groupedSet[name] = true
	}

	type sortableRow struct {
		row Row
		key string
	}

	var dataRows []sortableRow

	for row, err := range rows {
		if err != nil {
			return fmt.Errorf("error reading row at line %d: %w", row.LineNum(), err)
		}

		// Detect schema to determine if this is a grouped record
		sch, err := detector.Detect(row)
		if err != nil {
			// Unrecognized record type — collect for error reporting
			s.unkeyedRows = append(s.unkeyedRows, row)
			continue
		}

		// Check if this schema participates in grouping
		if !groupedSet[sch.Path] {
			// Non-grouped record: HEADER or TRAILER
			switch sch.RecordType {
			case "HEADER":
				// Add the extra HEADER record(s) to the unkeyedRows which are processed after keyedRows
				s.unkeyedRows = append(s.unkeyedRows, row)
			case "TRAILER":
				s.trailer = row
			default:
				s.unkeyedRows = append(s.unkeyedRows, row)
			}
			continue
		}

		// Extract sort key
		key, err := row.ExtractKey(keyFields)
		if err != nil {
			// Key extraction failed — collect for error reporting
			s.unkeyedRows = append(s.unkeyedRows, row)
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
	s.sortedRows = make([]Row, len(dataRows))
	for i, sr := range dataRows {
		s.sortedRows[i] = sr.row
	}

	s.sorted = true

	log.Printf("Presort complete: %d data rows sorted, %d unkeyed rows",
		len(s.sortedRows), len(s.unkeyedRows))
	if s.trailer != nil {
		log.Printf("Line %d: TRAILER (not accumulated)", s.trailer.LineNum())
	}

	return nil
}

// SortedRows returns an iterator that yields sorted rows followed by unkeyed rows.
func (s *Sortable) SortedRows() iter.Seq2[Row, error] {
	return func(yield func(Row, error) bool) {
		for _, row := range s.sortedRows {
			if !yield(row, nil) {
				return
			}
		}
		for _, row := range s.unkeyedRows {
			if !yield(row, nil) {
				return
			}
		}
	}
}
