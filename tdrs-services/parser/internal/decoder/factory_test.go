package decoder

import (
	"errors"
	"os"
	"testing"

	"go-parser/internal/config/filespec"
	"go-parser/internal/sentinel"
)

func TestCreateDecoder_Positional(t *testing.T) {
	// Create a temp file with positional content
	tmpFile, err := os.CreateTemp("", "goparser-pos-*.txt")
	if err != nil {
		t.Fatalf("Failed to create temp file: %v", err)
	}
	defer os.Remove(tmpFile.Name())

	content := "HEADER202401 some data\nT1202401CASE001    rest-of-data\n"
	if _, err := tmpFile.WriteString(content); err != nil {
		t.Fatalf("Failed to write temp file: %v", err)
	}
	if _, err := tmpFile.Seek(0, 0); err != nil {
		t.Fatalf("Failed to seek: %v", err)
	}

	spec := &filespec.FileSpec{
		Format: filespec.FormatPositional,
	}

	dec, err := CreateDecoder(tmpFile, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	if dec.Format() != filespec.FormatPositional {
		t.Errorf("expected format %s, got %s", filespec.FormatPositional, dec.Format())
	}

	if _, ok := dec.(*PostitionalDecoder); !ok {
		t.Errorf("expected *PostitionalDecoder, got %T", dec)
	}
}

func TestCreateDecoder_ColumnarCSV(t *testing.T) {
	// Create a temp file with CSV content.
	// http.DetectContentType needs enough text to detect as text/plain.
	tmpFile, err := os.CreateTemp("", "goparser-csv-*.csv")
	if err != nil {
		t.Fatalf("Failed to create temp file: %v", err)
	}
	defer os.Remove(tmpFile.Name())

	// Write enough rows so http.DetectContentType identifies this as text
	var content string
	for i := 0; i < 50; i++ {
		content += "col1,col2,col3,col4,col5,col6,col7,col8\n"
	}
	if _, err := tmpFile.WriteString(content); err != nil {
		t.Fatalf("Failed to write temp file: %v", err)
	}
	if _, err := tmpFile.Seek(0, 0); err != nil {
		t.Fatalf("Failed to seek: %v", err)
	}

	spec := &filespec.FileSpec{
		Format: filespec.FormatColumnar,
		RecordTypeDetection: filespec.RecordTypeDetection{
			Schema: "fra/te1",
		},
	}

	dec, err := CreateDecoder(tmpFile, spec)
	if err != nil {
		t.Fatalf("CreateDecoder failed: %v", err)
	}
	defer dec.Close()

	if dec.Format() != filespec.FormatColumnar {
		t.Errorf("expected format %s, got %s", filespec.FormatColumnar, dec.Format())
	}

	if _, ok := dec.(*CSVDecoder); !ok {
		t.Errorf("expected *CSVDecoder, got %T", dec)
	}
}

func TestCreateDecoder_UnknownFormat(t *testing.T) {
	// Create a temp file (content doesn't matter for this test)
	tmpFile, err := os.CreateTemp("", "goparser-unk-*")
	if err != nil {
		t.Fatalf("Failed to create temp file: %v", err)
	}
	defer os.Remove(tmpFile.Name())
	defer tmpFile.Close()

	spec := &filespec.FileSpec{
		Format: "unknown_format",
	}

	_, err = CreateDecoder(tmpFile, spec)
	if err == nil {
		t.Fatal("expected error for unknown format")
	}
	if !errors.Is(err, sentinel.ErrDecoderUnknown) {
		t.Fatalf("expected ErrDecoderUnknown, got %v", err)
	}
}

func TestCreateColumnarDecoder_UnknownContentTypeReturnsSentinel(t *testing.T) {
	tmpFile, err := os.CreateTemp("", "goparser-pdf-*.xlsx")
	if err != nil {
		t.Fatalf("Failed to create temp file: %v", err)
	}
	defer os.Remove(tmpFile.Name())

	if _, err := tmpFile.WriteString("%PDF-1.4\n"); err != nil {
		t.Fatalf("Failed to write temp file: %v", err)
	}
	if _, err := tmpFile.Seek(0, 0); err != nil {
		t.Fatalf("Failed to seek: %v", err)
	}

	spec := &filespec.FileSpec{
		Format: filespec.FormatColumnar,
		RecordTypeDetection: filespec.RecordTypeDetection{
			Schema: "test",
		},
	}

	_, err = CreateDecoder(tmpFile, spec)
	if err == nil {
		t.Fatal("expected error for unknown content type")
	}
	if !errors.Is(err, sentinel.ErrDecoderUnknown) {
		t.Fatalf("expected ErrDecoderUnknown, got %v", err)
	}
}

func TestCreateColumnarDecoder_BinaryContent(t *testing.T) {
	// Create a temp file with binary content that isn't zip or text
	tmpFile, err := os.CreateTemp("", "goparser-bin-*")
	if err != nil {
		t.Fatalf("Failed to create temp file: %v", err)
	}
	defer os.Remove(tmpFile.Name())

	// Write binary content that will be detected as application/octet-stream
	binaryData := make([]byte, 512)
	for i := range binaryData {
		binaryData[i] = byte(i % 256)
	}
	if _, err := tmpFile.Write(binaryData); err != nil {
		t.Fatalf("Failed to write temp file: %v", err)
	}
	if _, err := tmpFile.Seek(0, 0); err != nil {
		t.Fatalf("Failed to seek: %v", err)
	}

	spec := &filespec.FileSpec{
		Format: filespec.FormatColumnar,
		RecordTypeDetection: filespec.RecordTypeDetection{
			Schema: "test",
		},
	}

	_, err = CreateDecoder(tmpFile, spec)
	if err == nil {
		t.Fatal("expected error for binary content")
	}
}
