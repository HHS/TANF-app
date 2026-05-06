package config

import (
	"testing"

	"go-parser/internal/config/schema"
)

// ---------------------------------------------------------------------------
// recordSchemaToTable — exhaustive mapping for all real schema paths
// ---------------------------------------------------------------------------

func TestRecordSchemaToTable(t *testing.T) {
	tests := []struct {
		schemaPath string
		wantTable  string
	}{
		// TANF
		{"tanf/t1", "search_indexes_tanf_t1"},
		{"tanf/t2", "search_indexes_tanf_t2"},
		{"tanf/t3", "search_indexes_tanf_t3"},
		{"tanf/t4", "search_indexes_tanf_t4"},
		{"tanf/t5", "search_indexes_tanf_t5"},
		{"tanf/t6", "search_indexes_tanf_t6"},
		{"tanf/t7", "search_indexes_tanf_t7"},
		// SSP
		{"ssp/m1", "search_indexes_ssp_m1"},
		{"ssp/m2", "search_indexes_ssp_m2"},
		{"ssp/m3", "search_indexes_ssp_m3"},
		{"ssp/m4", "search_indexes_ssp_m4"},
		{"ssp/m5", "search_indexes_ssp_m5"},
		{"ssp/m6", "search_indexes_ssp_m6"},
		{"ssp/m7", "search_indexes_ssp_m7"},
		// Tribal TANF
		{"tribal_tanf/t1", "search_indexes_tribal_tanf_t1"},
		{"tribal_tanf/t2", "search_indexes_tribal_tanf_t2"},
		{"tribal_tanf/t3", "search_indexes_tribal_tanf_t3"},
		{"tribal_tanf/t4", "search_indexes_tribal_tanf_t4"},
		{"tribal_tanf/t5", "search_indexes_tribal_tanf_t5"},
		{"tribal_tanf/t6", "search_indexes_tribal_tanf_t6"},
		{"tribal_tanf/t7", "search_indexes_tribal_tanf_t7"},
		// FRA special case
		{"fra/te1", "search_indexes_tanf_exiter1"},
	}

	for _, tt := range tests {
		t.Run(tt.schemaPath, func(t *testing.T) {
			got := recordSchemaToTable(tt.schemaPath)
			if got != tt.wantTable {
				t.Errorf("recordSchemaToTable(%q) = %q, want %q", tt.schemaPath, got, tt.wantTable)
			}
		})
	}
}

// ---------------------------------------------------------------------------
// schemaPathToModelName — covers all programs including special cases
// ---------------------------------------------------------------------------

func TestSchemaPathToModelName(t *testing.T) {
	tests := []struct {
		schemaPath string
		wantModel  string
	}{
		{"tanf/t1", "tanf_t1"},
		{"tanf/t7", "tanf_t7"},
		{"ssp/m1", "ssp_m1"},
		{"ssp/m7", "ssp_m7"},
		{"tribal_tanf/t1", "tribal_tanf_t1"},
		{"tribal_tanf/t7", "tribal_tanf_t7"},
		{"fra/te1", "tanf_exiter1"},
	}

	for _, tt := range tests {
		t.Run(tt.schemaPath, func(t *testing.T) {
			got := schemaPathToModelName(tt.schemaPath)
			if got != tt.wantModel {
				t.Errorf("schemaPathToModelName(%q) = %q, want %q", tt.schemaPath, got, tt.wantModel)
			}
		})
	}
}

// ---------------------------------------------------------------------------
// Metadata from real production schemas
// ---------------------------------------------------------------------------

