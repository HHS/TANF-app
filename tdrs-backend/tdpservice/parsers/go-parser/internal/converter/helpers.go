package converter

import (
	"strconv"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
)

// Helper functions for converting parsed field values to pgtype wrappers.
// These handle the conversion from map[string]any to PostgreSQL-compatible types.

// toText converts a string value to pgtype.Text.
func toText(v any) pgtype.Text {
	if v == nil {
		return pgtype.Text{Valid: false}
	}
	if s, ok := v.(string); ok {
		return pgtype.Text{String: s, Valid: true}
	}
	return pgtype.Text{Valid: false}
}

// toInt4 converts value to pgtype.Int4.
func toInt4(v any) pgtype.Int4 {
	if v == nil {
		return pgtype.Int4{Valid: false}
	}
	switch n := v.(type) {
	case int:
		return pgtype.Int4{Int32: int32(n), Valid: true}
	case int32:
		return pgtype.Int4{Int32: n, Valid: true}
	case int64:
		return pgtype.Int4{Int32: int32(n), Valid: true}
	case float64:
		return pgtype.Int4{Int32: int32(n), Valid: true}
	case string:
		result, err := strconv.Atoi(n)
		if err != nil {
			return pgtype.Int4{Valid: false}
		}
		return pgtype.Int4{Int32: int32(result), Valid: true}
	}
	return pgtype.Int4{Valid: false}
}

// newUUID generates a new UUID for the record ID.
func newUUID() pgtype.UUID {
	id := uuid.New()
	return pgtype.UUID{Bytes: id, Valid: true}
}

// toDatafileID converts int32 to pgtype.Int4 for the datafile foreign key.
func toDatafileID(id int32) pgtype.Int4 {
	return pgtype.Int4{Int32: id, Valid: true}
}

// toLineNumber converts line number to pgtype.Int4.
func toLineNumber(lineNum int) pgtype.Int4 {
	return pgtype.Int4{Int32: int32(lineNum), Valid: true}
}

// getString safely retrieves a string from the fields map.
func getString(fields map[string]any, key string) string {
	if v, ok := fields[key]; ok {
		if s, ok := v.(string); ok {
			return s
		}
	}
	return ""
}

// getInt safely retrieves an int from the fields map.
func getInt(fields map[string]any, key string) int {
	if v, ok := fields[key]; ok {
		switch n := v.(type) {
		case int:
			return n
		case int32:
			return int(n)
		case int64:
			return int(n)
		case float64:
			return int(n)
		}
	}
	return 0
}

// singleRow wraps a single row in a slice for converters that produce one row.
func singleRow(row []any) [][]any {
	return [][]any{row}
}

// hasChild2Data checks if a T3 record has valid Child 2 data.
// Child 2 is considered present if FAMILY_AFFILIATION_2 has a non-empty value.
func hasChild2Data(fields map[string]any) bool {
	v, ok := fields["FAMILY_AFFILIATION_2"]
	if !ok {
		return false
	}
	// Check if it's a valid non-zero value
	switch val := v.(type) {
	case int:
		return val != 0
	case int32:
		return val != 0
	case int64:
		return val != 0
	case float64:
		return val != 0
	case string:
		return val != "" && val != " "
	}
	return false
}
