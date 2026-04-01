package db

import (
	"context"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
)

// NewPool creates a connection pool using the provided database configuration.
func NewPool(ctx context.Context, connString string, dbCfg config.DatabaseConfig) (*pgxpool.Pool, error) {
	poolCfg, err := pgxpool.ParseConfig(connString)
	if err != nil {
		return nil, err
	}

	poolCfg.MaxConns = int32(dbCfg.MaxConns)
	poolCfg.MinConns = int32(dbCfg.MinConns)
	poolCfg.MaxConnLifetime = dbCfg.MaxConnLifetime
	poolCfg.MaxConnIdleTime = dbCfg.MaxConnIdleTime
	poolCfg.HealthCheckPeriod = dbCfg.HealthCheckPeriod

	return pgxpool.NewWithConfig(ctx, poolCfg)
}
