package parser

import (
	"iter"
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
)

// mockDecoder implements decoder.Decoder for testing.
type mockDecoder struct {
	header decoder.Row
	rows   []decoder.Row
}

func (d *mockDecoder) Format() filespec.Format         { return filespec.FormatPositional }
func (d *mockDecoder) ReadFirst() (decoder.Row, error) { return d.header, nil }
func (d *mockDecoder) Close() error                    { return nil }
func (d *mockDecoder) Sort(_ *decoder.RecordTypeDetector, _ []filespec.KeyFieldDef, _ []string) error {
	return nil
}

func (d *mockDecoder) Rows() iter.Seq2[decoder.Row, error] {
	return func(yield func(decoder.Row, error) bool) {
		for _, row := range d.rows {
			if !yield(row, nil) {
				return
			}
		}
	}
}

// buildTestRegistry creates a minimal registry with the given schemas.
func buildTestRegistry(schemas map[string]*schema.CompiledSchema) *config.Registry {
	return config.NewTestRegistry(schemas)
}

// buildTANFS1Spec creates a TANF Section 1 filespec for testing.
func buildTANFS1Spec() *filespec.FileSpec {
	batchSize := 1
	return &filespec.FileSpec{
		Program: "TAN",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{"common/header", "common/trailer", "tanf/t1", "tanf/t2", "tanf/t3"},
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "prefix",
			Prefixes: []filespec.PrefixMapping{
				{Prefix: "HEADER", Schema: "common/header"},
				{Prefix: "TRAILER", Schema: "common/trailer"},
				{Prefix: "T1", Schema: "tanf/t1"},
				{Prefix: "T2", Schema: "tanf/t2"},
				{Prefix: "T3", Schema: "tanf/t3"},
			},
		},
		Accumulator: filespec.AccumulatorConfig{
			KeyFields: &filespec.KeyFieldsConfig{
				Fields: []filespec.KeyFieldDef{
					{Name: "rpt_month_year", PositionDef: filespec.PositionDef{Start: 2, End: 8}},
					{Name: "case_number", PositionDef: filespec.PositionDef{Start: 8, End: 19}},
				},
			},
			BatchSize:      &batchSize,
			GroupedSchemas: []string{"tanf/t1", "tanf/t2", "tanf/t3"},
			Presort:        true,
		},
	}
}

// buildTestSchemas creates minimal compiled schemas for testing.
func buildTestSchemas() map[string]*schema.CompiledSchema {
	return map[string]*schema.CompiledSchema{
		"common/header": {
			SchemaDef: &schema.SchemaDef{RecordType: "HEADER"},
			Path:      "common/header",
		},
		"common/trailer": {
			SchemaDef: &schema.SchemaDef{RecordType: "TRAILER"},
			Path:      "common/trailer",
		},
		"tanf/t1": {
			SchemaDef: &schema.SchemaDef{RecordType: "T1"},
			Path:      "tanf/t1",
		},
		"tanf/t2": {
			SchemaDef: &schema.SchemaDef{RecordType: "T2"},
			Path:      "tanf/t2",
		},
		"tanf/t3": {
			SchemaDef: &schema.SchemaDef{RecordType: "T3"},
			Path:      "tanf/t3",
		},
	}
}

// makeRow creates a PositionalRow with the given line number and data.
func makeRow(lineNum int, data string) *decoder.PositionalRow {
	// Detect record type from prefix
	rt := ""
	if len(data) >= 7 && data[:7] == "TRAILER" {
		rt = "TRAILER"
	} else if len(data) >= 6 && data[:6] == "HEADER" {
		rt = "HEADER"
	} else if len(data) >= 2 {
		rt = data[:2]
	}
	return decoder.NewPositionalRow(lineNum, rt, len(data), data)
}

func testSorterPositionalKeyFields() []filespec.KeyFieldDef {
	return []filespec.KeyFieldDef{
		{Name: "rpt_month_year", PositionDef: filespec.PositionDef{Start: 2, End: 8}},
		{Name: "case_number", PositionDef: filespec.PositionDef{Start: 8, End: 19}},
	}
}

