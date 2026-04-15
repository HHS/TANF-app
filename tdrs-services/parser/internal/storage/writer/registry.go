package writer

import (
	"go-parser/internal/parser"
)

// RowSerializer serializes a ParsedRecord to row values for COPY.
// Uses SQLC types internally for type safety, returns [][]any for flexibility.
// Most record types return a single row, but multi-record types like T3
// (which contains 2 children per line) return multiple rows.
type RowSerializer func(record *parser.ParsedRecord, datafileID int32) [][]any

// serializerRegistry maps schema paths to their serializer functions.
// Schema paths (e.g., "tanf/t1", "tribal_tanf/t1") allow different programs
// with the same record type prefix to use different serializers/tables.
var serializerRegistry = map[string]RowSerializer{
	// TANF record types
	"tanf/t1": serializeTanfT1,
	"tanf/t2": serializeTanfT2,
	"tanf/t3": serializeTanfT3,
	"tanf/t4": serializeTanfT4,
	"tanf/t5": serializeTanfT5,
	"tanf/t6": serializeTanfT6,
	"tanf/t7": serializeTanfT7,

	// SSP record types
	"ssp/m1": serializeSspM1,
	"ssp/m2": serializeSspM2,
	"ssp/m3": serializeSspM3,
	"ssp/m4": serializeSspM4,
	"ssp/m5": serializeSspM5,
	"ssp/m6": serializeSspM6,
	"ssp/m7": serializeSspM7,

	// Tribal TANF record types (same T1-T7 prefixes but different tables)
	"tribal_tanf/t1": serializeTribalT1,
	"tribal_tanf/t2": serializeTribalT2,
	"tribal_tanf/t3": serializeTribalT3,
	"tribal_tanf/t4": serializeTribalT4,
	"tribal_tanf/t5": serializeTribalT5,
	"tribal_tanf/t6": serializeTribalT6,
	"tribal_tanf/t7": serializeTribalT7,

	// FRA record types
	"fra/te1": serializeFraTE1,
}

// GetSerializer returns the serializer for a schema path.
// The schema path (e.g., "tanf/t1") determines which serializer to use,
// allowing different programs with the same record type to use different tables.
func GetSerializer(schemaPath string) RowSerializer {
	return serializerRegistry[schemaPath]
}
