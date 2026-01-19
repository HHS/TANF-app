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
	reader       *bufio.Reader
	closer       io.Closer
	lineNum      int
	firstRow     Row  // Stores the first row if ReadFirst() was called
	firstRowRead bool // True if ReadFirst() was called
}

// NewPostitionalDecoder creates a decoder for UTF-8 positional files.
func NewPostitionalDecoder(r io.ReadCloser) *PostitionalDecoder {
	return &PostitionalDecoder{
		reader:  bufio.NewReader(r),
		closer:  r,
		lineNum: 0,
	}
}

func (d *PostitionalDecoder) Format() filespec.Format {
	return filespec.FormatPositional
}

// ReadFirst reads and returns the first row of the file.
// For positional files, this is typically the HEADER record.
// After calling ReadFirst, Rows() will start from the second row.
// This method should only be called once, before Rows().
func (d *PostitionalDecoder) ReadFirst() (Row, error) {
	if d.firstRowRead {
		return d.firstRow, nil // Already read, return cached
	}

	// Read the first line
	line, err := d.reader.ReadString('\n')
	if err != nil && err != io.EOF {
		return nil, err
	}

	// Handle empty file
	if len(line) == 0 && err == io.EOF {
		d.firstRowRead = true
		return nil, nil
	}

	d.lineNum++
	d.firstRowRead = true
	decodedLength := len(line)

	// Remove trailing newline characters
	line = strings.TrimRight(line, "\r\n")

	// Detect record type from line prefix
	recordType := detectRecordTypeFromPrefix(line)

	// Create and store the row
	d.firstRow = NewPositionalRow(d.lineNum, recordType, decodedLength, line)

	return d.firstRow, nil
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
			if (len(line) == 0 && err != io.EOF) || strings.HasPrefix(line, "#") {
				continue
			}

			// TODO: We might need to update lineNum before this
			if err == io.EOF {
				return
			}

			d.lineNum++

			decodedLength := len(line)

			// Remove trailing newline characters
			line = strings.TrimRight(line, "\r\n")

			// Detect record type from line prefix
			recordType := detectRecordTypeFromPrefix(line)

			// Create the row
			row := NewPositionalRow(d.lineNum, recordType, decodedLength, line)

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
