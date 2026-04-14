package reader

import (
	"context"
	"fmt"
	"io"
	"os"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"

	"go-parser/internal/storage"
)

// S3Source reads files from Amazon S3 by downloading to a local temp file.
type S3Source struct {
	storage  *storage.S3Storage
	bucket   string
	key      string
	tempFile *os.File
}

// NewS3Source creates a FileSource that reads from an S3 bucket.
func NewS3Source(storage *storage.S3Storage, bucket, key string) *S3Source {
	return &S3Source{
		storage: storage,
		bucket:  bucket,
		key:     key,
	}
}

// Open downloads the S3 object to a temp file and returns it.
func (s *S3Source) Open(ctx context.Context) (*os.File, error) {
	result, err := s.storage.Client.GetObject(ctx, &s3.GetObjectInput{
		Bucket: aws.String(s.bucket),
		Key:    aws.String(s.key),
	})
	if err != nil {
		return nil, fmt.Errorf("failed to get S3 object %s/%s: %w", s.bucket, s.key, err)
	}
	defer result.Body.Close()

	tmpFile, err := os.CreateTemp("", "goparser-*")
	if err != nil {
		return nil, fmt.Errorf("failed to create temp file: %w", err)
	}

	if _, err := io.Copy(tmpFile, result.Body); err != nil {
		tmpFile.Close()
		os.Remove(tmpFile.Name())
		return nil, fmt.Errorf("failed to download S3 object to temp file: %w", err)
	}

	// Seek back to start so the decoder can read from the beginning
	if _, err := tmpFile.Seek(0, io.SeekStart); err != nil {
		tmpFile.Close()
		os.Remove(tmpFile.Name())
		return nil, fmt.Errorf("failed to seek temp file: %w", err)
	}

	s.tempFile = tmpFile
	return tmpFile, nil
}

// Cleanup removes the temp file created during Open.
func (s *S3Source) Cleanup() error {
	if s.tempFile != nil {
		name := s.tempFile.Name()
		s.tempFile = nil
		return os.Remove(name)
	}
	return nil
}
