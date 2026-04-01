package writer

import (
	"os"
	"path/filepath"
	"testing"
)

func TestCreateSink_FileMode_JSON(t *testing.T) {
	dir := t.TempDir()

	sink, err := CreateSink("file", dir, "json", nil)
	if err != nil {
		t.Fatalf("CreateSink failed: %v", err)
	}
	defer sink.Close()

	if _, ok := sink.(*FileSink); !ok {
		t.Errorf("expected *FileSink, got %T", sink)
	}
}

func TestCreateSink_FileMode_CSV(t *testing.T) {
	dir := t.TempDir()

	sink, err := CreateSink("file", dir, "csv", nil)
	if err != nil {
		t.Fatalf("CreateSink failed: %v", err)
	}
	defer sink.Close()

	if _, ok := sink.(*FileSink); !ok {
		t.Errorf("expected *FileSink, got %T", sink)
	}
}

func TestCreateSink_FileMode_DefaultOutputDir(t *testing.T) {
	// When outputDir is empty, it should default to "./output"
	sink, err := CreateSink("file", "", "json", nil)
	if err != nil {
		t.Fatalf("CreateSink failed: %v", err)
	}
	defer sink.Close()

	// Clean up the default output directory
	defer os.RemoveAll("./output")

	fs, ok := sink.(*FileSink)
	if !ok {
		t.Fatalf("expected *FileSink, got %T", sink)
	}
	if fs.outputDir != "./output" {
		t.Errorf("expected outputDir './output', got %q", fs.outputDir)
	}
}

func TestCreateSink_FileMode_CreatesDirectory(t *testing.T) {
	dir := filepath.Join(t.TempDir(), "nested", "output")

	sink, err := CreateSink("file", dir, "json", nil)
	if err != nil {
		t.Fatalf("CreateSink failed: %v", err)
	}
	defer sink.Close()

	// Verify directory was created
	info, err := os.Stat(dir)
	if err != nil {
		t.Fatalf("output directory not created: %v", err)
	}
	if !info.IsDir() {
		t.Error("expected directory")
	}
}

func TestCreateSink_DatabaseMode_NilPool(t *testing.T) {
	_, err := CreateSink("database", "", "", nil)
	if err == nil {
		t.Fatal("expected error for nil database pool")
	}
}

func TestCreateSink_DefaultMode_NilPool(t *testing.T) {
	// Empty mode defaults to database, which requires a pool
	_, err := CreateSink("", "", "", nil)
	if err == nil {
		t.Fatal("expected error for nil database pool with default mode")
	}
}
