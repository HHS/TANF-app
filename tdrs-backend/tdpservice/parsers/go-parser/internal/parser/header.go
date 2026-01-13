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

	// Extract convenience fields from parsed record
	if year, ok := record.Fields["year"].(int); ok {
		ctx.Year = year
	}

	if quarter, ok := record.Fields["quarter"].(string); ok {
		ctx.Quarter = quarter
	}

	if encryption, ok := record.Fields["encryption"].(string); ok {
		ctx.IsEncrypted = encryption == "E"
	}

	return ctx, nil
}

// ParseRecord parses a single row into a ParsedRecord using the given schema.
// This is the same logic used by the worker pool for parsing data records.
func ParseRecord(row decoder.Row, sch *schema.CompiledSchema) (*schema.ParsedRecord, error) {
	// Get the appropriate extractor based on format
	// Headers are always positional, but this keeps the pattern consistent
	extractor := GetExtractor(filespec.FormatPositional)

	// Parse shared fields first
	sharedFields := make(map[string]any, len(sch.Shared))
	for i := range sch.Shared {
		field := &sch.Shared[i]
		value, err := extractor.Extract(row, field, nil)
		if err != nil {
			continue
		}
		if value != nil {
			sharedFields[field.Name] = value
		}
	}

	// Parse segment fields (header has only one segment with no shared fields)
	if len(sch.Segments) == 0 {
		return &schema.ParsedRecord{
			Schema:       sch,
			LineNumber:   row.LineNum(),
			SegmentIndex: 0,
			Fields:       sharedFields,
		}, nil
	}

	// Parse the first segment
	segment := sch.Segments[0]
	fields := make(map[string]any, len(sharedFields)+len(segment.Fields))

	// Copy shared fields
	for k, v := range sharedFields {
		fields[k] = v
	}

	// Parse segment fields
	for i := range segment.Fields {
		field := &segment.Fields[i]
		value, err := extractor.Extract(row, field, nil)
		if err != nil {
			continue
		}
		if value != nil {
			fields[field.Name] = value
		}
	}

	return &schema.ParsedRecord{
		Schema:       sch,
		LineNumber:   row.LineNum(),
		SegmentIndex: 0,
		Fields:       fields,
	}, nil
}
