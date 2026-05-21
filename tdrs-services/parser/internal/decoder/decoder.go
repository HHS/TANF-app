package decoder

import (
	"iter"

	"go-parser/internal/config/filespec"
)

// Decoder reads a data file and produces rows.
type Decoder interface {
	// Format returns the format this decoder produces.
	Format() filespec.Format

	// ReadFirst reads and returns the first row of the file.
	// For positional files, this is typically the HEADER record.
	// For columnar files, this returns nil (no header record in the data).
	// After calling ReadFirst, Rows() will start from the second row.
	// This method should only be called once, before Rows().
	ReadFirst() (Row, error)

	// Rows returns an iterator over all rows in the file.
	// If ReadFirst() was called, iteration starts from the second row.
	// Otherwise, the first row is typically the header, and the last row is typically the trailer.
	// If Sort() was called, returns rows in sorted order.
	Rows() iter.Seq2[Row, error]

	// Sort reads all rows, classifies them, and stable-sorts data rows by key.
	// After calling Sort, subsequent calls to Rows() return sorted rows followed
	// by unkeyed rows. Header/trailer rows are separated out.
	// Must be called after ReadFirst() and before Rows().
	Sort(detector *RecordTypeDetector, keyFields []filespec.KeyFieldDef, groupedSchemas []string) error

	// Close releases any resources held by the decoder.
	Close() error
}
