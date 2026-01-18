package registry

import (
	"strings"

	"go-parser/internal/schema"
)

// DbSchemaMetadata holds database information derived from a schema.
type DbSchemaMetadata struct {
	TableName  string   // PostgreSQL table name (e.g., "search_indexes_tanf_t1")
	Columns    []string // Ordered column names for COPY (derived from schema fields)
	RecordType string   // e.g., "T1", "M2"
}

// buildDbSchemaMetadata derives database metadata from a compiled schema.
// Column names are extracted from shared fields + first segment fields.
// All segments have the same field names (just different byte positions),
// so we only need fields from the first segment for the database schema.
func buildDbSchemaMetadata(compiledSchema *schema.CompiledSchema) *DbSchemaMetadata {
	// Calculate capacity: shared + first segment fields + 3 standard columns
	capacity := len(compiledSchema.Shared) + 3
	if len(compiledSchema.Segments) > 0 {
		capacity += len(compiledSchema.Segments[0].Fields)
	}

	columns := make([]string, 0, capacity)

	// Add shared field names
	for _, field := range compiledSchema.Shared {
		columns = append(columns, field.Name)
	}

	// Add segment field names (from first segment - all segments have same names)
	if len(compiledSchema.Segments) > 0 {
		for _, field := range compiledSchema.Segments[0].Fields {
			columns = append(columns, field.Name)
		}
	}

	// Add standard columns that appear in all record tables
	columns = append(columns, "id", "datafile_id", "line_number")

	return &DbSchemaMetadata{
		TableName:  recordSchemaToTable(compiledSchema.Path),
		Columns:    columns,
		RecordType: compiledSchema.RecordType,
	}
}

// recordSchemaToTable converts a schema path to its database table name.
// Examples:
//
//	"tanf/t1"    -> "search_indexes_tanf_t1"
//	"ssp/m2"     -> "search_indexes_ssp_m2"
//	"tribal/t1"  -> "search_indexes_tribal_tanf_t1"
//	"fra/te1"    -> "search_indexes_tanf_exiter1"
func recordSchemaToTable(schemaPath string) string {
	// Special case mappings for schemas that don't follow the standard pattern
	specialCases := map[string]string{
		"fra/te1": "search_indexes_tanf_exiter1",
	}
	if tableName, ok := specialCases[schemaPath]; ok {
		return tableName
	}

	// Convert path separators and normalize
	normalized := strings.ReplaceAll(schemaPath, "/", "_")
	return "search_indexes_" + normalized
}

// Registry builds metadata for all schemas during Load()
func (r *Registry) buildAllMetadata() {
	r.metadata = make(map[string]*DbSchemaMetadata)

	for path, compiledSchema := range r.schemas {
		// Skip header/trailer - they don't have database tables
		if compiledSchema.RecordType == "HEADER" || compiledSchema.RecordType == "TRAILER" {
			continue
		}
		r.metadata[path] = buildDbSchemaMetadata(compiledSchema)
	}
}

// GetSchemaMetadata returns database metadata for a schema path.
func (r *Registry) GetSchemaMetadata(schemaPath string) *DbSchemaMetadata {
	return r.metadata[schemaPath]
}
