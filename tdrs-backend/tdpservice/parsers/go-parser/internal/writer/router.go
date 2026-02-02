package writer

import (
	"context"
	"errors"
	"fmt"
	"log"
	"sync"

	"github.com/jackc/pgx/v5/pgtype"
	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/parser"
	"go-parser/internal/writer/convert"
)

// Router coordinates writes for any file type.
// Writers are created dynamically based on the FileSpec.
// Router owns the converters and handles the full pipeline:
// ParsedRecord -> convert -> release to pool -> send []any to writer
type Router struct {
	pool       *pgxpool.Pool
	datafileID int32

	// Writers keyed by schema path (e.g., "tanf/t1", "tribal/t1")
	writers map[string]*TableWriter

	// Converters keyed by schema path - manager owns conversion
	converters map[string]convert.RowConverter

	// Content type IDs keyed by schema path - for error linking
	contentTypeIDs map[string]*int32

	errorWriter *TableWriter
}

// Error table columns (same for all file types)
var parserErrorColumns = []string{
	"row_number", "column_number", "item_number", "field_name",
	"case_number", "rpt_month_year", "error_message", "error_type",
	"created_at", "fields_json", "content_type_id", "file_id",
	"object_id", "deprecated", "values_json",
}

// RouterConfig holds configuration for the writer router.
type RouterConfig struct {
	PoolPrewarmSize     int
	FlushThreshold      int
	ErrorFlushThreshold int
}

// NewRouter creates a manager based on the FileSpec.
// Writers are created only for the record types in this specific file.
func NewRouter(
	pool *pgxpool.Pool,
	datafileID int32,
	spec *filespec.FileSpec,
	reg *config.Registry,
	cfg RouterConfig,
) *Router {
	wm := &Router{
		pool:           pool,
		datafileID:     datafileID,
		writers:        make(map[string]*TableWriter),
		converters:     make(map[string]convert.RowConverter),
		contentTypeIDs: make(map[string]*int32),
	}

	// Create a writer for each data record type in the FileSpec
	for _, schemaPath := range spec.Schemas {
		sch := reg.GetSchema(schemaPath)

		// Set schema object pool allocator
		newObjFunc := func() any {
			return &parser.ParsedRecord{
				Schema: sch,
				Fields: make([]parser.ParsedField, sch.FieldCount),
			}
		}
		sch.InitPool(newObjFunc)

		// Skip header/trailer - they don't get written to database
		if sch.RecordType == "HEADER" || sch.RecordType == "TRAILER" {
			continue
		}

		// Pre-warm the object pool for this schema to avoid allocation during parsing
		if cfg.PoolPrewarmSize > 0 {
			sch.PrewarmPool(cfg.PoolPrewarmSize)
		}

		// Get metadata (table name, columns derived from schema)
		meta := reg.GetSchemaMetadata(schemaPath)
		if meta == nil {
			continue
		}

		// Get the converter for this schema path
		// Schema path (e.g., "tanf/t1") distinguishes TANF vs Tribal T1
		conv := convert.GetConverter(schemaPath)
		if conv == nil {
			log.Printf("Warning: no converter for schema %s", schemaPath)
			continue
		}

		// Store converter in manager (conversion happens in RouteRecord)
		wm.converters[schemaPath] = conv

		// Store content type ID for error linking
		wm.contentTypeIDs[schemaPath] = meta.ContentTypeID

		// Create simplified TableWriter that receives []any rows
		wm.writers[schemaPath] = NewTableWriter(
			meta.TableName,
			meta.Columns,
			cfg.FlushThreshold,
		)

		log.Printf("Created writer for %s -> %s (%d columns)",
			schemaPath, meta.TableName, len(meta.Columns))
	}

	// Create error writer with higher threshold for error volume
	wm.errorWriter = NewTableWriter(
		"parser_error",
		parserErrorColumns,
		cfg.ErrorFlushThreshold,
	)
	log.Printf("Created error writer for parser_error (%d columns)", len(parserErrorColumns))

	return wm
}

// Start launches all writer goroutines.
// Must be called before RouteBatch/RouteRecord.
func (wm *Router) Start(ctx context.Context) {
	for _, tw := range wm.writers {
		tw.Start(ctx, wm.pool)
	}
	if wm.errorWriter != nil {
		wm.errorWriter.Start(ctx, wm.pool)
	}
}