func TestSorter_SortsByKey(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := buildTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)

	// Rows with interleaved cases: CASE002 before CASE001
	// Key positions: rpt_month_year=2:8, case_number=8:19
	dec := &mockDecoder{
		rows: []decoder.Row{
			makeRow(1, "T1202401CASE002    rest-of-data"), // line 1, case 002
			makeRow(2, "T2202401CASE002    rest-of-data"), // line 2, case 002
			makeRow(3, "T1202401CASE001    rest-of-data"), // line 3, case 001
			makeRow(4, "T2202401CASE001    rest-of-data"), // line 4, case 001
		},
	}

	sorter := NewSorter(spec, detector)
	result, err := sorter.Sort(dec)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	if len(result.SortedRows) != 4 {
		t.Fatalf("expected 4 sorted rows, got %d", len(result.SortedRows))
	}

	// After sort: CASE001 rows should come first
	// CASE001 was at lines 3,4 in original — should now be first
	if result.SortedRows[0].LineNum() != 3 {
		t.Errorf("expected first sorted row to be line 3 (CASE001 T1), got line %d", result.SortedRows[0].LineNum())
	}
	if result.SortedRows[1].LineNum() != 4 {
		t.Errorf("expected second sorted row to be line 4 (CASE001 T2), got line %d", result.SortedRows[1].LineNum())
	}
	// CASE002 was at lines 1,2 — should now be last
	if result.SortedRows[2].LineNum() != 1 {
		t.Errorf("expected third sorted row to be line 1 (CASE002 T1), got line %d", result.SortedRows[2].LineNum())
	}
	if result.SortedRows[3].LineNum() != 2 {
		t.Errorf("expected fourth sorted row to be line 2 (CASE002 T2), got line %d", result.SortedRows[3].LineNum())
	}
}

func TestSorter_PreservesLineNumbers(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := buildTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)

	dec := &mockDecoder{
		rows: []decoder.Row{
			makeRow(5, "T1202401CASE003    rest-of-data"),
			makeRow(10, "T1202401CASE001    rest-of-data"),
			makeRow(15, "T1202401CASE002    rest-of-data"),
		},
	}

	sorter := NewSorter(spec, detector)
	result, err := sorter.Sort(dec)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	// Line numbers must be preserved from original file
	expectedLineNums := []int{10, 15, 5} // CASE001(10), CASE002(15), CASE003(5)
	for i, row := range result.SortedRows {
		if row.LineNum() != expectedLineNums[i] {
			t.Errorf("row %d: expected LineNum %d, got %d", i, expectedLineNums[i], row.LineNum())
		}
	}
}

func TestSorter_StableSortPreservesRelativeOrder(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := buildTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)

	// Multiple records for same case — must preserve T1, T2, T3 order
	dec := &mockDecoder{
		rows: []decoder.Row{
			makeRow(1, "T1202401CASE001    rest-of-data"),
			makeRow(2, "T2202401CASE001    rest-of-data"),
			makeRow(3, "T3202401CASE001    rest-of-data"),
		},
	}

	sorter := NewSorter(spec, detector)
	result, err := sorter.Sort(dec)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	// Same key → stable sort preserves original order
	expectedLineNums := []int{1, 2, 3}
	for i, row := range result.SortedRows {
		if row.LineNum() != expectedLineNums[i] {
			t.Errorf("row %d: expected LineNum %d, got %d", i, expectedLineNums[i], row.LineNum())
		}
	}
}

func TestSorter_SeparatesTrailer(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := buildTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)

	dec := &mockDecoder{
		rows: []decoder.Row{
			makeRow(1, "T1202401CASE001    rest-of-data"),
			makeRow(2, "TRAILER0000001000000000000000001T10000000000000000"),
		},
	}

	sorter := NewSorter(spec, detector)
	result, err := sorter.Sort(dec)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	if result.Trailer == nil {
		t.Fatal("expected Trailer to be set")
	}
	if result.Trailer.LineNum() != 2 {
		t.Errorf("expected Trailer at line 2, got line %d", result.Trailer.LineNum())
	}
	if len(result.SortedRows) != 1 {
		t.Errorf("expected 1 sorted data row, got %d", len(result.SortedRows))
	}
}

