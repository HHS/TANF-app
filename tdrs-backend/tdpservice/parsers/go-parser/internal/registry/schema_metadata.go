package registry

import (
	"strings"

	"go-parser/internal/schema"
)

// SchemaMetadata holds database information derived from a schema.
type SchemaMetadata struct {
	TableName  string   // PostgreSQL table name (e.g., "search_indexes_tanf_t1")
	Columns    []string // Ordered column names for COPY (derived from schema fields)
	RecordType string   // e.g., "T1", "M2"
}

// buildSchemaMetadata derives database metadata from a compiled schema.
// Column names are extracted from shared fields + first segment fields.
// All segments have the same field names (just different byte positions),
// so we only need fields from the first segment for the database schema.
func buildSchemaMetadata(schemaPath string, compiled *schema.CompiledSchema) *SchemaMetadata {
	// Calculate capacity: shared + first segment fields + 3 standard columns
	capacity := len(compiled.Shared) + 3
	if len(compiled.Segments) > 0 {
		capacity += len(compiled.Segments[0].Fields)
	}

	columns := make([]string, 0, capacity)

	// Add shared field names
	for _, field := range compiled.Shared {
		columns = append(columns, field.Name)
	}

	// Add segment field names (from first segment - all segments have same names)
	if len(compiled.Segments) > 0 {
		for _, field := range compiled.Segments[0].Fields {
			columns = append(columns, field.Name)
		}
	}

	// Add standard columns that appear in all record tables
	columns = append(columns, "id", "datafile_id", "line_number")

	return &SchemaMetadata{
		TableName:  schemaPathToTableName(schemaPath),
		Columns:    columns,
		RecordType: compiled.RecordType,
	}
}

// schemaPathToTableName converts a schema path to its database table name.
// Examples:
//
//	"tanf/t1"    -> "search_indexes_tanf_t1"
//	"ssp/m2"     -> "search_indexes_ssp_m2"
//	"tribal/t1"  -> "search_indexes_tribal_tanf_t1"
func schemaPathToTableName(schemaPath string) string {
	// Convert path separators and normalize
	normalized := strings.ReplaceAll(schemaPath, "/", "_")
	return "search_indexes_" + normalized
}

// Registry builds metadata for all schemas during Load()
func (r *Registry) buildAllMetadata() {
	r.metadata = make(map[string]*SchemaMetadata)

	for path, compiled := range r.schemas {
		// Skip header/trailer - they don't have database tables
		if compiled.RecordType == "HEADER" || compiled.RecordType == "TRAILER" {
			continue
		}
		r.metadata[path] = buildSchemaMetadata(path, compiled)
	}
}

// GetSchemaMetadata returns database metadata for a schema path.
func (r *Registry) GetSchemaMetadata(schemaPath string) *SchemaMetadata {
	return r.metadata[schemaPath]
}
