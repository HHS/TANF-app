package config

import (
	"os"
	"path/filepath"
	"sort"
	"testing"

	"go-parser/internal/config/schema"
)

func configDir(t *testing.T) string {
	t.Helper()
	dir := filepath.Join("..", "..", "config")
	if _, err := os.Stat(dir); os.IsNotExist(err) {
		t.Fatal("real config directory not found — tests must run from go-parser root")
	}
	return dir
}

// loadRegistry loads the full registry from disk.
func loadRegistry(t *testing.T) *Registry {
	t.Helper()
	dir := configDir(t)
	cfg := &Config{
		Global:        GlobalConfig{ConfigDir: dir},
		SchemaFiles:   []string{"schemas/**/*.yaml"},
		FilespecFiles: []string{"filespecs/**/*.yaml"},
		Database:      DatabaseConfig{ShadowMode: true, TablePrefix: DefaultTablePrefix},
	}
	reg, err := NewRegistry(cfg)
	if err != nil {
		t.Fatalf("NewRegistry with real config failed: %v", err)
	}
	return reg
}

// ---------------------------------------------------------------------------
// Production schema loading & cross-reference validation
// ---------------------------------------------------------------------------

func TestConfig_LoadsSuccessfully(t *testing.T) {
	reg := loadRegistry(t)
	numFS, numS := reg.Stats()

	if numFS != 13 {
		t.Errorf("expected 13 filespecs, got %d", numFS)
	}
	// 24 schemas: 2 common + 7 tanf + 7 ssp + 7 tribal_tanf + 1 fra
	if numS != 24 {
		t.Errorf("expected 24 schemas, got %d", numS)
	}
}

func TestConfig_AllExpectedSchemasExist(t *testing.T) {
	reg := loadRegistry(t)

	expectedSchemas := []string{
		"common/header", "common/trailer",
		"tanf/t1", "tanf/t2", "tanf/t3", "tanf/t4", "tanf/t5", "tanf/t6", "tanf/t7",
		"ssp/m1", "ssp/m2", "ssp/m3", "ssp/m4", "ssp/m5", "ssp/m6", "ssp/m7",
		"tribal_tanf/t1", "tribal_tanf/t2", "tribal_tanf/t3", "tribal_tanf/t4",
		"tribal_tanf/t5", "tribal_tanf/t6", "tribal_tanf/t7",
		"fra/te1",
	}

	for _, path := range expectedSchemas {
		if reg.GetSchema(path) == nil {
			t.Errorf("missing expected schema: %s", path)
		}
	}

	got := reg.ListSchemas()
	sort.Strings(got)
	sort.Strings(expectedSchemas)
	if len(got) != len(expectedSchemas) {
		t.Errorf("schema count mismatch: got %d, want %d\ngot:  %v\nwant: %v",
			len(got), len(expectedSchemas), got, expectedSchemas)
	}
}

func TestConfig_AllExpectedFileSpecsExist(t *testing.T) {
	reg := loadRegistry(t)

	expectedSpecs := []struct {
		program string
		section int
	}{
		{"TAN", 1}, {"TAN", 2}, {"TAN", 3}, {"TAN", 4},
		{"SSP", 1}, {"SSP", 2}, {"SSP", 3}, {"SSP", 4},
		{"TRIBAL", 1}, {"TRIBAL", 2}, {"TRIBAL", 3}, {"TRIBAL", 4},
		{"FRA", 1},
	}

	for _, es := range expectedSpecs {
		spec := reg.GetFileSpec(es.program, es.section)
		if spec == nil {
			t.Errorf("missing expected filespec: %s:%d", es.program, es.section)
		}
	}
}

// ---------------------------------------------------------------------------
// Schema structure validation — catches breaking changes to schema YAML files
// ---------------------------------------------------------------------------

func TestConfig_SchemaRecordTypes(t *testing.T) {
	reg := loadRegistry(t)

	expectedRecordTypes := map[string]string{
		"common/header":  "HEADER",
		"common/trailer": "TRAILER",
		"tanf/t1":        "T1",
		"tanf/t2":        "T2",
		"tanf/t3":        "T3",
		"tanf/t4":        "T4",
		"tanf/t5":        "T5",
		"tanf/t6":        "T6",
		"tanf/t7":        "T7",
		"ssp/m1":         "M1",
		"ssp/m2":         "M2",
		"ssp/m3":         "M3",
		"ssp/m4":         "M4",
		"ssp/m5":         "M5",
		"ssp/m6":         "M6",
		"ssp/m7":         "M7",
		"tribal_tanf/t1": "T1",
		"tribal_tanf/t2": "T2",
		"tribal_tanf/t3": "T3",
		"tribal_tanf/t4": "T4",
		"tribal_tanf/t5": "T5",
		"tribal_tanf/t6": "T6",
		"tribal_tanf/t7": "T7",
		"fra/te1":        "TE1",
	}

	for path, wantRT := range expectedRecordTypes {
		s := reg.GetSchema(path)
		if s == nil {
			t.Errorf("schema %s not found", path)
			continue
		}
		if s.RecordType != wantRT {
			t.Errorf("schema %s: RecordType = %q, want %q", path, s.RecordType, wantRT)
		}
	}
}

