package parser

import (
	"testing"

	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
)

// buildSchemaWithPool creates a CompiledSchema with an initialized record pool.
// shared and segments are used directly; the pool allocator creates ParsedRecords.
func buildSchemaWithPool(recordType string, shared []schema.FieldDef, segments []schema.SegmentDef) *schema.CompiledSchema {
	sdef := &schema.SchemaDef{
		RecordType: recordType,
		Shared:     shared,
		Segments:   segments,
	}
	cs := sdef.Compile()
	cs.InitPool(func() any {
		return &ParsedRecord{
			Schema: cs,
			Fields: make([]ParsedField, cs.FieldCount),
		}
	})
	return cs
}

// --- NewParsingOrchestrator tests ---

func TestNewParsingOrchestrator_Positional(t *testing.T) {
	ctx := &ParseContext{}
	o := NewParsingOrchestrator(filespec.FormatPositional, ctx)

	if o == nil {
		t.Fatal("NewParsingOrchestrator returned nil")
	}
	if o.parseCtx != ctx {
		t.Error("parseCtx not set correctly")
	}
	if _, ok := o.extractor.(*PositionalExtractor); !ok {
		t.Errorf("expected PositionalExtractor, got %T", o.extractor)
	}
}

func TestNewParsingOrchestrator_Columnar(t *testing.T) {
	ctx := &ParseContext{}
	o := NewParsingOrchestrator(filespec.FormatColumnar, ctx)

	if o == nil {
		t.Fatal("NewParsingOrchestrator returned nil")
	}
	if _, ok := o.extractor.(*ColumnarExtractor); !ok {
		t.Errorf("expected ColumnarExtractor, got %T", o.extractor)
	}
}

// --- parseRow tests ---

func TestParseRow_NoSegments(t *testing.T) {
	cs := buildSchemaWithPool("T1",
		[]schema.FieldDef{{Name: "record_type", Type: "string", Start: 0, End: 2}},
		nil, // no segments
	)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	row := decoder.NewPositionalRow(1, "T1", 10, "T1abcdefgh")
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if records != nil {
		t.Errorf("parseRow() with no segments should return nil, got %d records", len(records))
	}
}

func TestParseRow_SingleSegment(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
		{Name: "rpt_month_year", Type: "string", Start: 2, End: 8},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "case_number", Type: "string", Start: 8, End: 19},
			{Name: "county_code", Type: "string", Start: 19, End: 22},
		}},
	}
	cs := buildSchemaWithPool("T1", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	data := "T1202401CASE001    044rest-of-data"
	row := decoder.NewPositionalRow(5, "T1", len(data), data)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if len(records) != 1 {
		t.Fatalf("parseRow() returned %d records, want 1", len(records))
	}

	rec := records[0]
	if rec.LineNumber != 5 {
		t.Errorf("LineNumber = %d, want 5", rec.LineNumber)
	}
	if rec.SegmentIndex != 0 {
		t.Errorf("SegmentIndex = %d, want 0", rec.SegmentIndex)
	}
	if rec.DecodedSize != len(data) {
		t.Errorf("DecodedSize = %d, want %d", rec.DecodedSize, len(data))
	}

	// Verify shared fields were copied into the record
	if got := rec.Get("record_type"); got != "T1" {
		t.Errorf("record_type = %v, want T1", got)
	}
	if got := rec.Get("rpt_month_year"); got != "202401" {
		t.Errorf("rpt_month_year = %v, want 202401", got)
	}

	// Verify segment fields
	if got := rec.Get("case_number"); got != "CASE001    " {
		t.Errorf("case_number = %q, want %q", got, "CASE001    ")
	}
	if got := rec.Get("county_code"); got != "044" {
		t.Errorf("county_code = %v, want 044", got)
	}
}

