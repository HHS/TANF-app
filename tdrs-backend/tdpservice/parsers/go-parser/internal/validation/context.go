package validation

import (
	"go-parser/internal/parser"
	"go-parser/internal/schema"
)

// FieldValue returns the value of the current field being validated (Cat 2).
// Returns nil if FieldIndex is out of range or Record is nil.
func (ctx *ValidationContext) FieldValue() any {
	if ctx.Record == nil || ctx.FieldName == "" {
		return nil
	}
	return ctx.Record.Fields[ctx.GetFieldIndex(ctx.FieldName)]
}

// FieldDef returns the field definition for the current field (Cat 2).
// Returns nil if Schema is nil or FieldIndex is invalid.
// TODO: revisit this. Im still not sure we need access to field def since field should have context.
func (ctx *ValidationContext) FieldDef() *schema.FieldDef {
	if ctx.Record == nil || ctx.FieldName == "" {
		return nil
	}

	// Check if field is a shared field first
	fieldDef, ok := ctx.Record.Schema.SharedFieldsByName[ctx.FieldName]
	if ok {
		return fieldDef
	} else {
		// If not a shared field, check if it's a segment field
		// TODO: it might be better to create indexes into the segment field defs
		segmentDef := ctx.Record.Schema.Segments[ctx.SegmentIndex]
		for _, field := range segmentDef.Fields {
			if field.Name == ctx.FieldName {
				return &field
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
	if ctx.Record == nil {
		return -1
	}
	idx, ok := ctx.Record.Schema.FieldIndex[name]
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

// RecordType returns the record type from the schema or row.
func (ctx *ValidationContext) RecordType() string {
	if ctx.Record != nil {
		return ctx.Record.Schema.RecordType
	}
	return "Unknown"
}

// LineNumber returns the line number of the current record or row.
func (ctx *ValidationContext) LineNumber() int {
	if ctx.Record != nil {
		return ctx.Record.LineNumber
	}
	return -1
}

// Reset clears the context for pool reuse.
// File-level fields (DatafileID, ParseCtx) are NOT cleared as they're set once per file.
func (ctx *ValidationContext) Reset() {
	ctx.Record = nil
	ctx.SegmentIndex = -1
	ctx.FieldName = ""
	ctx.Group = nil
	ctx.Category = 0
}

// SetRecord sets the record-level context for Cat 1, 2, 3 validation.
func (ctx *ValidationContext) SetRecord(record *parser.ParsedRecord, compiledSchema *schema.CompiledSchema) {
	ctx.Record = record
}

// TODO: I don't think these are needed.
// // Clone creates a shallow copy of the context.
// // Used when a validator needs to temporarily modify field context.
// func (ctx *ValidationContext) Clone() *ValidationContext {
// 	return &ValidationContext{
// 		Record:     ctx.Record,
// 		Group:      ctx.Group,
// 		Category:   ctx.Category,
// 	}
// }

// // WithField returns a copy of the context with a different field index.
// // Useful for cross-field validators that need to check multiple fields.
// func (ctx *ValidationContext) WithField(fieldIndex int) *ValidationContext {
// 	clone := ctx.Clone()
// 	clone.FieldIndex = fieldIndex
// 	return clone
// }

// // WithFieldName returns a copy of the context with a field by name.
// // Returns nil if the field name doesn't exist.
// func (ctx *ValidationContext) WithFieldName(name string) *ValidationContext {
// 	idx := ctx.GetFieldIndex(name)
// 	if idx < 0 {
// 		return nil
// 	}
// 	return ctx.WithField(idx)
// }