func TestConfig_SchemaFieldCounts(t *testing.T) {
	reg := loadRegistry(t)

	// Exact field counts for each schema: {shared, segments, firstSegmentFields}
	type fieldCounts struct {
		shared             int
		segments           int
		firstSegmentFields int
	}

	expected := map[string]fieldCounts{
		"common/header":  {0, 1, 10},
		"common/trailer": {0, 1, 2},
		"tanf/t1":        {3, 1, 42},
		"tanf/t2":        {3, 1, 66},
		"tanf/t3":        {3, 2, 18},
		"tanf/t4":        {3, 1, 9},
		"tanf/t5":        {3, 1, 26},
		"tanf/t6":        {2, 3, 16},
		"tanf/t7":        {2, 30, 4},
		"ssp/m1":         {3, 1, 39},
		"ssp/m2":         {4, 1, 63},
		"ssp/m3":         {3, 2, 18},
		"ssp/m4":         {3, 1, 9},
		"ssp/m5":         {3, 1, 24},
		"ssp/m6":         {2, 3, 11},
		"ssp/m7":         {2, 30, 4},
		"tribal_tanf/t1": {3, 1, 42},
		"tribal_tanf/t2": {3, 1, 49},
		"tribal_tanf/t3": {3, 2, 18},
		"tribal_tanf/t4": {3, 1, 9},
		"tribal_tanf/t5": {3, 1, 26},
		"tribal_tanf/t6": {2, 3, 16},
		"tribal_tanf/t7": {2, 30, 4},
		"fra/te1":        {1, 1, 2},
	}

	for path, want := range expected {
		s := reg.GetSchema(path)
		if s == nil {
			t.Errorf("schema %s not found", path)
			continue
		}
		if len(s.Shared) != want.shared {
			t.Errorf("schema %s: shared fields = %d, want %d", path, len(s.Shared), want.shared)
		}
		if len(s.Segments) != want.segments {
			t.Errorf("schema %s: segments = %d, want %d", path, len(s.Segments), want.segments)
		}
		if len(s.Segments) > 0 && len(s.Segments[0].Fields) != want.firstSegmentFields {
			t.Errorf("schema %s: first segment fields = %d, want %d",
				path, len(s.Segments[0].Fields), want.firstSegmentFields)
		}
	}
}

func TestConfig_SchemaPrograms(t *testing.T) {
	reg := loadRegistry(t)

	expectedPrograms := map[string]string{
		"common/header":  "ALL",
		"common/trailer": "ALL",
		"tanf/t1":        "TAN",
		"ssp/m1":         "SSP",
		"tribal_tanf/t1": "TRIBAL",
		"fra/te1":        "FRA",
	}

	for path, wantProg := range expectedPrograms {
		s := reg.GetSchema(path)
		if s == nil {
			t.Errorf("schema %s not found", path)
			continue
		}
		if s.Program != wantProg {
			t.Errorf("schema %s: Program = %q, want %q", path, s.Program, wantProg)
		}
	}
}

func TestConfig_SchemaFormats(t *testing.T) {
	reg := loadRegistry(t)

	// All schemas are positional except FRA which is csv
	for _, path := range reg.ListSchemas() {
		s := reg.GetSchema(path)
		if path == "fra/te1" {
			if s.Format != "csv" {
				t.Errorf("schema %s: Format = %q, want csv", path, s.Format)
			}
		} else {
			if s.Format != "positional" {
				t.Errorf("schema %s: Format = %q, want positional", path, s.Format)
			}
		}
	}
}

func TestConfig_SchemaPathsSetCorrectly(t *testing.T) {
	reg := loadRegistry(t)

	for _, path := range reg.ListSchemas() {
		s := reg.GetSchema(path)
		if s.Path != path {
			t.Errorf("schema %s has Path = %q (mismatch)", path, s.Path)
		}
	}
}

