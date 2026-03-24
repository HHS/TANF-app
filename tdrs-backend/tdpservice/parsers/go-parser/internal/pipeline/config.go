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
	FlushThreshold      int
	ErrorFlushThreshold int

	// Reader configuration
	ReaderSource string        // "local" (default), "s3"
	S3           config.S3Config
}

// DefaultConfig returns production defaults.
func DefaultConfig() PipelineConfig {
	return NewConfig(config.DefaultPipelineYAML())
}

// TestConfig returns conservative defaults for integration tests.
func TestConfig() PipelineConfig {
	return PipelineConfig{
		NumWorkers:     2,
		WorkBufferSize: 64,
		PoolPrewarmSize: 1000,
		FlushThreshold:      50000,
		ErrorFlushThreshold: 100000,
	}
}

// NewConfig creates a PipelineConfig from the loaded YAML configuration.
func NewConfig(cfg *config.PipelineYAML) PipelineConfig {
	readerSource := cfg.Reader.Source
	if readerSource == "" {
		readerSource = "local"
	}

	return PipelineConfig{
		NumWorkers:          cfg.Pipeline.NumWorkers,
		WorkBufferSize:      cfg.Pipeline.WorkBufferSize,
		PoolPrewarmSize:     cfg.Pipeline.PoolPrewarmSize,
		FlushThreshold:      cfg.Writer.FlushThreshold,
		ErrorFlushThreshold: cfg.Writer.ErrorFlushThreshold,
		ReaderSource:        readerSource,
		S3:                  cfg.Reader.S3,
	}
}
