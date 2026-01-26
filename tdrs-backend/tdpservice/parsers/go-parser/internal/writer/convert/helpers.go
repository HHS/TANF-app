package convert

import (
	"strconv"

	"github.com/google/uuid"
	"github.com/jackc/pgx/v5/pgtype"
)

// Helper functions for converting parsed field values to database-compatible types.
// These return raw Go types (string, int32) or nil for NULL values.
// pgx's CopyFrom handles encoding raw types directly, avoiding pgtype wrapper allocations.

// toText validates value is a string and returns it for TEXT columns.
// Returns the original interface value to avoid re-boxing allocations.
// pgx encodes string directly to TEXT, nil becomes NULL.
func toText(v any) any {
	if v == nil {
		return nil
	}
	// Check if it's a string, but return original 'v' to avoid re-boxing
	if _, ok := v.(string); ok {
		return v
	}
	return nil
}

// toInt4 converts value to int32 or nil for NULL.
// pgx encodes int32 directly to INT4, nil becomes NULL.
// Returns original interface value when already int32 to avoid re-boxing.
func toInt4(v any) any {
	if v == nil {
		return nil
	}
	switch n := v.(type) {
	case int:
		return int32(n)
	case int32:
		return v // Return original to avoid re-boxing
	case int64:
		return int32(n)
	case float64:
		return int32(n)
	case string:
		result, err := strconv.Atoi(n)
		if err != nil {
			return nil
		}
		return int32(result)
	}
	return nil
}

// newUUID generates a new UUID for the record ID.
// Returns pgtype.UUID as required for UUID columns.
func newUUID() pgtype.UUID {
	id := uuid.New()
	return pgtype.UUID{Bytes: id, Valid: true}
}

// toDatafileID converts int32 to the value for the datafile foreign key.
func toDatafileID(id int32) int32 {
	return id
}

// toLineNumber converts line number to int32.
func toLineNumber(lineNum int) int32 {
	return int32(lineNum)
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
