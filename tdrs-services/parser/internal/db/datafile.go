package db

import (
	"context"
	"crypto/rand"
	"encoding/json"
	"fmt"
	"io"
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

const lockCurrentProductionParseToken = `
	SELECT 1
	FROM data_files_datafile AS data_file
	WHERE data_file.id = $1
	  AND data_file.state = 'parse_started'
	  AND data_file.current_parse_token = $2::uuid
	FOR UPDATE
`

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
	StateChangedAt   pgtype.Timestamptz
}

type DataFileStateTransitionContext struct {
	EventID       string
	Note          string
	Source        string
	TaskName      string
	CeleryTaskID  string
	ReparseMetaID int32
	Metadata      map[string]any
}

const selectShadowDataFile = `
	SELECT id, original_filename, slug, extension, quarter, year, section, version,
	       stt_id, user_id, created_at, file, s3_versioning_id, program_type,
	       is_program_audit, state, state_changed_at
	FROM shadow_data_files_datafile
	WHERE id = $1
`

const selectProductionDataFile = `
	SELECT id, original_filename, slug, extension, quarter, year, section, version,
	       stt_id, user_id, created_at, file, s3_versioning_id, program_type,
	       is_program_audit, state, state_changed_at
	FROM data_files_datafile
	WHERE id = $1
`

const upsertShadowDataFile = `
	INSERT INTO shadow_data_files_datafile (
	    id, original_filename, slug, extension, quarter, year, section, version,
	    stt_id, user_id, created_at, file, s3_versioning_id, program_type,
	    is_program_audit, state, state_changed_at
	)
	VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
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
	    is_program_audit = EXCLUDED.is_program_audit
`

const upsertProductionDataFile = `
	INSERT INTO data_files_datafile (
	    id, original_filename, slug, extension, quarter, year, section, version,
	    stt_id, user_id, created_at, file, s3_versioning_id, program_type,
	    is_program_audit, state, state_changed_at
	)
	VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
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
	    is_program_audit = EXCLUDED.is_program_audit
`

const updateShadowDataFileState = `
	UPDATE shadow_data_files_datafile
	SET state = $1, state_changed_at = NOW()
	WHERE id = $2
`

const selectShadowDataFileStateForUpdate = `
	SELECT state
	FROM shadow_data_files_datafile
	WHERE id = $1
	FOR UPDATE
`

