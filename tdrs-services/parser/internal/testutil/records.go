package testutil

import (
	"go-parser/internal/config/schema"
	"go-parser/internal/parser"
)

// NewTestSchema creates a minimal CompiledSchema for testing.
// All fields are created as shared fields with type "string" and Required=false.
// To mark fields required, set schema.Shared[i].Required = true before creating records.
func NewTestSchema(recordType string, fieldNames ...string) *schema.CompiledSchema {
	sdef := &schema.SchemaDef{
		RecordType: recordType,
		Shared:     make([]schema.FieldDef, len(fieldNames)),
	}
	for i, name := range fieldNames {
		sdef.Shared[i] = schema.FieldDef{Name: name, Type: "string"}
	}
	return sdef.Compile()
}

// NewTestRecord creates a ParsedRecord with field values for testing.
// DecodedSize defaults to 156. Override with rec.DecodedSize = N after creation.
func NewTestRecord(s *schema.CompiledSchema, lineNum int, values map[string]any) *parser.ParsedRecord {
	rec := &parser.ParsedRecord{
		Schema:      s,
		LineNumber:  lineNum,
		DecodedSize: 156,
		Fields:      make([]parser.ParsedField, s.FieldCount),
	}
	// Set Def pointers from shared fields
	for i := range s.Shared {
		rec.Fields[i].Def = &s.Shared[i]
	}
	// Set values
	for name, val := range values {
		rec.Set(name, val)
	}
	return rec
}

// NewTestGroup creates a ParsedGroup with default key fields for testing.
func NewTestGroup(records ...*parser.ParsedRecord) *parser.ParsedGroup {
	return &parser.ParsedGroup{
		Key:     "202401|12345",
		Records: records,
	}
}
