package decoder

import (
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
)

func buildPrefixDetector() *RecordTypeDetector {
	schemas := map[string]*schema.CompiledSchema{
		"common/header":  {SchemaDef: &schema.SchemaDef{RecordType: "HEADER"}, Path: "common/header"},
		"common/trailer": {SchemaDef: &schema.SchemaDef{RecordType: "TRAILER"}, Path: "common/trailer"},
		"tanf/t1":        {SchemaDef: &schema.SchemaDef{RecordType: "T1"}, Path: "tanf/t1"},
		"tanf/t2":        {SchemaDef: &schema.SchemaDef{RecordType: "T2"}, Path: "tanf/t2"},
	}
	registry := config.NewTestRegistry(schemas)

	spec := &filespec.FileSpec{
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "prefix",
			Prefixes: []filespec.PrefixMapping{
				{Prefix: "HEADER", Schema: "common/header"},
				{Prefix: "TRAILER", Schema: "common/trailer"},
				{Prefix: "T1", Schema: "tanf/t1"},
				{Prefix: "T2", Schema: "tanf/t2"},
			},
		},
	}

	return NewRecordTypeDetector(spec, registry)
}

func buildColumnDetector() *RecordTypeDetector {
	schemas := map[string]*schema.CompiledSchema{
		"T1":  {SchemaDef: &schema.SchemaDef{RecordType: "T1"}, Path: "T1"},
		"TE1": {SchemaDef: &schema.SchemaDef{RecordType: "TE1"}, Path: "TE1"},
	}
	registry := config.NewTestRegistry(schemas)

	spec := &filespec.FileSpec{
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "column",
			Column: 0,
		},
	}

	return NewRecordTypeDetector(spec, registry)
}

func buildFixedDetector() *RecordTypeDetector {
	schemas := map[string]*schema.CompiledSchema{
		"fra/te1": {SchemaDef: &schema.SchemaDef{RecordType: "TE1"}, Path: "fra/te1"},
	}
	registry := config.NewTestRegistry(schemas)

	spec := &filespec.FileSpec{
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "fixed",
			Schema: "fra/te1",
		},
	}

	return NewRecordTypeDetector(spec, registry)
}

// --- Prefix detection tests ---

func TestDetector_Prefix_MatchesHeader(t *testing.T) {
	detector := buildPrefixDetector()
	row := NewPositionalRow(1, "HEADER", 30, "HEADER202401 some data")

	sch, err := detector.Detect(row)
	if err != nil {
		t.Fatalf("Detect() error: %v", err)
	}
	if sch.Path != "common/header" {
		t.Errorf("Detect() path = %q, want %q", sch.Path, "common/header")
	}
}

func TestDetector_Prefix_MatchesTrailer(t *testing.T) {
	detector := buildPrefixDetector()
	row := NewPositionalRow(1, "TRAILER", 50, "TRAILER0000001000000000000000001T10000000000000000")

	sch, err := detector.Detect(row)
	if err != nil {
		t.Fatalf("Detect() error: %v", err)
	}
	if sch.Path != "common/trailer" {
		t.Errorf("Detect() path = %q, want %q", sch.Path, "common/trailer")
	}
}

func TestDetector_Prefix_MatchesDataRecord(t *testing.T) {
	detector := buildPrefixDetector()
	row := NewPositionalRow(1, "T1", 30, "T1202401CASE001    rest-of-data")

	sch, err := detector.Detect(row)
	if err != nil {
		t.Fatalf("Detect() error: %v", err)
	}
	if sch.Path != "tanf/t1" {
		t.Errorf("Detect() path = %q, want %q", sch.Path, "tanf/t1")
	}
}

func TestDetector_Prefix_NoMatch(t *testing.T) {
	detector := buildPrefixDetector()
	row := NewPositionalRow(1, "XX", 30, "XX202401CASE001    unknown-data")

	_, err := detector.Detect(row)
	if err == nil {
		t.Fatal("Detect() expected error for unknown prefix")
	}
}

