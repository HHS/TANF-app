package db

import (
	"context"
	"fmt"
	"math"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	productionDataFileTable        = "data_files_datafile"
	shadowDataFileTable            = "shadow_data_files_datafile"
	productionDataFileSummaryTable = "parsers_datafilesummary"
	shadowDataFileSummaryTable     = "shadow_parsers_datafilesummary"
)

type DataFileRecord struct {
	ID               int32
	OriginalFilename string
	Slug             string
	Extension        string
	Quarter          string
	Year             int32
	Section          string
	Version          int32
	SttID            int32
	UserID           pgtype.UUID
	CreatedAt        pgtype.Timestamptz
	File             pgtype.Text
	S3VersioningID   pgtype.Text
	ProgramType      string
	IsProgramAudit   bool
	State            string
}

const selectShadowDataFile = `
	SELECT id, original_filename, slug, extension, quarter, year, section, version,
	       stt_id, user_id, created_at, file, s3_versioning_id, program_type,
	       is_program_audit, state
	FROM shadow_data_files_datafile
	WHERE id = $1
`

const selectProductionDataFile = `
	SELECT id, original_filename, slug, extension, quarter, year, section, version,
	       stt_id, user_id, created_at, file, s3_versioning_id, program_type,
	       is_program_audit, state
	FROM data_files_datafile
	WHERE id = $1
`

const upsertShadowDataFile = `
	INSERT INTO shadow_data_files_datafile (
	    id, original_filename, slug, extension, quarter, year, section, version,
	    stt_id, user_id, created_at, file, s3_versioning_id, program_type,
	    is_program_audit, state
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
`

const upsertProductionDataFile = `
	INSERT INTO data_files_datafile (
	    id, original_filename, slug, extension, quarter, year, section, version,
	    stt_id, user_id, created_at, file, s3_versioning_id, program_type,
	    is_program_audit, state
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
`

const updateShadowDataFileState = `
	UPDATE shadow_data_files_datafile
	SET state = $1
	WHERE id = $2
`

const updateProductionDataFileState = `
	UPDATE data_files_datafile
	SET state = $1
	WHERE id = $2
`

const upsertShadowDataFileSummary = `
	INSERT INTO shadow_parsers_datafilesummary (
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
`

const upsertProductionDataFileSummary = `
	INSERT INTO parsers_datafilesummary (
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
`

const updateShadowDataFileSummaryResult = `
	UPDATE shadow_parsers_datafilesummary
	SET total_number_of_records_in_file = $1,
	    total_number_of_records_created = $2
	WHERE datafile_id = $3
`

const updateProductionDataFileSummaryResult = `
	UPDATE parsers_datafilesummary
	SET total_number_of_records_in_file = $1,
	    total_number_of_records_created = $2
	WHERE datafile_id = $3
`

const updateShadowDataFileSummaryStatus = `
	UPDATE shadow_parsers_datafilesummary
	SET status = $1
	WHERE datafile_id = $2
`

const updateProductionDataFileSummaryStatus = `
	UPDATE parsers_datafilesummary
	SET status = $1
	WHERE datafile_id = $2
`

// GetDataFile retrieves a DataFile-compatible record by its primary key.
func GetDataFile(ctx context.Context, pool *pgxpool.Pool, tableName string, id int32) (*DataFileRecord, error) {
	var (
		df  DataFileRecord
		err error
	)

	switch tableName {
	case shadowDataFileTable:
		df, err = scanDataFile(pool.QueryRow(ctx, selectShadowDataFile, id))
	case productionDataFileTable:
		df, err = scanDataFile(pool.QueryRow(ctx, selectProductionDataFile, id))
	default:
		err = fmt.Errorf("unsupported datafile table %q", tableName)
	}
	if err != nil {
		return nil, fmt.Errorf("query %s id=%d: %w", tableName, id, err)
	}

	return &df, nil
}

// EnsureShadowDataFile copies production DataFile metadata into the Go parser shadow table.
func EnsureShadowDataFile(ctx context.Context, pool *pgxpool.Pool, tableName string, df *DataFileRecord) error {
	var err error
	switch tableName {
	case shadowDataFileTable:
		err = execDataFileUpsert(ctx, pool, upsertShadowDataFile, df)
	case productionDataFileTable:
		err = execDataFileUpsert(ctx, pool, upsertProductionDataFile, df)
	default:
		err = fmt.Errorf("unsupported datafile table %q", tableName)
	}
	if err != nil {
		return fmt.Errorf("upsert %s id=%d: %w", tableName, df.ID, err)
	}

	return nil
}

