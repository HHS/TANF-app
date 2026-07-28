package config

import (
	"time"
)

// PipelineWorkerConfig holds worker pool settings.
type PipelineWorkerConfig struct {
	NumWorkers      int `yaml:"num_workers"`
	WorkBufferSize  int `yaml:"work_buffer_size"`
	PoolPrewarmSize int `yaml:"pool_prewarm_size"`
}

// WriterConfig holds table writer flush thresholds and output mode.
type WriterConfig struct {
	Mode                string   `yaml:"mode"`       // "database" (default), "file"
	Format              string   `yaml:"format"`     // "json" or "csv" (only used when mode is "file")
	OutputDir           string   `yaml:"output_dir"` // output directory (only used when mode is "file")
	FlushThreshold      int      `yaml:"flush_threshold"`
	ErrorFlushThreshold int      `yaml:"error_flush_threshold"`
	IncludeSchemas      []string `yaml:"include_schemas"` // filter which record types get written (empty = all)
	IncludeRecords      bool     `yaml:"include_records"` // whether to write records (default true)
	IncludeErrors       bool     `yaml:"include_errors"`  // whether to write errors (default true)
}

// ValidationConfig controls validation behavior.
type ValidationConfig struct {
	ShortCircuit   bool     `yaml:"short_circuit"`   // Skip field/consistency validators when precheck or group validators fail
	Engine         string   `yaml:"engine"`          // "expr", "hybrid", or "native"
	ValidatorFiles []string `yaml:"validator_files"` // Glob patterns for validator definition files (resolved relative to config_dir)
}

// DatabaseConfig holds connection pool settings.
type DatabaseConfig struct {
	URL               string        `yaml:"url"` // Database connection URL (supports ${DATABASE_URL} interpolation)
	ShadowMode        bool          `yaml:"shadow_mode"`
	TablePrefix       string        `yaml:"table_prefix"`
	MaxConns          int           `yaml:"max_conns"`
	MinConns          int           `yaml:"min_conns"`
	MaxConnLifetime   time.Duration `yaml:"max_conn_lifetime"`
	MaxConnIdleTime   time.Duration `yaml:"max_conn_idle_time"`
	HealthCheckPeriod time.Duration `yaml:"health_check_period"`
}

// EffectiveTablePrefix returns the table prefix to use for parser-owned writes.
// When shadow mode is disabled, the Go parser writes to production tables.
func (c DatabaseConfig) EffectiveTablePrefix() string {
	if !c.ShadowMode {
		return ""
	}
	return c.TablePrefix
}

// S3Config holds S3-specific storage settings.
type S3Config struct {
	Bucket    string `yaml:"bucket"`
	Endpoint  string `yaml:"endpoint"` // Custom endpoint (empty = real AWS, set for LocalStack)
	Region    string `yaml:"region"`
	KeyPrefix string `yaml:"key_prefix"` // Prefix prepended to paths for environment separation
}

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
	RedisURL          string `yaml:"redis_url"`
	Queue             string `yaml:"queue"`
	NumWorkers        int    `yaml:"num_workers"` // Number of concurrent celery task workers (default 1)
	PostParseTaskName string `yaml:"post_parse_task_name"`
	PostParseQueue    string `yaml:"post_parse_queue"`
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
			Celery: CeleryConfig{
				Queue:             "go-parser",
				PostParseTaskName: "tdpservice.scheduling.parser_task.post_parse",
				PostParseQueue:    "celery",
			},
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
			Mode:                "database",
			Format:              "json",
			OutputDir:           "./output",
			FlushThreshold:      50000,
			ErrorFlushThreshold: 100000,
			IncludeRecords:      true,
			IncludeErrors:       true,
		},
		Validation: ValidationConfig{
			ShortCircuit:   true,
			Engine:         "expr",
			ValidatorFiles: []string{"validation/validators.yaml"},
		},
		Database: DatabaseConfig{
			ShadowMode:        true,
			TablePrefix:       DefaultTablePrefix,
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