const insertDataFileStateTransition = `
	WITH base_log AS (
	    INSERT INTO core_baselog (
	        object_id,
	        event_id,
	        event_type,
	        note,
	        metadata,
	        source,
	        task_name,
	        celery_task_id,
	        created_at,
	        actor_id,
	        content_type_id
	    )
	    VALUES (
	        $1::text,
	        $2,
	        'data_file_state_transition',
	        $5,
	        $6::jsonb,
	        NULLIF($7, ''),
	        NULLIF($8, ''),
	        NULLIF($9, ''),
	        NOW(),
	        NULL,
	        (
	            SELECT id
	            FROM django_content_type
	            WHERE app_label = 'data_files'
	              AND model = $11
	        )
	    )
	    RETURNING id
	)
	INSERT INTO data_files_datafilestatetransition (
	    baselog_ptr_id,
	    previous_state,
	    next_state,
	    reparse_meta_id
	)
	SELECT id, $3, $4, $10
	FROM base_log
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

// UpdateShadowDataFileState records shadow state and audit history; production writes are rejected.
func UpdateShadowDataFileState(
	ctx context.Context,
	pool *pgxpool.Pool,
	tableName string,
	datafileID int32,
	state string,
	transitionContexts ...DataFileStateTransitionContext,
) error {
	var selectStateQuery, updateStateQuery, contentTypeModel string
	switch tableName {
	case shadowDataFileTable:
		selectStateQuery = selectShadowDataFileStateForUpdate
		updateStateQuery = updateShadowDataFileState
		contentTypeModel = "shadowdatafile"
	case productionDataFileTable:
		return fmt.Errorf("production DataFile state is owned by the Django lifecycle controller")
	default:
		return fmt.Errorf("unsupported datafile table %q", tableName)
	}
	err := updateDataFileStateWithTransition(
		ctx, pool, datafileID, state, firstTransitionContext(transitionContexts),
		selectStateQuery, updateStateQuery, contentTypeModel,
	)
	if err != nil {
		return fmt.Errorf("update %s state for id=%d: %w", tableName, datafileID, err)
	}

	return nil
}

func updateDataFileStateWithTransition(
	ctx context.Context,
	pool *pgxpool.Pool,
	datafileID int32,
	state string,
	transitionContext DataFileStateTransitionContext,
	selectStateQuery, updateStateQuery, contentTypeModel string,
) error {
	tx, err := pool.Begin(ctx)
	if err != nil {
		return err
	}
	defer func() {
		_ = tx.Rollback(ctx)
	}()

	var previousState string
	if err := tx.QueryRow(
		ctx,
		selectStateQuery,
		datafileID,
	).Scan(&previousState); err != nil {
		return err
	}

	if previousState == state {
		return tx.Commit(ctx)
	}

	if _, err := tx.Exec(ctx, updateStateQuery, state, datafileID); err != nil {
		return err
	}

	metadataJSON, err := marshalStateTransitionMetadata(
		datafileID,
		previousState,
		state,
		transitionContext,
	)
	if err != nil {
		return err
	}

	reparseMetaID := pgtype.Int4{}
	if transitionContext.ReparseMetaID > 0 {
		reparseMetaID = pgtype.Int4{Int32: transitionContext.ReparseMetaID, Valid: true}
	}

	objectID := fmt.Sprint(datafileID)
	eventID, err := resolveLogEventUUID(transitionContext.EventID)
	if err != nil {
		return err
	}
	if _, err := tx.Exec(
		ctx,
		insertDataFileStateTransition,
		objectID,
		eventID,
		previousState,
		state,
		transitionContext.Note,
		metadataJSON,
		transitionContext.Source,
		transitionContext.TaskName,
		transitionContext.CeleryTaskID,
		reparseMetaID,
		contentTypeModel,
	); err != nil {
		return err
	}

	return tx.Commit(ctx)
}

func firstTransitionContext(contexts []DataFileStateTransitionContext) DataFileStateTransitionContext {
	if len(contexts) == 0 {
		return DataFileStateTransitionContext{}
	}
	return contexts[0]
}

func newLogEventUUID() pgtype.UUID {
	var id [16]byte
	if _, err := io.ReadFull(rand.Reader, id[:]); err != nil {
		panic(err)
	}
	id[6] = (id[6] & 0x0f) | 0x40
	id[8] = (id[8] & 0x3f) | 0x80
	return pgtype.UUID{Bytes: id, Valid: true}
}

func resolveLogEventUUID(eventID string) (pgtype.UUID, error) {
	if eventID == "" {
		return newLogEventUUID(), nil
	}

	var id pgtype.UUID
	if err := id.Scan(eventID); err != nil {
		return pgtype.UUID{}, fmt.Errorf("invalid event_id %q: %w", eventID, err)
	}
	return id, nil
}

func marshalStateTransitionMetadata(
	datafileID int32,
	previousState string,
	nextState string,
	transitionContext DataFileStateTransitionContext,
) ([]byte, error) {
	metadata := map[string]any{
		"data_file_id":    datafileID,
		"previous_state":  previousState,
		"next_state":      nextState,
		"note":            transitionContext.Note,
		"transition_path": "go_sql",
	}
	for key, value := range transitionContext.Metadata {
		metadata[key] = value
	}
	if transitionContext.Source != "" {
		metadata["source"] = transitionContext.Source
	}
	if transitionContext.TaskName != "" {
		metadata["task_name"] = transitionContext.TaskName
	}
	if transitionContext.CeleryTaskID != "" {
		metadata["celery_task_id"] = transitionContext.CeleryTaskID
	}
	if transitionContext.ReparseMetaID > 0 {
		metadata["reparse_meta_id"] = transitionContext.ReparseMetaID
		metadata["reparse_id"] = transitionContext.ReparseMetaID
	}
	if transitionContext.EventID != "" {
		metadata["event_id"] = transitionContext.EventID
	}

	return json.Marshal(metadata)
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

// EnsureDataFileSummaryForToken fences production summary creation with token ownership.
func EnsureDataFileSummaryForToken(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, parseToken string) error {
	if tableName != productionDataFileSummaryTable {
		return EnsureDataFileSummary(ctx, pool, tableName, datafileID)
	}
	return withProductionParseToken(ctx, pool, datafileID, parseToken, func(tx pgx.Tx) error {
		_, err := tx.Exec(ctx, upsertProductionDataFileSummary, datafileID)
		return err
	})
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

// UpdateDataFileSummaryResultForToken fences production totals with token ownership.
func UpdateDataFileSummaryResultForToken(ctx context.Context, pool *pgxpool.Pool, tableName string, datafileID int32, totalInFile int64, totalCreated int64, parseToken string) error {
	if tableName != productionDataFileSummaryTable {
		return UpdateDataFileSummaryResult(ctx, pool, tableName, datafileID, totalInFile, totalCreated)
	}
	totalInFileInt4, err := int64ToInt4(totalInFile)
	if err != nil {
		return err
	}
	totalCreatedInt4, err := int64ToInt4(totalCreated)
	if err != nil {
		return err
	}
	return withProductionParseToken(ctx, pool, datafileID, parseToken, func(tx pgx.Tx) error {
		_, err := tx.Exec(
			ctx,
			updateProductionDataFileSummaryResult,
			totalInFileInt4,
			totalCreatedInt4,
			datafileID,
		)
		return err
	})
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

func withProductionParseToken(
	ctx context.Context,
	pool *pgxpool.Pool,
	datafileID int32,
	parseToken string,
	write func(pgx.Tx) error,
) error {
	if parseToken == "" {
		return fmt.Errorf("production write for datafile %d requires a parse token", datafileID)
	}
	tx, err := pool.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx) // no-op after Commit

	var ownsToken int
	if err := tx.QueryRow(
		ctx,
		lockCurrentProductionParseToken,
		datafileID,
		parseToken,
	).Scan(&ownsToken); err != nil {
		if err == pgx.ErrNoRows {
			return fmt.Errorf(
				"parse token %s no longer owns datafile %d",
				parseToken,
				datafileID,
			)
		}
		return err
	}
	if err := write(tx); err != nil {
		return err
	}
	return tx.Commit(ctx)
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
		&df.StateChangedAt,
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
		df.StateChangedAt,
	)
	return err
}
