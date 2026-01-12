package registry

import (
	"fmt"
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
// Column names are extracted from the YAML schema fields - no duplication needed.
func buildSchemaMetadata(schemaPath string, compiled *schema.CompiledSchema) *SchemaMetadata {
	// Standard columns that appear in all record tables
	columns := make([]string, 0, len(compiled.Fields)+3)

	// Add columns from schema fields in order
	// Schema field names (e.g., "RPT_MONTH_YEAR") map directly to DB columns
	for _, field := range compiled.Fields {
		// PostgreSQL quoted identifiers for uppercase field names
		columns = append(columns, fmt.Sprintf(`"%s"`, field.Name))
	}

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