func TestParseRow_MultiSegment(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
	}
	// Two segments with same field names but different positions
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "ssn", Type: "string", Start: 2, End: 11},
		}},
		{Fields: []schema.FieldDef{
			{Name: "ssn", Type: "string", Start: 11, End: 20},
		}},
	}
	cs := buildSchemaWithPool("T3", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	data := "T3111222333444555666"
	row := decoder.NewPositionalRow(10, "T3", len(data), data)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if len(records) != 2 {
		t.Fatalf("parseRow() returned %d records, want 2", len(records))
	}

	// First segment
	if records[0].SegmentIndex != 0 {
		t.Errorf("records[0].SegmentIndex = %d, want 0", records[0].SegmentIndex)
	}
	if got := records[0].Get("record_type"); got != "T3" {
		t.Errorf("records[0] record_type = %v, want T3", got)
	}
	if got := records[0].Get("ssn"); got != "111222333" {
		t.Errorf("records[0] ssn = %v, want 111222333", got)
	}

	// Second segment
	if records[1].SegmentIndex != 1 {
		t.Errorf("records[1].SegmentIndex = %d, want 1", records[1].SegmentIndex)
	}
	if got := records[1].Get("record_type"); got != "T3" {
		t.Errorf("records[1] record_type = %v, want T3", got)
	}
	if got := records[1].Get("ssn"); got != "444555666" {
		t.Errorf("records[1] ssn = %v, want 444555666", got)
	}
}

func TestParseRow_MissingRequiredField_Segment0(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			// Required field at position that contains only spaces (will be nil after convert)
			{Name: "important", Type: "string", Start: 2, End: 5, Required: true},
		}},
	}
	cs := buildSchemaWithPool("T1", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	// Spaces at positions 2-5 will convert to nil for string type
	data := "T1   rest"
	row := decoder.NewPositionalRow(1, "T1", len(data), data)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if len(records) != 1 {
		t.Fatalf("parseRow() returned %d records, want 1 (record should survive for validation)", len(records))
	}
	if got := records[0].Get("important"); got != nil {
		t.Errorf("important = %v, want nil", got)
	}
	if !records[0].IsFieldRequired("important") {
		t.Error("important should retain required field metadata for validation")
	}
}

func TestParseRow_MissingField_Segment1_SkipsRecord(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "ssn", Type: "string", Start: 2, End: 11},
		}},
		{Fields: []schema.FieldDef{
			// Second segment field that will be blank (nil) - should be skipped
			// because segIdx >= 1 even without Required flag
			{Name: "ssn", Type: "string", Start: 11, End: 20},
		}},
	}
	cs := buildSchemaWithPool("T3", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	// Data has first SSN but second SSN is all spaces
	data := "T3111222333         "
	row := decoder.NewPositionalRow(1, "T3", len(data), data)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	// Only segment 0 should be present; segment 1 has nil field and segIdx >= 1
	if len(records) != 1 {
		t.Fatalf("parseRow() returned %d records, want 1", len(records))
	}
	if records[0].SegmentIndex != 0 {
		t.Errorf("SegmentIndex = %d, want 0", records[0].SegmentIndex)
	}
}

func TestParseRow_ComputedOnlySegment1_SkipsRecord(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "calendar_quarter", Type: "string", Start: 0, End: 5},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "rpt_month_year", Type: "string", SourceField: "calendar_quarter"},
			{Name: "families_month", Type: "string", Start: 5, End: 8},
		}},
		{Fields: []schema.FieldDef{
			{Name: "rpt_month_year", Type: "string", SourceField: "calendar_quarter"},
			{Name: "families_month", Type: "string", Start: 8, End: 11},
		}},
	}
	cs := buildSchemaWithPool("T7", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	// Segment 0 has data, segment 1 only has the computed/source field.
	data := "20241ABC   "
	row := decoder.NewPositionalRow(1, "T7", len(data), data)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if len(records) != 1 {
		t.Fatalf("parseRow() returned %d records, want 1", len(records))
	}
	if records[0].SegmentIndex != 0 {
		t.Errorf("SegmentIndex = %d, want 0", records[0].SegmentIndex)
	}
}

