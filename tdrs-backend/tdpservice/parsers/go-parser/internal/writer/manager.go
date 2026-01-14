package writer

import (
	"context"
	"errors"
	"fmt"
	"log"
	"sync"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/converter"
	"go-parser/internal/filespec"
	"go-parser/internal/registry"
	"go-parser/internal/schema"
	"go-parser/internal/worker"
)

// WriterManager coordinates writes for any file type.
// Writers are created dynamically based on the FileSpec.
type WriterManager struct {
	pool       *pgxpool.Pool
	datafileID int32

	// Writers keyed by schema path (e.g., "tanf/t1", "tribal/t1")
	// Direct TableWriter reference - no wrapper needed
	writers map[string]*TableWriter

	errorWriter *TableWriter
}

// Error table columns (same for all file types)
var parserErrorColumns = []string{
	"row_number", "column_number", "item_number", "field_name",
	"case_number", "rpt_month_year", "error_message", "error_type",
	"created_at", "fields_json", "content_type_id", "file_id",
	"object_id", "deprecated", "values_json",
}

// NewWriterManager creates a manager based on the FileSpec.
// Writers are created only for the record types in this specific file.
func NewWriterManager(
	pool *pgxpool.Pool,
	datafileID int32,
	spec *filespec.FileSpec,
	reg *registry.Registry,
) *WriterManager {
	wm := &WriterManager{
		pool:       pool,
		datafileID: datafileID,
		writers:    make(map[string]*TableWriter),
	}

	// Create a writer for each data record type in the FileSpec
	for _, schemaPath := range spec.Schemas {
		sch := reg.GetSchema(schemaPath)

		// Skip header/trailer - they don't get written to database
		if sch.RecordType == "HEADER" || sch.RecordType == "TRAILER" {
			continue
		}

		// Get metadata (table name, columns derived from schema)
		meta := reg.GetSchemaMetadata(schemaPath)
		if meta == nil {
			continue
		}

		// Get the converter for this schema path
		// Schema path (e.g., "tanf/t1") distinguishes TANF vs Tribal T1
		conv := converter.GetConverter(schemaPath)
		if conv == nil {
			log.Printf("Warning: no converter for schema %s", schemaPath)
			continue
		}

		// TableWriter now owns the converter - conversion happens in writer goroutine
		wm.writers[schemaPath] = NewTableWriter(
			meta.TableName,
			meta.Columns,
			DefaultFlushThreshold,
			datafileID,
			conv,
		)

		log.Printf("Created writer for %s -> %s (%d columns)",
			schemaPath, meta.TableName, len(meta.Columns))
	}

	// TODO: Create error writer when error handling is implemented
	// wm.errorWriter = NewErrorWriter(...)

	return wm
}

// Start launches all writer goroutines.
// Must be called before WriteBatch/WriteRecord.
func (wm *WriterManager) Start(ctx context.Context) {
	for _, tw := range wm.writers {
		tw.Start(ctx, wm.pool)
	}
	if wm.errorWriter != nil {
		wm.errorWriter.Start(ctx, wm.pool)
	}
}

// WriteRecord routes a record to the appropriate writer's channel.
// No conversion here - writer handles it.
func (wm *WriterManager) WriteRecord(ctx context.Context, record *schema.ParsedRecord) error {
	tw, ok := wm.writers[record.Schema.Path]
	if !ok {
		return fmt.Errorf("no writer for schema: %s", record.Schema.Path)
	}
	return tw.Send(ctx, record) // Send ParsedRecord directly
}

// WriteBatch routes all records in a batch to appropriate writers.
func (wm *WriterManager) WriteBatch(ctx context.Context, batch *worker.ParsedBatch) error {
	for _, group := range batch.Groups {
		for _, record := range group.Records {
			if err := wm.WriteRecord(ctx, record); err != nil {
				return err
			}
		}
	}
	return nil
}

// Stop closes all channels and waits for goroutines to finish.
// Returns combined errors from all writers.
func (wm *WriterManager) Stop() error {
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
func (wm *WriterManager) Stats() (records map[string]int64, errorCount int64) {
	result := make(map[string]int64)
	for path, tw := range wm.writers {
		result[path] = tw.TotalWritten()
	}
	if wm.errorWriter != nil {
		errorCount = wm.errorWriter.TotalWritten()
	}
	return result, errorCount
}
