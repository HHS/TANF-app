package reader

import (
	"context"
	"os"
)

// FileSource abstracts how the parser acquires input files.
// Implementations handle different backing stores (local disk, S3, HTTP, etc.).
type FileSource interface {
	// Open fetches the file and returns an *os.File.
	// For local files this is a direct os.Open.
	// For remote sources this downloads to a temp file first.
	Open(ctx context.Context) (*os.File, error)

	// Cleanup releases resources (e.g., deletes temp files).
	// Safe to call multiple times.
	Cleanup() error
}
