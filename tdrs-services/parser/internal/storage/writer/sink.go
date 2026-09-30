package writer

import (
	"context"
	"encoding/csv"
	"encoding/json"
	"errors"
	"fmt"
	"log/slog"
	"os"
	"path/filepath"
	"sync"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/logging"
)

// Sink is the destination for flushed row batches.
// Implementations handle the actual I/O (database, file, etc).
type Sink interface {
	// Flush writes a batch of rows to the destination.
	Flush(ctx context.Context, tableName string, columns []string, rows [][]any) (int64, error)

	// RollbackDatafile deletes all records and errors previously written for the
	// given datafile ID. The tables slice specifies which record tables to clean
	// up (only tables relevant to the current file spec). Parser errors are
	// always cleaned up.
	RollbackDatafile(ctx context.Context, datafileID int32, tables []string, errorTableName string) error

	// Close performs any final cleanup (close file handles, etc).
	Close() error
}

// DatabaseSink writes rows to PostgreSQL via pgx CopyFrom.
type DatabaseSink struct {
	pool        *pgxpool.Pool
	datafileID  int32
	parseToken  string
	guardWrites bool
}

// NewDatabaseSink creates a sink that writes to PostgreSQL.
func NewDatabaseSink(pool *pgxpool.Pool) *DatabaseSink {
	return &DatabaseSink{pool: pool}
}

// CreateGuardedDatabaseSink fences every production flush with parse token ownership.
func CreateGuardedDatabaseSink(pool *pgxpool.Pool, datafileID int32, parseToken string, guardWrites bool) (Sink, error) {
	if pool == nil {
		return nil, errors.New("database pool is required")
	}
	if guardWrites && parseToken == "" {
		return nil, errors.New("production database writes require a parse token")
	}
	return &DatabaseSink{
		pool:        pool,
		datafileID:  datafileID,
		parseToken:  parseToken,
		guardWrites: guardWrites,
	}, nil
}

type databaseExecer interface {
	Exec(context.Context, string, ...any) (pgconn.CommandTag, error)
}

const lockCurrentParseToken = `
	SELECT 1
	FROM data_files_datafile AS data_file
	WHERE data_file.id = $1
	  AND data_file.state = 'parse_started'
	  AND data_file.current_parse_token = $2::uuid
	FOR UPDATE
`

func (s *DatabaseSink) withTokenOwnership(ctx context.Context, write func(pgx.Tx) error) error {
	tx, err := s.pool.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx) // no-op after Commit

	var ownsToken int
	if err := tx.QueryRow(ctx, lockCurrentParseToken, s.datafileID, s.parseToken).Scan(&ownsToken); err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return fmt.Errorf("parse token %s no longer owns datafile %d", s.parseToken, s.datafileID)
		}
		return err
	}
	if err := write(tx); err != nil {
		return err
	}
	return tx.Commit(ctx)
}

func (s *DatabaseSink) Flush(ctx context.Context, tableName string, columns []string, rows [][]any) (int64, error) {
	if !s.guardWrites {
		return s.pool.CopyFrom(ctx, pgx.Identifier{tableName}, columns, pgx.CopyFromRows(rows))
	}

	var copied int64
	err := s.withTokenOwnership(ctx, func(tx pgx.Tx) error {
		var err error
		copied, err = tx.CopyFrom(ctx, pgx.Identifier{tableName}, columns, pgx.CopyFromRows(rows))
		return err
	})
	return copied, err
}

func (s *DatabaseSink) RollbackDatafile(ctx context.Context, datafileID int32, tables []string, errorTableName string) error {
	if s.guardWrites {
		return s.withTokenOwnership(ctx, func(tx pgx.Tx) error {
			return rollbackDatafile(ctx, tx, datafileID, tables, errorTableName)
		})
	}
	return rollbackDatafile(ctx, s.pool, datafileID, tables, errorTableName)
}