func TestRealConfig_MetadataTableNames(t *testing.T) {
	reg := loadRegistry(t)

	// Every record schema (non-header, non-trailer) must have metadata with correct table name
	expectedTables := map[string]string{
		"tanf/t1":        "search_indexes_tanf_t1",
		"tanf/t2":        "search_indexes_tanf_t2",
		"tanf/t3":        "search_indexes_tanf_t3",
		"tanf/t4":        "search_indexes_tanf_t4",
		"tanf/t5":        "search_indexes_tanf_t5",
		"tanf/t6":        "search_indexes_tanf_t6",
		"tanf/t7":        "search_indexes_tanf_t7",
		"ssp/m1":         "search_indexes_ssp_m1",
		"ssp/m2":         "search_indexes_ssp_m2",
		"ssp/m3":         "search_indexes_ssp_m3",
		"ssp/m4":         "search_indexes_ssp_m4",
		"ssp/m5":         "search_indexes_ssp_m5",
		"ssp/m6":         "search_indexes_ssp_m6",
		"ssp/m7":         "search_indexes_ssp_m7",
		"tribal_tanf/t1": "search_indexes_tribal_tanf_t1",
		"tribal_tanf/t2": "search_indexes_tribal_tanf_t2",
		"tribal_tanf/t3": "search_indexes_tribal_tanf_t3",
		"tribal_tanf/t4": "search_indexes_tribal_tanf_t4",
		"tribal_tanf/t5": "search_indexes_tribal_tanf_t5",
		"tribal_tanf/t6": "search_indexes_tribal_tanf_t6",
		"tribal_tanf/t7": "search_indexes_tribal_tanf_t7",
		"fra/te1":        "search_indexes_tanf_exiter1",
	}

	for path, wantTable := range expectedTables {
		meta := reg.GetSchemaMetadata(path)
		if meta == nil {
			t.Errorf("no metadata for %s", path)
			continue
		}
		if meta.TableName != wantTable {
			t.Errorf("schema %s: TableName = %q, want %q", path, meta.TableName, wantTable)
		}
	}
}

func TestRealConfig_MetadataRecordTypes(t *testing.T) {
	reg := loadRegistry(t)

	expectedRT := map[string]string{
		"tanf/t1": "T1", "tanf/t2": "T2", "tanf/t3": "T3",
		"tanf/t4": "T4", "tanf/t5": "T5", "tanf/t6": "T6", "tanf/t7": "T7",
		"ssp/m1": "M1", "ssp/m2": "M2", "ssp/m3": "M3",
		"ssp/m4": "M4", "ssp/m5": "M5", "ssp/m6": "M6", "ssp/m7": "M7",
		"tribal_tanf/t1": "T1", "tribal_tanf/t2": "T2", "tribal_tanf/t3": "T3",
		"tribal_tanf/t4": "T4", "tribal_tanf/t5": "T5", "tribal_tanf/t6": "T6", "tribal_tanf/t7": "T7",
		"fra/te1": "TE1",
	}

	for path, wantRT := range expectedRT {
		meta := reg.GetSchemaMetadata(path)
		if meta == nil {
			t.Errorf("no metadata for %s", path)
			continue
		}
		if meta.RecordType != wantRT {
			t.Errorf("schema %s: RecordType = %q, want %q", path, meta.RecordType, wantRT)
		}
	}
}

func TestRealConfig_MetadataColumnCounts(t *testing.T) {
	reg := loadRegistry(t)

	// Expected column counts: shared + first_segment_fields + 3 (id, datafile_id, line_number)
	expectedCounts := map[string]int{
		"tanf/t1":        3 + 42 + 3, // 48
		"tanf/t2":        3 + 66 + 3, // 72
		"tanf/t3":        3 + 18 + 3, // 24
		"tanf/t4":        3 + 9 + 3,  // 15
		"tanf/t5":        3 + 26 + 3, // 32
		"tanf/t6":        2 + 16 + 3, // 21
		"tanf/t7":        2 + 4 + 3,  // 9
		"ssp/m1":         3 + 39 + 3, // 46
		"ssp/m2":         4 + 63 + 3, // 70
		"ssp/m3":         4 + 18 + 3, // 25
		"ssp/m4":         3 + 9 + 3,  // 15
		"ssp/m5":         3 + 24 + 3, // 30
		"ssp/m6":         2 + 11 + 3, // 16
		"ssp/m7":         2 + 4 + 3,  // 9
		"tribal_tanf/t1": 3 + 42 + 3, // 48
		"tribal_tanf/t2": 3 + 49 + 3, // 55
		"tribal_tanf/t3": 3 + 18 + 3, // 24
		"tribal_tanf/t4": 3 + 9 + 3,  // 15
		"tribal_tanf/t5": 3 + 26 + 3, // 32
		"tribal_tanf/t6": 2 + 16 + 3, // 21
		"tribal_tanf/t7": 2 + 4 + 3,  // 9
		"fra/te1":        1 + 2 + 3,  // 6
	}

	for path, wantCount := range expectedCounts {
		meta := reg.GetSchemaMetadata(path)
		if meta == nil {
			t.Errorf("no metadata for %s", path)
			continue
		}
		if len(meta.Columns) != wantCount {
			t.Errorf("schema %s: column count = %d, want %d\n  columns: %v",
				path, len(meta.Columns), wantCount, meta.Columns)
		}
	}
}

