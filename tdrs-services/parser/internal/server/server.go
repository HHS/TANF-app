package server

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
	"go-parser/internal/validation"
)

// Base holds the shared dependencies for all server modes.
type Base struct {
	Config     *config.Config
	Registry   *config.Registry
	Validators *validation.ValidatorRegistry
}

// NewBase creates a Base with the given dependencies.
func NewBase(cfg *config.Config, reg *config.Registry, validators *validation.ValidatorRegistry) Base {
	return Base{
		Config:     cfg,
		Registry:   reg,
		Validators: validators,
	}
}

// ConnectDB creates a database pool and loads content types into the registry.
// The caller is responsible for closing the returned pool.
func (b *Base) ConnectDB(ctx context.Context) (*pgxpool.Pool, error) {
	if b.Config.Database.URL == "" {
		return nil, fmt.Errorf("database.url is required (set in config file, DATABASE_URL env var, or --database.url flag)")
	}

	pool, err := db.NewPool(ctx, b.Config.Database.URL, b.Config.Database)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	contentTypes, err := db.LoadContentTypes(ctx, pool)
	if err != nil {
		pool.Close()
		return nil, fmt.Errorf("failed to load content types: %w", err)
	}
	b.Registry.LoadContentTypes(contentTypes)
	log.Printf("Loaded %d content types from database", len(contentTypes))

	return pool, nil
}

// RunPipeline opens the file source, resolves the file spec, creates a decoder,
// and runs the parsing pipeline. It centralizes the shared orchestration logic
// used by all server modes.
func (b *Base) RunPipeline(ctx context.Context, source reader.FileSource, sink writer.Sink, dfCtx pipeline.DataFileContext) (*pipeline.ParsingResult, error) {
	file, err := source.Open(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()
	defer source.Cleanup()

	spec := b.Registry.GetFileSpec(dfCtx.Program, dfCtx.Section)
	if spec == nil {
		return nil, fmt.Errorf("no file spec for %s section %d", dfCtx.Program, dfCtx.Section)
	}

	dec, err := decoder.CreateDecoder(file, spec)
	if err != nil {
		return nil, fmt.Errorf("failed to create decoder: %w", err)
	}
	defer dec.Close()

	pipeln := pipeline.NewPipeline(sink, b.Registry, b.Validators, pipeline.NewConfig(b.Config))
	return pipeln.Process(ctx, dec, dfCtx)
}
