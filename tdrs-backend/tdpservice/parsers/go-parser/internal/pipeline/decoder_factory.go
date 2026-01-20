package pipeline

import (
	"fmt"
	"io"
	"net/http"
	"os"

	"go-parser/internal/config/filespec"
	"go-parser/internal/decoder"
)

// CreateDecoder creates the appropriate decoder based on file format and content type.
// For positional files, it returns a PositionalDecoder.
// For columnar files, it detects whether the file is CSV or XLSX based on MIME type.
func CreateDecoder(file *os.File, spec *filespec.FileSpec) (decoder.Decoder, error) {
	switch spec.Format {
	case filespec.FormatPositional:
		return decoder.NewPostitionalDecoder(file), nil
	case filespec.FormatColumnar:
		return createColumnarDecoder(file, spec)
	default:
		return nil, fmt.Errorf("unknown format: %s", spec.Format)
	}
}

// createColumnarDecoder determines whether the file is CSV or XLSX based on MIME type.
func createColumnarDecoder(file *os.File, spec *filespec.FileSpec) (decoder.Decoder, error) {
	buf := make([]byte, 512)
	_, err := file.Read(buf)
	if err != nil && err != io.EOF {
		return nil, err
	}

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
		return decoder.NewXLSXDecoder(file.Name(), spec.RecordTypeDetection.Schema)
	case "text/plain; charset=utf-8", "text/csv; charset=utf-8":
		return decoder.NewCSVDecoder(file, spec.RecordTypeDetection.Schema), nil
	default:
		return nil, fmt.Errorf("%s has an unknown or unexpected content type: %s", file.Name(), contentType)
	}
}
