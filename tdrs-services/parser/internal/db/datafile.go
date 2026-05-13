package db

import (
	"context"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

// GetDataFile retrieves a DataFile-compatible record by its primary key.
func GetDataFile(ctx context.Context, pool *pgxpool.Pool, tableName string, id int32) (*ShadowDataFilesDatafile, error) {
	table := pgx.Identifier{tableName}.Sanitize()
	query := fmt.Sprintf(`
		SELECT id, original_filename, slug, extension, quarter, year, section, version,
		       stt_id, user_id, created_at, file, s3_versioning_id, program_type, is_program_audit, state
		FROM %s
		WHERE id = $1
	`, table)

	var df ShadowDataFilesDatafile
	err := pool.QueryRow(ctx, query, id).Scan(
		&df.ID, &df.OriginalFilename, &df.Slug, &df.Extension,
		&df.Quarter, &df.Year, &df.Section, &df.Version,
		&df.SttID, &df.UserID, &df.CreatedAt, &df.File,
		&df.S3VersioningID, &df.ProgramType, &df.IsProgramAudit, &df.State,
	)
	if err != nil {
		return nil, fmt.Errorf("query %s id=%d: %w", tableName, id, err)
	}

	return &df, nil
}

// EnsureShadowDataFile copies production DataFile metadata into the Go parser shadow table.
func EnsureShadowDataFile(ctx context.Context, pool *pgxpool.Pool, tableName string, df *ShadowDataFilesDatafile) error {
	table := pgx.Identifier{tableName}.Sanitize()
	query := fmt.Sprintf(`
		INSERT INTO %s (
			id, original_filename, slug, extension, quarter, year, section, version,
			stt_id, user_id, created_at, file, s3_versioning_id, program_type, is_program_audit, state
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
		ON CONFLICT (id) DO UPDATE SET
			original_filename = EXCLUDED.original_filename,
			slug = EXCLUDED.slug,
			extension = EXCLUDED.extension,
			quarter = EXCLUDED.quarter,
			year = EXCLUDED.year,
			section = EXCLUDED.section,
			version = EXCLUDED.version,
			stt_id = EXCLUDED.stt_id,
			user_id = EXCLUDED.user_id,
			created_at = EXCLUDED.created_at,
			file = EXCLUDED.file,
			s3_versioning_id = EXCLUDED.s3_versioning_id,
			program_type = EXCLUDED.program_type,
			is_program_audit = EXCLUDED.is_program_audit,
			state = EXCLUDED.state
	`, table)

	_, err := pool.Exec(ctx, query,
		df.ID, df.OriginalFilename, df.Slug, df.Extension,
		df.Quarter, df.Year, df.Section, df.Version,
		df.SttID, df.UserID, df.CreatedAt, df.File,
		df.S3VersioningID, df.ProgramType, df.IsProgramAudit, df.State,
	)
	if err != nil {
		return fmt.Errorf("upsert %s id=%d: %w", tableName, df.ID, err)
	}

	return nil
}

// UpdateDataFileState updates the submission state for a DataFile-compatible table.
func UpdateDataFileState(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, state string) error {
	table := pgx.Identifier{tableName}.Sanitize()
	query := `
		UPDATE %s
		SET state = $1
		WHERE id = $2
	`

	_, err := pool.Exec(ctx, fmt.Sprintf(query, table), state, datafileID)
	if err != nil {
		return fmt.Errorf("update %s state for id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

// EnsureDataFileSummary creates or resets the shadow DataFileSummary for the given datafile.
func EnsureDataFileSummary(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32) error {
	table := pgx.Identifier{tableName}.Sanitize()
	query := fmt.Sprintf(`
		INSERT INTO %s (
			status, datafile_id, case_aggregates, total_number_of_records_in_file,
			total_number_of_records_created, error_report
		)
		VALUES ('Pending', $1, NULL, 0, 0, NULL)
		ON CONFLICT (datafile_id) DO UPDATE SET
			status = EXCLUDED.status,
			case_aggregates = EXCLUDED.case_aggregates,
			total_number_of_records_in_file = EXCLUDED.total_number_of_records_in_file,
			total_number_of_records_created = EXCLUDED.total_number_of_records_created,
			error_report = EXCLUDED.error_report
	`, table)

	_, err := pool.Exec(ctx, query, datafileID)
	if err != nil {
		return fmt.Errorf("upsert %s for datafile_id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

// UpdateDataFileSummaryResult updates the final status and aggregate counts for a summary row.
func UpdateDataFileSummaryResult(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, totalInFile int64, totalCreated int64) error {
	table := pgx.Identifier{tableName}.Sanitize()
	query := `
		UPDATE %s
		SET total_number_of_records_in_file = $1,
		    total_number_of_records_created = $2
		WHERE datafile_id = $3
	`

	_, err := pool.Exec(ctx, fmt.Sprintf(query, table), totalInFile, totalCreated, datafileID)
	if err != nil {
		return fmt.Errorf("update %s result for datafile_id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

// UpdateDataFileSummaryStatus updates the status of a DataFileSummary for the given datafile.
func UpdateDataFileSummaryStatus(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, status string) error {
	table := pgx.Identifier{tableName}.Sanitize()
	query := `
		UPDATE %s
		SET status = $1
		WHERE datafile_id = $2
	`

	_, err := pool.Exec(ctx, fmt.Sprintf(query, table), status, datafileID)
	if err != nil {
		return fmt.Errorf("update %s status for datafile_id=%d: %w", tableName, datafileID, err)
	}

	return nil
}
