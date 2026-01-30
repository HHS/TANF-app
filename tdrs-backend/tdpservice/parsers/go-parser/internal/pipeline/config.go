package pipeline

import "go-parser/internal/parser"

// PipelineConfig holds tunable parameters for the parsing pipeline.
type PipelineConfig struct {
	// WorkerPool configuration (passed through to worker.PoolConfig)
	NumWorkers       int
	WorkBufferSize   int
	ResultBufferSize int

	// Router configuration
	NumRouters      int
	PoolPrewarmSize int

	// Validation configuration
	NumValidators int
}

// DefaultConfig returns production defaults.
func DefaultConfig() PipelineConfig {
	return PipelineConfig{
		NumWorkers:       16,
		WorkBufferSize:   256,
		ResultBufferSize: 256,
		PoolPrewarmSize:  10000,
		NumRouters:       16,
		NumValidators:    4,
	}
}

// TestConfig returns conservative defaults for integration tests.
func TestConfig() PipelineConfig {
	return PipelineConfig{
		NumWorkers:       2,
		WorkBufferSize:   64,
		ResultBufferSize: 64,
		PoolPrewarmSize:  1000,
		NumRouters:       1,
		NumValidators:    2,
	}
}

// toWorkerConfig converts PipelineConfig to parser.PoolConfig.
func (c PipelineConfig) toWorkerConfig() parser.PoolConfig {
	return parser.PoolConfig{
		NumWorkers:       c.NumWorkers,
		WorkBufferSize:   c.WorkBufferSize,
		ResultBufferSize: c.ResultBufferSize,
	}
}
