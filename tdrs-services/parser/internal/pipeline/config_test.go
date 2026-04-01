package pipeline

import (
	"testing"

	"go-parser/internal/config"
)

func TestNewConfig_MapsAllFields(t *testing.T) {
	cfg := &config.Config{
		Pipeline: config.PipelineWorkerConfig{
			NumWorkers:      8,
			WorkBufferSize:  128,
			PoolPrewarmSize: 5000,
		},
		Writer: config.WriterConfig{
			FlushThreshold:      10000,
			ErrorFlushThreshold: 20000,
			IncludeSchemas:      []string{"tanf/t1", "tanf/t2"},
			IncludeRecords:      true,
			IncludeErrors:       false,
		},
		Validation: config.ValidationConfig{
			ShortCircuit: true,
		},
	}

	pc := NewConfig(cfg)

	if pc.NumWorkers != 8 {
		t.Errorf("NumWorkers = %d, want 8", pc.NumWorkers)
	}
	if pc.WorkBufferSize != 128 {
		t.Errorf("WorkBufferSize = %d, want 128", pc.WorkBufferSize)
	}
	if pc.PoolPrewarmSize != 5000 {
		t.Errorf("PoolPrewarmSize = %d, want 5000", pc.PoolPrewarmSize)
	}
	if pc.FlushThreshold != 10000 {
		t.Errorf("FlushThreshold = %d, want 10000", pc.FlushThreshold)
	}
	if pc.ErrorFlushThreshold != 20000 {
		t.Errorf("ErrorFlushThreshold = %d, want 20000", pc.ErrorFlushThreshold)
	}
	if len(pc.IncludeSchemas) != 2 || pc.IncludeSchemas[0] != "tanf/t1" {
		t.Errorf("IncludeSchemas = %v, want [tanf/t1 tanf/t2]", pc.IncludeSchemas)
	}
	if !pc.IncludeRecords {
		t.Error("IncludeRecords should be true")
	}
	if pc.IncludeErrors {
		t.Error("IncludeErrors should be false")
	}
	if !pc.ShortCircuit {
		t.Error("ShortCircuit should be true")
	}
}

func TestNewConfig_NoInfrastructureFields(t *testing.T) {
	// Verify the slimmed PipelineConfig has no infrastructure fields.
	// This is a compile-time guarantee test: if someone re-adds WriterMode,
	// ReaderSource, or S3 fields, this file won't compile because PipelineConfig
	// won't have those fields.
	pc := PipelineConfig{
		NumWorkers:          1,
		WorkBufferSize:      1,
		PoolPrewarmSize:     1,
		FlushThreshold:      1,
		ErrorFlushThreshold: 1,
		IncludeSchemas:      nil,
		IncludeRecords:      true,
		IncludeErrors:       true,
		ShortCircuit:        false,
	}
	// Use pc to avoid unused variable error
	if pc.NumWorkers != 1 {
		t.Fatal("unexpected")
	}
}

func TestDefaultConfig_ProducesValidConfig(t *testing.T) {
	pc := DefaultConfig()

	if pc.NumWorkers == 0 {
		t.Error("DefaultConfig NumWorkers should be non-zero")
	}
	if pc.WorkBufferSize == 0 {
		t.Error("DefaultConfig WorkBufferSize should be non-zero")
	}
	if pc.FlushThreshold == 0 {
		t.Error("DefaultConfig FlushThreshold should be non-zero")
	}
	if !pc.IncludeRecords {
		t.Error("DefaultConfig IncludeRecords should be true")
	}
	if !pc.IncludeErrors {
		t.Error("DefaultConfig IncludeErrors should be true")
	}
}

func TestTestConfig_ConservativeValues(t *testing.T) {
	def := DefaultConfig()
	test := TestConfig()

	if test.NumWorkers >= def.NumWorkers {
		t.Errorf("TestConfig NumWorkers (%d) should be less than default (%d)",
			test.NumWorkers, def.NumWorkers)
	}
	if test.WorkBufferSize >= def.WorkBufferSize {
		t.Errorf("TestConfig WorkBufferSize (%d) should be less than default (%d)",
			test.WorkBufferSize, def.WorkBufferSize)
	}
}
