package db

import (
	"context"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

// NewPool creates a connection pool optimized for write-heavy workloads.
func NewPool(ctx context.Context, connString string) (*pgxpool.Pool, error) {
	config, err := pgxpool.ParseConfig(connString)
	if err != nil {
		return nil, err
	}

	// Connection limits
	// With 4 table writers that may flush concurrently, plus some headroom
	config.MaxConns = 10
	config.MinConns = 2

	// Connection lifecycle
	// Connections are recycled periodically to handle PostgreSQL maintenance
	config.MaxConnLifetime = 30 * time.Minute
	config.MaxConnIdleTime = 5 * time.Minute

	// Health checks
	config.HealthCheckPeriod = 30 * time.Second

	return pgxpool.NewWithConfig(ctx, config)
}
