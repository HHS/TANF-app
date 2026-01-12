package decoder

import (
	"bufio"
	"io"
	"iter"
	"strings"

	"go-parser/internal/filespec"
)

// PostitionalDecoder reads positional (fixed-width) UTF-8 text files.
// Each line becomes a PositionalRow.
type PostitionalDecoder struct {
    reader  *bufio.Reader
    closer  io.Closer
    lineNum int
}

// NewPostitionalDecoder creates a decoder for UTF-8 positional files.
func NewPostitionalDecoder(r io.ReadCloser) *PostitionalDecoder {
    return &PostitionalDecoder{
        reader: bufio.NewReader(r),
        closer: r,
        lineNum: 0,
    }
}

func (d *PostitionalDecoder) Format() filespec.Format {
    return filespec.FormatPositional
}

func (d *PostitionalDecoder) Close() error {
    if d.closer != nil {
        return d.closer.Close()
    }
    return nil
}

func (d *PostitionalDecoder) Rows() iter.Seq2[Row, error] {
    return func(yield func(Row, error) bool) {
        for {
            // Read a line from the file
            line, err := d.reader.ReadString('\n')
            if err != nil && err != io.EOF {
                yield(nil, err)
                return
            }

            // Handle blank lines, comments, etc...
            if len(line) == 0 || strings.HasPrefix(line, "#") {
                continue
            }

			// TODO: We might need to update lineNum before this
            if err == io.EOF {
                return
            }

            d.lineNum++

            // Remove trailing newline characters
            line = strings.TrimRight(line, "\r\n")

            // Detect record type from line prefix
            recordType := detectRecordTypeFromPrefix(line)

            // Create the row
            row := NewPositionalRow(d.lineNum, recordType, line)

            // Yield the row to the caller
            if !yield(row, nil) {
                return // Caller wants to stop iteration
            }
        }
    }
}

// detectRecordTypeFromPrefix determines record type from line start.
// This is a basic implementation - the full logic uses FileSpec configuration.
func detectRecordTypeFromPrefix(line string) string {
    if strings.HasPrefix(line, "HEADER") {
        return "HEADER"
    }
    if strings.HasPrefix(line, "TRAILER") {
        return "TRAILER"
    }
    if len(line) >= 2 {
        return line[:2]
    }
    return ""
}
