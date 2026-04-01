package testutil

import (
	"context"
	"fmt"
	"math/rand"
	"time"

	"github.com/jackc/pgx/v5/pgxpool"
)

// DatafileParams contains parameters for creating a test datafile.
type DatafileParams struct {
	OriginalFilename string
	Quarter          string
	Year             int
	Section          string
	ProgramType      string // "TAN", "SSP", "Tribal TAN"
}

// DefaultDatafileParams returns sensible defaults for testing.
func DefaultDatafileParams() DatafileParams {
	return DatafileParams{
		OriginalFilename: "test_file.txt",
		Quarter:          "Q1",
		Year:             2024,
		Section:          "Active Case Data",
		ProgramType:      "TAN",
	}
}

// CreateTestDatafile creates a datafile record for testing purposes.
// It queries for an existing STT and user to satisfy foreign key constraints.
// Returns the created datafile ID.
func CreateTestDatafile(ctx context.Context, pool *pgxpool.Pool, params DatafileParams) (int32, error) {
	// Get an existing STT ID
	var sttID int
	err := pool.QueryRow(ctx, "SELECT id FROM stts_stt LIMIT 1").Scan(&sttID)
	if err != nil {
		return 0, fmt.Errorf("failed to get STT: %w (ensure stts_stt table has data)", err)
	}

	// Get an existing user ID
	var userID string
	err = pool.QueryRow(ctx, "SELECT id FROM users_user LIMIT 1").Scan(&userID)
	if err != nil {
		return 0, fmt.Errorf("failed to get user: %w (ensure users_user table has data)", err)
	}

	// Insert the datafile record
	var datafileID int32
	err = pool.QueryRow(ctx, `
		INSERT INTO data_files_datafile (
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
			is_program_audit
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
		RETURNING id
	`,
		params.OriginalFilename,
		fmt.Sprintf("test-%d", time.Now().UnixNano()), // unique slug
		"txt",
		params.Quarter,
		params.Year,
		params.Section,
		rand.Intn(10000000), // version
		sttID,
		userID,
		time.Now(),
		params.ProgramType,
		false, // is_program_audit
	).Scan(&datafileID)

	if err != nil {
		return 0, fmt.Errorf("failed to create datafile: %w", err)
	}

	return datafileID, nil
}

// DeleteTestDatafile removes a test datafile and its associated records.
func DeleteTestDatafile(ctx context.Context, pool *pgxpool.Pool, datafileID int32) error {
	_, err := pool.Exec(ctx, "DELETE FROM data_files_datafile WHERE id = $1", datafileID)
	return err
}
