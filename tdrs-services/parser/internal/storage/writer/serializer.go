package writer

import (
	"github.com/jackc/pgx/v5/pgtype"

	"go-parser/internal/parser"
)

// serializeRecord serializes a ParsedRecord according to YAML-derived COPY columns.
func serializeRecord(record *parser.ParsedRecord, datafileID int32, columns []string) ([][]any, *pgtype.UUID) {
	row := make([]any, len(columns))
	var recordUUID *pgtype.UUID

	for i, column := range columns {
		switch column {
		case "id":
			uuid := newUUID()
			row[i] = uuid
			recordUUID = &uuid
		case "datafile_id":
			row[i] = datafileID
		case "line_number":
			row[i] = int32(record.LineNumber)
		default:
			row[i] = record.Get(column)
		}
	}

	return singleRow(row), recordUUID
}
