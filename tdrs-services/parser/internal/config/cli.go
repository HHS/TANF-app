package config

import (
	"time"

	"github.com/alecthomas/kong"
)

// CLI is the Kong root command struct. It defines all flags that can be
// passed on the command line to override config file values.
//
// Override precedence (lowest → highest):
//  1. Compiled defaults (DefaultConfig)
//  2. Config file (parser.yaml)
//  3. Environment variable interpolation (${VAR} in YAML)
//  4. CLI flags (this struct)
type CLI struct {
	// ConfigFile is the path to the primary config file.
	ConfigFile string `kong:"type=path,default='config/parser.yaml',short='c',help='Path to config file',name='config-file'"`

	// Profiling flags
	CPUProfile string `kong:"type=path,name='cpuprofile',help='Write CPU profile to file'"`
	MemProfile string `kong:"type=path,name='memprofile',help='Write memory profile to file'"`

	// Global
	GlobalLogLevel  string `kong:"name='global.log-level',help='Log level (debug, info, warn, error)'"`
	GlobalConfigDir string `kong:"name='global.config-dir',help='Config directory'"`

	// Server
	ServerMode              string `kong:"name='server.mode',help='Server mode (celery, grpc, http, local)'"`
	ServerCeleryRedisURL    string `kong:"name='server.celery.redis-url',help='Redis URL for Celery broker'"`
	ServerCeleryQueue       string `kong:"name='server.celery.queue',env='GO_PARSER_QUEUE',help='Redis queue name for Celery tasks'"`
	ServerCeleryNumWorkers  int    `kong:"name='server.celery.num-workers',help='Number of concurrent celery task workers'"`
	ServerGRPCListenAddress string `kong:"name='server.grpc.listen-address',help='gRPC listen address'"`
	ServerHTTPListenAddress string `kong:"name='server.http.listen-address',help='HTTP listen address'"`
	ServerLocalFilePath     string `kong:"name='server.local.file-path',help='File path for local processing'"`
	ServerLocalProgram      string `kong:"name='server.local.program',help='Program type (TANF, SSP, TRIBAL, FRA)'"`
	ServerLocalSection      int    `kong:"name='server.local.section',help='Section number'"`
	ServerLocalFiscalYear   int    `kong:"name='server.local.fiscal-year',help='Fiscal year'"`
	ServerLocalQuarter      int    `kong:"name='server.local.quarter',help='Quarter (1-4)'"`
	ServerLocalProgramAudit bool   `kong:"name='server.local.program-audit',help='Program audit flag'"`

	// Pipeline
	PipelineNumWorkers      int `kong:"name='pipeline.num-workers',help='Parser worker goroutines'"`
	PipelineWorkBufferSize  int `kong:"name='pipeline.work-buffer-size',help='Worker channel buffer size'"`
	PipelinePoolPrewarmSize int `kong:"name='pipeline.pool-prewarm-size',help='Object pool pre-allocation size'"`

	// Writer
	WriterMode                string   `kong:"name='writer.mode',help='Output mode: database or file'"`
	WriterFormat              string   `kong:"name='writer.format',help='File output format: json or csv (used with mode=file)'"`
	WriterOutputDir           string   `kong:"name='writer.output-dir',help='Output directory for file mode'"`
	WriterFlushThreshold      int      `kong:"name='writer.flush-threshold',help='Records per table before flush'"`
	WriterErrorFlushThreshold int      `kong:"name='writer.error-flush-threshold',help='Error records before flush'"`
	WriterIncludeSchemas      []string `kong:"name='writer.include-schemas',help='Schema paths to include (e.g. tanf/t1). Empty=all'"`
	WriterIncludeRecords      bool     `kong:"name='writer.include-records',help='Whether to write records (default true)'"`
	WriterIncludeErrors       bool     `kong:"name='writer.include-errors',help='Whether to write errors (default true)'"`

	// Convenience flag: --dry-run sets writer.mode=file with a temp-style output dir
	DryRun bool `kong:"name='dry-run',help='Run without database: output records/errors to local files'"`

	// Validation
	ValidationShortCircuit bool `kong:"name='validation.short-circuit',help='Skip field/consistency validators on precheck failure'"`

	// Database
	DatabaseURL               string        `kong:"name='database.url',env='DATABASE_URL',help='Database connection URL'"`
	DatabaseMaxConns          int           `kong:"name='database.max-conns',help='Max database connections'"`
	DatabaseMinConns          int           `kong:"name='database.min-conns',help='Min database connections'"`
	DatabaseMaxConnLifetime   time.Duration `kong:"name='database.max-conn-lifetime',help='Max connection lifetime'"`
	DatabaseMaxConnIdleTime   time.Duration `kong:"name='database.max-conn-idle-time',help='Max connection idle time'"`
	DatabaseHealthCheckPeriod time.Duration `kong:"name='database.health-check-period',help='Health check period'"`

	// Storage
	StorageSource      string `kong:"name='storage.source',help='File storage source (local, s3)'"`
	StorageS3Bucket    string `kong:"name='storage.s3.bucket',help='S3 bucket name'"`
	StorageS3Endpoint  string `kong:"name='storage.s3.endpoint',help='S3 endpoint (for LocalStack)'"`
	StorageS3Region    string `kong:"name='storage.s3.region',help='S3 region'"`
	StorageS3KeyPrefix string `kong:"name='storage.s3.key-prefix',help='S3 key prefix (Django APP_NAME)'"`
}

