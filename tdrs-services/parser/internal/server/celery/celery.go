package celery

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/server"
	"go-parser/internal/storage"
	"go-parser/internal/validation"
)

// Server owns the full lifecycle for celery worker mode.
// It maintains long-lived connections (DB pool, S3 client) and processes
// tasks as they arrive from the celery broker.
type Server struct {
	server.Base
	dbPool    *pgxpool.Pool
	s3Storage *storage.S3Storage
}

// New creates a celery mode runner. It connects to the database,
// loads content types, and initializes the S3 client.
func New(cfg *config.Config, reg *config.Registry, validators *validation.ValidatorRegistry) (*Server, error) {
	ctx := context.Background()
	base := server.NewBase(cfg, reg, validators)

	dbPool, err := base.ConnectDB(ctx)
	if err != nil {
		return nil, err
	}

	// Initialize S3 client
	s3Storage, err := storage.NewS3Storage(storage.S3StorageConfig{
		Region:   cfg.Storage.S3.Region,
		Endpoint: cfg.Storage.S3.Endpoint,
	})
	if err != nil {
		dbPool.Close()
		return nil, fmt.Errorf("failed to initialize S3 storage: %w", err)
	}

	return &Server{
		Base:      base,
		dbPool:    dbPool,
		s3Storage: s3Storage,
	}, nil
}

// Run starts the celery worker loop. It blocks until the context is cancelled
// or the worker is stopped.
func (celery *Server) Run(ctx context.Context) error {
	defer celery.dbPool.Close()

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
