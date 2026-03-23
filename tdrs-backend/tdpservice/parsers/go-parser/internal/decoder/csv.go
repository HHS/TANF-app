package decoder

import (
	"encoding/csv"
	"io"
	"iter"
	"strings"

	"go-parser/internal/config/filespec"
)

// CSVDecoder reads CSV files.
// Each row becomes a ColumnarRow with string values.
type CSVDecoder struct {
	Sortable
	reader  *csv.Reader
	closer  io.Closer
	lineNum int

	// recordType is the fixed record type for this file.
	// For FRA files, this is always "TE1".
	recordType string
}

// NewCSVDecoder creates a decoder for CSV files.
func NewCSVDecoder(r io.ReadCloser, recordType string) *CSVDecoder {
	csvReader := csv.NewReader(r)
	// Configure CSV reader
	csvReader.FieldsPerRecord = -1 // Allow variable number of fields
	csvReader.TrimLeadingSpace = true

	return &CSVDecoder{
		reader:     csvReader,
		closer:     r,
		lineNum:    0,
		recordType: recordType,
	}
}

func (d *CSVDecoder) Format() filespec.Format {
	return filespec.FormatColumnar
}

// ReadFirst returns nil for columnar files.
// CSV/columnar files don't have a header record in the data stream.
func (d *CSVDecoder) ReadFirst() (Row, error) {
	return nil, nil
}

func (d *CSVDecoder) Close() error {
	if d.closer != nil {
		return d.closer.Close()
	}
	return nil
}

// Sort reads all rows, sorts them by key, and makes subsequent Rows() calls return sorted output.
func (d *CSVDecoder) Sort(detector *RecordTypeDetector, keyExtractor KeyExtractor, groupedSchemas []string) error {
	return d.Sortable.DoSort(d.unsortedRows(), detector, keyExtractor, groupedSchemas)
}

func (d *CSVDecoder) Rows() iter.Seq2[Row, error] {
	if d.IsSorted() {
		return d.SortedRows()
	}
	return d.unsortedRows()
}

func (d *CSVDecoder) unsortedRows() iter.Seq2[Row, error] {
	return func(yield func(Row, error) bool) {
		for {
			// Read a row from the CSV
			record, err := d.reader.Read()
			if err == io.EOF {
				return
			}
			if err != nil {
				yield(nil, err)
				return
			}

			d.lineNum++

			// Skip empty rows or comment rows
			if len(record) == 0 || (len(record) > 0 && strings.HasPrefix(record[0], "#")) {
				continue
			}

			// Convert []string to []any for consistent interface
			columns := make([]any, len(record))
			for i, v := range record {
				columns[i] = v
			}

			// Create the row
			row := NewColumnarRow(d.lineNum, d.recordType, len(columns), columns)

			if !yield(row, nil) {
				return
			}
		}
	}
}