func TestConfig_SharedFieldsByNamePopulated(t *testing.T) {
	reg := loadRegistry(t)

	for _, path := range reg.ListSchemas() {
		s := reg.GetSchema(path)
		if len(s.Shared) != len(s.SharedFieldsByName) {
			t.Errorf("schema %s: SharedFieldsByName has %d entries, want %d (matching Shared)",
				path, len(s.SharedFieldsByName), len(s.Shared))
		}
		for _, field := range s.Shared {
			if s.GetSharedField(field.Name) == nil {
				t.Errorf("schema %s: shared field %q not in SharedFieldsByName", path, field.Name)
			}
		}
	}
}

func TestConfig_FieldIndexCoversAllFields(t *testing.T) {
	reg := loadRegistry(t)

	for _, path := range reg.ListSchemas() {
		s := reg.GetSchema(path)

		expectedCount := len(s.Shared)
		if len(s.Segments) > 0 {
			expectedCount += len(s.Segments[0].Fields)
		}

		if s.FieldCount != expectedCount {
			t.Errorf("schema %s: FieldCount = %d, want %d (shared=%d + seg0=%d)",
				path, s.FieldCount, expectedCount, len(s.Shared),
				func() int {
					if len(s.Segments) > 0 {
						return len(s.Segments[0].Fields)
					}
					return 0
				}())
		}

		if len(s.FieldIndex) != expectedCount {
			t.Errorf("schema %s: FieldIndex has %d entries, want %d",
				path, len(s.FieldIndex), expectedCount)
		}
	}
}

func TestConfig_MultiSegmentSchemasHaveConsistentFieldNames(t *testing.T) {
	reg := loadRegistry(t)

	// T3, M3, tribal T3 have 2 segments; T6, M6, tribal T6 have 3; T7, M7, tribal T7 have 30.
	// All segments within a schema must have the same field names.
	multiSegSchemas := []string{
		"tanf/t3", "tanf/t6", "tanf/t7",
		"ssp/m3", "ssp/m6", "ssp/m7",
		"tribal_tanf/t3", "tribal_tanf/t6", "tribal_tanf/t7",
	}

	for _, path := range multiSegSchemas {
		s := reg.GetSchema(path)
		if s == nil {
			t.Errorf("schema %s not found", path)
			continue
		}
		if len(s.Segments) < 2 {
			t.Errorf("schema %s: expected multiple segments, got %d", path, len(s.Segments))
			continue
		}

		// Extract field names from first segment
		firstNames := make([]string, len(s.Segments[0].Fields))
		for i, f := range s.Segments[0].Fields {
			firstNames[i] = f.Name
		}

		for segIdx := 1; segIdx < len(s.Segments); segIdx++ {
			if len(s.Segments[segIdx].Fields) != len(firstNames) {
				t.Errorf("schema %s: segment %d has %d fields, segment 0 has %d",
					path, segIdx, len(s.Segments[segIdx].Fields), len(firstNames))
				continue
			}
			for fi, f := range s.Segments[segIdx].Fields {
				if f.Name != firstNames[fi] {
					t.Errorf("schema %s: segment %d field %d name = %q, want %q (from segment 0)",
						path, segIdx, fi, f.Name, firstNames[fi])
				}
			}
		}
	}
}

func TestConfig_RecordTypeFieldIsFirst(t *testing.T) {
	reg := loadRegistry(t)

	// All record schemas should have RecordType as the first shared field
	// (header and trailer have it in segments instead)
	recordSchemas := []string{
		"tanf/t1", "tanf/t2", "tanf/t3", "tanf/t4", "tanf/t5", "tanf/t6", "tanf/t7",
		"ssp/m1", "ssp/m2", "ssp/m3", "ssp/m4", "ssp/m5", "ssp/m6", "ssp/m7",
		"tribal_tanf/t1", "tribal_tanf/t2", "tribal_tanf/t3", "tribal_tanf/t4",
		"tribal_tanf/t5", "tribal_tanf/t6", "tribal_tanf/t7",
		"fra/te1",
	}

	for _, path := range recordSchemas {
		s := reg.GetSchema(path)
		if s == nil {
			t.Errorf("schema %s not found", path)
			continue
		}
		if len(s.Shared) == 0 || s.Shared[0].Name != "RecordType" {
			firstShared := "<none>"
			if len(s.Shared) > 0 {
				firstShared = s.Shared[0].Name
			}
			t.Errorf("schema %s: first shared field = %q, want RecordType", path, firstShared)
		}
	}
}