// UpdateDataFileState updates the submission state for a DataFile-compatible table.
func UpdateDataFileState(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, state string) error {
	var err error
	switch tableName {
	case shadowDataFileTable:
		_, err = pool.Exec(ctx, updateShadowDataFileState, state, datafileID)
	case productionDataFileTable:
		_, err = pool.Exec(ctx, updateProductionDataFileState, state, datafileID)
	default:
		err = fmt.Errorf("unsupported datafile table %q", tableName)
	}
	if err != nil {
		return fmt.Errorf("update %s state for id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

// EnsureDataFileSummary creates or resets the shadow DataFileSummary for the given datafile.
func EnsureDataFileSummary(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32) error {
	var err error
	switch tableName {
	case shadowDataFileSummaryTable:
		_, err = pool.Exec(ctx, upsertShadowDataFileSummary, datafileID)
	case productionDataFileSummaryTable:
		_, err = pool.Exec(ctx, upsertProductionDataFileSummary, datafileID)
	default:
		err = fmt.Errorf("unsupported datafile summary table %q", tableName)
	}
	if err != nil {
		return fmt.Errorf("upsert %s for datafile_id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

// UpdateDataFileSummaryResult updates the final aggregate counts for a summary row.
func UpdateDataFileSummaryResult(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, totalInFile int64, totalCreated int64) error {
	totalInFileInt4, err := int64ToInt4(totalInFile)
	if err != nil {
		return fmt.Errorf("update %s result for datafile_id=%d: %w", tableName, datafileID, err)
	}
	totalCreatedInt4, err := int64ToInt4(totalCreated)
	if err != nil {
		return fmt.Errorf("update %s result for datafile_id=%d: %w", tableName, datafileID, err)
	}

	switch tableName {
	case shadowDataFileSummaryTable:
		_, err = pool.Exec(ctx, updateShadowDataFileSummaryResult, totalInFileInt4, totalCreatedInt4, datafileID)
	case productionDataFileSummaryTable:
		_, err = pool.Exec(ctx, updateProductionDataFileSummaryResult, totalInFileInt4, totalCreatedInt4, datafileID)
	default:
		err = fmt.Errorf("unsupported datafile summary table %q", tableName)
	}
	if err != nil {
		return fmt.Errorf("update %s result for datafile_id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

// UpdateDataFileSummaryStatus updates the status of a DataFileSummary for the given datafile.
func UpdateDataFileSummaryStatus(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, status string) error {
	var err error
	switch tableName {
	case shadowDataFileSummaryTable:
		_, err = pool.Exec(ctx, updateShadowDataFileSummaryStatus, status, datafileID)
	case productionDataFileSummaryTable:
		_, err = pool.Exec(ctx, updateProductionDataFileSummaryStatus, status, datafileID)
	default:
		err = fmt.Errorf("unsupported datafile summary table %q", tableName)
	}
	if err != nil {
		return fmt.Errorf("update %s status for datafile_id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

func int64ToInt4(value int64) (pgtype.Int4, error) {
	if value < 0 || value > math.MaxInt32 {
		return pgtype.Int4{}, fmt.Errorf("value %d is outside int4 range", value)
	}
	return pgtype.Int4{Int32: int32(value), Valid: true}, nil
}

func scanDataFile(row pgx.Row) (DataFileRecord, error) {
	var df DataFileRecord
	err := row.Scan(
		&df.ID,
		&df.OriginalFilename,
		&df.Slug,
		&df.Extension,
		&df.Quarter,
		&df.Year,
		&df.Section,
		&df.Version,
		&df.SttID,
		&df.UserID,
		&df.CreatedAt,
		&df.File,
		&df.S3VersioningID,
		&df.ProgramType,
		&df.IsProgramAudit,
		&df.State,
	)
	return df, err
}

func execDataFileUpsert(
	ctx context.Context,
	pool *pgxpool.Pool,
	query string,
	df *DataFileRecord,
) error {
	_, err := pool.Exec(
		ctx,
		query,
		df.ID,
		df.OriginalFilename,
		df.Slug,
		df.Extension,
		df.Quarter,
		df.Year,
		df.Section,
		df.Version,
		df.SttID,
		df.UserID,
		df.CreatedAt,
		df.File,
		df.S3VersioningID,
		df.ProgramType,
		df.IsProgramAudit,
		df.State,
	)
	return err
}
