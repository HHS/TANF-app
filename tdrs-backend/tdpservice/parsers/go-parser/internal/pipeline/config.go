package pipeline

import (
	"go-parser/internal/config"
)

// PipelineConfig holds tunable parameters for the parsing pipeline.
type PipelineConfig struct {
	// WorkerPool configuration
	NumWorkers     int
	WorkBufferSize int

	// Writer configuration (object pool)
	PoolPrewarmSize int

	// Writer configuration
	WriterMode          string // "database" (default), "file"
	WriterFormat        string // "json" or "csv" (for file mode)
	WriterOutputDir     string // output directory (for file mode)
	FlushThreshold      int
	ErrorFlushThreshold int
	IncludeSchemas      []string // filter which record types get written (empty = all)
	IncludeRecords      bool     // whether to write records
	IncludeErrors       bool     // whether to write errors

	// Validation configuration
	ShortCircuit bool // Skip field/consistency validators when precheck or group validators fail

	// Storage configuration
	ReaderSource string // "local" (default), "s3"
	S3           config.S3Config
}

// DefaultConfig returns production defaults.
func DefaultConfig() PipelineConfig {
	return NewConfig(config.DefaultConfig())
}

// TestConfig returns conservative defaults for integration tests.
func TestConfig() PipelineConfig {
	return NewConfig(config.TestConfig())
}

// NewConfig creates a PipelineConfig from the unified Config.
func NewConfig(cfg *config.Config) PipelineConfig {
	readerSource := cfg.Storage.Source
	if readerSource == "" {
		readerSource = "local"
	}

	writerMode := cfg.Writer.Mode
	if writerMode == "" {
		writerMode = "database"
	}
	writerFormat := cfg.Writer.Format
	if writerFormat == "" {
		writerFormat = "json"
	}

	return PipelineConfig{
		NumWorkers:          cfg.Pipeline.NumWorkers,
		WorkBufferSize:      cfg.Pipeline.WorkBufferSize,
		PoolPrewarmSize:     cfg.Pipeline.PoolPrewarmSize,
		WriterMode:          writerMode,
		WriterFormat:        writerFormat,
		WriterOutputDir:     cfg.Writer.OutputDir,
		FlushThreshold:      cfg.Writer.FlushThreshold,
		ErrorFlushThreshold: cfg.Writer.ErrorFlushThreshold,
		IncludeSchemas:      cfg.Writer.IncludeSchemas,
		IncludeRecords:      cfg.Writer.IncludeRecords,
		IncludeErrors:       cfg.Writer.IncludeErrors,
		ShortCircuit:        cfg.Validation.ShortCircuit,
		ReaderSource:        readerSource,
		S3:                  cfg.Storage.S3,
	}
}
