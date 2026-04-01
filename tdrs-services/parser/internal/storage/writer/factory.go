package writer

import (
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
)

// CreateSink creates the appropriate Sink based on the writer mode.
func CreateSink(mode, outputDir, format string, dbPool *pgxpool.Pool) (Sink, error) {
	switch mode {
	case "file":
		if outputDir == "" {
			outputDir = "./output"
		}
		return NewFileSink(outputDir, format)
	default:
		if dbPool == nil {
			return nil, fmt.Errorf("database pool is required for writer mode %q", mode)
		}
		return NewDatabaseSink(dbPool), nil
	}
}