// ---------------------------------------------------------------------------
// FileSpec structure validation
// ---------------------------------------------------------------------------

func TestConfig_FileSpecSchemaReferences(t *testing.T) {
	reg := loadRegistry(t)

	expectedSchemas := map[string][]string{
		"TAN:1":    {"common/header", "common/trailer", "tanf/t1", "tanf/t2", "tanf/t3"},
		"TAN:2":    {"common/header", "common/trailer", "tanf/t4", "tanf/t5"},
		"TAN:3":    {"common/header", "common/trailer", "tanf/t6"},
		"TAN:4":    {"common/header", "common/trailer", "tanf/t7"},
		"SSP:1":    {"common/header", "common/trailer", "ssp/m1", "ssp/m2", "ssp/m3"},
		"SSP:2":    {"common/header", "common/trailer", "ssp/m4", "ssp/m5"},
		"SSP:3":    {"common/header", "common/trailer", "ssp/m6"},
		"SSP:4":    {"common/header", "common/trailer", "ssp/m7"},
		"TRIBAL:1": {"common/header", "common/trailer", "tribal_tanf/t1", "tribal_tanf/t2", "tribal_tanf/t3"},
		"TRIBAL:2": {"common/header", "common/trailer", "tribal_tanf/t4", "tribal_tanf/t5"},
		"TRIBAL:3": {"common/header", "common/trailer", "tribal_tanf/t6"},
		"TRIBAL:4": {"common/header", "common/trailer", "tribal_tanf/t7"},
		"FRA:1":    {"fra/te1"},
	}

	for _, key := range reg.ListFileSpecs() {
		want, ok := expectedSchemas[key]
		if !ok {
			t.Errorf("unexpected filespec key: %s", key)
			continue
		}
		spec := reg.FileSpecs()[key]
		got := make([]string, len(spec.Schemas))
		copy(got, spec.Schemas)
		sort.Strings(got)
		sort.Strings(want)
		if len(got) != len(want) {
			t.Errorf("filespec %s: schemas = %v, want %v", key, got, want)
			continue
		}
		for i := range want {
			if got[i] != want[i] {
				t.Errorf("filespec %s: schemas = %v, want %v", key, got, want)
				break
			}
		}
	}
}

func TestConfig_FileSpecDetectionMethods(t *testing.T) {
	reg := loadRegistry(t)

	for _, key := range reg.ListFileSpecs() {
		spec := reg.FileSpecs()[key]
		if key == "FRA:1" {
			if spec.RecordTypeDetection.Method != "fixed" {
				t.Errorf("filespec %s: detection method = %q, want fixed", key, spec.RecordTypeDetection.Method)
			}
			if spec.RecordTypeDetection.Schema != "fra/te1" {
				t.Errorf("filespec %s: fixed schema = %q, want fra/te1", key, spec.RecordTypeDetection.Schema)
			}
		} else {
			if spec.RecordTypeDetection.Method != "prefix" {
				t.Errorf("filespec %s: detection method = %q, want prefix", key, spec.RecordTypeDetection.Method)
			}
			// All positional filespecs must have HEADER and TRAILER prefixes
			hasHeader := false
			hasTrailer := false
			for _, p := range spec.RecordTypeDetection.Prefixes {
				if p.Prefix == "HEADER" && p.Schema == "common/header" {
					hasHeader = true
				}
				if p.Prefix == "TRAILER" && p.Schema == "common/trailer" {
					hasTrailer = true
				}
			}
			if !hasHeader {
				t.Errorf("filespec %s: missing HEADER prefix mapping", key)
			}
			if !hasTrailer {
				t.Errorf("filespec %s: missing TRAILER prefix mapping", key)
			}
		}
	}
}

