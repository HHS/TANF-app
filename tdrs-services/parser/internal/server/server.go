package server

import (
	"context"
	"fmt"
	"log"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/db"
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