func TestDetector_Prefix_LongestPrefixWins(t *testing.T) {
	// "HEADER" should match "HEADER" prefix, not "H" if one existed
	schemas := map[string]*schema.CompiledSchema{
		"common/header": {SchemaDef: &schema.SchemaDef{RecordType: "HEADER"}, Path: "common/header"},
		"other/h":       {SchemaDef: &schema.SchemaDef{RecordType: "H"}, Path: "other/h"},
	}
	registry := config.NewTestRegistry(schemas)

	spec := &filespec.FileSpec{
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "prefix",
			Prefixes: []filespec.PrefixMapping{
				{Prefix: "H", Schema: "other/h"},
				{Prefix: "HEADER", Schema: "common/header"},
			},
		},
	}

	detector := NewRecordTypeDetector(spec, registry)
	row := NewPositionalRow(1, "HEADER", 30, "HEADER202401 some data")

	sch, err := detector.Detect(row)
	if err != nil {
		t.Fatalf("Detect() error: %v", err)
	}
	if sch.Path != "common/header" {
		t.Errorf("Detect() path = %q, want %q (longest prefix should win)", sch.Path, "common/header")
	}
}

func TestDetector_Prefix_WrongRowType(t *testing.T) {
	detector := buildPrefixDetector()
	row := NewColumnarRow(1, "T1", 3, []any{"a", "b", "c"})

	_, err := detector.Detect(row)
	if err == nil {
		t.Fatal("Detect() expected error for ColumnarRow with prefix detection")
	}
}

func TestDetector_Prefix_PreviewTruncated(t *testing.T) {
	detector := buildPrefixDetector()
	longData := "ZZAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBCCCCCCCC"
	row := NewPositionalRow(1, "ZZ", len(longData), longData)

	_, err := detector.Detect(row)
	if err == nil {
		t.Fatal("Detect() expected error for unknown prefix")
	}
	// Error message should contain truncated preview
	if len(err.Error()) == 0 {
		t.Error("error message should not be empty")
	}
}

// --- Column detection tests ---

func TestDetector_Column_MatchesRecordType(t *testing.T) {
	detector := buildColumnDetector()
	row := NewColumnarRow(1, "T1", 3, []any{"T1", "val2", "val3"})

	sch, err := detector.Detect(row)
	if err != nil {
		t.Fatalf("Detect() error: %v", err)
	}
	if sch.Path != "T1" {
		t.Errorf("Detect() path = %q, want %q", sch.Path, "T1")
	}
}

func TestDetector_Column_UnknownRecordType(t *testing.T) {
	detector := buildColumnDetector()
	row := NewColumnarRow(1, "XX", 3, []any{"XX", "val2", "val3"})

	_, err := detector.Detect(row)
	if err == nil {
		t.Fatal("Detect() expected error for unknown record type")
	}
}

func TestDetector_Column_EmptyColumn(t *testing.T) {
	detector := buildColumnDetector()
	row := NewColumnarRow(1, "", 0, []any{})

	_, err := detector.Detect(row)
	if err == nil {
		t.Fatal("Detect() expected error for empty columns")
	}
}

func TestDetector_Column_TrimsWhitespace(t *testing.T) {
	detector := buildColumnDetector()
	row := NewColumnarRow(1, "TE1", 3, []any{"  TE1  ", "val2", "val3"})

	sch, err := detector.Detect(row)
	if err != nil {
		t.Fatalf("Detect() error: %v", err)
	}
	if sch.Path != "TE1" {
		t.Errorf("Detect() path = %q, want %q", sch.Path, "TE1")
	}
}

func TestDetector_Column_WrongRowType(t *testing.T) {
	detector := buildColumnDetector()
	row := NewPositionalRow(1, "T1", 30, "T1202401CASE001    rest-of-data")

	_, err := detector.Detect(row)
	if err == nil {
		t.Fatal("Detect() expected error for PositionalRow with column detection")
	}
}

// --- Fixed detection tests ---

