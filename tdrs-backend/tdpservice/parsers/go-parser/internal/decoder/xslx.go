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
	file    *excelize.File
	sheet   string
	rows    *excelize.Rows
	lineNum int

	recordType string
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

// ReadFirst returns nil for columnar files.
// CSV/columnar files don't have a header record in the data stream.
func (d *XLSXDecoder) ReadFirst() (Row, error) {
	return nil, nil
}

func (d *XLSXDecoder) Rows() iter.Seq2[Row, error] {
	return func(yield func(Row, error) bool) {
		for d.rows.Next() {
			d.lineNum++

			cols, err := d.rows.Columns()
			if err != nil {
				yield(nil, err)
				return
			}

			// Skip empty rows
			if len(cols) == 0 || allEmpty(cols) || strings.HasPrefix(cols[0], "#") {
				continue
			}

			// Convert to []any
			// TODO: This could probably be []string since the package always converts cells to strings. Need to test further.
			columns := make([]any, len(cols))
			for i, v := range cols {
				columns[i] = v
			}

			row := NewColumnarRow(d.lineNum, d.recordType, len(columns), columns)

			if !yield(row, nil) {
				return
			}
		}
	}
}

func allEmpty(cols []string) bool {
	for _, c := range cols {
		if strings.TrimSpace(c) != "" {
			return false
		}
	}
	return true
}