func rollbackDatafile(ctx context.Context, executor databaseExecer, datafileID int32, tables []string, errorTableName string) error {
	var errs []error

	// Always clean up parser errors
	errorTable := pgx.Identifier{errorTableName}.Sanitize()
	if _, err := executor.Exec(ctx, fmt.Sprintf("DELETE FROM %s WHERE file_id = $1", errorTable), datafileID); err != nil {
		logging.Error(ctx, "rollback failed to delete parser errors",
			slog.Int(logging.KeyFileID, int(datafileID)),
			slog.String("table_name", errorTableName),
			slog.Any(logging.KeyError, err),
		)
		errs = append(errs, fmt.Errorf("delete %s for datafile %d: %w", errorTableName, datafileID, err))
	}

	// Only delete from tables relevant to the current file spec
	for _, table := range tables {
		query := fmt.Sprintf("DELETE FROM %s WHERE datafile_id = $1", pgx.Identifier{table}.Sanitize())
		if _, err := executor.Exec(ctx, query, datafileID); err != nil {
			logging.Error(ctx, "rollback failed to delete records",
				slog.Int(logging.KeyFileID, int(datafileID)),
				slog.String("table_name", table),
				slog.Any(logging.KeyError, err),
			)
			errs = append(errs, fmt.Errorf("delete %s for datafile %d: %w", table, datafileID, err))
		}
	}
	return errors.Join(errs...)
}

func (s *DatabaseSink) Close() error {
	return nil
}

// FileSink writes rows to local files, one file per table.
// Supports NDJSON and CSV output formats.
type FileSink struct {
	outputDir string
	format    string // "json" or "csv"

	mu      sync.Mutex
	writers map[string]*fileWriter
}

type fileWriter struct {
	file    *os.File
	columns []string
	format  string

	// format-specific encoders
	jsonEnc *json.Encoder
	csvW    *csv.Writer
}

// NewFileSink creates a sink that writes to local files.
// Format must be "json" or "csv".
func NewFileSink(outputDir string, format string) (*FileSink, error) {
	if err := os.MkdirAll(outputDir, 0o755); err != nil {
		return nil, fmt.Errorf("failed to create output directory %s: %w", outputDir, err)
	}
	return &FileSink{
		outputDir: outputDir,
		format:    format,
		writers:   make(map[string]*fileWriter),
	}, nil
}

func (s *FileSink) Flush(ctx context.Context, tableName string, columns []string, rows [][]any) (int64, error) {
	s.mu.Lock()
	fw, err := s.getOrCreate(tableName, columns)
	s.mu.Unlock()
	if err != nil {
		return 0, err
	}

	var written int64
	for _, row := range rows {
		if err := fw.writeRow(row); err != nil {
			return written, err
		}
		written++
	}
	return written, nil
}

// RollbackDatafile is a best-effort no-op for file sinks since file output
// does not support selective deletion by datafile ID.
func (s *FileSink) RollbackDatafile(_ context.Context, _ int32, _ []string, _ string) error {
	return nil
}

func (s *FileSink) Close() error {
	s.mu.Lock()
	defer s.mu.Unlock()

	var firstErr error
	for name, fw := range s.writers {
		if fw.csvW != nil {
			fw.csvW.Flush()
			if err := fw.csvW.Error(); err != nil && firstErr == nil {
				firstErr = fmt.Errorf("csv flush %s: %w", name, err)
			}
		}
		if err := fw.file.Close(); err != nil && firstErr == nil {
			firstErr = fmt.Errorf("close %s: %w", name, err)
		}
	}
	return firstErr
}

func (s *FileSink) getOrCreate(tableName string, columns []string) (*fileWriter, error) {
	if fw, ok := s.writers[tableName]; ok {
		return fw, nil
	}

	ext := s.format
	if ext == "json" {
		ext = "ndjson"
	}
	path := filepath.Join(s.outputDir, tableName+"."+ext)

	f, err := os.Create(path)
	if err != nil {
		return nil, fmt.Errorf("failed to create output file %s: %w", path, err)
	}

	fw := &fileWriter{
		file:    f,
		columns: columns,
		format:  s.format,
	}

	switch s.format {
	case "json":
		fw.jsonEnc = json.NewEncoder(f)
	case "csv":
		fw.csvW = csv.NewWriter(f)
		// Write header row
		if err := fw.csvW.Write(columns); err != nil {
			f.Close()
			return nil, fmt.Errorf("failed to write CSV header for %s: %w", tableName, err)
		}
	}

	s.writers[tableName] = fw
	return fw, nil
}

func (fw *fileWriter) writeRow(row []any) error {
	switch fw.format {
	case "json":
		obj := make(map[string]any, len(fw.columns))
		for i, col := range fw.columns {
			if i < len(row) {
				obj[col] = row[i]
			}
		}
		return fw.jsonEnc.Encode(obj)
	case "csv":
		record := make([]string, len(fw.columns))
		for i := range fw.columns {
			if i < len(row) {
				record[i] = fmt.Sprintf("%v", row[i])
			}
		}
		return fw.csvW.Write(record)
	default:
		return fmt.Errorf("unsupported format: %s", fw.format)
	}
}
