package db

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5/pgxpool"
)

// GetDataFile retrieves a DataFile record by its primary key.
func GetDataFile(ctx context.Context, pool *pgxpool.Pool, id int32) (*DataFilesDatafile, error) {
	query := `
		SELECT id, original_filename, slug, extension, quarter, year, section, version,
		       stt_id, user_id, created_at, file, s3_versioning_id, program_type, is_program_audit
		FROM data_files_datafile
		WHERE id = $1
	`

	var df DataFilesDatafile
	err := pool.QueryRow(ctx, query, id).Scan(
		&df.ID, &df.OriginalFilename, &df.Slug, &df.Extension,
		&df.Quarter, &df.Year, &df.Section, &df.Version,
		&df.SttID, &df.UserID, &df.CreatedAt, &df.File,
		&df.S3VersioningID, &df.ProgramType, &df.IsProgramAudit,
	)
	if err != nil {
		return nil, fmt.Errorf("query data_files_datafile id=%d: %w", id, err)
	}

	return &df, nil
}

// UpdateDataFileSummaryStatus updates the status of a DataFileSummary for the given datafile.
func UpdateDataFileSummaryStatus(ctx context.Context, pool *pgxpool.Pool, datafileID int32, status string) error {
	query := `
		UPDATE parsers_datafilesummary
		SET status = $1
		WHERE datafile_id = $2
	`

	_, err := pool.Exec(ctx, query, status, datafileID)
	if err != nil {
		return fmt.Errorf("update datafilesummary status for datafile_id=%d: %w", datafileID, err)
	}

	return nil
}
