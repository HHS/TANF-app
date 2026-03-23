package config

import (
	"fmt"
	"os"
	"path/filepath"
	"time"

	"gopkg.in/yaml.v3"
)

// PipelineYAML is the top-level structure of config/pipeline.yaml.
type PipelineYAML struct {
	Pipeline PipelineWorkerConfig `yaml:"pipeline"`
	Writer   WriterConfig         `yaml:"writer"`
	Database DatabaseConfig       `yaml:"database"`
	Reader   ReaderConfig         `yaml:"reader"`
}

// ReaderConfig controls how the parser acquires input files.
type ReaderConfig struct {
	Source string   `yaml:"source"` // "local" (default), "s3"
	S3     S3Config `yaml:"s3"`
}

// S3Config holds S3-specific reader settings.
type S3Config struct {
	Bucket   string `yaml:"bucket"`
	Endpoint string `yaml:"endpoint"` // Custom endpoint (empty = real AWS, set for LocalStack)
	Region   string `yaml:"region"`
}

// PipelineWorkerConfig holds worker pool and routing settings.
type PipelineWorkerConfig struct {
	NumWorkers       int `yaml:"num_workers"`
	WorkBufferSize   int `yaml:"work_buffer_size"`
	ResultBufferSize int `yaml:"result_buffer_size"`
	NumRouters       int `yaml:"num_routers"`
	PoolPrewarmSize  int `yaml:"pool_prewarm_size"`
}

// WriterConfig holds table writer flush thresholds.
type WriterConfig struct {
	FlushThreshold      int `yaml:"flush_threshold"`
	ErrorFlushThreshold int `yaml:"error_flush_threshold"`
}

// DatabaseConfig holds connection pool settings.
type DatabaseConfig struct {
	MaxConns          int           `yaml:"max_conns"`
	MinConns          int           `yaml:"min_conns"`
	MaxConnLifetime   time.Duration `yaml:"max_conn_lifetime"`
	MaxConnIdleTime   time.Duration `yaml:"max_conn_idle_time"`
	HealthCheckPeriod time.Duration `yaml:"health_check_period"`
}

// DefaultPipelineYAML returns production defaults matching the previously hardcoded values.
func DefaultPipelineYAML() *PipelineYAML {
	return &PipelineYAML{
		Pipeline: PipelineWorkerConfig{
			NumWorkers:       16,
			WorkBufferSize:   256,
			ResultBufferSize: 256,
			NumRouters:       4,
			PoolPrewarmSize:  10000,
		},
		Writer: WriterConfig{
			FlushThreshold:      50000,
			ErrorFlushThreshold: 100000,
		},
		Database: DatabaseConfig{
			MaxConns:          10,
			MinConns:          2,
			MaxConnLifetime:   30 * time.Minute,
			MaxConnIdleTime:   5 * time.Minute,
			HealthCheckPeriod: 30 * time.Second,
		},
	}
}

// LoadPipelineConfig reads config/pipeline.yaml from the given config directory.
// If the file does not exist, production defaults are returned.
func LoadPipelineConfig(configDir string) (*PipelineYAML, error) {
	path := filepath.Join(configDir, "pipeline.yaml")

	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return DefaultPipelineYAML(), nil
		}
		return nil, fmt.Errorf("reading %s: %w", path, err)
	}

	cfg := DefaultPipelineYAML()
	if err := yaml.Unmarshal(data, cfg); err != nil {
		return nil, fmt.Errorf("parsing %s: %w", path, err)
	}

	return cfg, nil
}
