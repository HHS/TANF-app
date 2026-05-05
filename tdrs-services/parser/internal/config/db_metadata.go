package config

import (
	"strings"

	"go-parser/internal/config/schema"
)

const (
	// DefaultTablePrefix keeps Go parser output isolated from Django/Python parser tables.
	DefaultTablePrefix = "shadow_"

	ParserErrorTable       = "parser_error"
	DataFileTable          = "data_files_datafile"
	DataFileSummaryTable   = "parsers_datafilesummary"
	searchIndexTablePrefix = "search_indexes_"
)

// DbSchemaMetadata holds database information derived from a schema.
type DbSchemaMetadata struct {
	TableName     string   // PostgreSQL table name (e.g., "search_indexes_tanf_t1")
	Columns       []string // Ordered column names for COPY (derived from schema fields)
	RecordType    string   // e.g., "T1", "M2"
	ContentTypeID *int32   // Django content type ID for this model (nil if not loaded)
}

// buildDbSchemaMetadata derives database metadata from a compiled schema.
// Column names are extracted from shared fields + first segment fields.
// All segments have the same field names (just different byte positions),
// so we only need fields from the first segment for the database schema.
func buildDbSchemaMetadata(compiledSchema *schema.CompiledSchema, tablePrefix string) *DbSchemaMetadata {
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
		TableName:  ApplyTablePrefix(recordSchemaToTable(compiledSchema.Path), tablePrefix),
		Columns:    columns,
		RecordType: compiledSchema.RecordType,
	}
}

// ApplyTablePrefix prefixes Go parser-owned output tables.
func ApplyTablePrefix(tableName, tablePrefix string) string {
	if tablePrefix == "" || strings.HasPrefix(tableName, tablePrefix) {
		return tableName
	}
	return tablePrefix + tableName
}

// ParserErrorTableName returns the configured Go parser error output table.
func ParserErrorTableName(tablePrefix string) string {
	return ApplyTablePrefix(ParserErrorTable, tablePrefix)
}

// DataFileTableName returns the configured Go parser datafile metadata table.
func DataFileTableName(tablePrefix string) string {
	return ApplyTablePrefix(DataFileTable, tablePrefix)
}

// DataFileSummaryTableName returns the configured Go parser summary output table.
func DataFileSummaryTableName(tablePrefix string) string {
	return ApplyTablePrefix(DataFileSummaryTable, tablePrefix)
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
		r.metadata[path] = buildDbSchemaMetadata(compiledSchema, r.tablePrefix)
	}
}

// GetSchemaMetadata returns database metadata for a schema path.
func (r *Registry) GetSchemaMetadata(schemaPath string) *DbSchemaMetadata {
	return r.metadata[schemaPath]
}

// schemaPathToModelName converts a schema path to its Django model name.
// The model name is the table name without the "search_indexes_" prefix.
// Examples:
//
//	"tanf/t1"    -> "tanf_t1"
//	"ssp/m2"     -> "ssp_m2"
//	"tribal/t1"  -> "tribal_tanf_t1"
//	"fra/te1"    -> "tanf_exiter1"
func schemaPathToModelName(schemaPath string) string {
	tableName := recordSchemaToTable(schemaPath)
	return strings.TrimPrefix(tableName, searchIndexTablePrefix)
}

// SetContentTypeIDs sets content type IDs for all metadata entries.
// contentTypes is a map from model name (e.g., "tanf_t1") to content type ID.
// This should be called after buildAllMetadata and after querying django_content_type.
func (r *Registry) SetContentTypeIDs(contentTypes map[string]int32) {
	for path, meta := range r.metadata {
		modelName := schemaPathToModelName(path)
		if r.tablePrefix != "" && strings.HasPrefix(meta.TableName, r.tablePrefix) {
			if id, ok := contentTypes["shadow"+modelName]; ok {
				meta.ContentTypeID = &id
				continue
			}
		}
		if id, ok := contentTypes[modelName]; ok {
			meta.ContentTypeID = &id
		}
	}
}
