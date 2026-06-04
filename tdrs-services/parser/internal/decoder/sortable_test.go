package decoder

import (
	"iter"
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
)

// testDecoder implements Decoder for testing.
type testDecoder struct {
	Sortable
	rows []Row
}

func (d *testDecoder) Format() filespec.Format { return filespec.FormatPositional }
func (d *testDecoder) ReadFirst() (Row, error) { return nil, nil }
func (d *testDecoder) Close() error            { return nil }
func (d *testDecoder) Sort(det *RecordTypeDetector, keyFields []filespec.KeyFieldDef, gs []string) error {
	return d.Sortable.DoSort(d.unsortedRows(), det, keyFields, gs)
}
func (d *testDecoder) Rows() iter.Seq2[Row, error] {
	if d.IsSorted() {
		return d.SortedRows()
	}
	return d.unsortedRows()
}
func (d *testDecoder) unsortedRows() iter.Seq2[Row, error] {
	return func(yield func(Row, error) bool) {
		for _, row := range d.rows {
			if !yield(row, nil) {
				return
			}
		}
	}
}

func makeTestRow(lineNum int, data string) *PositionalRow {
	rt := ""
	if len(data) >= 7 && data[:7] == "TRAILER" {
		rt = "TRAILER"
	} else if len(data) >= 6 && data[:6] == "HEADER" {
		rt = "HEADER"
	} else if len(data) >= 2 {
		rt = data[:2]
	}
	return NewPositionalRow(lineNum, rt, len(data), data)
}

func testPositionalKeyFields() []filespec.KeyFieldDef {
	return []filespec.KeyFieldDef{
		{Name: "rpt_month_year", PositionDef: filespec.PositionDef{Start: 2, End: 8}},
		{Name: "case_number", PositionDef: filespec.PositionDef{Start: 8, End: 19}},
	}
}

func buildTestDetector() *RecordTypeDetector {
	schemas := map[string]*schema.CompiledSchema{
		"common/header":  {SchemaDef: &schema.SchemaDef{RecordType: "HEADER"}, Path: "common/header"},
		"common/trailer": {SchemaDef: &schema.SchemaDef{RecordType: "TRAILER"}, Path: "common/trailer"},
		"tanf/t1":        {SchemaDef: &schema.SchemaDef{RecordType: "T1"}, Path: "tanf/t1"},
		"tanf/t2":        {SchemaDef: &schema.SchemaDef{RecordType: "T2"}, Path: "tanf/t2"},
		"tanf/t3":        {SchemaDef: &schema.SchemaDef{RecordType: "T3"}, Path: "tanf/t3"},
	}
	registry := config.NewTestRegistry(schemas)

	spec := &filespec.FileSpec{
		Program: "TAN",
		Section: 1,
		Format:  filespec.FormatPositional,
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
	}

	return NewRecordTypeDetector(spec, registry)
}

func TestSortable_SortsByKey(t *testing.T) {
	detector := buildTestDetector()
	keyFields := testPositionalKeyFields()
	groupedSchemas := []string{"tanf/t1", "tanf/t2", "tanf/t3"}

	dec := &testDecoder{
		rows: []Row{
			makeTestRow(1, "T1202401CASE002    rest-of-data"),
			makeTestRow(2, "T2202401CASE002    rest-of-data"),
			makeTestRow(3, "T1202401CASE001    rest-of-data"),
			makeTestRow(4, "T2202401CASE001    rest-of-data"),
		},
	}

	err := dec.Sort(detector, keyFields, groupedSchemas)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	if len(rows) != 4 {
		t.Fatalf("expected 4 rows, got %d", len(rows))
	}

	// After sort: CASE001 rows should come first
	expectedLineNums := []int{3, 4, 1, 2}
	for i, row := range rows {
		if row.LineNum() != expectedLineNums[i] {
			t.Errorf("row %d: expected line %d, got %d", i, expectedLineNums[i], row.LineNum())
		}
	}
}

func TestSortable_RetainsFileLevelAndUnkeyedRows(t *testing.T) {
	detector := buildTestDetector()
	keyFields := testPositionalKeyFields()
	groupedSchemas := []string{"tanf/t1", "tanf/t2", "tanf/t3"}

	dec := &testDecoder{
		rows: []Row{
			makeTestRow(1, "T1202401CASE001    rest-of-data"),
			makeTestRow(2, "TRAILER0000001000000000000000001T10000000000000000"),
			makeTestRow(3, "XX202401CASE001    bogus-data"), // unrecognized
			makeTestRow(4, "T1short"),                       // too short for key
		},
	}

	err := dec.Sort(detector, keyFields, groupedSchemas)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	// 1 sorted data row + 3 unkeyed rows (trailer + XX unrecognized + T1short)
	if len(rows) != 4 {
		t.Fatalf("expected 4 rows (1 sorted + 3 unkeyed), got %d", len(rows))
	}

	// First row should be the sorted data row
	if rows[0].LineNum() != 1 {
		t.Errorf("expected sorted row at line 1, got line %d", rows[0].LineNum())
	}

	// Unkeyed rows follow in original order.
	if rows[1].LineNum() != 2 {
		t.Errorf("expected trailer row at line 2, got line %d", rows[1].LineNum())
	}
	if rows[2].LineNum() != 3 {
		t.Errorf("expected unkeyed row at line 3, got line %d", rows[2].LineNum())
	}
	if rows[3].LineNum() != 4 {
		t.Errorf("expected unkeyed row at line 4, got line %d", rows[3].LineNum())
	}
}

func TestSortable_UnsortedWhenNotSorted(t *testing.T) {
	dec := &testDecoder{
		rows: []Row{
			makeTestRow(3, "T1202401CASE002    rest-of-data"),
			makeTestRow(1, "T1202401CASE001    rest-of-data"),
		},
	}

	// Without calling Sort(), Rows() should return original order
	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	if len(rows) != 2 {
		t.Fatalf("expected 2 rows, got %d", len(rows))
	}
	if rows[0].LineNum() != 3 {
		t.Errorf("expected first row at line 3, got line %d", rows[0].LineNum())
	}
	if rows[1].LineNum() != 1 {
		t.Errorf("expected second row at line 1, got line %d", rows[1].LineNum())
	}
}

func TestSortable_StableSort(t *testing.T) {
	detector := buildTestDetector()
	keyFields := testPositionalKeyFields()
	groupedSchemas := []string{"tanf/t1", "tanf/t2", "tanf/t3"}

	// Multiple records for same case — must preserve T1, T2, T3 order
	dec := &testDecoder{
		rows: []Row{
			makeTestRow(1, "T1202401CASE001    rest-of-data"),
			makeTestRow(2, "T2202401CASE001    rest-of-data"),
			makeTestRow(3, "T3202401CASE001    rest-of-data"),
		},
	}

	err := dec.Sort(detector, keyFields, groupedSchemas)
	if err != nil {
		t.Fatalf("Sort failed: %v", err)
	}

	var rows []Row
	for row, err := range dec.Rows() {
		if err != nil {
			t.Fatalf("Rows() error: %v", err)
		}
		rows = append(rows, row)
	}

	expectedLineNums := []int{1, 2, 3}
	for i, row := range rows {
		if row.LineNum() != expectedLineNums[i] {
			t.Errorf("row %d: expected line %d, got %d", i, expectedLineNums[i], row.LineNum())
		}
	}
}
