package main

import (
	"context"
	"log"
	"os"
	"runtime/pprof"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/db"
	"go-parser/internal/pipeline"
	"go-parser/internal/storage/writer"
	"go-parser/internal/testutil"
	"go-parser/internal/validation"
)

// needsDatabase determines whether a database connection is required based on
// the combination of input source (server mode) and output sink (writer mode).
//
// The two axes are orthogonal:
//
//	                    | Output: database | Output: file                    |
//	--------------------|------------------|--------------------------------|
//	Input: local file   | DB needed        | No DB needed (fully offline)   |
//	Input: server req   | DB needed        | DB needed (read datafile/meta) |
//
// Server modes (celery, grpc, http) always need DB to look up the datafile
// record and resolve the S3 object key. Local mode only needs DB when the
// output sink is the database.
func needsDatabase(cfg *config.Config) bool {
	if cfg.Writer.Mode == "file" && cfg.Server.Mode == "local" {
		return false
	}
	return true
}

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

	// Load schemas and filespecs via glob patterns from config
	// TODO: Need to revisit storing the object pools on the schemas. Since the registry will exist for as long as the
	// celery worker does, the object pools could grow to an enormous size since there isn't a way to clear them after a
	// parsing run. We should consider implementing/importing a better solution that allows clearing. Or, we could reload
	// the registry each time a new parsing request comes in (simpler).
	reg, err := config.NewRegistry(cfg)
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Load and compile validators
	validators, err := validation.NewValidatorRegistry(cfg, reg)
	if err != nil {
		log.Fatalf("Failed to load validators: %v", err)
	}

	// ---- Database connection (conditional) ----
	// See needsDatabase() for the decision matrix.
	var dbPool *pgxpool.Pool
	if needsDatabase(cfg) {
		if cfg.Database.URL == "" {
			log.Fatal("database.url is required (set in config file, DATABASE_URL env var, or --database.url flag)")
		}
		pool, err := db.NewPool(bgCtx, cfg.Database.URL, cfg.Database)
		if err != nil {
			log.Fatalf("Failed to connect to database: %v", err)
		}
		defer pool.Close()
		dbPool = pool

		// Content types are needed for error→record linking in the database.
		// When writing to files, content_type_id columns are nil — which is fine.
		contentTypes, err := db.LoadContentTypes(bgCtx, dbPool)
		if err != nil {
			log.Fatalf("Failed to load content types: %v", err)
		}
		reg.LoadContentTypes(contentTypes)
		log.Printf("Loaded %d content types from database", len(contentTypes))
	} else {
		log.Printf("No database connection required (server.mode=%s, writer.mode=%s)",
			cfg.Server.Mode, cfg.Writer.Mode)
	}

	// ---- Output sink ----
	pipelineCfg := pipeline.NewConfig(cfg)
	sink, err := pipeline.SinkFactory(pipelineCfg, dbPool)
	if err != nil {
		log.Fatalf("Failed to create writer sink: %v", err)
	}
	defer sink.Close()

	// ---- Server mode dispatch ----
	switch cfg.Server.Mode {
	case "local":
		runLocal(bgCtx, cfg, sink, dbPool, reg, validators)
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
// When dbPool is non-nil, a test datafile record is created to satisfy FK constraints.
// When dbPool is nil (file output mode), datafileID is 0 — the pipeline and sink
// still function, but records won't have a real FK reference.
func runLocal(ctx context.Context, cfg *config.Config, sink writer.Sink, dbPool *pgxpool.Pool, reg *config.Registry, validators *validation.ValidatorRegistry) {
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

	// Create a test datafile record to satisfy FK constraints (only when writing to database)
	var datafileID int32
	if dbPool != nil {
		datafileParams := testutil.DefaultDatafileParams()
		datafileParams.ProgramType = local.Program
		datafileParams.Section = "Active Case Data"
		var err error
		datafileID, err = testutil.CreateTestDatafile(ctx, dbPool, datafileParams)
		if err != nil {
			log.Fatalf("Failed to create test datafile: %v", err)
		}
		log.Printf("Created test datafile with ID: %d", datafileID)
		defer func() {
			testutil.DeleteTestDatafile(ctx, dbPool, datafileID)
		}()
	}

	// Create and run pipeline
	pipeln := pipeline.NewPipeline(sink, reg, validators, pipeline.NewConfig(cfg), nil)
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