func TestConfig_FRAAndTribalFileSpecValidationOrchestrators(t *testing.T) {
	reg := loadRegistry(t)

	tests := []struct {
		program       string
		section       int
		errorTypeByID map[int]string
	}{
		{
			program: "FRA",
			section: 1,
			errorTypeByID: map[int]string{
				1: "CASE_CONSISTENCY",
				2: "CASE_CONSISTENCY",
				3: "CASE_CONSISTENCY",
				4: "CASE_CONSISTENCY",
			},
		},
		{
			program: "TRIBAL",
			section: 1,
			errorTypeByID: map[int]string{
				1: "RECORD_PRE_CHECK",
				2: "FIELD_VALUE",
				3: "VALUE_CONSISTENCY",
				4: "CASE_CONSISTENCY",
			},
		},
		{
			program: "TRIBAL",
			section: 2,
			errorTypeByID: map[int]string{
				1: "RECORD_PRE_CHECK",
				2: "FIELD_VALUE",
				3: "VALUE_CONSISTENCY",
				4: "CASE_CONSISTENCY",
			},
		},
		{
			program: "TRIBAL",
			section: 3,
			errorTypeByID: map[int]string{
				1: "RECORD_PRE_CHECK",
				2: "FIELD_VALUE",
				3: "VALUE_CONSISTENCY",
				4: "CASE_CONSISTENCY",
			},
		},
		{
			program: "TRIBAL",
			section: 4,
			errorTypeByID: map[int]string{
				1: "RECORD_PRE_CHECK",
				2: "FIELD_VALUE",
				3: "VALUE_CONSISTENCY",
				4: "CASE_CONSISTENCY",
			},
		},
	}

	for _, tc := range tests {
		spec := reg.GetFileSpec(tc.program, tc.section)
		if spec == nil {
			t.Fatalf("missing filespec %s:%d", tc.program, tc.section)
		}
		if len(spec.ValidationOrchestrator.Categories) != len(tc.errorTypeByID) {
			t.Fatalf("%s:%d categories = %d, want %d", tc.program, tc.section, len(spec.ValidationOrchestrator.Categories), len(tc.errorTypeByID))
		}
		for _, category := range spec.ValidationOrchestrator.Categories {
			want := tc.errorTypeByID[category.ID]
			if category.DefaultErrorType != want {
				t.Errorf("%s:%d category %d default_error_type = %s, want %s", tc.program, tc.section, category.ID, category.DefaultErrorType, want)
			}
		}
	}
}

func TestConfig_FileSpecFormats(t *testing.T) {
	reg := loadRegistry(t)

	for _, key := range reg.ListFileSpecs() {
		spec := reg.FileSpecs()[key]
		if key == "FRA:1" {
			if string(spec.Format) != "columnar" {
				t.Errorf("filespec %s: format = %q, want columnar", key, spec.Format)
			}
		} else {
			if string(spec.Format) != "positional" {
				t.Errorf("filespec %s: format = %q, want positional", key, spec.Format)
			}
		}
	}
}

func TestConfig_FileSpecAccumulatorKeyFields(t *testing.T) {
	reg := loadRegistry(t)

	// Sections 1 and 2 group case records; sections 3 and 4 group aggregate
	// records by record type for duplicate checks. FRA groups by EXIT_DATE + SSN.
	expectKeyFields := map[string]bool{
		"TAN:1": true, "TAN:2": true, "TAN:3": true, "TAN:4": true,
		"SSP:1": true, "SSP:2": true, "SSP:3": true, "SSP:4": true,
		"TRIBAL:1": true, "TRIBAL:2": true, "TRIBAL:3": true, "TRIBAL:4": true,
		"FRA:1": true,
	}

	for key, wantKF := range expectKeyFields {
		spec := reg.FileSpecs()[key]
		if spec == nil {
			t.Errorf("filespec %s not found", key)
			continue
		}
		gotKF := spec.Accumulator.HasKeyFields()
		if gotKF != wantKF {
			t.Errorf("filespec %s: HasKeyFields() = %v, want %v", key, gotKF, wantKF)
		}
	}
}

func TestConfig_FileSpecGroupedSchemas(t *testing.T) {
	reg := loadRegistry(t)

	// Grouped schemas must exclude header/trailer and include only the record schemas.
	expectedGrouped := map[string][]string{
		"TAN:1":    {"tanf/t1", "tanf/t2", "tanf/t3"},
		"TAN:2":    {"tanf/t4", "tanf/t5"},
		"TAN:3":    {"tanf/t6"},
		"TAN:4":    {"tanf/t7"},
		"SSP:1":    {"ssp/m1", "ssp/m2", "ssp/m3"},
		"SSP:2":    {"ssp/m4", "ssp/m5"},
		"SSP:3":    {"ssp/m6"},
		"SSP:4":    {"ssp/m7"},
		"TRIBAL:1": {"tribal_tanf/t1", "tribal_tanf/t2", "tribal_tanf/t3"},
		"TRIBAL:2": {"tribal_tanf/t4", "tribal_tanf/t5"},
		"TRIBAL:3": {"tribal_tanf/t6"},
		"TRIBAL:4": {"tribal_tanf/t7"},
		"FRA:1":    {"fra/te1"},
	}

	for key, want := range expectedGrouped {
		spec := reg.FileSpecs()[key]
		if spec == nil {
			t.Errorf("filespec %s not found", key)
			continue
		}
		got := make([]string, len(spec.Accumulator.GroupedSchemas))
		copy(got, spec.Accumulator.GroupedSchemas)
		sort.Strings(got)
		sort.Strings(want)
		if len(got) != len(want) {
			t.Errorf("filespec %s: grouped schemas = %v, want %v", key, got, want)
			continue
		}
		for i := range want {
			if got[i] != want[i] {
				t.Errorf("filespec %s: grouped schemas = %v, want %v", key, got, want)
				break
			}
		}
	}

}

