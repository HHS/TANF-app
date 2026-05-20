package decoder

import (
	"fmt"
	"sort"
	"strings"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/sentinel"
)

// RecordTypeDetector determines which schema applies to each row.
type RecordTypeDetector struct {
	spec     *filespec.FileSpec
	registry *config.Registry

	// Cached lookup for prefix detection (sorted by prefix length, longest first)
	sortedPrefixes []filespec.PrefixMapping
}

// NewRecordTypeDetector creates a detector for the given file specification.
func NewRecordTypeDetector(spec *filespec.FileSpec, registry *config.Registry) *RecordTypeDetector {
	d := &RecordTypeDetector{
		spec:     spec,
		registry: registry,
	}

	// Sort prefixes by length (longest first) for correct matching
	// This ensures "HEADER" matches before "H" would
	if spec.RecordTypeDetection.Method == "prefix" {
		d.sortedPrefixes = sortPrefixesByLength(spec.RecordTypeDetection.Prefixes)
	}

	return d
}

// Detect determines the schema for a given row.
// Returns the compiled schema or an error if no matching schema is found.
func (d *RecordTypeDetector) Detect(row Row) (*schema.CompiledSchema, error) {
	switch d.spec.RecordTypeDetection.Method {
	case "prefix":
		return d.detectByPrefix(row)
	case "column":
		return d.detectByColumn(row)
	case "fixed":
		return d.detectFixed()
	default:
		return nil, fmt.Errorf("unknown detection method: %s", d.spec.RecordTypeDetection.Method)
	}
}

// detectByPrefix determines schema by looking at line prefix (for positional files).
func (d *RecordTypeDetector) detectByPrefix(row Row) (*schema.CompiledSchema, error) {
	pr, ok := row.(*PositionalRow)
	if !ok {
		return nil, fmt.Errorf("prefix detection requires PositionalRow, got %T", row)
	}

	data := pr.Data()

	// Try each prefix in order (longest first)
	for _, mapping := range d.sortedPrefixes {
		if strings.HasPrefix(data, mapping.Prefix) {
			sch := d.registry.GetSchema(mapping.Schema)
			if sch == nil {
				return nil, fmt.Errorf("schema not found: %s", mapping.Schema)
			}
			return sch, nil
		}
	}

	// No matching prefix found
	preview := data
	if len(preview) > 20 {
		preview = preview[:20] + "..."
	}
	return nil, fmt.Errorf("%w: no matching prefix for line: %q", sentinel.ErrUnknownRecordType, preview)
}

// detectByColumn determines schema by looking at a column value (for columnar files).
func (d *RecordTypeDetector) detectByColumn(row Row) (*schema.CompiledSchema, error) {
	cr, ok := row.(*ColumnarRow)
	if !ok {
		return nil, fmt.Errorf("column detection requires ColumnarRow, got %T", row)
	}

	colIdx := d.spec.RecordTypeDetection.Column
	val := cr.Column(colIdx)
	if val == nil {
		return nil, fmt.Errorf("column %d is empty or missing", colIdx)
	}

	recordType := strings.TrimSpace(fmt.Sprintf("%v", val))

	sch := d.registry.GetSchema(recordType)
	if sch == nil {
		return nil, fmt.Errorf("%w: %s", sentinel.ErrUnknownRecordType, recordType)
	}

	return sch, nil
}

// detectFixed returns the fixed schema configured for this file type.
func (d *RecordTypeDetector) detectFixed() (*schema.CompiledSchema, error) {
	schemaName := d.spec.RecordTypeDetection.Schema
	sch := d.registry.GetSchema(schemaName)
	if sch == nil {
		return nil, fmt.Errorf("fixed schema not found: %s", schemaName)
	}
	return sch, nil
}

// sortPrefixesByLength returns prefixes sorted by length (longest first).
func sortPrefixesByLength(prefixes []filespec.PrefixMapping) []filespec.PrefixMapping {
	// Make a copy to avoid modifying the original
	sorted := make([]filespec.PrefixMapping, len(prefixes))
	copy(sorted, prefixes)

	// Sort by prefix length, longest first
	sort.Slice(sorted, func(i, j int) bool {
		return len(sorted[i].Prefix) > len(sorted[j].Prefix)
	})

	return sorted
}
