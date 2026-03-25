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

	// Validation configuration
	ShortCircuit bool // Skip field/consistency validators when precheck or group validators fail

	// Storage configuration
	ReaderSource string // "local" (default), "s3"
	S3           config.S3Config
}

// DefaultConfig returns production defaults.
func DefaultConfig() PipelineConfig {
	return NewConfigFromUnified(config.DefaultConfig())
}

// TestConfig returns conservative defaults for integration tests.
func TestConfig() PipelineConfig {
	return NewConfigFromUnified(config.TestConfig())
}

// NewConfigFromUnified creates a PipelineConfig from the unified Config.
func NewConfigFromUnified(cfg *config.Config) PipelineConfig {
	readerSource := cfg.Storage.Source
	if readerSource == "" {
		readerSource = "local"
	}

	return PipelineConfig{
		NumWorkers:          cfg.Pipeline.NumWorkers,
		WorkBufferSize:      cfg.Pipeline.WorkBufferSize,
		PoolPrewarmSize:     cfg.Pipeline.PoolPrewarmSize,
		FlushThreshold:      cfg.Writer.FlushThreshold,
		ErrorFlushThreshold: cfg.Writer.ErrorFlushThreshold,
		ShortCircuit:        cfg.Validation.ShortCircuit,
		ReaderSource:        readerSource,
		S3:                  cfg.Storage.S3,
	}
}

// Deprecated: NewConfig creates a PipelineConfig from the legacy PipelineYAML.
// Use NewConfigFromUnified instead.
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
		ShortCircuit:        cfg.Validation.ShortCircuit,
		ReaderSource:        readerSource,
		S3:                  cfg.Reader.S3,
	}
}
