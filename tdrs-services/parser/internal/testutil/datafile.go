package testutil

import (
	"context"
	"fmt"
	"math/rand"
	"os"
	"strings"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
)

func dataFileTableName() string {
	if strings.EqualFold(os.Getenv("GO_PARSER_SHADOW_MODE"), "true") {
		return config.DataFileTableName(config.DefaultTablePrefix)
	}
	return config.DataFileTableName("")
}

// CreateTestDatafile creates a datafile record for testing purposes.
// It queries for an existing STT and user to satisfy foreign key constraints.
// Returns the created datafile ID.
func CreateTestDatafile(ctx context.Context, pool *pgxpool.Pool, quarter string, year int, sectionName string, programType string) (int32, error) {
	// Get an existing STT ID
	var sttID int
	err := pool.QueryRow(ctx, "SELECT id FROM stts_stt LIMIT 1").Scan(&sttID)
	if err != nil {
		return 0, fmt.Errorf("failed to get STT: %w (ensure stts_stt table has data)", err)
	}

	// Get an existing user ID
	// TODO: this might fail on fresh DB
	var userID string
	err = pool.QueryRow(ctx, "SELECT id FROM users_user LIMIT 1").Scan(&userID)
	if err != nil {
		return 0, fmt.Errorf("failed to get user: %w (ensure users_user table has data)", err)
	}

	// Insert the datafile record
	var datafileID int32
	err = pool.QueryRow(ctx, fmt.Sprintf(`
		INSERT INTO %s (
			original_filename,
			slug,
			extension,
			quarter,
			year,
			section,
			version,
			stt_id,
			user_id,
			created_at,
			program_type,
			is_program_audit,
			state
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
		RETURNING id
	`, dataFileTableName()),
		"test_file.txt",
		fmt.Sprintf("test-%d", time.Now().UnixNano()),
		"txt",
		quarter,
		year,
		sectionName,
		rand.Intn(10000000),
		sttID,
		userID,
		time.Now(),
		programType,
		false,
		"uploaded",
	).Scan(&datafileID)

	if err != nil {
		return 0, fmt.Errorf("failed to create datafile: %w", err)
	}

	return datafileID, nil
}

// DeleteTestDatafile removes a test datafile and its associated records.
func DeleteTestDatafile(ctx context.Context, pool *pgxpool.Pool, datafileID int32) error {
	_, err := pool.Exec(ctx, fmt.Sprintf("DELETE FROM %s WHERE id = $1", dataFileTableName()), datafileID)
	return err
}
