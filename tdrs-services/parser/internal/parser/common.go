package parser

import (
	"fmt"

	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
)

// HeaderSchemaPath is the registry path for the header schema.
const HeaderSchemaPath = "common/header"

// TrailerSchemaPath is the registry path for the trailer schema.
const TrailerSchemaPath = "common/trailer"

// ParseHeader parses a header row and returns a ParseContext with the full parsed record.
// Returns nil if the row is nil (e.g., for columnar files that don't have headers).
// The header is parsed using the same logic as any other record type.
func ParseHeader(row decoder.Row, headerSchema *schema.CompiledSchema) (*ParseContext, error) {
	// Verify this is actually a HEADER record
	if row == nil || row.RecordType() != "HEADER" {
		return nil, fmt.Errorf("Your file does not start with a HEADER.")
	}

	// Parse the header using the same approach as worker.parseRow
	record, err := parseRecord(row, headerSchema)
	if err != nil {
		return nil, fmt.Errorf("Failed to parse header: %w", err)
	}

	// Build the ParseContext with the full record and convenience fields
	ctx := &ParseContext{
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

// ParseTrailer parses a trailer row and returns the parsed record.
// The trailer is parsed with the same single-record path as the header.
func ParseTrailer(row decoder.Row, trailerSchema *schema.CompiledSchema) (*ParsedRecord, error) {
	if row == nil || row.RecordType() != "TRAILER" {
		return nil, fmt.Errorf("Your file does not end with a TRAILER record.")
	}

	record, err := parseRecord(row, trailerSchema)
	if err != nil {
		return nil, fmt.Errorf("Failed to parse trailer: %w", err)
	}

	return record, nil
}

// parseRecord parses a single row into a ParsedRecord using the given schema.
// This is the same logic used by the worker pool for parsing data records.
// Note: The returned record is acquired from the schema's object pool.
// For header records (which are kept for the session), DO NOT release them.
func parseRecord(row decoder.Row, sch *schema.CompiledSchema) (*ParsedRecord, error) {
	// Get the appropriate extractor based on format
	// Headers are always positional, but this keeps the pattern consistent
	extractor := GetExtractor(filespec.FormatPositional)

	// Acquire record from pool (header records are kept, not released)
	record := sch.AcquireRecord().(*ParsedRecord)
	record.LineNumber = row.LineNum()
	record.DecodedSize = row.DecodedLength()
	record.SegmentIndex = 0

	// Parse segment fields (header has only one segment with no shared fields)
	segment := sch.Segments[0]
	for i := range segment.Fields {
		field := &segment.Fields[i]
		value, err := extractor.Extract(row, field, nil, record)
		if err != nil {
			continue
		}
		record.SetField(field, value)
	}

	return record, nil
}
