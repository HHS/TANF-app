package config

import "time"

// Config is the top-level configuration structure matching config/parser.yaml.
// It replaces PipelineYAML as the canonical configuration type, supporting
// Prometheus-style file pointers, environment variable interpolation, and
// CLI flag overrides via Kong.
type Config struct {
	Global        GlobalConfig         `yaml:"global"`
	SchemaFiles   []string             `yaml:"schema_files"`
	FilespecFiles []string             `yaml:"filespec_files"`
	Server        ServerConfig         `yaml:"server"`
	Pipeline      PipelineWorkerConfig `yaml:"pipeline"`
	Writer        WriterConfig         `yaml:"writer"`
	Validation    ValidationConfig     `yaml:"validation"`
	Database      DatabaseConfig       `yaml:"database"`
	Storage       StorageConfig        `yaml:"storage"`
}

// GlobalConfig holds settings that apply across all subsystems.
type GlobalConfig struct {
	LogLevel  string `yaml:"log_level"`
	ConfigDir string `yaml:"config_dir"`
}

// ServerConfig controls how the parser receives work.
type ServerConfig struct {
	Mode   string       `yaml:"mode"` // "celery", "grpc", "http", "local"
	Celery CeleryConfig `yaml:"celery"`
	GRPC   GRPCConfig   `yaml:"grpc"`
	HTTP   HTTPConfig   `yaml:"http"`
	Local  LocalConfig  `yaml:"local"`
}

// CeleryConfig holds Celery worker settings.
type CeleryConfig struct {
	RedisURL string `yaml:"redis_url"`
}

// GRPCConfig holds gRPC server settings.
type GRPCConfig struct {
	ListenAddress string `yaml:"listen_address"`
}

// HTTPConfig holds HTTP server settings.
type HTTPConfig struct {
	ListenAddress string `yaml:"listen_address"`
}

// LocalConfig holds settings for local file processing mode.
type LocalConfig struct {
	FilePath     string `yaml:"file_path"`
	Program      string `yaml:"program"`
	Section      int    `yaml:"section"`
	FiscalYear   int    `yaml:"fiscal_year"`
	Quarter      int    `yaml:"quarter"`
	ProgramAudit bool   `yaml:"program_audit"`
}

// StorageConfig controls how the parser acquires files.
// This is top-level because blob storage is used across all server modes
// (except local), making it infrastructure config rather than server-specific.
type StorageConfig struct {
	Source string   `yaml:"source"` // "local" (default), "s3"
	S3     S3Config `yaml:"s3"`
}

// DefaultConfig returns production defaults. These form the bottom of
// the override precedence chain: defaults < config file < env vars < CLI flags.
func DefaultConfig() *Config {
	return &Config{
		Global: GlobalConfig{
			LogLevel:  "info",
			ConfigDir: "config",
		},
		SchemaFiles:   []string{"schemas/**/*.yaml"},
		FilespecFiles: []string{"filespecs/**/*.yaml"},
		Server: ServerConfig{
			Mode: "local",
			GRPC: GRPCConfig{
				ListenAddress: ":50051",
			},
			HTTP: HTTPConfig{
				ListenAddress: ":8080",
			},
		},
		Pipeline: PipelineWorkerConfig{
			NumWorkers:      16,
			WorkBufferSize:  256,
			PoolPrewarmSize: 10000,
		},
		Writer: WriterConfig{
			FlushThreshold:      50000,
			ErrorFlushThreshold: 100000,
		},
		Validation: ValidationConfig{
			ShortCircuit:   true,
			ValidatorFiles: []string{"validation/validators.yaml"},
		},
		Database: DatabaseConfig{
			MaxConns:          10,
			MinConns:          2,
			MaxConnLifetime:   30 * time.Minute,
			MaxConnIdleTime:   5 * time.Minute,
			HealthCheckPeriod: 30 * time.Second,
		},
		Storage: StorageConfig{
			Source: "local",
		},
	}
}

// TestConfig returns a Config with conservative values suitable for testing.
func TestConfig() *Config {
	cfg := DefaultConfig()
	cfg.Pipeline.NumWorkers = 2
	cfg.Pipeline.WorkBufferSize = 64
	cfg.Pipeline.PoolPrewarmSize = 1000
	cfg.Server.Mode = "local"
	cfg.Database.URL = "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable"
	return cfg
}
