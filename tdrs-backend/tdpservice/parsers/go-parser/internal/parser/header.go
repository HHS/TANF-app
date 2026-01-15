package parser

import (
	"fmt"

	"go-parser/internal/decoder"
	"go-parser/internal/filespec"
	"go-parser/internal/schema"
)

// HeaderSchemaPath is the registry path for the header schema.
const HeaderSchemaPath = "common/header"

// ParseHeader parses a header row and returns a ParseContext with the full parsed record.
// Returns nil if the row is nil (e.g., for columnar files that don't have headers).
// The header is parsed using the same logic as any other record type.
func ParseHeader(row decoder.Row, headerSchema *schema.CompiledSchema) (*schema.ParseContext, error) {
	if row == nil {
		return nil, nil
	}

	// Verify this is actually a HEADER record
	if row.RecordType() != "HEADER" {
		return nil, fmt.Errorf("expected HEADER record, got %s", row.RecordType())
	}

	// Parse the header using the same approach as worker.parseRow
	record, err := ParseRecord(row, headerSchema)
	if err != nil {
		return nil, fmt.Errorf("parsing header: %w", err)
	}

	// Build the ParseContext with the full record and convenience fields
	ctx := &schema.ParseContext{
		Header: record,
	}

	// Extract convenience fields from parsed record using accessor methods
	if year := record.GetInt("year"); year != 0 {
		ctx.Year = year
	}

	if quarter := record.GetString("quarter"); quarter != "" {
		ctx.Quarter = quarter
	}

	if encryption := record.GetString("encryption"); encryption != "" {
		ctx.IsEncrypted = encryption == "E"
	}

	return ctx, nil
}

// ParseRecord parses a single row into a ParsedRecord using the given schema.
// This is the same logic used by the worker pool for parsing data records.
// Note: The returned record is acquired from the schema's object pool.
// For header records (which are kept for the session), DO NOT release them.
func ParseRecord(row decoder.Row, sch *schema.CompiledSchema) (*schema.ParsedRecord, error) {
	// Get the appropriate extractor based on format
	// Headers are always positional, but this keeps the pattern consistent
	extractor := GetExtractor(filespec.FormatPositional)

	// Parse shared fields into a temporary cache
	sharedCache := make(MapFieldGetter, len(sch.Shared))
	for i := range sch.Shared {
		field := &sch.Shared[i]
		value, err := extractor.Extract(row, field, nil, sharedCache)
		if err != nil {
			continue
		}
		if value != nil {
			sharedCache[field.Name] = value
		}
	}

	// Acquire record from pool (header records are kept, not released)
	record := sch.AcquireRecord()
	record.LineNumber = row.LineNum()
	record.SegmentIndex = 0

	// Copy shared fields into record
	for name, value := range sharedCache {
		record.Set(name, value)
	}

	// Parse segment fields (header has only one segment with no shared fields)
	if len(sch.Segments) == 0 {
		return record, nil
	}

	// Parse the first segment fields directly into record
	segment := sch.Segments[0]
	for i := range segment.Fields {
		field := &segment.Fields[i]
		value, err := extractor.Extract(row, field, nil, record)
		if err != nil {
			continue
		}
		if value != nil {
			record.Set(field.Name, value)
		}
	}

	return record, nil
}
