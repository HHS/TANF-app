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
	IncludeSchemas      []string // filter which record types get written (empty = all)
	IncludeRecords      bool     // whether to write records
	IncludeErrors       bool     // whether to write errors
	TablePrefix         string   // prefix for Go parser-owned output tables

	// Validation configuration
	ShortCircuit bool // Skip field/consistency validators when precheck or group validators fail
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
	return PipelineConfig{
		NumWorkers:          cfg.Pipeline.NumWorkers,
		WorkBufferSize:      cfg.Pipeline.WorkBufferSize,
		PoolPrewarmSize:     cfg.Pipeline.PoolPrewarmSize,
		FlushThreshold:      cfg.Writer.FlushThreshold,
		ErrorFlushThreshold: cfg.Writer.ErrorFlushThreshold,
		IncludeSchemas:      cfg.Writer.IncludeSchemas,
		IncludeRecords:      cfg.Writer.IncludeRecords,
		IncludeErrors:       cfg.Writer.IncludeErrors,
		TablePrefix:         cfg.Database.EffectiveTablePrefix(),
		ShortCircuit:        cfg.Validation.ShortCircuit,
	}
}
