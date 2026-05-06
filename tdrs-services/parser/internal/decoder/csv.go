package decoder

import (
	"bufio"
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
	rawReader *bufio.Reader
	reader    *csv.Reader
	closer    io.Closer
	lineNum   int

	// recordType is the fixed record type for this file.
	// For FRA files, this is always "TE1".
	recordType string

	firstRead bool
	firstRow  Row
}

// NewCSVDecoder creates a decoder for CSV files.
func NewCSVDecoder(r io.ReadCloser, recordType string) *CSVDecoder {
	rawReader := bufio.NewReader(r)
	csvReader := csv.NewReader(rawReader)
	// Configure CSV reader
	csvReader.FieldsPerRecord = -1 // Allow variable number of fields
	csvReader.TrimLeadingSpace = true

	return &CSVDecoder{
		rawReader:  rawReader,
		reader:     csvReader,
		closer:     r,
		lineNum:    0,
		recordType: recordType,
	}
}

func (d *CSVDecoder) Format() filespec.Format {
	return filespec.FormatColumnar
}

// ReadFirst returns the first physical row and buffers it for Rows.
// CSV/columnar files don't have a header record, but FRA uses this row for
// file-level sanity checks before normal record processing.
func (d *CSVDecoder) ReadFirst() (Row, error) {
	if d.firstRead {
		return d.firstRow, nil
	}
	d.firstRead = true

	row, err := d.readNextRow(false)
	if err == io.EOF {
		return nil, nil
	}
	if err != nil {
		return nil, err
	}
	d.firstRow = row
	return row, nil
}

func (d *CSVDecoder) Close() error {
	if d.closer != nil {
		return d.closer.Close()
	}
	return nil
}

// Sort reads all rows, sorts them by key, and makes subsequent Rows() calls return sorted output.
func (d *CSVDecoder) Sort(detector *RecordTypeDetector, keyFields []filespec.KeyFieldDef, groupedSchemas []string) error {
	return d.Sortable.DoSort(d.rowsWithBufferedFirst(), detector, keyFields, groupedSchemas)
}

func (d *CSVDecoder) Rows() iter.Seq2[Row, error] {
	if d.IsSorted() {
		return d.SortedRows()
	}
	return d.rowsWithBufferedFirst()
}

func (d *CSVDecoder) rowsWithBufferedFirst() iter.Seq2[Row, error] {
	return func(yield func(Row, error) bool) {
		if d.firstRow != nil {
			row := d.firstRow
			d.firstRow = nil
			if !yield(row, nil) {
				return
			}
		}

		for row, err := range d.unsortedRows() {
			if !yield(row, err) {
				return
			}
		}
	}
}

func (d *CSVDecoder) unsortedRows() iter.Seq2[Row, error] {
	return func(yield func(Row, error) bool) {
		for {
			row, err := d.readNextRow(true)
			if err == io.EOF {
				return
			}
			if err != nil {
				yield(nil, err)
				return
			}

			if !yield(row, nil) {
				return
			}
		}
	}
}

func (d *CSVDecoder) readNextRow(skipSkippable bool) (Row, error) {
	for {
		if !skipSkippable {
			// csv.Reader skips blank physical lines; ReadFirst needs to expose one
			// so FRA can reject files whose first row is empty.
			blank, err := d.consumeLeadingBlankLine()
			if err != nil {
				return nil, err
			}
			if blank {
				return NewColumnarRow(d.lineNum, d.recordType, 0, []any{}), nil
			}
		}

		record, err := d.reader.Read()
		if err != nil {
			return nil, err
		}
		d.lineNum++

		// Normal row iteration keeps the historical behavior of ignoring
		// comments and empty rows. ReadFirst does not, because FRA validates
		// the first physical row before streaming records.
		if skipSkippable && (len(record) == 0 || strings.HasPrefix(record[0], "#")) {
			continue
		}

		columns := make([]any, len(record))
		for i, v := range record {
			columns[i] = v
		}

		return NewColumnarRow(d.lineNum, d.recordType, len(columns), columns), nil
	}
}

func (d *CSVDecoder) consumeLeadingBlankLine() (bool, error) {
	b, err := d.rawReader.Peek(1)
	if err == io.EOF {
		return false, nil
	}
	if err != nil {
		return false, err
	}

	switch b[0] {
	case '\n':
		if _, err := d.rawReader.ReadByte(); err != nil {
			return false, err
		}
	case '\r':
		if _, err := d.rawReader.ReadByte(); err != nil {
			return false, err
		}
		if next, err := d.rawReader.Peek(1); err == nil && next[0] == '\n' {
			if _, err := d.rawReader.ReadByte(); err != nil {
				return false, err
			}
		}
	default:
		return false, nil
	}

	d.lineNum++
	return true, nil
}