// RouteRecord converts a record, releases it to pool, and sends rows to writer.
// This is the release point for valid records in the normal flow.
// Records without writers (e.g., HEADER, TRAILER) are silently skipped.
func (wm *Router) RouteRecord(ctx context.Context, record *parser.ParsedRecord) error {
	tw, ok := wm.writers[record.Schema.Path]
	if !ok {
		// No writer for this schema (e.g., header/trailer) - skip silently
		return nil
	}

	conv, ok := wm.converters[record.Schema.Path]
	if !ok {
		return fmt.Errorf("no converter for schema: %s", record.Schema.Path)
	}

	// Convert ParsedRecord to []any rows
	rows := conv(record, wm.datafileID)

	// Release record back to pool - it's no longer needed after conversion
	record.Schema.ReleaseRecord(record)

	// Send converted rows to writer
	for _, row := range rows {
		if err := tw.SendRow(ctx, row); err != nil {
			return err
		}
	}

	return nil
}

// RouteBatch routes all records in a batch to appropriate writers.
func (wm *Router) RouteBatch(ctx context.Context, batch *parser.ParsedBatch) error {
	for _, group := range batch.Groups {
		for _, record := range group.Records {
			if err := wm.RouteRecord(ctx, record); err != nil {
				return err
			}
		}
	}
	return nil
}

// RouteErrorRow sends a pre-converted error row to the error writer.
// Errors are converted at call site (in result_router) while record is available.
func (wm *Router) RouteErrorRow(ctx context.Context, row []any) error {
	if wm.errorWriter == nil {
		return nil
	}
	return wm.errorWriter.SendRow(ctx, row)
}

// ConvertRecord converts a record to database rows and extracts the UUID.
// Does NOT release the record or send rows - caller handles that.
// Returns the converted rows, the record's UUID, and any error.
// The UUID is extracted from the converted row at position len(row)-3 (third from end).
func (wm *Router) ConvertRecord(record *parser.ParsedRecord) ([][]any, *pgtype.UUID, error) {
	conv, ok := wm.converters[record.Schema.Path]
	if !ok {
		return nil, nil, fmt.Errorf("no converter for schema: %s", record.Schema.Path)
	}

	rows := conv(record, wm.datafileID)
	if len(rows) == 0 {
		return rows, nil, nil
	}

	// Extract UUID from first row at position len(row)-3
	// All converters place ID, DatafileID, LineNumber at the end
	firstRow := rows[0]
	uuidIdx := len(firstRow) - 3
	if uuidIdx >= 0 {
		if uuid, ok := firstRow[uuidIdx].(pgtype.UUID); ok {
			return rows, &uuid, nil
		}
	}

	return rows, nil, nil
}

// SendRecordRowsByPath sends pre-converted record rows to the writer for the given schema path.
// Used in conjunction with ConvertRecord for the error-linking flow.
func (wm *Router) SendRecordRowsByPath(ctx context.Context, schemaPath string, rows [][]any) error {
	tw, ok := wm.writers[schemaPath]
	if !ok {
		// No writer for this schema (e.g., header/trailer) - skip silently
		return nil
	}

	for _, row := range rows {
		if err := tw.SendRow(ctx, row); err != nil {
			return err
		}
	}
	return nil
}

// HasWriter returns true if there's a writer for this schema path.
func (wm *Router) HasWriter(schemaPath string) bool {
	_, ok := wm.writers[schemaPath]
	return ok
}

// GetContentTypeID returns the Django content type ID for a schema path.
// Returns nil if the schema has no content type (e.g., not loaded from DB).
func (wm *Router) GetContentTypeID(schemaPath string) *int32 {
	return wm.contentTypeIDs[schemaPath]
}

// Stop closes all channels and waits for goroutines to finish.
// Returns combined errors from all writers.
func (wm *Router) Stop() error {
	var errs []error
	var wg sync.WaitGroup
	var errMu sync.Mutex

	// Stop all writers in parallel
	for name, tw := range wm.writers {
		wg.Add(1)
		go func(name string, tw *TableWriter) {
			defer wg.Done()
			if err := tw.Stop(); err != nil {
				errMu.Lock()
				errs = append(errs, fmt.Errorf("%s: %w", name, err))
				errMu.Unlock()
			}
		}(name, tw)
	}
	wg.Wait()

	if wm.errorWriter != nil {
		if err := wm.errorWriter.Stop(); err != nil {
			errs = append(errs, fmt.Errorf("error_writer: %w", err))
		}
	}

	if len(errs) > 0 {
		return errors.Join(errs...)
	}
	return nil
}

// Stats returns totals from all writers.
func (wm *Router) Stats() (records map[string]int64, errorCount int64) {
	result := make(map[string]int64)
	for path, tw := range wm.writers {
		result[path] = tw.TotalWritten()
	}
	if wm.errorWriter != nil {
		errorCount = wm.errorWriter.TotalWritten()
	}
	return result, errorCount
}
