package db

import (
	"context"
	"fmt"
	"math"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
)

// GetDataFile retrieves a DataFile-compatible record by its primary key.
func GetDataFile(ctx context.Context, pool *pgxpool.Pool, tableName string, id int32) (*ShadowDataFilesDatafile, error) {
	df, err := New(pool).GetDataFile(ctx, id)
	if err != nil {
		return nil, fmt.Errorf("query %s id=%d: %w", tableName, id, err)
	}

	return &df, nil
}

// EnsureShadowDataFile copies production DataFile metadata into the Go parser shadow table.
func EnsureShadowDataFile(ctx context.Context, pool *pgxpool.Pool, tableName string, df *ShadowDataFilesDatafile) error {
	if err := New(pool).EnsureShadowDataFile(ctx, EnsureShadowDataFileParams{
		ID:               df.ID,
		OriginalFilename: df.OriginalFilename,
		Slug:             df.Slug,
		Extension:        df.Extension,
		Quarter:          df.Quarter,
		Year:             df.Year,
		Section:          df.Section,
		Version:          df.Version,
		SttID:            df.SttID,
		UserID:           df.UserID,
		CreatedAt:        df.CreatedAt,
		File:             df.File,
		S3VersioningID:   df.S3VersioningID,
		ProgramType:      df.ProgramType,
		IsProgramAudit:   df.IsProgramAudit,
		State:            df.State,
	}); err != nil {
		return fmt.Errorf("upsert %s id=%d: %w", tableName, df.ID, err)
	}

	return nil
}

// UpdateDataFileState updates the submission state for a DataFile-compatible table.
func UpdateDataFileState(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, state string) error {
	if err := New(pool).UpdateDataFileState(ctx, UpdateDataFileStateParams{
		ID:    datafileID,
		State: state,
	}); err != nil {
		return fmt.Errorf("update %s state for id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

// EnsureDataFileSummary creates or resets the shadow DataFileSummary for the given datafile.
func EnsureDataFileSummary(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32) error {
	if err := New(pool).EnsureDataFileSummary(ctx, datafileID); err != nil {
		return fmt.Errorf("upsert %s for datafile_id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

// UpdateDataFileSummaryResult updates the final status and aggregate counts for a summary row.
func UpdateDataFileSummaryResult(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, totalInFile int64, totalCreated int64) error {
	totalInFileInt4, err := int64ToInt4(totalInFile)
	if err != nil {
		return fmt.Errorf("update %s result for datafile_id=%d: %w", tableName, datafileID, err)
	}
	totalCreatedInt4, err := int64ToInt4(totalCreated)
	if err != nil {
		return fmt.Errorf("update %s result for datafile_id=%d: %w", tableName, datafileID, err)
	}

	if err := New(pool).UpdateDataFileSummaryResult(ctx, UpdateDataFileSummaryResultParams{
		DatafileID:                  datafileID,
		TotalNumberOfRecordsInFile:  totalInFileInt4,
		TotalNumberOfRecordsCreated: totalCreatedInt4,
	}); err != nil {
		return fmt.Errorf("update %s result for datafile_id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

// UpdateDataFileSummaryStatus updates the status of a DataFileSummary for the given datafile.
func UpdateDataFileSummaryStatus(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, status string) error {
	if err := New(pool).UpdateDataFileSummaryStatus(ctx, UpdateDataFileSummaryStatusParams{
		DatafileID: datafileID,
		Status:     status,
	}); err != nil {
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