func TestParseRow_OptionalField_Segment0_Included(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			// Optional field with blank value in segment 0 should NOT cause skip
			{Name: "optional_field", Type: "string", Start: 2, End: 5, Required: false},
		}},
	}
	cs := buildSchemaWithPool("T1", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	data := "T1   rest"
	row := decoder.NewPositionalRow(1, "T1", len(data), data)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if len(records) != 1 {
		t.Errorf("parseRow() returned %d records, want 1 (optional nil field in segment 0 should not skip)", len(records))
	}
}

// --- processGroup / ParseBatch tests ---

func TestParseBatch_SingleGroupSingleSegment(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
		{Name: "rpt_month_year", Type: "string", Start: 2, End: 8},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "case_number", Type: "string", Start: 8, End: 19},
		}},
	}
	cs := buildSchemaWithPool("T1", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	data := "T1202401CASE001    rest-of-data"
	row := decoder.NewPositionalRow(1, "T1", len(data), data)

	batch := &DecodedBatch{
		BatchID: 42,
		DecodedGroups: []*DecodedGroup{
			{
				Key:          "202401|CASE001",
				RptMonthYear: "202401",
				CaseNumber:   "CASE001",
				DecodedRecords: []DecodedRecord{
					{Row: row, Schema: cs},
				},
			},
		},
	}

	result := o.ParseBatch(batch)

	if result.BatchID != 42 {
		t.Errorf("BatchID = %d, want 42", result.BatchID)
	}
	if len(result.Groups) != 1 {
		t.Fatalf("len(Groups) = %d, want 1", len(result.Groups))
	}

	group := result.Groups[0]
	if len(group.Records) != 1 {
		t.Fatalf("len(Records) = %d, want 1", len(group.Records))
	}

	rec := group.Records[0]
	if got := rec.Get("record_type"); got != "T1" {
		t.Errorf("record_type = %v, want T1", got)
	}
	if got := rec.Get("rpt_month_year"); got != "202401" {
		t.Errorf("rpt_month_year = %v, want 202401", got)
	}
	if got := rec.Get("case_number"); got != "CASE001    " {
		t.Errorf("case_number = %q, want %q", got, "CASE001    ")
	}
}

func TestParseBatch_MultipleGroups(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "value", Type: "string", Start: 2, End: 5},
		}},
	}
	cs := buildSchemaWithPool("T1", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	row1 := decoder.NewPositionalRow(1, "T1", 10, "T1AAA_____")
	row2 := decoder.NewPositionalRow(2, "T1", 10, "T1BBB_____")
	row3 := decoder.NewPositionalRow(3, "T1", 10, "T1CCC_____")

	batch := &DecodedBatch{
		BatchID: 1,
		DecodedGroups: []*DecodedGroup{
			{
				Key:            "key1",
				RptMonthYear:   "202401",
				CaseNumber:     "CASE1",
				DecodedRecords: []DecodedRecord{{Row: row1, Schema: cs}},
			},
			{
				Key:            "key2",
				RptMonthYear:   "202402",
				CaseNumber:     "CASE2",
				DecodedRecords: []DecodedRecord{{Row: row2, Schema: cs}, {Row: row3, Schema: cs}},
			},
		},
	}

	result := o.ParseBatch(batch)

	if len(result.Groups) != 2 {
		t.Fatalf("len(Groups) = %d, want 2", len(result.Groups))
	}
	if len(result.Groups[0].Records) != 1 {
		t.Errorf("group[0] records = %d, want 1", len(result.Groups[0].Records))
	}
	if len(result.Groups[1].Records) != 2 {
		t.Errorf("group[1] records = %d, want 2", len(result.Groups[1].Records))
	}
	if result.TotalRecords() != 3 {
		t.Errorf("TotalRecords() = %d, want 3", result.TotalRecords())
	}
}

