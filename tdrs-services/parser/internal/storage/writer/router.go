package writer

import (
	"context"
	"errors"
	"fmt"
	"log"
	"sync"

	"github.com/jackc/pgx/v5/pgtype"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/parser"
)

// Router coordinates writes for any file type.
// Writers are created dynamically based on the FileSpec.
// Router owns the serializers and handles the full pipeline:
// ParsedRecord -> serialize -> release to pool -> send []any to writer
type Router struct {
	sink       Sink
	datafileID int32

	// Writers keyed by schema path (e.g., "tanf/t1", "tribal/t1")
	writers map[string]*TableWriter

	// Serializers keyed by schema path - manager owns serialization
	serializers map[string]RowSerializer

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

// ParserErrorColumns returns the column names for the parser_error table.
func ParserErrorColumns() []string {
	return parserErrorColumns
}

// RouterConfig holds configuration for the writer router.
type RouterConfig struct {
	PoolPrewarmSize     int
	FlushThreshold      int
	ErrorFlushThreshold int

	// IncludeSchemas filters which record types get written.
	// Empty means write all. Example: ["tanf/t1"] writes only T1 records.
	// Only applied when IncludeRecords is true.
	IncludeSchemas []string

	// IncludeRecords controls whether record data is written. Default true.
	// When false, no record writers are created regardless of IncludeSchemas.
	IncludeRecords bool

	// IncludeErrors controls whether errors are written. Default true.
	IncludeErrors bool
}

// NewRouter creates a manager based on the FileSpec.
// Writers are created only for the record types in this specific file.
func NewRouter(
	sink Sink,
	datafileID int32,
	spec *filespec.FileSpec,
	reg *config.Registry,
	cfg RouterConfig,
) *Router {
	// Build include set for fast lookup
	includeSet := make(map[string]bool, len(cfg.IncludeSchemas))
	for _, s := range cfg.IncludeSchemas {
		includeSet[s] = true
	}

	router := &Router{
		sink:           sink,
		datafileID:     datafileID,
		writers:        make(map[string]*TableWriter),
		serializers:    make(map[string]RowSerializer),
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

		// Skip header/trailer - they don't get written
		if sch.RecordType == "HEADER" || sch.RecordType == "TRAILER" {
			continue
		}

		// Pre-warm the object pool for this schema to avoid allocation during parsing
		// (needed even when records aren't written — parsing still uses the pool)
		if cfg.PoolPrewarmSize > 0 {
			sch.PrewarmPool(cfg.PoolPrewarmSize)
		}

		// Skip record writer creation when records are disabled
		if !cfg.IncludeRecords {
			continue
		}

		// Apply schema filter if configured
		if len(includeSet) > 0 && !includeSet[schemaPath] {
			log.Printf("Skipping writer for %s (not in include_schemas)", schemaPath)
			continue
		}

		// Get metadata (table name, columns derived from schema)
		meta := reg.GetSchemaMetadata(schemaPath)
		if meta == nil {
			continue
		}

		// Get the serializer for this schema path
		// Schema path (e.g., "tanf/t1") distinguishes TANF vs Tribal T1
		conv := GetSerializer(schemaPath)
		if conv == nil {
			log.Printf("Warning: no serializer for schema %s", schemaPath)
			continue
		}

		// Store serializer in manager (serialization happens in RouteRecord)
		router.serializers[schemaPath] = conv

		// Store content type ID for error linking
		router.contentTypeIDs[schemaPath] = meta.ContentTypeID

		// Create simplified TableWriter that receives []any rows
		router.writers[schemaPath] = NewTableWriter(
			meta.TableName,
			meta.Columns,
			cfg.FlushThreshold,
		)

		log.Printf("Created writer for %s -> %s (%d columns)",
			schemaPath, meta.TableName, len(meta.Columns))
	}

	// Create error writer with higher threshold for error volume
	if cfg.IncludeErrors {
		router.errorWriter = NewTableWriter(
			"parser_error",
			parserErrorColumns,
			cfg.ErrorFlushThreshold,
		)
		log.Printf("Created error writer for parser_error (%d columns)", len(parserErrorColumns))
	} else {
		log.Printf("Error writing disabled (include_errors=false)")
	}

	return router
}

// Start launches all writer goroutines.
// Must be called before RouteBatch/RouteRecord.
func (router *Router) Start(ctx context.Context) {
	for _, writer := range router.writers {
		writer.Start(ctx, router.sink)
	}
	if router.errorWriter != nil {
		router.errorWriter.Start(ctx, router.sink)
	}
}

// RouteRecord serializes a record, releases it to pool, and sends rows to writer.
// This is the release point for valid records in the normal flow.
// Records without writers (e.g., HEADER, TRAILER) are silently skipped.
func (router *Router) RouteRecord(ctx context.Context, record *parser.ParsedRecord) error {
	writer, ok := router.writers[record.Schema.Path]
	if !ok {
		// No writer for this schema (e.g., header/trailer) - skip silently
		return nil
	}

	conv, ok := router.serializers[record.Schema.Path]
	if !ok {
		return fmt.Errorf("no serializer for schema: %s", record.Schema.Path)
	}

	// Serialize ParsedRecord to []any rows
	rows := conv(record, router.datafileID)

	// Release record back to pool - it's no longer needed after serialization
	record.Schema.ReleaseRecord(record)

	// Send serialized rows to writer
	for _, row := range rows {
		if err := writer.SendRow(ctx, row); err != nil {
			return err
		}
	}

	return nil
}

// RouteBatch routes all records in a batch to appropriate writers.
func (router *Router) RouteBatch(ctx context.Context, batch *parser.ParsedBatch) error {
	for _, group := range batch.Groups {
		for _, record := range group.Records {
			if err := router.RouteRecord(ctx, record); err != nil {
				return err
			}
		}
	}
	return nil
}

// RouteErrorRow sends a pre-serialized error row to the error writer.
// Errors are serialized at call site (in result_router) while record is available.
func (router *Router) RouteErrorRow(ctx context.Context, row []any) error {
	if router.errorWriter == nil {
		return nil
	}
	return router.errorWriter.SendRow(ctx, row)
}

// RouteErrorRows sends multiple pre-serialized error rows to the error writer.
// More efficient than calling RouteErrorRow in a loop — single error check
// and batched channel sends.
func (router *Router) RouteErrorRows(ctx context.Context, rows [][]any) error {
	if router.errorWriter == nil || len(rows) == 0 {
		return nil
	}
	return router.errorWriter.SendRows(ctx, rows)
}

// SerializeRecord serializes a record to database rows and extracts the UUID.
// Does NOT release the record or send rows - caller handles that.
// Returns the serialized rows, the record's UUID, and any error.
// The UUID is extracted from the serialized row at position len(row)-3 (third from end).
func (router *Router) SerializeRecord(record *parser.ParsedRecord) ([][]any, *pgtype.UUID, error) {
	conv, ok := router.serializers[record.Schema.Path]
	if !ok {
		return nil, nil, fmt.Errorf("no serializer for schema: %s", record.Schema.Path)
	}

	rows := conv(record, router.datafileID)
	if len(rows) == 0 {
		return rows, nil, nil
	}

	// Extract UUID from first row at position len(row)-3
	// All serializers place ID, DatafileID, LineNumber at the end
	firstRow := rows[0]
	uuidIdx := len(firstRow) - 3
	if uuidIdx >= 0 {
		if uuid, ok := firstRow[uuidIdx].(pgtype.UUID); ok {
			return rows, &uuid, nil
		}
	}

	return rows, nil, nil
}

// SendRecordRowsByPath sends pre-serialized record rows to the writer for the given schema path.
// Used in conjunction with SerializeRecord for the error-linking flow.
func (router *Router) SendRecordRowsByPath(ctx context.Context, schemaPath string, rows [][]any) error {
	writer, ok := router.writers[schemaPath]
	if !ok {
		// No writer for this schema (e.g., header/trailer) - skip silently
		return nil
	}

	for _, row := range rows {
		if err := writer.SendRow(ctx, row); err != nil {
			return err
		}
	}
	return nil
}

// HasWriter returns true if there's a writer for this schema path.
func (router *Router) HasWriter(schemaPath string) bool {
	_, ok := router.writers[schemaPath]
	return ok
}

// GetContentTypeID returns the Django content type ID for a schema path.
// Returns nil if the schema has no content type (e.g., not loaded from DB).
func (router *Router) GetContentTypeID(schemaPath string) *int32 {
	return router.contentTypeIDs[schemaPath]
}

// Stop closes all channels and waits for goroutines to finish.
// Returns combined errors from all writers.
func (router *Router) Stop() error {
	var errs []error
	var wg sync.WaitGroup
	var errMu sync.Mutex

	// Stop all writers in parallel
	for name, writer := range router.writers {
		wg.Add(1)
		go func(name string, writer *TableWriter) {
			defer wg.Done()
			if err := writer.Stop(); err != nil {
				errMu.Lock()
				errs = append(errs, fmt.Errorf("%s: %w", name, err))
				errMu.Unlock()
			}
		}(name, writer)
	}
	wg.Wait()

	if router.errorWriter != nil {
		if err := router.errorWriter.Stop(); err != nil {
			errs = append(errs, fmt.Errorf("error_writer: %w", err))
		}
	}

	if len(errs) > 0 {
		return errors.Join(errs...)
	}
	return nil
}

// Abort stops all per-run writers without flushing buffered rows.
func (router *Router) Abort() error {
	var errs []error
	var wg sync.WaitGroup
	var errMu sync.Mutex

	for name, writer := range router.writers {
		wg.Add(1)
		go func(name string, writer *TableWriter) {
			defer wg.Done()
			if err := writer.Abort(); err != nil {
				errMu.Lock()
				errs = append(errs, fmt.Errorf("%s: %w", name, err))
				errMu.Unlock()
			}
		}(name, writer)
	}
	wg.Wait()

	if router.errorWriter != nil {
		if err := router.errorWriter.Abort(); err != nil {
			errs = append(errs, fmt.Errorf("error_writer: %w", err))
		}
	}

	if len(errs) > 0 {
		return errors.Join(errs...)
	}
	return nil
}

// TableNames returns the database table names for all record writers.
// Used to scope rollback operations to only the tables relevant to this file.
func (router *Router) TableNames() []string {
	names := make([]string, 0, len(router.writers))
	for _, w := range router.writers {
		names = append(names, w.tableName)
	}
	return names
}

// Stats returns totals from all writers.
func (router *Router) Stats() (records map[string]int64, errorCount int64) {
	result := make(map[string]int64)
	for path, writer := range router.writers {
		result[path] = writer.TotalWritten()
	}
	if router.errorWriter != nil {
		errorCount = router.errorWriter.TotalWritten()
	}
	return result, errorCount
}
