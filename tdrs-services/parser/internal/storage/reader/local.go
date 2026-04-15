package reader

import (
	"context"
	"os"
)

// LocalSource reads files from the local filesystem.
type LocalSource struct {
	path string
}

// NewLocalSource creates a FileSource that reads from a local file path.
func NewLocalSource(path string) *LocalSource {
	return &LocalSource{path: path}
}

// Open opens the local file for reading.
func (s *LocalSource) Open(_ context.Context) (*os.File, error) {
	return os.Open(s.path)
}

// Cleanup is a no-op for local files — the caller handles file.Close().
func (s *LocalSource) Cleanup() error {
	return nil
}
