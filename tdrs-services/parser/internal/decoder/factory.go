package decoder

import (
	"bytes"
	"fmt"
	"io"
	"net/http"
	"os"
	"unicode/utf8"

	"go-parser/internal/config/filespec"
	"go-parser/internal/sentinel"
)

// CreateDecoder creates the appropriate decoder based on file format and content type.
// For positional files, it returns a PositionalDecoder.
// For columnar files, it detects whether the file is CSV or XLSX based on MIME type.
func CreateDecoder(file *os.File, spec *filespec.FileSpec) (Decoder, error) {
	switch spec.Format {
	case filespec.FormatPositional:
		return NewPostitionalDecoder(file), nil
	case filespec.FormatColumnar:
		return createColumnarDecoder(file, spec)
	default:
		return nil, fmt.Errorf("%w: unknown format %q", sentinel.ErrDecoderUnknown, spec.Format)
	}
}

// createColumnarDecoder determines whether the file is CSV or XLSX based on MIME type.
func createColumnarDecoder(file *os.File, spec *filespec.FileSpec) (Decoder, error) {
	buf := make([]byte, 512)
	n, err := file.Read(buf)
	if err != nil && err != io.EOF {
		return nil, err
	}
	sample := buf[:n]

	// Rewind the file pointer for later reading
	if _, err := file.Seek(0, io.SeekStart); err != nil {
		return nil, fmt.Errorf("failed to rewind file: %w", err)
	}

	contentType := http.DetectContentType(buf)
	switch contentType {
	case "application/zip":
		// XLSX files are detected as application/zip because they are Open XML formats wrapped in a zip container.
		// Let the XLSX decoder handle opening the file in the format it needs
		defer file.Close()
		return NewXLSXDecoder(file.Name(), spec.RecordTypeDetection.Schema)
	case "text/plain; charset=utf-8", "text/csv; charset=utf-8":
		return NewCSVDecoder(file, spec.RecordTypeDetection.Schema), nil
	case "application/octet-stream":
		if isBinaryContent(sample) {
			return nil, fmt.Errorf("%w: %s has binary content", sentinel.ErrDecoderUnknown, file.Name())
		}
		return NewCSVDecoder(file, spec.RecordTypeDetection.Schema), nil
	default:
		return nil, fmt.Errorf("%w: %s has an unknown or unexpected content type: %s", sentinel.ErrDecoderUnknown, file.Name(), contentType)
	}
}

func isBinaryContent(sample []byte) bool {
	return bytes.Contains(sample, []byte{0}) || !utf8.Valid(sample)
}
