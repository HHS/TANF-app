package writer

import (
	"go-parser/internal/parser"
)

// FRA TE1 Converter - TANF Exiter work outcome data
// RecordType is always "TE1" for FRA records (not present in CSV data)

func convertFraTE1(record *parser.ParsedRecord, datafileID int32) [][]any {
	// RecordType defaults to "TE1" if not present in fields
	recordType := record.Get("RecordType")
	if recordType == nil {
		recordType = "TE1"
	}

	return singleRow([]any{
		recordType,
		record.Get("EXIT_DATE"),
		record.Get("SSN"),
		newUUID(),
		datafileID,
		int32(record.LineNumber),
	})
}