// ---------------------------------------------------------------------------
// Registry accessor methods (tested against real data)
// ---------------------------------------------------------------------------

func TestConfig_GetFileSpecReturnsNilForMissing(t *testing.T) {
	reg := loadRegistry(t)

	if reg.GetFileSpec("TAN", 99) != nil {
		t.Error("expected nil for non-existent section")
	}
	if reg.GetFileSpec("UNKNOWN", 1) != nil {
		t.Error("expected nil for unknown program")
	}
}

func TestConfig_GetSchemaReturnsNilForMissing(t *testing.T) {
	reg := loadRegistry(t)

	if reg.GetSchema("nonexistent") != nil {
		t.Error("expected nil for non-existent schema")
	}
}

func TestConfig_MustGetSchemaPanicsForMissing(t *testing.T) {
	reg := loadRegistry(t)

	// Should not panic for existing schema
	s := reg.MustGetSchema("tanf/t1")
	if s == nil {
		t.Fatal("MustGetSchema returned nil for existing schema")
	}

	defer func() {
		if r := recover(); r == nil {
			t.Error("expected panic for missing schema")
		}
	}()
	reg.MustGetSchema("nonexistent/schema")
}

func TestConfig_ConfigDirSet(t *testing.T) {
	reg := loadRegistry(t)

	if reg.ConfigDir() == "" {
		t.Error("ConfigDir() returned empty string")
	}
}

// ---------------------------------------------------------------------------
// Error handling (synthetic configs for edge cases)
// ---------------------------------------------------------------------------

func TestNewRegistry_InvalidSchemaYAML(t *testing.T) {
	dir := t.TempDir()
	os.MkdirAll(filepath.Join(dir, "schemas"), 0755)
	os.WriteFile(filepath.Join(dir, "schemas", "bad.yaml"), []byte("{{{{not yaml"), 0644)

	cfg := &Config{
		Global:      GlobalConfig{ConfigDir: dir},
		SchemaFiles: []string{"schemas/*.yaml"},
	}

	_, err := NewRegistry(cfg)
	if err == nil {
		t.Fatal("expected error for invalid YAML, got nil")
	}
}

func TestNewRegistry_InvalidFileSpecYAML(t *testing.T) {
	dir := t.TempDir()
	os.MkdirAll(filepath.Join(dir, "filespecs"), 0755)
	os.WriteFile(filepath.Join(dir, "filespecs", "bad.yaml"), []byte("{{{{not yaml"), 0644)

	cfg := &Config{
		Global:        GlobalConfig{ConfigDir: dir},
		SchemaFiles:   []string{},
		FilespecFiles: []string{"filespecs/*.yaml"},
	}

	_, err := NewRegistry(cfg)
	if err == nil {
		t.Fatal("expected error for invalid filespec YAML, got nil")
	}
}

func TestNewRegistry_UnresolvableSchemaReference(t *testing.T) {
	dir := t.TempDir()
	os.MkdirAll(filepath.Join(dir, "schemas", "tanf"), 0755)
	os.MkdirAll(filepath.Join(dir, "filespecs"), 0755)

	os.WriteFile(filepath.Join(dir, "schemas", "tanf", "t1.yaml"),
		[]byte("record_type: T1\nprogram: TAN\nshared: []\nsegments:\n  - fields:\n    - name: x\n"), 0644)

	badSpec := `program: TAN
				section: 1
				format: positional
				schemas:
				- tanf/t1
				- tanf/t99
				record_type_detection:
				method: prefix
				prefixes:
					- prefix: "T1"
					schema: tanf/t1
				accumulator: {}
				`
	os.WriteFile(filepath.Join(dir, "filespecs", "s1.yaml"), []byte(badSpec), 0644)

	cfg := &Config{
		Global:        GlobalConfig{ConfigDir: dir},
		SchemaFiles:   []string{"schemas/**/*.yaml"},
		FilespecFiles: []string{"filespecs/*.yaml"},
	}

	_, err := NewRegistry(cfg)
	if err == nil {
		t.Fatal("expected error for unresolvable schema reference")
	}
}

