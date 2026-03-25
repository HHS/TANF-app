package main

import (
	"context"
	"log"
	"os"
	"path/filepath"
	"runtime/pprof"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/db"
	"go-parser/internal/pipeline"
	"go-parser/internal/testutil"
	"go-parser/internal/validation"
)

func main() {
	// Parse CLI flags (Kong)
	cli, ctx, err := config.ParseCLI(os.Args[1:])
	if err != nil {
		log.Fatalf("Failed to parse CLI: %v", err)
	}

	// Load config file with env var interpolation
	cfg, err := config.LoadConfig(cli.ConfigFile)
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Apply CLI flag overrides (highest precedence)
	cli.ApplyTo(cfg, ctx)

	// CPU profiling
	if cli.CPUProfile != "" {
		f, err := os.Create(cli.CPUProfile)
		if err != nil {
			log.Fatal(err)
		}
		pprof.StartCPUProfile(f)
		defer pprof.StopCPUProfile()
	}

	bgCtx := context.Background()

	// Resolve file globs for schemas and filespecs
	configDir := cfg.Global.ConfigDir
	schemasBaseDir := filepath.Join(configDir, "schemas")

	schemaFiles, err := config.ResolveFileGlobs(configDir, cfg.SchemaFiles)
	if err != nil {
		log.Fatalf("Failed to resolve schema files: %v", err)
	}
	filespecFiles, err := config.ResolveFileGlobs(configDir, cfg.FilespecFiles)
	if err != nil {
		log.Fatalf("Failed to resolve filespec files: %v", err)
	}

	// Load schemas and filespecs from resolved file lists
	// TODO: Need to revisit storing the object pools on the schemas. Since the registry will exist for as long as the
	// celery worker does, the object pools could grow to an enormous size since there isn't a way to clear them after a
	// parsing run. We should consider implementing/importing a better solution that allows clearing. Or, we could reload
	// the registry each time a new parsing request comes in (simpler).
	reg, err := config.LoadFromFiles(schemaFiles, filespecFiles, schemasBaseDir, configDir)
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Load and compile validators
	validatorFiles, err := config.ResolveFileGlobs(configDir, cfg.Validation.ValidatorFiles)
	if err != nil {
		log.Fatalf("Failed to resolve validator files: %v", err)
	}
	validators := validation.NewValidatorRegistry()
	if err := validators.Load(reg.ConfigDir(), reg.Schemas(), reg.FileSpecs()); err != nil {
		log.Fatalf("Failed to load validators: %v", err)
	}
	_ = validatorFiles // TODO: pass to validators.LoadFromFiles() when implemented

	// Connect to database
	if cfg.Database.URL == "" {
		log.Fatal("database.url is required (set in config file, DATABASE_URL env var, or --database.url flag)")
	}
	dbPool, err := db.NewPool(bgCtx, cfg.Database.URL, cfg.Database)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer dbPool.Close()

	// Load content types from database for error linking
	contentTypes, err := db.LoadContentTypes(bgCtx, dbPool)
	if err != nil {
		log.Fatalf("Failed to load content types: %v", err)
	}
	reg.LoadContentTypes(contentTypes)
	log.Printf("Loaded %d content types from database", len(contentTypes))

	// Route to server mode
	switch cfg.Server.Mode {
	case "local":
		runLocal(bgCtx, cfg, dbPool, reg, validators)
	case "celery":
		log.Fatal("celery server mode not yet implemented")
	case "grpc":
		log.Fatal("gRPC server mode not yet implemented")
	case "http":
		log.Fatal("HTTP server mode not yet implemented")
	default:
		log.Fatalf("unknown server mode: %s", cfg.Server.Mode)
	}

	// Memory profiling (after work completes)
	if cli.MemProfile != "" {
		f, err := os.Create(cli.MemProfile)
		if err != nil {
			log.Fatal(err)
		}
		pprof.WriteHeapProfile(f)
		f.Close()
	}
}

// runLocal processes a single file in local mode (for development and testing).
func runLocal(ctx context.Context, cfg *config.Config, dbPool *pgxpool.Pool, reg *config.Registry, validators *validation.ValidatorRegistry) {
	local := cfg.Server.Local
	if local.FilePath == "" {
		log.Fatal("server.local.file-path is required in local mode")
	}
	if local.Program == "" {
		log.Fatal("server.local.program is required in local mode")
	}
	if local.Section == 0 {
		log.Fatal("server.local.section is required in local mode")
	}

	// Create a test datafile record to satisfy foreign key constraints
	datafileParams := testutil.DefaultDatafileParams()
	datafileParams.ProgramType = local.Program
	datafileParams.Section = "Active Case Data"
	datafileID, err := testutil.CreateTestDatafile(ctx, dbPool, datafileParams)
	if err != nil {
		log.Fatalf("Failed to create test datafile: %v", err)
	}
	log.Printf("Created test datafile with ID: %d", datafileID)
	defer func() {
		testutil.DeleteTestDatafile(ctx, dbPool, datafileID)
	}()

	// Create and run pipeline
	pipeln := pipeline.NewPipline(dbPool, reg, validators, pipeline.NewConfigFromUnified(cfg), nil)
	result, err := pipeln.ProcessFile(ctx, pipeline.DataFileParams{
		Program:    local.Program,
		Section:    local.Section,
		FilePath:   local.FilePath,
		DatafileID: datafileID,
	})
	if err != nil {
		log.Fatalf("Failed to process file: %v", err)
	}

	log.Printf("File processed successfully in %s", result.Duration)
	for table, count := range result.RecordCounts {
		log.Printf("Written to %s: %d records", table, count)
	}
}
