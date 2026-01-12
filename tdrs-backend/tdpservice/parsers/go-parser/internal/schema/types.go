package schema

// FieldDef represents a single field within a record.
type FieldDef struct {
	// Name is the internal field name (used in code and database)
	Name string `yaml:"name"`

	// Item is the item number from the federal specification
	Item string `yaml:"item"`

	// FriendlyName is a human-readable name for error messages
	FriendlyName string `yaml:"friendly_name"`

	// Type is the data type: "string" or "integer"
	Type string `yaml:"type"`

	// Required indicates whether the field must have a non-empty value
	Required bool `yaml:"required"`

	// Transform is an optional transformation to apply (e.g., "zero_pad_3")
	Transform string `yaml:"transform,omitempty"`

	// === Positional Format Fields ===
	// Used when the schema is for a positional (fixed-width) file

	// Start is the starting byte position (0-indexed, inclusive)
	Start int `yaml:"start,omitempty"`

	// End is the ending byte position (0-indexed, exclusive)
	End int `yaml:"end,omitempty"`

	// === Columnar Format Fields ===
	// Used when the schema is for a columnar (CSV/XLSX) file

	// Column is the column index (0-indexed)
	Column int `yaml:"column,omitempty"`

	// ColumnHeader is the expected column header name (optional)
	ColumnHeader string `yaml:"column_header,omitempty"`
}

// SegmentDef defines a segment within a record.
// Each segment represents a repeating group of fields that produces one output row.
type SegmentDef struct {
	// Fields defines all fields in this segment
	Fields []FieldDef `yaml:"fields"`
}

// SchemaDef defines the structure of a single record type.
type SchemaDef struct {
	// RecordType is the identifier (e.g., "T1", "TE1")
	RecordType string `yaml:"record_type"`

	// Program is the program this schema belongs to
	Program string `yaml:"program"`

	// Section is the section number (1, 2, 3, or 4)
	Section int `yaml:"section,omitempty"`

	// Document is the document name for this record type
	Document string `yaml:"document,omitempty"`

	// Format is the file format: "positional" or "columnar"
	Format string `yaml:"format,omitempty"`

	// Description is a human-readable description
	Description string `yaml:"description,omitempty"`

	// Shared contains fields that are common to all segments.
	// These fields are included in every output row.
	Shared []FieldDef `yaml:"shared"`

	// Segments contains the segment definitions.
	// Each segment produces one output row (combined with shared fields).
	Segments []SegmentDef `yaml:"segments"`
}

// CompiledSchema wraps a SchemaDef with precomputed lookup structures.
type CompiledSchema struct {
	*SchemaDef

	// Path is the schema path (e.g., "tanf/t1", "tribal/t1")
	// Set by the registry when loading schemas
	Path string

	// SharedFieldsByName provides O(1) lookup for shared fields by name
	SharedFieldsByName map[string]*FieldDef
}

// Compile creates a CompiledSchema with lookup maps.
func (s *SchemaDef) Compile() *CompiledSchema {
	cs := &CompiledSchema{
		SchemaDef:          s,
		SharedFieldsByName: make(map[string]*FieldDef, len(s.Shared)),
	}

	for i := range s.Shared {
		field := &s.Shared[i]
		cs.SharedFieldsByName[field.Name] = field
	}

	return cs
}

// NumSegments returns the number of segments in this schema.
func (cs *CompiledSchema) NumSegments() int {
	return len(cs.Segments)
}

// GetSharedField returns a shared field by name, or nil if not found.
func (cs *CompiledSchema) GetSharedField(name string) *FieldDef {
	return cs.SharedFieldsByName[name]
}

// GetSegmentField returns a field from a specific segment by name, or nil if not found.
func (cs *CompiledSchema) GetSegmentField(segmentIndex int, name string) *FieldDef {
	if segmentIndex < 0 || segmentIndex >= len(cs.Segments) {
		return nil
	}
	for i := range cs.Segments[segmentIndex].Fields {
		if cs.Segments[segmentIndex].Fields[i].Name == name {
			return &cs.Segments[segmentIndex].Fields[i]
		}
	}
	return nil
}
