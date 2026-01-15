package pipeline

import "go-parser/internal/worker"

// PipelineConfig holds tunable parameters for the parsing pipeline.
type PipelineConfig struct {
	// WorkerPool configuration (passed through to worker.PoolConfig)
	NumWorkers       int
	WorkBufferSize   int
	ResultBufferSize int

	// Router configuration
	PoolPrewarmSize int

	// Dispatcher configuration
	NumDispatchers int
}

// DefaultConfig returns production defaults.
func DefaultConfig() PipelineConfig {
	return PipelineConfig{
		NumWorkers:       4,
		WorkBufferSize:   256,
		ResultBufferSize: 256,
		PoolPrewarmSize:  10000,
		NumDispatchers:   4,
	}
}

// TestConfig returns conservative defaults for integration tests.
func TestConfig() PipelineConfig {
	return PipelineConfig{
		NumWorkers:       2,
		WorkBufferSize:   64,
		ResultBufferSize: 64,
		PoolPrewarmSize:  1000,
		NumDispatchers:   1,
	}
}

// toWorkerConfig converts PipelineConfig to worker.PoolConfig.
func (c PipelineConfig) toWorkerConfig() worker.PoolConfig {
	return worker.PoolConfig{
		NumWorkers:       c.NumWorkers,
		WorkBufferSize:   c.WorkBufferSize,
		ResultBufferSize: c.ResultBufferSize,
	}
}
