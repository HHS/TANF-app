package schema

import "sync"

// TransformDef defines a field transformation with optional parameters.
type TransformDef struct {
	// Name is the transform function name (e.g., "zero_pad", "ssn_decrypt")
	Name string `yaml:"name"`

	// Params contains static configuration from the schema YAML.
	// These are known at schema load time, not runtime.
	Params map[string]any `yaml:"params,omitempty"`
}

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

	// Transform defines an optional transformation to apply to the raw value.
	Transform *TransformDef `yaml:"transform,omitempty"`

	// SourceField references another field's raw value for computed fields.
	// If set, the raw value comes from the named field instead of Start/End.
	SourceField string `yaml:"source_field,omitempty"`

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

// PoolableRecord is an interface for records that can be pooled and reset.
// This allows for the object pools to be tied to the Schemas without importing
// the parser package which is very convenient and prevents circular dependencies.
type PoolableRecord interface {
	Reset()
}

// CompiledSchema wraps a SchemaDef with precomputed lookup structures.
type CompiledSchema struct {
	*SchemaDef

	// Path is the schema path (e.g., "tanf/t1", "tribal/t1")
	// Set by the registry when loading schemas
	Path string

	// SharedFieldsByName provides O(1) lookup for shared fields by name
	SharedFieldsByName map[string]*FieldDef

	// FieldIndex maps field name to index in ParsedRecord.Fields slice.
	// Built at schema compile time for O(1) field access.
	FieldIndex map[string]int

	// FieldCount is the total number of field slots needed in ParsedRecord.Fields.
	FieldCount int

	// recordPool provides reusable ParsedRecord objects to reduce GC pressure.
	recordPool sync.Pool
}

// Compile creates a CompiledSchema with lookup maps and field indexing.
func (s *SchemaDef) Compile() *CompiledSchema {
	cs := &CompiledSchema{
		SchemaDef:          s,
		SharedFieldsByName: make(map[string]*FieldDef, len(s.Shared)),
		FieldIndex:         make(map[string]int),
	}

	idx := 0

	// Index shared fields first (present in all segments)
	for i := range s.Shared {
		field := &s.Shared[i]
		cs.SharedFieldsByName[field.Name] = field
		cs.FieldIndex[field.Name] = idx
		idx++
	}

	// Index segment fields from first segment.
	// All segments have the same field names (e.g., T3's two child segments
	// both have FAMILY_AFFILIATION, SSN, etc.)
	if len(s.Segments) > 0 {
		for _, field := range s.Segments[0].Fields {
			cs.FieldIndex[field.Name] = idx
			idx++
		}
	}

	cs.FieldCount = idx
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

// InitPool creates a new record pool for this schema with the given object allocator function.
func (cs *CompiledSchema) InitPool(poolAllocator func() any) {
	cs.recordPool = sync.Pool{New: poolAllocator}
}

// AcquireRecord gets a record from the pool or creates a new one.
// The returned record has Fields slice allocated but all values nil.
func (cs *CompiledSchema) AcquireRecord() PoolableRecord {
	if r := cs.recordPool.Get(); r != nil {
		rec := r.(PoolableRecord)
		return rec
	}
	return nil
}

// ReleaseRecord returns a record to the pool for reuse.
// The record must not be used after calling this method.
func (cs *CompiledSchema) ReleaseRecord(rec PoolableRecord) {
	rec.Reset()
	cs.recordPool.Put(rec)
}

// PrewarmPool pre-allocates n records with the newObjFunc to avoid allocation during parsing.
// Call this after schema compilation but before parsing begins.
// A good value for n is 2x the number of worker goroutines.
func (cs *CompiledSchema) PrewarmPool(n int) {
	records := make([]PoolableRecord, n)
	for i := range n {
		records[i] = cs.recordPool.Get().(PoolableRecord)
	}
	// Release all to pool
	for _, rec := range records {
		cs.recordPool.Put(rec)
	}
}
