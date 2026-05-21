package server

import (
	"context"
	"os"
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/pipeline"
	"go-parser/internal/sentinel"
	"go-parser/internal/storage/reader"
	"go-parser/internal/storage/writer"
)

type captureSink struct {
	table   string
	columns []string
	rows    [][]any
}

func (s *captureSink) Flush(_ context.Context, tableName string, columns []string, rows [][]any) (int64, error) {
	s.table = tableName
	s.columns = columns
	s.rows = append(s.rows, rows...)
	return int64(len(rows)), nil
}

func (s *captureSink) RollbackDatafile(_ context.Context, _ int32, _ []string) error {
	return nil
}

func (s *captureSink) Close() error {
	return nil
}

var _ writer.Sink = (*captureSink)(nil)

func TestRunPipeline_DecoderUnknownWritesPreCheckError(t *testing.T) {
	tmpFile, err := os.CreateTemp("", "fra-decoder-unknown-*.xlsx")
	if err != nil {
		t.Fatalf("CreateTemp failed: %v", err)
	}
	defer os.Remove(tmpFile.Name())

	if _, err := tmpFile.WriteString("%PDF-1.4\n"); err != nil {
		t.Fatalf("WriteString failed: %v", err)
	}
	if err := tmpFile.Close(); err != nil {
		t.Fatalf("Close failed: %v", err)
	}

	cfg := config.DefaultConfig()
	reg := config.NewTestRegistry(nil)
	reg.FileSpecs()["FRA:1"] = &filespec.FileSpec{
		Program: "FRA",
		Section: 1,
		Format:  filespec.FormatColumnar,
		RecordTypeDetection: filespec.RecordTypeDetection{
			Schema: "TE1",
		},
	}

	sink := &captureSink{}
	base := NewBase(cfg, reg, nil)
	result, err := base.RunPipeline(
		context.Background(),
		reader.NewLocalSource(tmpFile.Name()),
		sink,
		pipeline.DataFileContext{
			Program:    "FRA",
			Section:    1,
			DatafileID: 42,
		},
	)
	if err != nil {
		t.Fatalf("RunPipeline failed: %v", err)
	}

	if result.ErrorCount != 1 {
		t.Fatalf("ErrorCount = %d, want 1", result.ErrorCount)
	}
	if sink.table != "parser_error" {
		t.Fatalf("table = %q, want parser_error", sink.table)
	}
	if len(sink.rows) != 1 {
		t.Fatalf("rows = %d, want 1", len(sink.rows))
	}

	row := sink.rows[0]
	if row[6] != sentinel.DecoderUnknownMessage {
		t.Fatalf("error message = %q, want %q", row[6], sentinel.DecoderUnknownMessage)
	}
	if row[7] != "1" {
		t.Fatalf("error type = %v, want PRE_CHECK db value 1", row[7])
	}
	if row[11] != int32(42) {
		t.Fatalf("file id = %v, want 42", row[11])
	}
}
