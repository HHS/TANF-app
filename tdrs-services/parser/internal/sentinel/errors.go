// Package sentinel centralizes operational parser errors. These are not
// validators.yaml rules because they control parser flow rather than describe
// data validation failures. This lives in it's own package to avoid cycles.
package sentinel

import "errors"

var (
	// ErrUnknownRecordType identifies rows whose record type cannot be matched
	// to any schema in the active file specification.
	ErrUnknownRecordType = errors.New("unknown record type")

	// ErrDecoderUnknown identifies files whose bytes cannot be matched to a
	// supported decoder before normal parser validation can begin.
	ErrDecoderUnknown = errors.New("decoder unknown")

	// ErrWriterAborted identifies writes attempted after a per-run rollback abort.
	ErrWriterAborted = errors.New("writer aborted")
)

const DecoderUnknownMessage = "Could not determine encoding of FRA file. If the file is an XLSX file, ensure it can be opened in Excel. If the file is a CSV, ensure it can be opened in a text editor and is UTF-8 encoded."

// MultipleHeadersError identifies a second HEADER record and carries the
// offending row number for parser error reporting.
type MultipleHeadersError struct {
	rowNumber int
}

// NewMultipleHeadersError creates an error for a duplicate HEADER row.
func NewMultipleHeadersError(rowNumber int) *MultipleHeadersError {
	return &MultipleHeadersError{rowNumber: rowNumber}
}

func (e *MultipleHeadersError) Error() string {
	return "Multiple headers found."
}

// RowNumber returns the offending HEADER row number.
func (e *MultipleHeadersError) RowNumber() int {
	return e.rowNumber
}
