package local

import (
	"context"
	"fmt"
	"log"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/decoder"
	"go-parser/internal/pipeline"
	"go-parser/internal/server"
	"go-parser/internal/storage/reader"
	"go-parser/internal/storage/writer"
	"go-parser/internal/testutil"
	"go-parser/internal/validation"
)

// Server owns the full lifecycle for local file processing.
type Server struct {
	server.Base
}

// New creates a local mode runner.
func New(cfg *config.Config, reg *config.Registry, validators *validation.ValidatorRegistry) *Server {
	return &Server{
		Base: server.NewBase(cfg, reg, validators),
	}
}

// needsDatabase determines whether a database connection is required.
// Local mode only needs DB when the output sink is the database.
func (local *Server) needsDatabase() bool {
	return local.Config.Writer.Mode != "file"
}

// dbResources holds the database-related resources created for a local run.
type dbResources struct {
	pool       *pgxpool.Pool
	datafileID int32
}

// setupDatabase conditionally connects to the database, loads content types,
// and creates a test datafile record for FK constraints.
// Returns nil resources (no cleanup needed) when the writer mode is "file".
func (local *Server) setupDatabase(ctx context.Context, dfCtx pipeline.DataFileContext) (*dbResources, func(), error) {
	noop := func() {}

	if !local.needsDatabase() {
		return nil, noop, nil
	}

	pool, err := local.ConnectDB(ctx)
	if err != nil {
		return nil, noop, err
	}

	datafileID, err := testutil.CreateTestDatafile(ctx, pool, dfCtx.FiscalQuarter, dfCtx.FiscalYear, dfCtx.SectionName, dfCtx.ProgramType)
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
func (server *Server) Run(ctx context.Context) error {
	local := server.Config.Server.Local
	if local.FilePath == "" {
		return errRequired("server.local.file-path")
	}
	if local.Program == "" {
		return errRequired("server.local.program")
	}
	if local.Section == 0 {
		return errRequired("server.local.section")
	}

	// ---- Build DataFileContext from CLI args ----
	dfCtx := pipeline.DataFileContext{
		Program:       local.Program,
		Section:       local.Section,
		FiscalYear:    local.FiscalYear,
		FiscalQuarter: fmt.Sprintf("Q%d", local.Quarter),
		SectionName:   sectionName(local.Section),
		ProgramType:   local.Program,
	}

	// ---- Database + test datafile setup ----
	dbRes, cleanup, err := server.setupDatabase(ctx, dfCtx)
	if err != nil {
		return err
	}
	defer cleanup()

	var dbPool *pgxpool.Pool
	if dbRes != nil {
		dbPool = dbRes.pool
		dfCtx.DatafileID = dbRes.datafileID
	}

	// ---- Output sink ----
	sink, err := writer.CreateSink(server.Config.Writer.Mode, server.Config.Writer.OutputDir, server.Config.Writer.Format, dbPool)
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

	spec := server.Registry.GetFileSpec(dfCtx.Program, dfCtx.Section)
	if spec == nil {
		return fmt.Errorf("no file spec for %s section %d", dfCtx.Program, dfCtx.Section)
	}

	dec, err := decoder.CreateDecoder(file, spec)
	if err != nil {
		return fmt.Errorf("failed to create decoder: %w", err)
	}
	defer dec.Close()

	// ---- Run pipeline ----
	pipeln := pipeline.NewPipeline(sink, server.Registry, server.Validators, pipeline.NewConfig(server.Config))
	result, err := pipeln.Process(ctx, dec, dfCtx)
	if err != nil {
		return fmt.Errorf("failed to process file: %w", err)
	}

	log.Printf("File processed successfully in %s", result.Duration)
	for table, count := range result.RecordCounts {
		log.Printf("Written to %s: %d records", table, count)
	}

	return nil
}

// sectionName maps a section number to the DataFile section name.
func sectionName(section int) string {
	switch section {
	case 1:
		return "Active Case Data"
	case 2:
		return "Closed Case Data"
	case 3:
		return "Aggregate Data"
	case 4:
		return "Stratum Data"
	default:
		return ""
	}
}

func errRequired(field string) error {
	return fmt.Errorf("%s is required in local mode", field)
}
