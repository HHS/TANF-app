package writer

import (
	"encoding/binary"
	"math/rand/v2"

	"github.com/jackc/pgx/v5/pgtype"
)

// newUUID generates a new v4 UUID for the record ID using math/rand.
// These are database primary keys and do not require cryptographic randomness,
// just uniqueness.
func newUUID() pgtype.UUID {
	var id [16]byte
	binary.LittleEndian.PutUint64(id[:8], rand.Uint64())
	binary.LittleEndian.PutUint64(id[8:], rand.Uint64())
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
