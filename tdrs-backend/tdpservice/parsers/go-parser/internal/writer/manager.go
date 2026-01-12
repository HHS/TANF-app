package writer

import (
	"context"
	"fmt"
	"log"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/converter"
	"go-parser/internal/filespec"
	"go-parser/internal/registry"
	"go-parser/internal/worker"
)

// RecordWriter pairs a TableWriter with its converter function.
type RecordWriter struct {
	writer    *TableWriter
	converter converter.RowConverter
}

// WriterManager coordinates writes for any file type.
// Writers are created dynamically based on the FileSpec.
type WriterManager struct {
	pool       *pgxpool.Pool
	datafileID int32

	// Writers keyed by schema path (e.g., "tanf/t1", "tribal/t1")
	writers map[string]*RecordWriter

	errorWriter *TableWriter

	// Stats tracking
	totalWritten map[string]int64
	totalErrors  int64
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
		pool:         pool,
		datafileID:   datafileID,
		writers:      make(map[string]*RecordWriter),
		totalWritten: make(map[string]int64),
	}

	// Create a writer for each data record type in the FileSpec
	for _, schemaPath := range spec.Schemas {
		schema := reg.GetSchema(schemaPath)

		// Skip header/trailer - they don't get written to database
		if schema.RecordType == "HEADER" || schema.RecordType == "TRAILER" {
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

		// Key by schema path to support different programs with same record type prefix
		wm.writers[schemaPath] = &RecordWriter{
			writer:    NewTableWriter(meta.TableName, meta.Columns, DefaultFlushThreshold),
			converter: conv,
		}

		log.Printf("Created writer for %s -> %s (%d columns)",
			schemaPath, meta.TableName, len(meta.Columns))
	}

	// Error writer is always the same
	wm.errorWriter = NewTableWriter("parser_error", parserErrorColumns, DefaultFlushThreshold)

	return wm
}

// WriteBatch processes all records from a ParsedBatch.
// Records are converted and routed to the appropriate writer.
func (wm *WriterManager) WriteBatch(ctx context.Context, batch *worker.ParsedBatch) error {
	for _, group := range batch.Groups {
		// Write successful records
		for _, record := range group.Records {
			if err := wm.writeRecord(ctx, record); err != nil {
				return err
			}
		}

		// Write parser errors
		// TODO
		// for _, perr := range group.Errors {
		//     if err := wm.writeError(ctx, perr); err != nil {
		//         return err
		//     }
		// }
	}

	return nil
}

// writeRecord converts and writes a single record.
// Some record types (like T3 with 2 children per line) produce multiple rows.
func (wm *WriterManager) writeRecord(ctx context.Context, record *worker.ParsedRecord) error {
	// Look up writer by schema path (stored in CompiledSchema)
	rw, ok := wm.writers[record.Schema.Path]
	if !ok {
		return fmt.Errorf("no writer for schema: %s", record.Schema.Path)
	}

	// Convert ParsedRecord to row values using the registered converter
	// The converter uses SQLC types internally for type safety
	// Returns [][]any to support multi-row records (e.g., T3 with 2 children)
	rows := rw.converter(record, wm.datafileID)

	// Add each row to buffer; flush if threshold reached
	for _, row := range rows {
		if rw.writer.Add(row) {
			count, err := rw.writer.Flush(ctx, wm.pool)
			if err != nil {
				return err
			}
			wm.totalWritten[rw.writer.TableName()] += count
			log.Printf("Flushed %d %s records", count, record.Schema.RecordType)
		}
	}

	return nil
}

// writeError writes a parser error.
// TODO
// func (wm *WriterManager) writeError(ctx context.Context, perr worker.ParseError) error {
//     row := converter.ToParserErrorRow(perr, wm.datafileID)

//     if wm.errorWriter.Add(row) {
//         count, err := wm.errorWriter.Flush(ctx, wm.pool)
//         if err != nil {
//             return err
//         }
//         wm.totalErrors += count
//         log.Printf("Flushed %d errors", count)
//     }

//     return nil
// }

// FlushAll flushes all writers. Call this at the end of file processing.
func (wm *WriterManager) FlushAll(ctx context.Context) error {
	// Flush all record writers
	for recordType, rw := range wm.writers {
		count, err := rw.writer.Flush(ctx, wm.pool)
		if err != nil {
			return fmt.Errorf("final flush %s: %w", recordType, err)
		}
		wm.totalWritten[rw.writer.TableName()] += count
		if count > 0 {
			log.Printf("Final flush: %d %s records", count, recordType)
		}
	}

	// Flush error writer
	count, err := wm.errorWriter.Flush(ctx, wm.pool)
	if err != nil {
		return fmt.Errorf("final flush errors: %w", err)
	}
	wm.totalErrors += count
	if count > 0 {
		log.Printf("Final flush: %d errors", count)
	}

	return nil
}

// Stats returns the total records written per table.
func (wm *WriterManager) Stats() (records map[string]int64, errors int64) {
	// Return a copy to prevent modification
	result := make(map[string]int64)
	for k, v := range wm.totalWritten {
		result[k] = v
	}
	return result, wm.totalErrors
}

// Pending returns the total number of unflushed records across all writers.
func (wm *WriterManager) Pending() int {
	total := wm.errorWriter.Pending()
	for _, rw := range wm.writers {
		total += rw.writer.Pending()
	}
	return total
}
