package parser

import (
	"testing"

	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
)

// buildHeaderSchema creates a compiled header schema matching config/schemas/common/header.yaml.
// All fields are in a single segment with no shared fields.
func buildHeaderSchema() *schema.CompiledSchema {
	sdef := &schema.SchemaDef{
		RecordType: "HEADER",
		Program:    "ALL",
		Section:    0,
		Document:   "Header Record",
		Format:     "positional",
		Shared:     []schema.FieldDef{},
		Segments: []schema.SegmentDef{
			{Fields: []schema.FieldDef{
				{Name: "title", FriendlyName: "Title", Item: "1", Type: "string", Start: 0, End: 6, Required: true},
				{Name: "year", FriendlyName: "Calendar Year", Item: "2", Type: "integer", Start: 6, End: 10, Required: true},
				{Name: "quarter", FriendlyName: "Calendar Quarter", Item: "3", Type: "string", Start: 10, End: 11, Required: true},
				{Name: "type", FriendlyName: "Type", Item: "4", Type: "string", Start: 11, End: 12, Required: true},
				{Name: "state_fips", FriendlyName: "State FIPS Code", Item: "5", Type: "string", Start: 12, End: 14},
				{Name: "tribe_code", FriendlyName: "Tribe Code", Item: "6", Type: "string", Start: 14, End: 17},
				{Name: "program_type", FriendlyName: "Program Type", Item: "7", Type: "string", Start: 17, End: 20, Required: true},
				{Name: "edit", FriendlyName: "Edit Indicator", Item: "8", Type: "string", Start: 20, End: 21, Required: true},
				{Name: "encryption", FriendlyName: "Encryption Indicator", Item: "9", Type: "string", Start: 21, End: 22},
				{Name: "update", FriendlyName: "Update Indicator", Item: "10", Type: "string", Start: 22, End: 23, Required: true},
			}},
		},
	}
	cs := sdef.Compile()
	cs.Path = "common/header"
	cs.InitPool(func() any {
		return &ParsedRecord{
			Schema: cs,
			Fields: make([]ParsedField, cs.FieldCount),
		}
	})
	return cs
}

func TestParseHeader_NilRow(t *testing.T) {
	sch := buildHeaderSchema()

	ctx, err := ParseHeader(nil, sch)
	if err == nil {
		t.Fatal("expected error: Your file does not start with a HEADER.")
	}
	if err.Error() != "Your file does not start with a HEADER." {
		t.Fatal("expected error: Your file does not start with a HEADER.")
	}
	if ctx != nil {
		t.Fatalf("expected nil context, got %+v", ctx)
	}
}

func TestParseHeader_NonHeaderRecordType(t *testing.T) {
	sch := buildHeaderSchema()
	row := decoder.NewPositionalRow(1, "T1", 20, "T1202401CASE001    X")

	_, err := ParseHeader(row, sch)
	if err == nil {
		t.Fatal("expected error for non-HEADER record type")
	}
}

func TestParseHeader_ValidHeader(t *testing.T) {
	sch := buildHeaderSchema()
	//                                          title |year|q|t|sf|tri|pgm|e|E|u
	row := decoder.NewPositionalRow(1, "HEADER", 23, "HEADER20241A06   TAN1ED")

	ctx, err := ParseHeader(row, sch)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if ctx == nil {
		t.Fatal("expected non-nil context")
	}
	if ctx.Year != 2024 {
		t.Errorf("expected Year=2024, got %d", ctx.Year)
	}
	if ctx.Quarter != "1" {
		t.Errorf("expected Quarter=%q, got %q", "1", ctx.Quarter)
	}
	if !ctx.IsEncrypted {
		t.Error("expected IsEncrypted=true when encryption field is 'E'")
	}
	if ctx.Header == nil {
		t.Fatal("expected Header record to be set")
	}
	if ctx.Header.LineNumber != 1 {
		t.Errorf("expected LineNumber=1, got %d", ctx.Header.LineNumber)
	}

	// Verify segment fields were parsed
	title := ctx.Header.GetString("title")
	if title != "HEADER" {
		t.Errorf("expected title=%q, got %q", "HEADER", title)
	}
	stateFips := ctx.Header.GetString("state_fips")
	if stateFips != "06" {
		t.Errorf("expected state_fips=%q, got %q", "06", stateFips)
	}
	programType := ctx.Header.GetString("program_type")
	if programType != "TAN" {
		t.Errorf("expected program_type=%q, got %q", "TAN", programType)
	}
	update := ctx.Header.GetString("update")
	if update != "D" {
		t.Errorf("expected update=%q, got %q", "D", update)
	}
}

func TestParseHeader_NoEncryptionField(t *testing.T) {
	sch := buildHeaderSchema()
	// Row too short for encryption position (21-22) — Slice returns ""
	row := decoder.NewPositionalRow(1, "HEADER", 21, "HEADER20214A06   TAN1")

	ctx, err := ParseHeader(row, sch)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if ctx == nil {
		t.Fatal("expected non-nil context")
	}
	if ctx.IsEncrypted {
		t.Error("expected IsEncrypted=false when encryption field is missing")
	}
}

func TestParseHeader_EncryptionNotE(t *testing.T) {
	sch := buildHeaderSchema()
	//                                                encryption='X' at pos 21
	row := decoder.NewPositionalRow(1, "HEADER", 23, "HEADER20241A06   TAN1XD")

	ctx, err := ParseHeader(row, sch)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if ctx == nil {
		t.Fatal("expected non-nil context")
	}
	if ctx.IsEncrypted {
		t.Error("expected IsEncrypted=false when encryption field is not 'E'")
	}
}