func TestParseBatch_PreservesGroupMetadata(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "value", Type: "string", Start: 2, End: 5},
		}},
	}
	cs := buildSchemaWithPool("T1", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	row := decoder.NewPositionalRow(1, "T1", 10, "T1AAA_____")

	batch := &DecodedBatch{
		BatchID: 7,
		DecodedGroups: []*DecodedGroup{
			{
				Key:            "202403|MYCASE",
				RptMonthYear:   "202403",
				CaseNumber:     "MYCASE",
				DecodedRecords: []DecodedRecord{{Row: row, Schema: cs}},
			},
		},
	}

	result := o.ParseBatch(batch)

	group := result.Groups[0]
	if group.Key != "202403|MYCASE" {
		t.Errorf("Key = %q, want %q", group.Key, "202403|MYCASE")
	}
	if group.RptMonthYear != "202403" {
		t.Errorf("RptMonthYear = %q, want %q", group.RptMonthYear, "202403")
	}
	if group.CaseNumber != "MYCASE" {
		t.Errorf("CaseNumber = %q, want %q", group.CaseNumber, "MYCASE")
	}
}

func TestParseBatch_EmptyBatch(t *testing.T) {
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	batch := &DecodedBatch{
		BatchID:       99,
		DecodedGroups: []*DecodedGroup{},
	}

	result := o.ParseBatch(batch)

	if result.BatchID != 99 {
		t.Errorf("BatchID = %d, want 99", result.BatchID)
	}
	if len(result.Groups) != 0 {
		t.Errorf("len(Groups) = %d, want 0", len(result.Groups))
	}
	if result.TotalRecords() != 0 {
		t.Errorf("TotalRecords() = %d, want 0", result.TotalRecords())
	}
}

func TestParseBatch_GroupWithEmptyRecords(t *testing.T) {
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	batch := &DecodedBatch{
		BatchID: 1,
		DecodedGroups: []*DecodedGroup{
			{
				Key:            "key",
				DecodedRecords: []DecodedRecord{},
			},
		},
	}

	result := o.ParseBatch(batch)

	if len(result.Groups) != 1 {
		t.Fatalf("len(Groups) = %d, want 1", len(result.Groups))
	}
	if len(result.Groups[0].Records) != 0 {
		t.Errorf("len(Records) = %d, want 0", len(result.Groups[0].Records))
	}
}

// --- Columnar format tests ---

func TestParseRow_ColumnarFormat(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Column: 0},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "name", Type: "string", Column: 1},
			{Name: "age", Type: "string", Column: 2},
		}},
	}
	cs := buildSchemaWithPool("FRA", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatColumnar, &ParseContext{})

	columns := []any{"FRA", "Alice", "30"}
	row := decoder.NewColumnarRow(3, "FRA", 3, columns)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if len(records) != 1 {
		t.Fatalf("parseRow() returned %d records, want 1", len(records))
	}

	rec := records[0]
	if rec.LineNumber != 3 {
		t.Errorf("LineNumber = %d, want 3", rec.LineNumber)
	}
	if got := rec.Get("record_type"); got != "FRA" {
		t.Errorf("record_type = %v, want FRA", got)
	}
	if got := rec.Get("name"); got != "Alice" {
		t.Errorf("name = %v, want Alice", got)
	}
	if got := rec.Get("age"); got != "30" {
		t.Errorf("age = %v, want 30", got)
	}
}

func TestParseBatch_ColumnarFormat(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Column: 0},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "value", Type: "string", Column: 1},
		}},
	}
	cs := buildSchemaWithPool("FRA", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatColumnar, &ParseContext{})

	row1 := decoder.NewColumnarRow(1, "FRA", 2, []any{"FRA", "val1"})
	row2 := decoder.NewColumnarRow(2, "FRA", 2, []any{"FRA", "val2"})

	batch := &DecodedBatch{
		BatchID: 5,
		DecodedGroups: []*DecodedGroup{
			{
				Key: "group1",
				DecodedRecords: []DecodedRecord{
					{Row: row1, Schema: cs},
					{Row: row2, Schema: cs},
				},
			},
		},
	}

	result := o.ParseBatch(batch)

	if result.BatchID != 5 {
		t.Errorf("BatchID = %d, want 5", result.BatchID)
	}
	if len(result.Groups[0].Records) != 2 {
		t.Fatalf("len(Records) = %d, want 2", len(result.Groups[0].Records))
	}
	if got := result.Groups[0].Records[0].Get("value"); got != "val1" {
		t.Errorf("record[0] value = %v, want val1", got)
	}
	if got := result.Groups[0].Records[1].Get("value"); got != "val2" {
		t.Errorf("record[1] value = %v, want val2", got)
	}
}

