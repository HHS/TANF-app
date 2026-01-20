package filespec

import "go-parser/internal/config/validation"

// Format represents the file format type.
// This determines how fields are extracted from row data.
type Format string

const (
	// FormatPositional is for fixed-width text files where fields are at specific byte positions.
	// Used by TANF, SSP, and Tribal TANF programs.
	FormatPositional Format = "positional"

	// FormatColumnar is for CSV or XLSX files where fields are in specific columns.
	// Used by FRA program.
	FormatColumnar Format = "columnar"
)

// FileSpec defines the structure and processing rules for a specific (program, section) file type.
type FileSpec struct {
	// Program is the assistance program: TANF, SSP, TRIBAL, or FRA
	Program string `yaml:"program"`

	// Section is the section number (1-4 for most programs, 1 for FRA)
	Section int `yaml:"section"`

	// Description is a human-readable description of the file type
	Description string `yaml:"description"`

	// Format specifies whether this is a positional or columnar file
	Format Format `yaml:"format"`

	// Schemas lists the schema names that can appear in this file type.
	// These correspond to schema files in the schemas/ directory.
	Schemas []string `yaml:"schemas"`

	// RecordTypeDetection configures how to determine the schema for each row
	RecordTypeDetection RecordTypeDetection `yaml:"record_type_detection"`

	// Accumulator configures how records are collected and grouped for processing
	Accumulator AccumulatorConfig `yaml:"accumulator"`

	// Validation orchestrator configures the validation category types, execution order, and short-circuit rules
	ValidationOrchestrator validation.OrchestratorDef `yaml:"validation_orchestrator"`

	// Category4 configures the category 4 validators associated with this file type
	Category4 []validation.ValidatorDef `yaml:"category4"`
}

// RecordTypeDetection configures how to determine which schema applies to a row.
type RecordTypeDetection struct {
	// Method is the detection method: "prefix", "column", or "fixed"
	Method string `yaml:"method"`

	// Prefixes maps line prefixes to schema names (for positional files)
	// Only used when Method is "prefix"
	Prefixes []PrefixMapping `yaml:"prefixes,omitempty"`

	// Column is the column index containing the record type (for columnar files)
	// Only used when Method is "column"
	Column int `yaml:"column,omitempty"`

	// ColumnHeader is the column header name containing the record type
	// Alternative to Column - used when columns might be reordered
	ColumnHeader string `yaml:"column_header,omitempty"`

	// Schema is the fixed schema name when all rows are the same type
	// Only used when Method is "fixed"
	Schema string `yaml:"schema,omitempty"`
}

// PrefixMapping maps a line prefix to a schema name.
type PrefixMapping struct {
	// Prefix is the string that appears at the start of the line
	Prefix string `yaml:"prefix"`

	// Schema is the name of the schema to use for lines with this prefix
	Schema string `yaml:"schema"`
}

// AccumulatorConfig configures how records are collected and grouped for processing.
//
// The accumulator uses two independent, inclusive settings:
//   - KeyFields: Groups records by composite key (creates RecordGroups)
//   - BatchSize: Batches N groups together (creates Batches)
//
// The four modes are:
//
//	| KeyFields | BatchSize | Behavior                                      |
//	|-----------|-----------|-----------------------------------------------|
//	| nil       | 0         | Per-record: each record emitted individually  |
//	| nil       | 100       | Batches of 100 individual records             |
//	| set       | 0         | Group by key, emit each group individually    |
//	| set       | 10        | Group by key, then batch 10 groups together   |
type AccumulatorConfig struct {
	// KeyFields defines how to extract grouping keys from raw data.
	// If nil or empty, each record is its own group (no case-based grouping).
	// If set, records with the same composite key are grouped together.
	KeyFields *KeyFieldsConfig `yaml:"key_fields,omitempty"`

	// BatchSize is the number of groups to batch together before dispatch.
	// If 0, each group is dispatched individually (one batch per group).
	// If > 0, groups are collected until batch_size is reached.
	BatchSize int `yaml:"batch_size,omitempty"`

	// GroupedSchemas lists which schemas participate in key-based grouping.
	// Schemas not in this list (e.g., HEADER, TRAILER) are processed individually.
	GroupedSchemas []string `yaml:"grouped_schemas,omitempty"`
}

// HasKeyFields returns true if key-based grouping is configured.
func (c *AccumulatorConfig) HasKeyFields() bool {
	return c.KeyFields != nil && (c.KeyFields.RptMonthYear.End > 0 || c.KeyFields.CaseNumber.End > 0)
}

// KeyFieldsConfig defines byte positions for extracting the grouping key.
type KeyFieldsConfig struct {
	// RptMonthYear is the position of the reporting month/year field
	RptMonthYear PositionDef `yaml:"rpt_month_year"`

	// CaseNumber is the position of the case number field
	CaseNumber PositionDef `yaml:"case_number"`
}

// PositionDef defines a byte range within a line.
type PositionDef struct {
	// Start is the starting byte position (0-indexed, inclusive)
	Start int `yaml:"start"`

	// End is the ending byte position (0-indexed, exclusive)
	End int `yaml:"end"`
}