func TestNewRegistry_UnresolvablePrefixReference(t *testing.T) {
	dir := t.TempDir()
	os.MkdirAll(filepath.Join(dir, "schemas", "tanf"), 0755)
	os.MkdirAll(filepath.Join(dir, "filespecs"), 0755)

	os.WriteFile(filepath.Join(dir, "schemas", "tanf", "t1.yaml"),
		[]byte("record_type: T1\nprogram: TAN\nshared: []\nsegments:\n  - fields:\n    - name: x\n"), 0644)

	badSpec := `program: TAN
				section: 1
				format: positional
				schemas:
				- tanf/t1
				record_type_detection:
				method: prefix
				prefixes:
					- prefix: "T1"
					schema: tanf/t1
					- prefix: "T2"
					schema: tanf/t2_missing
				accumulator: {}
				`
	os.WriteFile(filepath.Join(dir, "filespecs", "s1.yaml"), []byte(badSpec), 0644)

	cfg := &Config{
		Global:        GlobalConfig{ConfigDir: dir},
		SchemaFiles:   []string{"schemas/**/*.yaml"},
		FilespecFiles: []string{"filespecs/*.yaml"},
	}

	_, err := NewRegistry(cfg)
	if err == nil {
		t.Fatal("expected error for unresolvable prefix schema reference")
	}
}

func TestNewRegistry_UnresolvableGroupedSchemasReference(t *testing.T) {
	dir := t.TempDir()
	os.MkdirAll(filepath.Join(dir, "schemas", "tanf"), 0755)
	os.MkdirAll(filepath.Join(dir, "filespecs"), 0755)

	os.WriteFile(filepath.Join(dir, "schemas", "tanf", "t1.yaml"),
		[]byte("record_type: T1\nprogram: TAN\nshared: []\nsegments:\n  - fields:\n    - name: x\n"), 0644)

	badSpec := `program: TAN
				section: 1
				format: positional
				schemas:
				- tanf/t1
				record_type_detection:
				method: prefix
				prefixes:
					- prefix: "T1"
					schema: tanf/t1
				accumulator:
				grouped_schemas:
					- tanf/t1
					- tanf/nonexistent
				`
	os.WriteFile(filepath.Join(dir, "filespecs", "s1.yaml"), []byte(badSpec), 0644)

	cfg := &Config{
		Global:        GlobalConfig{ConfigDir: dir},
		SchemaFiles:   []string{"schemas/**/*.yaml"},
		FilespecFiles: []string{"filespecs/*.yaml"},
	}

	_, err := NewRegistry(cfg)
	if err == nil {
		t.Fatal("expected error for unresolvable grouped_schemas reference")
	}
}

func TestNewRegistry_UnreadableSchemaFile(t *testing.T) {
	dir := t.TempDir()
	os.MkdirAll(filepath.Join(dir, "schemas"), 0755)

	path := filepath.Join(dir, "schemas", "bad.yaml")
	os.WriteFile(path, []byte("test"), 0644)
	os.Chmod(path, 0000)
	t.Cleanup(func() { os.Chmod(path, 0644) })

	cfg := &Config{
		Global:      GlobalConfig{ConfigDir: dir},
		SchemaFiles: []string{"schemas/*.yaml"},
	}

	_, err := NewRegistry(cfg)
	if err == nil {
		t.Fatal("expected error for unreadable schema file")
	}
}

func TestNewRegistry_UnreadableFileSpecFile(t *testing.T) {
	dir := t.TempDir()
	os.MkdirAll(filepath.Join(dir, "filespecs"), 0755)

	path := filepath.Join(dir, "filespecs", "bad.yaml")
	os.WriteFile(path, []byte("test"), 0644)
	os.Chmod(path, 0000)
	t.Cleanup(func() { os.Chmod(path, 0644) })

	cfg := &Config{
		Global:        GlobalConfig{ConfigDir: dir},
		SchemaFiles:   []string{},
		FilespecFiles: []string{"filespecs/*.yaml"},
	}

	_, err := NewRegistry(cfg)
	if err == nil {
		t.Fatal("expected error for unreadable filespec file")
	}
}

func TestNewRegistry_EmptyGlobsProduceEmptyRegistry(t *testing.T) {
	dir := t.TempDir()

	cfg := &Config{
		Global:      GlobalConfig{ConfigDir: dir},
		SchemaFiles: []string{"schemas/**/*.yaml"},
	}

	reg, err := NewRegistry(cfg)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	_, numS := reg.Stats()
	if numS != 0 {
		t.Errorf("expected 0 schemas, got %d", numS)
	}
}

