package converter

import (
	"go-parser/internal/worker"
)

// RowConverter converts a ParsedRecord to row values for COPY.
// Uses SQLC types internally for type safety, returns []any for flexibility.
type RowConverter func(record *worker.ParsedRecord, datafileID int32) []any

// converterRegistry maps record types to their converter functions.
// TODO: Implement converters for all record types.
var converterRegistry = map[string]RowConverter{
	// TANF record types
	// "T1": convertT1,
	// "T2": convertT2,
	// "T3": convertT3,
	// "T4": convertT4,
	// "T5": convertT5,
	// "T6": convertT6,
	// "T7": convertT7,
	// // SSP record types
	// "M1": convertM1,
	// "M2": convertM2,
	// "M3": convertM3,
	// "M4": convertM4,
	// "M5": convertM5,
	// "M6": convertM6,
	// "M7": convertM7,
	// Tribal uses same T1-T7 prefixes but different tables
	// The WriterManager routes based on FileSpec, not just record type
}

// GetConverter returns the converter for a record type.
func GetConverter(recordType string) RowConverter {
	return converterRegistry[recordType]
}
