package db

import (
	"context"
	"fmt"
	"math"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	productionDataFileTable        = "data_files_datafile"
	shadowDataFileTable            = "shadow_data_files_datafile"
	productionDataFileSummaryTable = "parsers_datafilesummary"
	shadowDataFileSummaryTable     = "shadow_parsers_datafilesummary"
)

// GetDataFile retrieves a DataFile-compatible record by its primary key.
func GetDataFile(ctx context.Context, pool *pgxpool.Pool, tableName string, id int32) (*ShadowDataFilesDatafile, error) {
	queries := New(pool)
	var (
		df  ShadowDataFilesDatafile
		err error
	)

	switch tableName {
	case shadowDataFileTable:
		df, err = queries.GetDataFile(ctx, id)
	case productionDataFileTable:
		var productionDf DataFilesDatafile
		productionDf, err = queries.GetProductionDataFile(ctx, id)
		df = shadowDataFileFromProduction(productionDf)
	default:
		err = fmt.Errorf("unsupported datafile table %q", tableName)
	}
	if err != nil {
		return nil, fmt.Errorf("query %s id=%d: %w", tableName, id, err)
	}

	return &df, nil
}

// EnsureShadowDataFile copies production DataFile metadata into the Go parser shadow table.
func EnsureShadowDataFile(ctx context.Context, pool *pgxpool.Pool, tableName string, df *ShadowDataFilesDatafile) error {
	queries := New(pool)
	var err error
	switch tableName {
	case shadowDataFileTable:
		err = queries.EnsureShadowDataFile(ctx, ensureShadowDataFileParams(df))
	case productionDataFileTable:
		err = queries.EnsureProductionDataFile(ctx, ensureProductionDataFileParams(df))
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
	queries := New(pool)
	var err error
	switch tableName {
	case shadowDataFileTable:
		err = queries.UpdateDataFileState(ctx, UpdateDataFileStateParams{
			ID:    datafileID,
			State: state,
		})
	case productionDataFileTable:
		err = queries.UpdateProductionDataFileState(ctx, UpdateProductionDataFileStateParams{
			ID:    datafileID,
			State: state,
		})
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
	queries := New(pool)
	var err error
	switch tableName {
	case shadowDataFileSummaryTable:
		err = queries.EnsureDataFileSummary(ctx, datafileID)
	case productionDataFileSummaryTable:
		err = queries.EnsureProductionDataFileSummary(ctx, datafileID)
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

	queries := New(pool)
	switch tableName {
	case shadowDataFileSummaryTable:
		err = queries.UpdateDataFileSummaryResult(ctx, UpdateDataFileSummaryResultParams{
			DatafileID:                  datafileID,
			TotalNumberOfRecordsInFile:  totalInFileInt4,
			TotalNumberOfRecordsCreated: totalCreatedInt4,
		})
	case productionDataFileSummaryTable:
		err = queries.UpdateProductionDataFileSummaryResult(ctx, UpdateProductionDataFileSummaryResultParams{
			DatafileID:                  datafileID,
			TotalNumberOfRecordsInFile:  totalInFileInt4,
			TotalNumberOfRecordsCreated: totalCreatedInt4,
		})
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
	queries := New(pool)
	var err error
	switch tableName {
	case shadowDataFileSummaryTable:
		err = queries.UpdateDataFileSummaryStatus(ctx, UpdateDataFileSummaryStatusParams{
			DatafileID: datafileID,
			Status:     status,
		})
	case productionDataFileSummaryTable:
		err = queries.UpdateProductionDataFileSummaryStatus(ctx, UpdateProductionDataFileSummaryStatusParams{
			DatafileID: datafileID,
			Status:     status,
		})
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

func shadowDataFileFromProduction(df DataFilesDatafile) ShadowDataFilesDatafile {
	return ShadowDataFilesDatafile{
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
	}
}

func ensureShadowDataFileParams(df *ShadowDataFilesDatafile) EnsureShadowDataFileParams {
	return EnsureShadowDataFileParams{
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
	}
}

func ensureProductionDataFileParams(df *ShadowDataFilesDatafile) EnsureProductionDataFileParams {
	return EnsureProductionDataFileParams{
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
	}
}
