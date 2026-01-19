package validation

import (
	"go-parser/internal/decoder"
	"go-parser/internal/parser"
	"go-parser/internal/schema"
)

// FieldValue returns the value of the current field being validated (Cat 2).
// Returns nil if FieldIndex is out of range or Record is nil.
func (ctx *ValidationContext) FieldValue() any {
	if ctx.Record == nil || ctx.FieldIndex < 0 || ctx.FieldIndex >= len(ctx.Record.Fields) {
		return nil
	}
	return ctx.Record.Fields[ctx.FieldIndex]
}

// FieldDef returns the field definition for the current field (Cat 2).
// Returns nil if Schema is nil or FieldIndex is invalid.
// TODO: revisit this. Im still not sure we need access to field def since field should have context.
func (ctx *ValidationContext) FieldDef() *schema.FieldDef {
	if ctx.Schema == nil || ctx.FieldIndex < 0 {
		return nil
	}

	// Walk through shared fields first
	sharedFields := ctx.Schema.Shared
	if ctx.FieldIndex < len(sharedFields) {
		return &sharedFields[ctx.FieldIndex]
	}

	// Then check segment fields if record has a segment
	if ctx.Record != nil && ctx.Schema.NumSegments() > 0 {
		segIdx := ctx.Record.SegmentIndex
		if segIdx >= 0 && segIdx < len(ctx.Schema.Segments) {
			segFields := ctx.Schema.Segments[segIdx].Fields
			adjustedIdx := ctx.FieldIndex - len(sharedFields)
			if adjustedIdx >= 0 && adjustedIdx < len(segFields) {
				return &segFields[adjustedIdx]
			}
		}
	}

	return nil
}

// GetField returns a field value by name from the current record.
// Returns nil if the field doesn't exist or Record is nil.
func (ctx *ValidationContext) GetField(name string) any {
	if ctx.Record == nil {
		return nil
	}
	return ctx.Record.Get(name)
}

// GetFieldIndex returns the index for a field name in the current schema.
// Returns -1 if the field doesn't exist or Schema is nil.
func (ctx *ValidationContext) GetFieldIndex(name string) int {
	if ctx.Schema == nil {
		return -1
	}
	idx, ok := ctx.Schema.FieldIndex[name]
	if !ok {
		return -1
	}
	return idx
}

// GetString returns a field value as a string.
// Returns empty string if field doesn't exist or isn't a string.
func (ctx *ValidationContext) GetString(name string) string {
	if ctx.Record == nil {
		return ""
	}
	return ctx.Record.GetString(name)
}

// GetInt returns a field value as an integer.
// Returns 0 if field doesn't exist or isn't an integer.
func (ctx *ValidationContext) GetInt(name string) int {
	if ctx.Record == nil {
		return 0
	}
	return ctx.Record.GetInt(name)
}

// RawRowData returns the raw row data for Cat 1 validators.
// Returns empty string if Row is nil or not a PositionalRow.
func (ctx *ValidationContext) RawRowData() string {
	if ctx.Row == nil {
		return ""
	}
	if pr, ok := ctx.Row.(*decoder.PositionalRow); ok {
		return pr.Data()
	}
	return ""
}

// RawRowSlice returns a slice of the raw row data (Cat 1).
// Uses Python-style slice semantics (start inclusive, end exclusive).
func (ctx *ValidationContext) RawRowSlice(start, end int) string {
	if ctx.Row == nil {
		return ""
	}
	if pr, ok := ctx.Row.(*decoder.PositionalRow); ok {
		return pr.Slice(start, end)
	}
	return ""
}

// RecordType returns the record type from the schema or row.
func (ctx *ValidationContext) RecordType() string {
	if ctx.Schema != nil {
		return ctx.Schema.RecordType
	}
	if ctx.Row != nil {
		return ctx.Row.RecordType()
	}
	return ""
}

// LineNumber returns the line number of the current record or row.
func (ctx *ValidationContext) LineNumber() int {
	if ctx.Record != nil {
		return ctx.Record.LineNumber
	}
	if ctx.Row != nil {
		return ctx.Row.LineNum()
	}
	return 0
}

// Reset clears the context for pool reuse.
// File-level fields (DatafileID, ParseCtx) are NOT cleared as they're set once per file.
func (ctx *ValidationContext) Reset() {
	ctx.Record = nil
	ctx.Schema = nil
	ctx.Row = nil
	ctx.FieldIndex = -1
	ctx.Group = nil
	ctx.Category = 0
}

// SetRecord sets the record-level context for Cat 1, 2, 3 validation.
func (ctx *ValidationContext) SetRecord(record *parser.ParsedRecord, compiledSchema *schema.CompiledSchema) {
	ctx.Record = record
	ctx.Schema = compiledSchema
	ctx.FieldIndex = -1
}

// SetRow sets the raw row for Cat 1 validation.
func (ctx *ValidationContext) SetRow(row decoder.Row, compiledSchema *schema.CompiledSchema) {
	ctx.Row = row
	ctx.Schema = compiledSchema
}

// SetField sets the field index for Cat 2 validation.
func (ctx *ValidationContext) SetField(fieldIndex int) {
	ctx.FieldIndex = fieldIndex
}

// SetFieldByName sets the field index by name for Cat 2 validation.
// Returns false if the field name doesn't exist.
func (ctx *ValidationContext) SetFieldByName(name string) bool {
	idx := ctx.GetFieldIndex(name)
	if idx < 0 {
		return false
	}
	ctx.FieldIndex = idx
	return true
}

// Clone creates a shallow copy of the context.
// Used when a validator needs to temporarily modify field context.
func (ctx *ValidationContext) Clone() *ValidationContext {
	return &ValidationContext{
		DatafileID: ctx.DatafileID,
		ParseCtx:   ctx.ParseCtx,
		Record:     ctx.Record,
		Schema:     ctx.Schema,
		Row:        ctx.Row,
		FieldIndex: ctx.FieldIndex,
		Group:      ctx.Group,
		Category:   ctx.Category,
	}
}

// WithField returns a copy of the context with a different field index.
// Useful for cross-field validators that need to check multiple fields.
func (ctx *ValidationContext) WithField(fieldIndex int) *ValidationContext {
	clone := ctx.Clone()
	clone.FieldIndex = fieldIndex
	return clone
}

// WithFieldName returns a copy of the context with a field by name.
// Returns nil if the field name doesn't exist.
func (ctx *ValidationContext) WithFieldName(name string) *ValidationContext {
	idx := ctx.GetFieldIndex(name)
	if idx < 0 {
		return nil
	}
	return ctx.WithField(idx)
}