// ---------------------------------------------------------------------------
// NewTestRegistry
// ---------------------------------------------------------------------------

func TestNewTestRegistry(t *testing.T) {
	schemas := map[string]*schema.CompiledSchema{
		"tanf/t1": (&schema.SchemaDef{
			RecordType: "T1",
			Program:    "TAN",
			Section:    1,
			Shared:     []schema.FieldDef{{Name: "RecordType", Start: 0, End: 2, Type: "string"}},
			Segments: []schema.SegmentDef{
				{Fields: []schema.FieldDef{{Name: "COUNTY_FIPS_CODE", Start: 19, End: 22, Type: "string"}}},
			},
		}).Compile(),
	}
	schemas["tanf/t1"].Path = "tanf/t1"

	reg := NewTestRegistry(schemas)

	if reg.GetSchema("tanf/t1") == nil {
		t.Error("expected tanf/t1 schema in test registry")
	}
	if len(reg.ListFileSpecs()) != 0 {
		t.Error("expected empty filespecs in test registry")
	}
	// FileSpecs and metadata maps should be initialized (not nil)
	if reg.FileSpecs() == nil {
		t.Error("FileSpecs() returned nil, expected empty map")
	}
	if reg.GetSchemaMetadata("anything") != nil {
		t.Error("expected nil metadata in fresh test registry")
	}
}

func TestNewTestRegistry_EmptySchemas(t *testing.T) {
	reg := NewTestRegistry(map[string]*schema.CompiledSchema{})

	if len(reg.ListSchemas()) != 0 {
		t.Error("expected 0 schemas")
	}
	_, numS := reg.Stats()
	if numS != 0 {
		t.Errorf("expected 0 schemas in stats, got %d", numS)
	}
}

// ---------------------------------------------------------------------------
// LoadContentTypes
// ---------------------------------------------------------------------------

func TestConfig_LoadContentTypes(t *testing.T) {
	reg := loadRegistry(t)

	contentTypes := map[string]int32{
		"shadowtanf_t1":        42,
		"shadowtanf_t2":        43,
		"shadowssp_m1":         44,
		"shadowtribal_tanf_t1": 45,
		"shadowtanf_exiter1":   46,
	}
	reg.LoadContentTypes(contentTypes)

	checks := []struct {
		schemaPath string
		wantID     int32
	}{
		{"tanf/t1", 42},
		{"tanf/t2", 43},
		{"ssp/m1", 44},
		{"tribal_tanf/t1", 45},
		{"fra/te1", 46},
	}

	for _, c := range checks {
		meta := reg.GetSchemaMetadata(c.schemaPath)
		if meta == nil {
			t.Errorf("no metadata for %s", c.schemaPath)
			continue
		}
		if meta.ContentTypeID == nil {
			t.Errorf("schema %s: ContentTypeID is nil, want %d", c.schemaPath, c.wantID)
			continue
		}
		if *meta.ContentTypeID != c.wantID {
			t.Errorf("schema %s: ContentTypeID = %d, want %d", c.schemaPath, *meta.ContentTypeID, c.wantID)
		}
	}
}

func TestLoadContentTypes_MatchesSetContentTypeIDs(t *testing.T) {
	schemas := map[string]*schema.CompiledSchema{
		"tanf/t1": (&schema.SchemaDef{
			RecordType: "T1",
			Shared:     []schema.FieldDef{{Name: "RecordType"}},
		}).Compile(),
	}
	schemas["tanf/t1"].Path = "tanf/t1"

	reg1 := NewTestRegistry(schemas)
	reg1.buildAllMetadata()
	reg2 := NewTestRegistry(schemas)
	reg2.buildAllMetadata()

	ct := map[string]int32{"tanf_t1": 99}
	reg1.LoadContentTypes(ct)
	reg2.SetContentTypeIDs(ct)

	m1 := reg1.GetSchemaMetadata("tanf/t1")
	m2 := reg2.GetSchemaMetadata("tanf/t1")

	if m1 == nil || m2 == nil || m1.ContentTypeID == nil || m2.ContentTypeID == nil {
		t.Fatal("metadata or content type ID not set")
	}
	if *m1.ContentTypeID != *m2.ContentTypeID {
		t.Errorf("LoadContentTypes and SetContentTypeIDs differ: %d vs %d",
			*m1.ContentTypeID, *m2.ContentTypeID)
	}
}
