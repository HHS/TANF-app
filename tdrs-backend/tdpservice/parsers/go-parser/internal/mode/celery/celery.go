package celery

import (
	"context"
	"fmt"
	"log"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/db"
	"go-parser/internal/storage"
	"go-parser/internal/validation"
)

// Mode owns the full lifecycle for celery worker mode.
// It maintains long-lived connections (DB pool, S3 client) and processes
// tasks as they arrive from the celery broker.
type Mode struct {
	cfg        *config.Config
	registry   *config.Registry
	validators *validation.ValidatorRegistry
	dbPool     *pgxpool.Pool
	s3Storage  *storage.S3Storage
}

// New creates a celery mode runner. It connects to the database,
// loads content types, and initializes the S3 client.
func New(cfg *config.Config, reg *config.Registry, validators *validation.ValidatorRegistry) (*Mode, error) {
	ctx := context.Background()

	// Initialize DB pool
	if cfg.Database.URL == "" {
		return nil, fmt.Errorf("database.url is required for celery mode")
	}
	dbPool, err := db.NewPool(ctx, cfg.Database.URL, cfg.Database)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	contentTypes, err := db.LoadContentTypes(ctx, dbPool)
	if err != nil {
		dbPool.Close()
		return nil, fmt.Errorf("failed to load content types: %w", err)
	}
	reg.LoadContentTypes(contentTypes)
	log.Printf("Loaded %d content types from database", len(contentTypes))

	// Initialize S3 client
	s3Storage, err := storage.NewS3Storage(storage.S3StorageConfig{
		Region:   cfg.Storage.S3.Region,
		Endpoint: cfg.Storage.S3.Endpoint,
	})
	if err != nil {
		dbPool.Close()
		return nil, fmt.Errorf("failed to initialize S3 storage: %w", err)
	}

	return &Mode{
		cfg:        cfg,
		registry:   reg,
		validators: validators,
		dbPool:     dbPool,
		s3Storage:  s3Storage,
	}, nil
}

// Run starts the celery worker loop. It blocks until the context is cancelled
// or the worker is stopped.
func (m *Mode) Run(ctx context.Context) error {
	defer m.dbPool.Close()

	// TODO: Implement celery worker loop.
	// Each task should:
	// 1. Query DB for datafile metadata (program, section, S3 key)
	// 2. Download file from S3 via reader.NewS3Source
	// 3. Create decoder via decoder.CreateDecoder
	// 4. Create DatabaseSink using shared pool
	// 5. Create Pipeline, call Process
	// 6. Update datafile status in DB
	return fmt.Errorf("celery mode not yet implemented")
}