// ParseCLI parses command-line arguments using Kong and returns the CLI struct.
// The returned *kong.Context can be used for error handling.
func ParseCLI(args []string) (*CLI, *kong.Context, error) {
	cli := &CLI{}
	parser, err := kong.New(cli,
		kong.Name("go-parser"),
		kong.Description("TANF Data Portal Go Parser"),
		kong.UsageOnError(),
	)
	if err != nil {
		return nil, nil, err
	}

	ctx, err := parser.Parse(args)
	if err != nil {
		return nil, nil, err
	}

	return cli, ctx, nil
}

// ApplyTo overlays CLI flag values onto a Config that was already loaded
// from a YAML file. Only flags that were explicitly set on the command line
// override the YAML values.
//
// Kong doesn't natively track "was this flag set?", so we use the kong.Context
// to check which flags were explicitly provided. For flags not explicitly set,
// the YAML/default values are preserved.
func (c *CLI) ApplyTo(cfg *Config, ctx *kong.Context) {
	set := flagsSet(ctx)

	if set["global.log-level"] {
		cfg.Global.LogLevel = c.GlobalLogLevel
	}
	if set["global.config-dir"] {
		cfg.Global.ConfigDir = c.GlobalConfigDir
	}

	if set["server.mode"] {
		cfg.Server.Mode = c.ServerMode
	}
	if set["server.celery.redis-url"] {
		cfg.Server.Celery.RedisURL = c.ServerCeleryRedisURL
	}
	if set["server.celery.queue"] {
		cfg.Server.Celery.Queue = c.ServerCeleryQueue
	}
	if set["server.celery.num-workers"] {
		cfg.Server.Celery.NumWorkers = c.ServerCeleryNumWorkers
	}
	if set["server.grpc.listen-address"] {
		cfg.Server.GRPC.ListenAddress = c.ServerGRPCListenAddress
	}
	if set["server.http.listen-address"] {
		cfg.Server.HTTP.ListenAddress = c.ServerHTTPListenAddress
	}
	if set["server.local.file-path"] {
		cfg.Server.Local.FilePath = c.ServerLocalFilePath
	}
	if set["server.local.program"] {
		cfg.Server.Local.Program = c.ServerLocalProgram
	}
	if set["server.local.section"] {
		cfg.Server.Local.Section = c.ServerLocalSection
	}
	if set["server.local.fiscal-year"] {
		cfg.Server.Local.FiscalYear = c.ServerLocalFiscalYear
	}
	if set["server.local.quarter"] {
		cfg.Server.Local.Quarter = c.ServerLocalQuarter
	}
	if set["server.local.program-audit"] {
		cfg.Server.Local.ProgramAudit = c.ServerLocalProgramAudit
	}

	if set["pipeline.num-workers"] {
		cfg.Pipeline.NumWorkers = c.PipelineNumWorkers
	}
	if set["pipeline.work-buffer-size"] {
		cfg.Pipeline.WorkBufferSize = c.PipelineWorkBufferSize
	}
	if set["pipeline.pool-prewarm-size"] {
		cfg.Pipeline.PoolPrewarmSize = c.PipelinePoolPrewarmSize
	}

	if set["writer.mode"] {
		cfg.Writer.Mode = c.WriterMode
	}
	if set["writer.format"] {
		cfg.Writer.Format = c.WriterFormat
	}
	if set["writer.output-dir"] {
		cfg.Writer.OutputDir = c.WriterOutputDir
	}
	if set["writer.flush-threshold"] {
		cfg.Writer.FlushThreshold = c.WriterFlushThreshold
	}
	if set["writer.error-flush-threshold"] {
		cfg.Writer.ErrorFlushThreshold = c.WriterErrorFlushThreshold
	}
	if set["writer.include-schemas"] {
		cfg.Writer.IncludeSchemas = c.WriterIncludeSchemas
	}
	if set["writer.include-records"] {
		cfg.Writer.IncludeRecords = c.WriterIncludeRecords
	}
	if set["writer.include-errors"] {
		cfg.Writer.IncludeErrors = c.WriterIncludeErrors
	}

	// --dry-run is a convenience flag that forces file mode
	if set["dry-run"] && c.DryRun {
		cfg.Writer.Mode = "file"
	}

	if set["validation.short-circuit"] {
		cfg.Validation.ShortCircuit = c.ValidationShortCircuit
	}

	if set["database.url"] {
		cfg.Database.URL = c.DatabaseURL
	}
	if set["database.max-conns"] {
		cfg.Database.MaxConns = c.DatabaseMaxConns
	}
	if set["database.min-conns"] {
		cfg.Database.MinConns = c.DatabaseMinConns
	}
	if set["database.max-conn-lifetime"] {
		cfg.Database.MaxConnLifetime = c.DatabaseMaxConnLifetime
	}
	if set["database.max-conn-idle-time"] {
		cfg.Database.MaxConnIdleTime = c.DatabaseMaxConnIdleTime
	}
	if set["database.health-check-period"] {
		cfg.Database.HealthCheckPeriod = c.DatabaseHealthCheckPeriod
	}

	if set["storage.source"] {
		cfg.Storage.Source = c.StorageSource
	}
	if set["storage.s3.bucket"] {
		cfg.Storage.S3.Bucket = c.StorageS3Bucket
	}
	if set["storage.s3.endpoint"] {
		cfg.Storage.S3.Endpoint = c.StorageS3Endpoint
	}
	if set["storage.s3.region"] {
		cfg.Storage.S3.Region = c.StorageS3Region
	}
	if set["storage.s3.key-prefix"] {
		cfg.Storage.S3.KeyPrefix = c.StorageS3KeyPrefix
	}
}

// flagsSet returns a map of flag names that were explicitly set on the command line.
func flagsSet(ctx *kong.Context) map[string]bool {
	set := make(map[string]bool)
	for _, flag := range ctx.Flags() {
		if flag.Set {
			set[flag.Name] = true
		}
	}
	return set
}
