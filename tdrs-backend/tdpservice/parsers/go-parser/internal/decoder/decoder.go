package decoder

import (
	"iter"

	"go-parser/internal/filespec"
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
	Rows() iter.Seq2[Row, error]

	// Close releases any resources held by the decoder.
	Close() error
}