func TestDetector_Fixed_ReturnsFixedSchema(t *testing.T) {
	detector := buildFixedDetector()
	// Fixed detection ignores the row content entirely
	row := NewColumnarRow(1, "TE1", 3, []any{"a", "b", "c"})

	sch, err := detector.Detect(row)
	if err != nil {
		t.Fatalf("Detect() error: %v", err)
	}
	if sch.Path != "fra/te1" {
		t.Errorf("Detect() path = %q, want %q", sch.Path, "fra/te1")
	}
}

func TestDetector_Fixed_MissingSchema(t *testing.T) {
	schemas := map[string]*schema.CompiledSchema{}
	registry := config.NewTestRegistry(schemas)

	spec := &filespec.FileSpec{
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "fixed",
			Schema: "nonexistent",
		},
	}

	detector := NewRecordTypeDetector(spec, registry)
	row := NewColumnarRow(1, "TE1", 3, []any{"a", "b", "c"})

	_, err := detector.Detect(row)
	if err == nil {
		t.Fatal("Detect() expected error for missing fixed schema")
	}
}

// --- Unknown method test ---

func TestDetector_UnknownMethod(t *testing.T) {
	schemas := map[string]*schema.CompiledSchema{}
	registry := config.NewTestRegistry(schemas)

	spec := &filespec.FileSpec{
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "unknown_method",
		},
	}

	detector := NewRecordTypeDetector(spec, registry)
	row := NewPositionalRow(1, "T1", 10, "T1somedata")

	_, err := detector.Detect(row)
	if err == nil {
		t.Fatal("Detect() expected error for unknown detection method")
	}
}

// --- sortPrefixesByLength tests ---

func TestSortPrefixesByLength(t *testing.T) {
	prefixes := []filespec.PrefixMapping{
		{Prefix: "T1", Schema: "tanf/t1"},
		{Prefix: "HEADER", Schema: "common/header"},
		{Prefix: "T2", Schema: "tanf/t2"},
		{Prefix: "TRAILER", Schema: "common/trailer"},
	}

	sorted := sortPrefixesByLength(prefixes)

	// Longest first
	if sorted[0].Prefix != "TRAILER" {
		t.Errorf("sorted[0].Prefix = %q, want %q", sorted[0].Prefix, "TRAILER")
	}
	if sorted[1].Prefix != "HEADER" {
		t.Errorf("sorted[1].Prefix = %q, want %q", sorted[1].Prefix, "HEADER")
	}

	// Original should be unchanged
	if prefixes[0].Prefix != "T1" {
		t.Error("original slice was modified")
	}
}

func TestSortPrefixesByLength_Empty(t *testing.T) {
	sorted := sortPrefixesByLength(nil)
	if len(sorted) != 0 {
		t.Errorf("len(sorted) = %d, want 0", len(sorted))
	}
}

func TestDetector_Prefix_SchemaNotInRegistry(t *testing.T) {
	// Schema referenced by prefix mapping but not loaded in registry
	schemas := map[string]*schema.CompiledSchema{
		"tanf/t1": {SchemaDef: &schema.SchemaDef{RecordType: "T1"}, Path: "tanf/t1"},
	}
	registry := config.NewTestRegistry(schemas)

	spec := &filespec.FileSpec{
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "prefix",
			Prefixes: []filespec.PrefixMapping{
				{Prefix: "T1", Schema: "tanf/t1"},
				{Prefix: "T2", Schema: "tanf/t2"}, // not in registry
			},
		},
	}

	detector := NewRecordTypeDetector(spec, registry)

	// T1 should work
	row := NewPositionalRow(1, "T1", 20, "T1202401CASE001    ")
	sch, err := detector.Detect(row)
	if err != nil {
		t.Fatalf("Detect(T1) error: %v", err)
	}
	if sch.Path != "tanf/t1" {
		t.Errorf("Detect(T1) path = %q, want %q", sch.Path, "tanf/t1")
	}

	// T2 should error because schema not in registry
	row2 := NewPositionalRow(2, "T2", 20, "T2202401CASE001    ")
	_, err = detector.Detect(row2)
	if err == nil {
		t.Fatal("Detect(T2) expected error for missing schema in registry")
	}
}
