package reader

import (
	"context"
	"os"
	"testing"
)

func TestLocalSource_Open(t *testing.T) {
	// Create a temp file to read
	tmpFile, err := os.CreateTemp("", "goparser-test-*")
	if err != nil {
		t.Fatalf("Failed to create temp file: %v", err)
	}
	defer os.Remove(tmpFile.Name())

	content := "test file content\n"
	if _, err := tmpFile.WriteString(content); err != nil {
		t.Fatalf("Failed to write temp file: %v", err)
	}
	tmpFile.Close()

	// Open via LocalSource
	source := NewLocalSource(tmpFile.Name())
	file, err := source.Open(context.Background())
	if err != nil {
		t.Fatalf("Open failed: %v", err)
	}
	defer file.Close()

	// Verify contents
	buf := make([]byte, len(content))
	n, err := file.Read(buf)
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if string(buf[:n]) != content {
		t.Errorf("content mismatch: got %q, want %q", string(buf[:n]), content)
	}
}

func TestLocalSource_OpenNonExistent(t *testing.T) {
	source := NewLocalSource("/nonexistent/path/file.txt")
	_, err := source.Open(context.Background())
	if err == nil {
		t.Fatal("expected error for non-existent file")
	}
}

func TestLocalSource_Cleanup(t *testing.T) {
	source := NewLocalSource("/any/path")
	// Cleanup should be a no-op and not error
	if err := source.Cleanup(); err != nil {
		t.Errorf("Cleanup returned error: %v", err)
	}
}
