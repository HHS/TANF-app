package local

import (
	"context"
	"fmt"
	"log"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/db"
	"go-parser/internal/decoder"
	"go-parser/internal/pipeline"
	"go-parser/internal/storage/reader"
	"go-parser/internal/storage/writer"
	"go-parser/internal/testutil"
	"go-parser/internal/validation"
)

// Mode owns the full lifecycle for local file processing.
type Mode struct {
	cfg        *config.Config
	registry   *config.Registry
	validators *validation.ValidatorRegistry
}

// New creates a local mode runner.
func New(cfg *config.Config, reg *config.Registry, validators *validation.ValidatorRegistry) *Mode {
	return &Mode{
		cfg:        cfg,
		registry:   reg,
		validators: validators,
	}
}

// needsDatabase determines whether a database connection is required.
// Local mode only needs DB when the output sink is the database.
func (m *Mode) needsDatabase() bool {
	return m.cfg.Writer.Mode != "file"
}

// dbResources holds the database-related resources created for a local run.
type dbResources struct {
	pool       *pgxpool.Pool
	datafileID int32
}

// setupDatabase conditionally connects to the database, loads content types,
// and creates a test datafile record for FK constraints.
// Returns nil resources (no cleanup needed) when the writer mode is "file".
func (m *Mode) setupDatabase(ctx context.Context, program string) (*dbResources, func(), error) {
	noop := func() {}

	if !m.needsDatabase() {
		return nil, noop, nil
	}

	if m.cfg.Database.URL == "" {
		return nil, noop, fmt.Errorf("database.url is required (set in config file, DATABASE_URL env var, or --database.url flag)")
	}

	pool, err := db.NewPool(ctx, m.cfg.Database.URL, m.cfg.Database)
	if err != nil {
		return nil, noop, fmt.Errorf("failed to connect to database: %w", err)
	}

	contentTypes, err := db.LoadContentTypes(ctx, pool)
	if err != nil {
		pool.Close()
		return nil, noop, fmt.Errorf("failed to load content types: %w", err)
	}
	m.registry.LoadContentTypes(contentTypes)
	log.Printf("Loaded %d content types from database", len(contentTypes))

	datafileParams := testutil.DefaultDatafileParams()
	datafileParams.ProgramType = program
	datafileParams.Section = "Active Case Data"
	datafileID, err := testutil.CreateTestDatafile(ctx, pool, datafileParams)
	if err != nil {
		pool.Close()
		return nil, noop, fmt.Errorf("failed to create test datafile: %w", err)
	}
	log.Printf("Created test datafile with ID: %d", datafileID)

	cleanup := func() {
		testutil.DeleteTestDatafile(ctx, pool, datafileID)
		pool.Close()
	}

	return &dbResources{pool: pool, datafileID: datafileID}, cleanup, nil
}

// Run processes a single file in local mode.
func (m *Mode) Run(ctx context.Context) error {
	local := m.cfg.Server.Local
	if local.FilePath == "" {
		return errRequired("server.local.file-path")
	}
	if local.Program == "" {
		return errRequired("server.local.program")
	}
	if local.Section == 0 {
		return errRequired("server.local.section")
	}

	// ---- Database + test datafile setup ----
	dbRes, cleanup, err := m.setupDatabase(ctx, local.Program)
	if err != nil {
		return err
	}
	defer cleanup()

	var dbPool *pgxpool.Pool
	var datafileID int32
	if dbRes != nil {
		dbPool = dbRes.pool
		datafileID = dbRes.datafileID
	}

	// ---- Output sink ----
	sink, err := writer.CreateSink(m.cfg.Writer.Mode, m.cfg.Writer.OutputDir, m.cfg.Writer.Format, dbPool)
	if err != nil {
		return fmt.Errorf("failed to create writer sink: %w", err)
	}
	defer sink.Close()

	// ---- Open file and create decoder ----
	source := reader.NewLocalSource(local.FilePath)
	file, err := source.Open(ctx)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()
	defer source.Cleanup()

	spec := m.registry.GetFileSpec(local.Program, local.Section)
	if spec == nil {
		return fmt.Errorf("no file spec for %s section %d", local.Program, local.Section)
	}

	dec, err := decoder.CreateDecoder(file, spec)
	if err != nil {
		return fmt.Errorf("failed to create decoder: %w", err)
	}
	defer dec.Close()

	// ---- Run pipeline ----
	pipeln := pipeline.NewPipeline(sink, m.registry, m.validators, pipeline.NewConfig(m.cfg))
	result, err := pipeln.Process(ctx, dec, pipeline.ProcessParams{
		Program:    local.Program,
		Section:    local.Section,
		DatafileID: datafileID,
	})
	if err != nil {
		return fmt.Errorf("failed to process file: %w", err)
	}

	log.Printf("File processed successfully in %s", result.Duration)
	for table, count := range result.RecordCounts {
		log.Printf("Written to %s: %d records", table, count)
	}

	return nil
}

func errRequired(field string) error {
	return fmt.Errorf("%s is required in local mode", field)
}
