package writer

import (
	"testing"

	"github.com/jackc/pgx/v5/pgtype"

	"go-parser/internal/config/schema"
)

func TestSerializeRecordUsesYamlDerivedColumnOrder(t *testing.T) {
	cs := makeTestSchema("M6", []schema.FieldDef{
		{Name: "RecordType"},
		{Name: "CALENDAR_QUARTER"},
		{Name: "RPT_MONTH_YEAR"},
		{Name: "SSPMOE_FAMILIES"},
	})
	rec := makeTestRecord(cs, 7, map[string]any{
		"RecordType":       "M6",
		"CALENDAR_QUARTER": 20214,
		"RPT_MONTH_YEAR":   202112,
		"SSPMOE_FAMILIES":  15869,
	})
	columns := []string{
		"RecordType", "CALENDAR_QUARTER", "RPT_MONTH_YEAR", "SSPMOE_FAMILIES",
		"id", "datafile_id", "line_number",
	}

	rows, recordUUID := serializeRecord(rec, 101, columns)

	if len(rows) != 1 {
		t.Fatalf("expected 1 row, got %d", len(rows))
	}
	row := rows[0]
	if len(row) != len(columns) {
		t.Fatalf("expected %d columns, got %d: %v", len(columns), len(row), row)
	}
	if row[0] != "M6" || row[1] != 20214 || row[2] != 202112 || row[3] != 15869 {
		t.Errorf("schema field values = %v, want [M6 20214 202112 15869]", row[:4])
	}
	if _, ok := row[4].(pgtype.UUID); !ok {
		t.Fatalf("id column = %T, want pgtype.UUID", row[4])
	}
	if recordUUID == nil || !recordUUID.Valid {
		t.Fatalf("recordUUID = %v, want valid UUID", recordUUID)
	}
	if row[4] != *recordUUID {
		t.Errorf("id column = %v, want returned UUID %v", row[4], *recordUUID)
	}
	if row[5] != int32(101) {
		t.Errorf("datafile_id = %v, want 101", row[5])
	}
	if row[6] != int32(7) {
		t.Errorf("line_number = %v, want 7", row[6])
	}
}

func TestSerializeRecordWritesFraRecordTypeFromParsedDefault(t *testing.T) {
	cs := makeTestSchema("TE1", []schema.FieldDef{
		{Name: "RecordType", Default: "TE1"},
		{Name: "EXIT_DATE"},
		{Name: "SSN"},
	})
	rec := makeTestRecord(cs, 3, map[string]any{
		"RecordType": "TE1",
		"EXIT_DATE":  202401,
		"SSN":        "123456789",
	})
	columns := []string{"RecordType", "EXIT_DATE", "SSN", "id", "datafile_id", "line_number"}

	rows, _ := serializeRecord(rec, 11, columns)

	if got := rows[0][0]; got != "TE1" {
		t.Errorf("RecordType = %v, want TE1", got)
	}
}
