// Package sentinel centralizes operational parser errors. These are not
// validators.yaml rules because they control parser flow rather than describe
// data validation failures. This lives in it's own package to avoid cycles.
package sentinel

import "errors"

var (
	// ErrUnknownRecordType identifies rows whose record type cannot be matched
	// to any schema in the active file specification.
	ErrUnknownRecordType = errors.New("unknown record type")

	// ErrWriterAborted identifies writes attempted after a per-run rollback abort.
	ErrWriterAborted = errors.New("writer aborted")
)

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