func TestRealConfig_MetadataStandardColumnsAlwaysLast(t *testing.T) {
	reg := loadRegistry(t)

	for _, path := range reg.ListSchemas() {
		meta := reg.GetSchemaMetadata(path)
		if meta == nil {
			continue // header/trailer have no metadata
		}
		n := len(meta.Columns)
		if n < 3 {
			t.Errorf("schema %s: too few columns (%d)", path, n)
			continue
		}
		if meta.Columns[n-3] != "id" || meta.Columns[n-2] != "datafile_id" || meta.Columns[n-1] != "line_number" {
			t.Errorf("schema %s: last 3 columns = [%q, %q, %q], want [id, datafile_id, line_number]",
				path, meta.Columns[n-3], meta.Columns[n-2], meta.Columns[n-1])
		}
	}
}

func TestRealConfig_MetadataSkipsHeaderAndTrailer(t *testing.T) {
	reg := loadRegistry(t)

	if reg.GetSchemaMetadata("common/header") != nil {
		t.Error("header should not have db metadata")
	}
	if reg.GetSchemaMetadata("common/trailer") != nil {
		t.Error("trailer should not have db metadata")
	}
}

func TestRealConfig_MetadataFirstColumnIsRecordType(t *testing.T) {
	reg := loadRegistry(t)

	for _, path := range reg.ListSchemas() {
		meta := reg.GetSchemaMetadata(path)
		if meta == nil {
			continue
		}
		// All record schemas have RecordType as first shared field, so first column
		if meta.Columns[0] != "RecordType" {
			t.Errorf("schema %s: first column = %q, want RecordType", path, meta.Columns[0])
		}
	}
}

func TestRealConfig_MetadataContentTypeIDsNilBeforeLoad(t *testing.T) {
	reg := loadRegistry(t)

	for _, path := range reg.ListSchemas() {
		meta := reg.GetSchemaMetadata(path)
		if meta == nil {
			continue
		}
		if meta.ContentTypeID != nil {
			t.Errorf("schema %s: ContentTypeID should be nil before LoadContentTypes", path)
		}
	}
}

// ---------------------------------------------------------------------------
// buildDbSchemaMetadata unit tests (edge cases with synthetic schemas)
// ---------------------------------------------------------------------------

func TestBuildDbSchemaMetadata_ColumnOrder(t *testing.T) {
	cs := (&schema.SchemaDef{
		RecordType: "M1",
		Program:    "SSP",
		Shared: []schema.FieldDef{
			{Name: "RecordType"},
			{Name: "RPT_MONTH_YEAR"},
		},
		Segments: []schema.SegmentDef{
			{Fields: []schema.FieldDef{
				{Name: "CASH_AMOUNT"},
				{Name: "NBR_MONTHS"},
			}},
		},
	}).Compile()
	cs.Path = "ssp/m1"

	meta := buildDbSchemaMetadata(cs)

	// Verify exact ordering: shared, then segment, then standard
	expected := []string{
		"RecordType", "RPT_MONTH_YEAR",
		"CASH_AMOUNT", "NBR_MONTHS",
		"id", "datafile_id", "line_number",
	}
	if len(meta.Columns) != len(expected) {
		t.Fatalf("columns = %v, want %v", meta.Columns, expected)
	}
	for i := range expected {
		if meta.Columns[i] != expected[i] {
			t.Errorf("column[%d] = %q, want %q", i, meta.Columns[i], expected[i])
		}
	}
}

func TestBuildDbSchemaMetadata_NoSegments(t *testing.T) {
	cs := (&schema.SchemaDef{
		RecordType: "T1",
		Program:    "TAN",
		Shared:     []schema.FieldDef{{Name: "RecordType"}},
		Segments:   nil,
	}).Compile()
	cs.Path = "tanf/t1"

	meta := buildDbSchemaMetadata(cs)

	expectedColumns := []string{"RecordType", "id", "datafile_id", "line_number"}
	if len(meta.Columns) != len(expectedColumns) {
		t.Fatalf("got %d columns, want %d: %v", len(meta.Columns), len(expectedColumns), meta.Columns)
	}
	for i, want := range expectedColumns {
		if meta.Columns[i] != want {
			t.Errorf("column[%d] = %q, want %q", i, meta.Columns[i], want)
		}
	}
}

