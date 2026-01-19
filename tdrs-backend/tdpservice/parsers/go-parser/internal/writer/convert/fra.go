package convert

import (
	"go-parser/internal/db"
	"go-parser/internal/parser"

	"github.com/jackc/pgx/v5/pgtype"
)

// FRA TE1 Converter - TANF Exiter work outcome data
// RecordType is always "TE1" for FRA records (not present in CSV data)

func convertFraTE1(record *parser.ParsedRecord, datafileID int32) [][]any {
	// RecordType defaults to "TE1" if not present in fields
	recordType := toText(record.Get("RecordType"))
	if !recordType.Valid {
		recordType = pgtype.Text{String: "TE1", Valid: true}
	}

	rec := &db.SearchIndexesTanfExiter1{
		RecordType: recordType,
		EXITDATE:   toInt4(record.Get("EXIT_DATE")),
		SSN:        toText(record.Get("SSN")),
		ID:         newUUID(),
		DatafileID: toDatafileID(datafileID),
		LineNumber: toLineNumber(record.LineNumber),
	}

	// Return values in schema field order: shared fields, then segment fields, then standard columns
	// Order: RecordType, EXIT_DATE, SSN, id, datafile_id, line_number
	return singleRow([]any{
		rec.RecordType,
		rec.EXITDATE,
		rec.SSN,
		rec.ID,
		rec.DatafileID,
		rec.LineNumber,
	})
}
