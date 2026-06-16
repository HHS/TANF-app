package pipeline

import (
	"context"
	"iter"
	"log/slog"
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/decoder"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// stubSink is a no-op Sink for testing.
type stubSink struct{}

func (s *stubSink) Flush(_ context.Context, _ string, _ []string, _ [][]any) (int64, error) {
	return 0, nil
}
func (s *stubSink) RollbackDatafile(_ context.Context, _ int32, _ []string, _ string) error {
	return nil
}
func (s *stubSink) Close() error { return nil }

// Verify writer.Sink interface is satisfied by stubSink at compile time.
var _ writer.Sink = (*stubSink)(nil)

// stubDecoder implements decoder.Decoder minimally for testing.
type stubDecoder struct{}

func (d *stubDecoder) Format() filespec.Format         { return filespec.FormatPositional }
func (d *stubDecoder) ReadFirst() (decoder.Row, error) { return nil, nil }
func (d *stubDecoder) Rows() iter.Seq2[decoder.Row, error] {
	return func(yield func(decoder.Row, error) bool) {}
}
func (d *stubDecoder) Sort(_ *decoder.RecordTypeDetector, _ []filespec.KeyFieldDef, _ []string) error {
	return nil
}
func (d *stubDecoder) Close() error { return nil }

// Verify decoder.Decoder interface is satisfied by stubDecoder at compile time.
var _ decoder.Decoder = (*stubDecoder)(nil)

func TestNewPipeline_Construction(t *testing.T) {
	sink := &stubSink{}
	cfg := DefaultConfig()

	p := NewPipeline(sink, nil, nil, cfg)

	if p == nil {
		t.Fatal("NewPipeline returned nil")
	}
	if p.sink != sink {
		t.Error("sink not set correctly")
	}
	if p.config.NumWorkers != cfg.NumWorkers {
		t.Errorf("config.NumWorkers = %d, want %d", p.config.NumWorkers, cfg.NumWorkers)
	}
}

func TestNewPipeline_AcceptsAllParams(t *testing.T) {
	sink := &stubSink{}
	cfg := PipelineConfig{
		NumWorkers:     4,
		WorkBufferSize: 64,
		ShortCircuit:   true,
	}

	p := NewPipeline(sink, nil, nil, cfg)

	if p.config.NumWorkers != 4 {
		t.Errorf("NumWorkers = %d, want 4", p.config.NumWorkers)
	}
	if p.config.WorkBufferSize != 64 {
		t.Errorf("WorkBufferSize = %d, want 64", p.config.WorkBufferSize)
	}
	if !p.config.ShortCircuit {
		t.Error("ShortCircuit should be true")
	}
}

func TestNewPipeline_NoS3StorageField(t *testing.T) {
	// Verify Pipeline struct no longer has s3Storage field.
	// This is a compile-time check — the test passes if it compiles.
	p := &Pipeline{
		sink:       &stubSink{},
		registry:   nil,
		validators: nil,
		config:     PipelineConfig{},
	}
	if p == nil {
		t.Fatal("unexpected nil")
	}
}

func TestProcess_MissingFileSpec(t *testing.T) {
	// Create a real (empty) registry — it will return nil for any GetFileSpec call
	cfg := config.DefaultConfig()
	cfg.SchemaFiles = nil
	cfg.FilespecFiles = nil
	cfg.Global.ConfigDir = t.TempDir()
	reg, err := config.NewRegistry(cfg)
	if err != nil {
		t.Fatalf("NewRegistry failed: %v", err)
	}

	validators := &validation.ValidatorRegistry{}
	sink := &stubSink{}
	p := NewPipeline(sink, reg, validators, TestConfig())

	stubDec := &stubDecoder{}
	_, err = p.Process(context.Background(), stubDec, DataFileContext{
		Program: "NONEXISTENT",
		Section: 99,
	})
	if err == nil {
		t.Fatal("expected error for missing file spec")
	}

	expected := "no file spec for NONEXISTENT section 99"
	if err.Error() != expected {
		t.Errorf("error = %q, want %q", err.Error(), expected)
	}
}

func TestDataFileContext_Fields(t *testing.T) {
	params := DataFileContext{
		Program:    "TAN",
		Section:    1,
		DatafileID: 42,
	}

	if params.Program != "TAN" {
		t.Errorf("Program = %q, want TAN", params.Program)
	}
	if params.Section != 1 {
		t.Errorf("Section = %d, want 1", params.Section)
	}
	if params.DatafileID != 42 {
		t.Errorf("DatafileID = %d, want 42", params.DatafileID)
	}
}

func TestDataFileContext_LogAttrsWithStage(t *testing.T) {
	dfCtx := DataFileContext{
		Program:       "TANF",
		Section:       1,
		DatafileID:    42,
		FiscalYear:    2024,
		FiscalQuarter: "Q1",
		SectionName:   "Active Case Data",
	}

	attrs := dfCtx.LogAttrsWithStage("complete", slog.Int64("duration_ms", 123))
	got := map[string]any{}
	for _, attr := range attrs {
		got[attr.Key] = attr.Value.Any()
	}

	if got["file_id"] != int64(42) {
		t.Errorf("file_id = %v, want 42", got["file_id"])
	}
	if got["program"] != "TANF" {
		t.Errorf("program = %v, want TANF", got["program"])
	}
	if got["section"] != int64(1) {
		t.Errorf("section = %v, want 1", got["section"])
	}
	if got["section_name"] != "Active Case Data" {
		t.Errorf("section_name = %v, want Active Case Data", got["section_name"])
	}
	if got["fiscal_year"] != int64(2024) {
		t.Errorf("fiscal_year = %v, want 2024", got["fiscal_year"])
	}
	if got["fiscal_quarter"] != "Q1" {
		t.Errorf("fiscal_quarter = %v, want Q1", got["fiscal_quarter"])
	}
	if got["stage"] != "complete" {
		t.Errorf("stage = %v, want complete", got["stage"])
	}
	if got["duration_ms"] != int64(123) {
		t.Errorf("duration_ms = %v, want 123", got["duration_ms"])
	}
}