// --- Integer field type tests ---

func TestParseRow_IntegerFieldType(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "count", Type: "integer", Start: 2, End: 5},
		}},
	}
	cs := buildSchemaWithPool("T1", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	data := "T1042rest"
	row := decoder.NewPositionalRow(1, "T1", len(data), data)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if len(records) != 1 {
		t.Fatalf("parseRow() returned %d records, want 1", len(records))
	}

	got := records[0].Get("count")
	if got != 42 {
		t.Errorf("count = %v (%T), want 42 (int)", got, got)
	}
}

// --- Shared fields are present in all segment records ---

func TestParseRow_SharedFieldsCopiedToAllSegments(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Start: 0, End: 2},
		{Name: "rpt_month_year", Type: "string", Start: 2, End: 8},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "ssn", Type: "string", Start: 8, End: 17},
		}},
		{Fields: []schema.FieldDef{
			{Name: "ssn", Type: "string", Start: 17, End: 26},
		}},
	}
	cs := buildSchemaWithPool("T3", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatPositional, &ParseContext{})

	data := "T3202401111222333444555666"
	row := decoder.NewPositionalRow(1, "T3", len(data), data)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if len(records) != 2 {
		t.Fatalf("parseRow() returned %d records, want 2", len(records))
	}

	// Both segment records should have the shared fields
	for i, rec := range records {
		if got := rec.Get("record_type"); got != "T3" {
			t.Errorf("records[%d] record_type = %v, want T3", i, got)
		}
		if got := rec.Get("rpt_month_year"); got != "202401" {
			t.Errorf("records[%d] rpt_month_year = %v, want 202401", i, got)
		}
	}

	// Segment-specific fields should differ
	if got := records[0].Get("ssn"); got != "111222333" {
		t.Errorf("records[0] ssn = %v, want 111222333", got)
	}
	if got := records[1].Get("ssn"); got != "444555666" {
		t.Errorf("records[1] ssn = %v, want 444555666", got)
	}
}

func TestParseRow_ColumnarNilColumn_SkipsSegment1(t *testing.T) {
	shared := []schema.FieldDef{
		{Name: "record_type", Type: "string", Column: 0},
	}
	segments := []schema.SegmentDef{
		{Fields: []schema.FieldDef{
			{Name: "val", Type: "string", Column: 1},
		}},
		{Fields: []schema.FieldDef{
			// Column 2 will be out of bounds (nil) -> nil value -> segIdx >= 1 -> skip
			{Name: "val", Type: "string", Column: 2},
		}},
	}
	cs := buildSchemaWithPool("T3", shared, segments)
	o := NewParsingOrchestrator(filespec.FormatColumnar, &ParseContext{})

	// Only 2 columns; column index 2 is out of bounds
	columns := []any{"T3", "present"}
	row := decoder.NewColumnarRow(1, "T3", 2, columns)
	records, err := o.parseRow(DecodedRecord{Row: row, Schema: cs})

	if err != nil {
		t.Fatalf("parseRow() error = %v", err)
	}
	if len(records) != 1 {
		t.Fatalf("parseRow() returned %d records, want 1 (segment 1 should be skipped)", len(records))
	}
	if records[0].SegmentIndex != 0 {
		t.Errorf("SegmentIndex = %d, want 0", records[0].SegmentIndex)
	}
}
