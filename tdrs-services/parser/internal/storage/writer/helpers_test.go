package writer

import (
	"testing"
)

func TestNewUUID_Valid(t *testing.T) {
	uuid := newUUID()
	if !uuid.Valid {
		t.Fatal("expected valid UUID")
	}
}

func TestNewUUID_Version4(t *testing.T) {
	uuid := newUUID()
	// Version 4: byte 6 high nibble should be 0x40
	version := uuid.Bytes[6] >> 4
	if version != 4 {
		t.Errorf("expected UUID version 4, got %d", version)
	}
}

func TestNewUUID_VariantRFC9562(t *testing.T) {
	uuid := newUUID()
	// Variant: byte 8 high 2 bits should be 10 (0x80)
	variant := uuid.Bytes[8] >> 6
	if variant != 2 {
		t.Errorf("expected UUID variant 2 (RFC 9562), got %d", variant)
	}
}

func TestNewUUID_Unique(t *testing.T) {
	seen := make(map[[16]byte]bool)
	for range 1000 {
		uuid := newUUID()
		if seen[uuid.Bytes] {
			t.Fatal("UUID collision detected")
		}
		seen[uuid.Bytes] = true
	}
}

func TestSingleRow(t *testing.T) {
	row := []any{1, "test", true}
	result := singleRow(row)

	if len(result) != 1 {
		t.Fatalf("expected 1 row, got %d", len(result))
	}
	if len(result[0]) != 3 {
		t.Errorf("expected 3 columns, got %d", len(result[0]))
	}
	if result[0][0] != 1 {
		t.Errorf("expected first value 1, got %v", result[0][0])
	}
}
