package converter

import (
	"go-parser/internal/schema"
)

// RowConverter converts a ParsedRecord to row values for COPY.
// Uses SQLC types internally for type safety, returns [][]any for flexibility.
// Most record types return a single row, but multi-record types like T3
// (which contains 2 children per line) return multiple rows.
type RowConverter func(record *schema.ParsedRecord, datafileID int32) [][]any

// converterRegistry maps schema paths to their converter functions.
// Schema paths (e.g., "tanf/t1", "tribal_tanf/t1") allow different programs
// with the same record type prefix to use different converters/tables.
var converterRegistry = map[string]RowConverter{
	// TANF record types
	"tanf/t1": convertTanfT1,
	"tanf/t2": convertTanfT2,
	"tanf/t3": convertTanfT3,
	"tanf/t4": convertTanfT4,
	"tanf/t5": convertTanfT5,
	"tanf/t6": convertTanfT6,
	"tanf/t7": convertTanfT7,

	// SSP record types
	"ssp/m1": convertSspM1,
	"ssp/m2": convertSspM2,
	"ssp/m3": convertSspM3,
	"ssp/m4": convertSspM4,
	"ssp/m5": convertSspM5,
	"ssp/m6": convertSspM6,
	"ssp/m7": convertSspM7,

	// Tribal TANF record types (same T1-T7 prefixes but different tables)
	"tribal_tanf/t1": convertTribalT1,
	"tribal_tanf/t2": convertTribalT2,
	"tribal_tanf/t3": convertTribalT3,
	"tribal_tanf/t4": convertTribalT4,
	"tribal_tanf/t5": convertTribalT5,
	"tribal_tanf/t6": convertTribalT6,
	"tribal_tanf/t7": convertTribalT7,

	// FRA record types
	"fra/te1": convertFraTE1,
}

// GetConverter returns the converter for a schema path.
// The schema path (e.g., "tanf/t1") determines which converter to use,
// allowing different programs with the same record type to use different tables.
func GetConverter(schemaPath string) RowConverter {
	return converterRegistry[schemaPath]
}