func TestBuildDbSchemaMetadata_MultipleSegmentsUsesFirst(t *testing.T) {
	cs := (&schema.SchemaDef{
		RecordType: "T3",
		Program:    "TAN",
		Shared:     []schema.FieldDef{{Name: "RecordType"}, {Name: "RPT_MONTH_YEAR"}},
		Segments: []schema.SegmentDef{
			{Fields: []schema.FieldDef{{Name: "FAMILY_AFFILIATION"}, {Name: "SSN"}}},
			{Fields: []schema.FieldDef{{Name: "FAMILY_AFFILIATION"}, {Name: "SSN"}}},
		},
	}).Compile()
	cs.Path = "tanf/t3"

	meta := buildDbSchemaMetadata(cs)

	// 2 shared + 2 segment (first only) + 3 standard = 7
	if len(meta.Columns) != 7 {
		t.Fatalf("got %d columns, want 7: %v", len(meta.Columns), meta.Columns)
	}

	count := 0
	for _, col := range meta.Columns {
		if col == "FAMILY_AFFILIATION" {
			count++
		}
	}
	if count != 1 {
		t.Errorf("FAMILY_AFFILIATION appears %d times, want 1", count)
	}
}

func TestBuildDbSchemaMetadata_EmptySchema(t *testing.T) {
	cs := (&schema.SchemaDef{
		RecordType: "T1",
		Program:    "TAN",
		Shared:     nil,
		Segments:   nil,
	}).Compile()
	cs.Path = "tanf/t1"

	meta := buildDbSchemaMetadata(cs)

	if len(meta.Columns) != 3 {
		t.Fatalf("expected 3 standard columns, got %d: %v", len(meta.Columns), meta.Columns)
	}
	if meta.Columns[0] != "id" || meta.Columns[1] != "datafile_id" || meta.Columns[2] != "line_number" {
		t.Errorf("standard columns = %v, want [id, datafile_id, line_number]", meta.Columns)
	}
}

// ---------------------------------------------------------------------------
// SetContentTypeIDs unit tests
// ---------------------------------------------------------------------------

func TestSetContentTypeIDs_PartialMatch(t *testing.T) {
	schemas := map[string]*schema.CompiledSchema{
		"tanf/t1": (&schema.SchemaDef{RecordType: "T1", Shared: []schema.FieldDef{{Name: "RecordType"}}}).Compile(),
		"ssp/m1":  (&schema.SchemaDef{RecordType: "M1", Shared: []schema.FieldDef{{Name: "RecordType"}}}).Compile(),
		"tanf/t2": (&schema.SchemaDef{RecordType: "T2", Shared: []schema.FieldDef{{Name: "RecordType"}}}).Compile(),
	}
	schemas["tanf/t1"].Path = "tanf/t1"
	schemas["ssp/m1"].Path = "ssp/m1"
	schemas["tanf/t2"].Path = "tanf/t2"

	reg := NewTestRegistry(schemas)
	reg.buildAllMetadata()

	contentTypes := map[string]int32{
		"tanf_t1": 10,
		"ssp_m1":  20,
		// tanf_t2 intentionally missing
	}
	reg.SetContentTypeIDs(contentTypes)

	meta := reg.GetSchemaMetadata("tanf/t1")
	if meta == nil || meta.ContentTypeID == nil || *meta.ContentTypeID != 10 {
		t.Error("tanf/t1 content type should be 10")
	}

	meta = reg.GetSchemaMetadata("ssp/m1")
	if meta == nil || meta.ContentTypeID == nil || *meta.ContentTypeID != 20 {
		t.Error("ssp/m1 content type should be 20")
	}

	meta = reg.GetSchemaMetadata("tanf/t2")
	if meta == nil {
		t.Fatal("tanf/t2 metadata not found")
	}
	if meta.ContentTypeID != nil {
		t.Errorf("tanf/t2 content type = %d, want nil", *meta.ContentTypeID)
	}
}

func TestSetContentTypeIDs_EmptyMap(t *testing.T) {
	schemas := map[string]*schema.CompiledSchema{
		"tanf/t1": (&schema.SchemaDef{RecordType: "T1", Shared: []schema.FieldDef{{Name: "RecordType"}}}).Compile(),
	}
	schemas["tanf/t1"].Path = "tanf/t1"

	reg := NewTestRegistry(schemas)
	reg.buildAllMetadata()

	reg.SetContentTypeIDs(map[string]int32{})

	meta := reg.GetSchemaMetadata("tanf/t1")
	if meta == nil {
		t.Fatal("metadata not found")
	}
	if meta.ContentTypeID != nil {
		t.Error("expected nil content type with empty map")
	}
}

func TestGetSchemaMetadata_NonExistent(t *testing.T) {
	reg := NewTestRegistry(map[string]*schema.CompiledSchema{})

	if reg.GetSchemaMetadata("nonexistent") != nil {
		t.Error("expected nil for non-existent schema metadata")
	}
}