func TestSorter_EmptyFile(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := buildTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)

	dec := &mockDecoder{rows: []decoder.Row{}}

	sorter := NewSorter(spec, detector)
	result, err := sorter.Sort(dec)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	if len(result.SortedRows) != 0 {
		t.Errorf("expected 0 sorted rows, got %d", len(result.SortedRows))
	}
	if result.Header != nil {
		t.Error("expected nil Header")
	}
	if result.Trailer != nil {
		t.Error("expected nil Trailer")
	}
}

func TestSorter_MalformedRowsGoToUnkeyed(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := buildTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)

	dec := &mockDecoder{
		rows: []decoder.Row{
			makeRow(1, "T1202401CASE001    rest-of-data"),
			makeRow(2, "T1short"), // too short for key extraction
			makeRow(3, "T1202401CASE002    rest-of-data"),
		},
	}

	sorter := NewSorter(spec, detector)
	result, err := sorter.Sort(dec)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	if len(result.SortedRows) != 2 {
		t.Errorf("expected 2 sorted rows, got %d", len(result.SortedRows))
	}
	if len(result.UnkeyedRows) != 1 {
		t.Errorf("expected 1 unkeyed row, got %d", len(result.UnkeyedRows))
	}
	if result.UnkeyedRows[0].LineNum() != 2 {
		t.Errorf("expected unkeyed row at line 2, got line %d", result.UnkeyedRows[0].LineNum())
	}
}

func TestSorter_MultipleRptMonths(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := buildTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)

	// Different rpt_month_year values — should sort by month first, then case
	dec := &mockDecoder{
		rows: []decoder.Row{
			makeRow(1, "T1202402CASE001    rest-of-data"), // Feb 2024
			makeRow(2, "T1202401CASE002    rest-of-data"), // Jan 2024
			makeRow(3, "T1202401CASE001    rest-of-data"), // Jan 2024
		},
	}

	sorter := NewSorter(spec, detector)
	result, err := sorter.Sort(dec)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	// Sorted by composite key: "202401|CASE001" < "202401|CASE002" < "202402|CASE001"
	expectedLineNums := []int{3, 2, 1}
	for i, row := range result.SortedRows {
		if row.LineNum() != expectedLineNums[i] {
			t.Errorf("row %d: expected LineNum %d, got %d", i, expectedLineNums[i], row.LineNum())
		}
	}
}

func TestSorter_UnrecognizedRecordType(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := buildTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)

	dec := &mockDecoder{
		rows: []decoder.Row{
			makeRow(1, "T1202401CASE001    rest-of-data"),
			makeRow(2, "XX202401CASE001    bogus-data"), // unrecognized prefix
			makeRow(3, "T2202401CASE001    rest-of-data"),
		},
	}

	sorter := NewSorter(spec, detector)
	result, err := sorter.Sort(dec)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	if len(result.SortedRows) != 2 {
		t.Errorf("expected 2 sorted rows, got %d", len(result.SortedRows))
	}
	if len(result.UnkeyedRows) != 1 {
		t.Errorf("expected 1 unkeyed row, got %d", len(result.UnkeyedRows))
	}
}

func TestRowKeyExtraction_ExtractKey(t *testing.T) {
	row := makeRow(1, "T1202401CASE001    rest-of-data")
	key, err := row.ExtractKey(testSorterPositionalKeyFields())
	if err != nil {
		t.Fatalf("ExtractKey failed: %v", err)
	}
	if key != "202401|CASE001    " {
		t.Errorf("expected key '202401|CASE001    ', got %q", key)
	}
}

func TestRowKeyExtraction_TooShort(t *testing.T) {
	row := makeRow(1, "T1short")
	_, err := row.ExtractKey(testSorterPositionalKeyFields())
	if err == nil {
		t.Fatal("expected error for short row")
	}
}
