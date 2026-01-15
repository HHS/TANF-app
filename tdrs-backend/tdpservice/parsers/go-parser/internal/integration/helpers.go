//go:build integration

package integration

import (
	"context"
	"fmt"
	"path/filepath"
	"testing"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/pipeline"
	"go-parser/internal/registry"
)

// TestDataDir returns the absolute path to the test data directory.
func TestDataDir() string {
	return filepath.Join("..", "..", "..", "test", "data")
}

// ParseFile parses a file through the full pipeline and writes to the database.
func ParseFile(t *testing.T, ctx context.Context, pool *pgxpool.Pool, reg *registry.Registry, program string, section int, filePath string, datafileID int32) {
	t.Helper()

	p := pipeline.New(pool, reg, pipeline.TestConfig())
	result, err := p.ProcessFile(ctx, pipeline.ProcessParams{
		Program:    program,
		Section:    section,
		FilePath:   filePath,
		DatafileID: datafileID,
	})
	if err != nil {
		t.Fatalf("Pipeline failed: %v", err)
	}

	t.Logf("Processed in %s, errors: %d", result.Duration, result.ErrorCount)
}

// AssertTableCount verifies the record count in a table for a given datafile.
func AssertTableCount(t *testing.T, ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, expected int) {
	t.Helper()

	query := fmt.Sprintf("SELECT COUNT(*) FROM %s WHERE datafile_id = $1", tableName)
	var count int
	err := pool.QueryRow(ctx, query, datafileID).Scan(&count)
	if err != nil {
		t.Fatalf("Failed to count records in %s: %v", tableName, err)
	}

	if count != expected {
		t.Errorf("Record count in %s: got %d, want %d", tableName, count, expected)
	}
}

// QueryRecord returns a single record from a table by offset (0-indexed).
// Records are ordered by line_number to ensure deterministic ordering matching input file.
func QueryRecord(t *testing.T, ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, offset int) map[string]any {
	t.Helper()

	query := fmt.Sprintf(`
		SELECT * FROM %s
		WHERE datafile_id = $1
		ORDER BY line_number
		LIMIT 1 OFFSET $2
	`, tableName)

	rows, err := pool.Query(ctx, query, datafileID, offset)
	if err != nil {
		t.Fatalf("Failed to query %s: %v", tableName, err)
	}
	defer rows.Close()

	result, err := pgx.CollectOneRow(rows, pgx.RowToMap)
	if err != nil {
		t.Fatalf("Failed to collect row from %s at offset %d: %v", tableName, offset, err)
	}

	return result
}

// AssertFieldValue verifies a field value in a record map.
func AssertFieldValue(t *testing.T, record map[string]any, fieldName string, expected any) {
	t.Helper()

	actual, ok := record[fieldName]
	if !ok {
		t.Errorf("Field %s not found in record", fieldName)
		return
	}

	// Handle type conversions for comparison
	if !valuesEqual(actual, expected) {
		t.Errorf("Field %s: got %v (%T), want %v (%T)", fieldName, actual, actual, expected, expected)
	}
}

// valuesEqual compares two values with type flexibility.
func valuesEqual(actual, expected any) bool {
	// Direct equality
	if actual == expected {
		return true
	}

	// Handle numeric type conversions (database may return int64, int32, etc.)
	switch exp := expected.(type) {
	case int:
		switch act := actual.(type) {
		case int:
			return act == exp
		case int32:
			return int(act) == exp
		case int64:
			return int(act) == exp
		}
	case int32:
		switch act := actual.(type) {
		case int:
			return int32(act) == exp
		case int32:
			return act == exp
		case int64:
			return int32(act) == exp
		}
	case string:
		if act, ok := actual.(string); ok {
			return act == exp
		}
	}

	return false
}

// CleanupDatafile deletes all records associated with a datafile.
// This includes cascade deletes of parsed records.
func CleanupDatafile(t *testing.T, ctx context.Context, pool *pgxpool.Pool, datafileID int32) {
	t.Helper()

	// The tables that reference datafile_id
	tables := []string{
		"search_indexes_tanf_t1",
		"search_indexes_tanf_t2",
		"search_indexes_tanf_t3",
		"search_indexes_tanf_t4",
		"search_indexes_tanf_t5",
		"search_indexes_tanf_t6",
		"search_indexes_tanf_t7",
		"search_indexes_ssp_m1",
		"search_indexes_ssp_m2",
		"search_indexes_ssp_m3",
		"search_indexes_ssp_m4",
		"search_indexes_ssp_m5",
		"search_indexes_ssp_m6",
		"search_indexes_ssp_m7",
		"search_indexes_tribal_tanf_t1",
		"search_indexes_tribal_tanf_t2",
		"search_indexes_tribal_tanf_t3",
		"search_indexes_tribal_tanf_t4",
		"search_indexes_tribal_tanf_t5",
		"search_indexes_tribal_tanf_t6",
		"search_indexes_tribal_tanf_t7",
	}

	// Delete from all record tables first
	for _, table := range tables {
		query := fmt.Sprintf("DELETE FROM %s WHERE datafile_id = $1", table)
		_, _ = pool.Exec(ctx, query, datafileID) // Ignore errors for non-existent tables
	}

	// Delete the datafile itself
	_, err := pool.Exec(ctx, "DELETE FROM data_files_datafile WHERE id = $1", datafileID)
	if err != nil {
		t.Logf("Warning: failed to delete datafile %d: %v", datafileID, err)
	}
}
