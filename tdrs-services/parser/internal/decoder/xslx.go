package decoder

import (
	"fmt"
	"iter"
	"strings"

	"github.com/xuri/excelize/v2"

	"go-parser/internal/config/filespec"
)

// XLSXDecoder reads XLSX (Excel) files.
// Each row becomes a ColumnarRow with typed values (string, int, float64).
type XLSXDecoder struct {
	Sortable
	file    *excelize.File
	sheet   string
	rows    *excelize.Rows
	lineNum int

	recordType string

	firstRead bool
	firstRow  Row
}

// NewXLSXDecoder creates a decoder for XLSX files.
func NewXLSXDecoder(path string, recordType string) (*XLSXDecoder, error) {
	f, err := excelize.OpenFile(path)
	if err != nil {
		return nil, err
	}

	// Get the first sheet
	sheets := f.GetSheetList()
	if len(sheets) == 0 {
		return nil, fmt.Errorf("xlsx file has no sheets")
	}
	sheet := sheets[0]

	rows, err := f.Rows(sheet)
	if err != nil {
		return nil, err
	}

	return &XLSXDecoder{
		file:       f,
		sheet:      sheet,
		rows:       rows,
		lineNum:    0,
		recordType: recordType,
	}, nil
}

func (d *XLSXDecoder) Format() filespec.Format {
	return filespec.FormatColumnar
}

func (d *XLSXDecoder) Close() error {
	if d.rows != nil {
		d.rows.Close()
	}
	if d.file != nil {
		return d.file.Close()
	}
	return nil
}

// ReadFirst returns the first physical row and buffers it for Rows.
// XLSX/columnar files don't have a header record, but FRA uses this row for
// file-level sanity checks before normal record processing.
func (d *XLSXDecoder) ReadFirst() (Row, error) {
	if d.firstRead {
		return d.firstRow, nil
	}
	d.firstRead = true

	row, err := d.readNextRow(false)
	if err != nil {
		return nil, err
	}
	d.firstRow = row
	return row, nil
}

// Sort reads all rows, sorts them by key, and makes subsequent Rows() calls return sorted output.
func (d *XLSXDecoder) Sort(detector *RecordTypeDetector, keyFields []filespec.KeyFieldDef, groupedSchemas []string) error {
	return d.Sortable.DoSort(d.rowsWithBufferedFirst(), detector, keyFields, groupedSchemas)
}

func (d *XLSXDecoder) Rows() iter.Seq2[Row, error] {
	if d.IsSorted() {
		return d.SortedRows()
	}
	return d.rowsWithBufferedFirst()
}

func (d *XLSXDecoder) rowsWithBufferedFirst() iter.Seq2[Row, error] {
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

func (d *XLSXDecoder) unsortedRows() iter.Seq2[Row, error] {
	return func(yield func(Row, error) bool) {
		for {
			row, err := d.readNextRow(true)
			if err != nil {
				yield(nil, err)
				return
			}
			if row == nil {
				return
			}

			if !yield(row, nil) {
				return
			}
		}
	}
}

func (d *XLSXDecoder) readNextRow(skipSkippable bool) (Row, error) {
	for d.rows.Next() {
		d.lineNum++

		cols, err := d.rows.Columns()
		if err != nil {
			return nil, err
		}

		if skipSkippable && (len(cols) == 0 || allEmpty(cols) || strings.HasPrefix(cols[0], "#")) {
			continue
		}

		// Convert to []any
		// TODO: This could probably be []string since the package always converts cells to strings. Need to test further.
		columns := make([]any, len(cols))
		for i, v := range cols {
			columns[i] = v
		}

		return NewColumnarRow(d.lineNum, d.recordType, len(columns), columns), nil
	}

	return nil, nil
}

func allEmpty(cols []string) bool {
	for _, c := range cols {
		if strings.TrimSpace(c) != "" {
			return false
		}
	}
	return true
}
