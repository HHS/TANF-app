package decoder

import (
	"iter"

	"go-parser/internal/filespec"
)

// Decoder reads a data file and produces rows.
type Decoder interface {
    // Format returns the format this decoder produces.
    Format() filespec.Format

    // Rows returns an iterator over all rows in the file.
    // The first row is typically the header, and the last row is typically the trailer.
    Rows() iter.Seq2[Row, error]

    // Close releases any resources held by the decoder.
    Close() error
}
