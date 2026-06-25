package writer

import (
	"crypto/rand"
	"io"

	"github.com/jackc/pgx/v5/pgtype"
)

// newUUID generates a new v4 UUID for the record ID.
func newUUID() pgtype.UUID {
	var id [16]byte
	if _, err := io.ReadFull(rand.Reader, id[:]); err != nil {
		panic(err)
	}
	// Set version 4 (random) bits
	id[6] = (id[6] & 0x0f) | 0x40
	// Set variant bits (RFC 9562)
	id[8] = (id[8] & 0x3f) | 0x80
	return pgtype.UUID{Bytes: id, Valid: true}
}

// singleRow wraps a single row in a slice for converters that produce one row.
func singleRow(row []any) [][]any {
	return [][]any{row}
}
