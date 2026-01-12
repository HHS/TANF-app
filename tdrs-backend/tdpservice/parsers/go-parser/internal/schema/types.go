package schema

// FieldDef represents a single field within a record.
type FieldDef struct {
    // Name is the internal field name (used in code and database)
    Name string `yaml:"name"`

    // Item is the item number from the federal specification
    Item string `yaml:"item"`

    // FriendlyName is a human-readable name for error messages
    FriendlyName string `yaml:"friendly_name"`

    // Type is the data type: "string" or "int"
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

// SchemaDef defines the structure of a single record type.
type SchemaDef struct {
    // RecordType is the identifier (e.g., "T1", "TE1")
    RecordType string `yaml:"record_type"`

    // Program is the program this schema belongs to
    Program string `yaml:"program"`

    // Description is a human-readable description
    Description string `yaml:"description"`

    // Fields defines all fields in the record
    Fields []FieldDef `yaml:"fields"`
}

// CompiledSchema wraps a SchemaDef with precomputed lookup structures.
type CompiledSchema struct {
    *SchemaDef

    // FieldsByName provides O(1) lookup by field name
    FieldsByName map[string]*FieldDef

    // FieldsByItem provides O(1) lookup by item number
    FieldsByItem map[string]*FieldDef
}

// Compile creates a CompiledSchema with lookup maps.
func (s *SchemaDef) Compile() *CompiledSchema {
    cs := &CompiledSchema{
        SchemaDef: s,
        FieldsByName: make(map[string]*FieldDef, len(s.Fields)),
        FieldsByItem: make(map[string]*FieldDef, len(s.Fields)),
    }

    for i := range s.Fields {
        field := &s.Fields[i]
        cs.FieldsByName[field.Name] = field
        cs.FieldsByItem[field.Item] = field
    }

    return cs
}

// GetField returns a field by name, or nil if not found.
func (cs *CompiledSchema) GetField(name string) *FieldDef {
    return cs.FieldsByName[name]
}
