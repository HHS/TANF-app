package storage

import (
	"bytes"
	"context"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"os"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/feature/s3/manager"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/s3/types"
	"github.com/aws/smithy-go"

	"go-parser/internal/logging"
)

// S3Storage encapsulates Amazon S3 actions for file storage operations.
type S3Storage struct {
	Client *s3.Client
}

// S3StorageConfig holds configuration for connecting to S3.
type S3StorageConfig struct {
	Region   string // AWS region (e.g., "us-gov-west-1")
	Endpoint string // Custom endpoint URL (empty = real AWS, set for LocalStack/testing)
}

// NewS3Storage creates an S3Storage client using the provided configuration.
// Credentials are resolved via the standard AWS SDK credential chain
// (environment variables, IAM role, ECS task role, etc.).
func NewS3Storage(cfg S3StorageConfig) (*S3Storage, error) {
	opts := []func(*config.LoadOptions) error{
		config.WithRegion(cfg.Region),
	}

	awsCfg, err := config.LoadDefaultConfig(context.TODO(), opts...)
	if err != nil {
		return nil, fmt.Errorf("failed to load AWS config: %w", err)
	}

	clientOpts := func(o *s3.Options) {
		if cfg.Endpoint != "" {
			o.BaseEndpoint = aws.String(cfg.Endpoint)
			o.UsePathStyle = true
		}
	}

	client := s3.NewFromConfig(awsCfg, clientOpts)

	return &S3Storage{
		Client: client,
	}, nil
}

// ListBuckets lists the buckets in the current account.
func (s S3Storage) ListBuckets(ctx context.Context) ([]types.Bucket, error) {
	var err error
	var output *s3.ListBucketsOutput
	var buckets []types.Bucket
	bucketPaginator := s3.NewListBucketsPaginator(s.Client, &s3.ListBucketsInput{})
	for bucketPaginator.HasMorePages() {
		output, err = bucketPaginator.NextPage(ctx)
		if err != nil {
			var apiErr smithy.APIError
			if errors.As(err, &apiErr) && apiErr.ErrorCode() == "AccessDenied" {
				logging.Warn(ctx, "permission denied listing buckets")
				err = apiErr
			} else {
				logging.Error(ctx, "could not list buckets", slog.Any(logging.KeyError, err))
			}
			break
		} else {
			buckets = append(buckets, output.Buckets...)
		}
	}
	return buckets, err
}

// BucketExists checks whether a bucket exists in the current account.
func (s S3Storage) BucketExists(ctx context.Context, bucketName string) (bool, error) {
	_, err := s.Client.HeadBucket(ctx, &s3.HeadBucketInput{
		Bucket: aws.String(bucketName),
	})
	exists := true
	if err != nil {
		var apiError smithy.APIError
		if errors.As(err, &apiError) {
			switch apiError.(type) {
			case *types.NotFound:
				logging.Debug(ctx, "bucket is available", slog.String("bucket", bucketName))
				exists = false
				err = nil
			default:
				logging.Error(ctx, "bucket access check failed",
					slog.String("bucket", bucketName),
					slog.Any(logging.KeyError, err),
				)
			}
		}
	} else {
		logging.Debug(ctx, "bucket exists", slog.String("bucket", bucketName))
	}

	return exists, err
}

// CreateBucket creates a bucket with the specified name in the specified Region.
func (s S3Storage) CreateBucket(ctx context.Context, name string, region string) error {
	_, err := s.Client.CreateBucket(ctx, &s3.CreateBucketInput{
		Bucket: aws.String(name),
		CreateBucketConfiguration: &types.CreateBucketConfiguration{
			LocationConstraint: types.BucketLocationConstraint(region),
		},
	})
	if err != nil {
		var owned *types.BucketAlreadyOwnedByYou
		var exists *types.BucketAlreadyExists
		if errors.As(err, &owned) {
			logging.Warn(ctx, "bucket already owned", slog.String("bucket", name))
			err = owned
		} else if errors.As(err, &exists) {
			logging.Warn(ctx, "bucket already exists", slog.String("bucket", name))
			err = exists
		}
	} else {
		err = s3.NewBucketExistsWaiter(s.Client).Wait(
			ctx, &s3.HeadBucketInput{Bucket: aws.String(name)}, time.Minute)
		if err != nil {
			logging.Error(ctx, "failed waiting for bucket to exist", slog.String("bucket", name), slog.Any(logging.KeyError, err))
		}
	}
	return err
}

// UploadFile reads from a file and puts the data into an object in a bucket.
func (s S3Storage) UploadFile(ctx context.Context, bucketName string, objectKey string, fileName string) error {
	file, err := os.Open(fileName)
	if err != nil {
		logging.Error(ctx, "could not open file for upload", slog.String("file_name", fileName), slog.Any(logging.KeyError, err))
	} else {
		defer file.Close()
		_, err = s.Client.PutObject(ctx, &s3.PutObjectInput{
			Bucket: aws.String(bucketName),
			Key:    aws.String(objectKey),
			Body:   file,
		})
		if err != nil {
			var apiErr smithy.APIError
			if errors.As(err, &apiErr) && apiErr.ErrorCode() == "EntityTooLarge" {
				logging.Error(ctx, "object too large for single upload", slog.String("bucket", bucketName), slog.Any(logging.KeyError, err))
			} else {
				logging.Error(ctx, "could not upload file",
					slog.String("file_name", fileName),
					slog.String("bucket", bucketName),
					slog.String("object_key", objectKey),
					slog.Any(logging.KeyError, err),
				)
			}
		} else {
			err = s3.NewObjectExistsWaiter(s.Client).Wait(
				ctx, &s3.HeadObjectInput{Bucket: aws.String(bucketName), Key: aws.String(objectKey)}, time.Minute)
			if err != nil {
				logging.Error(ctx, "failed waiting for object to exist",
					slog.String("bucket", bucketName),
					slog.String("object_key", objectKey),
					slog.Any(logging.KeyError, err),
				)
			}
		}
	}
	return err
}

// UploadLargeObject uses an upload manager to upload data to an object in a bucket.
// The upload manager breaks large data into parts and uploads the parts concurrently.
func (s S3Storage) UploadLargeObject(ctx context.Context, bucketName string, objectKey string, largeObject []byte) error {
	largeBuffer := bytes.NewReader(largeObject)
	var partMiBs int64 = 10
	uploader := manager.NewUploader(s.Client, func(u *manager.Uploader) {
		u.PartSize = partMiBs * 1024 * 1024
	})
	_, err := uploader.Upload(ctx, &s3.PutObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(objectKey),
		Body:   largeBuffer,
	})
	if err != nil {
		var apiErr smithy.APIError
		if errors.As(err, &apiErr) && apiErr.ErrorCode() == "EntityTooLarge" {
			logging.Error(ctx, "object too large for multipart upload", slog.String("bucket", bucketName), slog.Any(logging.KeyError, err))
		} else {
			logging.Error(ctx, "could not upload large object",
				slog.String("bucket", bucketName),
				slog.String("object_key", objectKey),
				slog.Any(logging.KeyError, err),
			)
		}
	} else {
		err = s3.NewObjectExistsWaiter(s.Client).Wait(
			ctx, &s3.HeadObjectInput{Bucket: aws.String(bucketName), Key: aws.String(objectKey)}, time.Minute)
		if err != nil {
			logging.Error(ctx, "failed waiting for object to exist",
				slog.String("bucket", bucketName),
				slog.String("object_key", objectKey),
				slog.Any(logging.KeyError, err),
			)
		}
	}

	return err
}

// DownloadFile gets an object from a bucket and stores it in a local file.
func (s S3Storage) DownloadFile(ctx context.Context, bucketName string, objectKey string, fileName string) error {
	result, err := s.Client.GetObject(ctx, &s3.GetObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(objectKey),
	})
	if err != nil {
		var noKey *types.NoSuchKey
		if errors.As(err, &noKey) {
			logging.Warn(ctx, "object does not exist",
				slog.String("bucket", bucketName),
				slog.String("object_key", objectKey),
			)
			err = noKey
		} else {
			logging.Error(ctx, "could not get object",
				slog.String("bucket", bucketName),
				slog.String("object_key", objectKey),
				slog.Any(logging.KeyError, err),
			)
		}
		return err
	}
	defer result.Body.Close()
	file, err := os.Create(fileName)
	if err != nil {
		logging.Error(ctx, "could not create file", slog.String("file_name", fileName), slog.Any(logging.KeyError, err))
		return err
	}
	defer file.Close()
	body, err := io.ReadAll(result.Body)
	if err != nil {
		logging.Error(ctx, "could not read object body",
			slog.String("bucket", bucketName),
			slog.String("object_key", objectKey),
			slog.Any(logging.KeyError, err),
		)
	}
	_, err = file.Write(body)
	return err
}

// DownloadLargeObject uses a download manager to download an object from a bucket.
// The download manager gets the data in parts and writes them to a buffer until all of
// the data has been downloaded.
func (s S3Storage) DownloadLargeObject(ctx context.Context, bucketName string, objectKey string) ([]byte, error) {
	var partMiBs int64 = 10
	downloader := manager.NewDownloader(s.Client, func(d *manager.Downloader) {
		d.PartSize = partMiBs * 1024 * 1024
	})
	buffer := manager.NewWriteAtBuffer([]byte{})
	_, err := downloader.Download(ctx, buffer, &s3.GetObjectInput{
		Bucket: aws.String(bucketName),
		Key:    aws.String(objectKey),
	})
	if err != nil {
		logging.Error(ctx, "could not download large object",
			slog.String("bucket", bucketName),
			slog.String("object_key", objectKey),
			slog.Any(logging.KeyError, err),
		)
	}
	return buffer.Bytes(), err
}

// CopyToFolder copies an object in a bucket to a subfolder in the same bucket.
func (s S3Storage) CopyToFolder(ctx context.Context, bucketName string, objectKey string, folderName string) error {
	objectDest := fmt.Sprintf("%v/%v", folderName, objectKey)
	_, err := s.Client.CopyObject(ctx, &s3.CopyObjectInput{
		Bucket:     aws.String(bucketName),
		CopySource: aws.String(fmt.Sprintf("%v/%v", bucketName, objectKey)),
		Key:        aws.String(objectDest),
	})
	if err != nil {
		var notActive *types.ObjectNotInActiveTierError
		if errors.As(err, &notActive) {
			logging.Warn(ctx, "object is not in active tier",
				slog.String("bucket", bucketName),
				slog.String("object_key", objectKey),
			)
			err = notActive
		}
	} else {
		err = s3.NewObjectExistsWaiter(s.Client).Wait(
			ctx, &s3.HeadObjectInput{Bucket: aws.String(bucketName), Key: aws.String(objectDest)}, time.Minute)
		if err != nil {
			logging.Error(ctx, "failed waiting for copied object to exist",
				slog.String("bucket", bucketName),
				slog.String("object_key", objectDest),
				slog.Any(logging.KeyError, err),
			)
		}
	}
	return err
}

// CopyToBucket copies an object in a bucket to another bucket.
func (s S3Storage) CopyToBucket(ctx context.Context, sourceBucket string, destinationBucket string, objectKey string) error {
	_, err := s.Client.CopyObject(ctx, &s3.CopyObjectInput{
		Bucket:     aws.String(destinationBucket),
		CopySource: aws.String(fmt.Sprintf("%v/%v", sourceBucket, objectKey)),
		Key:        aws.String(objectKey),
	})
	if err != nil {
		var notActive *types.ObjectNotInActiveTierError
		if errors.As(err, &notActive) {
			logging.Warn(ctx, "object is not in active tier",
				slog.String("bucket", sourceBucket),
				slog.String("object_key", objectKey),
			)
			err = notActive
		}
	} else {
		err = s3.NewObjectExistsWaiter(s.Client).Wait(
			ctx, &s3.HeadObjectInput{Bucket: aws.String(destinationBucket), Key: aws.String(objectKey)}, time.Minute)
		if err != nil {
			logging.Error(ctx, "failed waiting for copied object to exist",
				slog.String("bucket", destinationBucket),
				slog.String("object_key", objectKey),
				slog.Any(logging.KeyError, err),
			)
		}
	}
	return err
}

// ListObjects lists the objects in a bucket.
func (s S3Storage) ListObjects(ctx context.Context, bucketName string) ([]types.Object, error) {
	var err error
	var output *s3.ListObjectsV2Output
	input := &s3.ListObjectsV2Input{
		Bucket: aws.String(bucketName),
	}
	var objects []types.Object
	objectPaginator := s3.NewListObjectsV2Paginator(s.Client, input)
	for objectPaginator.HasMorePages() {
		output, err = objectPaginator.NextPage(ctx)
		if err != nil {
			var noBucket *types.NoSuchBucket
			if errors.As(err, &noBucket) {
				logging.Warn(ctx, "bucket does not exist", slog.String("bucket", bucketName))
				err = noBucket
			}
			break
		} else {
			objects = append(objects, output.Contents...)
		}
	}
	return objects, err
}

// DeleteObjects deletes a list of objects from a bucket.
func (s S3Storage) DeleteObjects(ctx context.Context, bucketName string, objectKeys []string) error {
	var objectIds []types.ObjectIdentifier
	for _, key := range objectKeys {
		objectIds = append(objectIds, types.ObjectIdentifier{Key: aws.String(key)})
	}
	output, err := s.Client.DeleteObjects(ctx, &s3.DeleteObjectsInput{
		Bucket: aws.String(bucketName),
		Delete: &types.Delete{Objects: objectIds, Quiet: aws.Bool(true)},
	})
	if err != nil || len(output.Errors) > 0 {
		logging.Error(ctx, "error deleting objects from bucket", slog.String("bucket", bucketName), slog.Any(logging.KeyError, err))
		if err != nil {
			var noBucket *types.NoSuchBucket
			if errors.As(err, &noBucket) {
				logging.Warn(ctx, "bucket does not exist", slog.String("bucket", bucketName))
				err = noBucket
			}
		} else if len(output.Errors) > 0 {
			for _, outErr := range output.Errors {
				logging.Error(ctx, "object delete failed",
					slog.String("bucket", bucketName),
					slog.String("object_key", *outErr.Key),
					slog.String("message", *outErr.Message),
				)
			}
			err = fmt.Errorf("%s", *output.Errors[0].Message)
		}
	} else {
		for _, delObjs := range output.Deleted {
			err = s3.NewObjectNotExistsWaiter(s.Client).Wait(
				ctx, &s3.HeadObjectInput{Bucket: aws.String(bucketName), Key: delObjs.Key}, time.Minute)
			if err != nil {
				logging.Error(ctx, "failed waiting for object deletion",
					slog.String("bucket", bucketName),
					slog.String("object_key", *delObjs.Key),
					slog.Any(logging.KeyError, err),
				)
			} else {
				logging.Debug(ctx, "object deleted",
					slog.String("bucket", bucketName),
					slog.String("object_key", *delObjs.Key),
				)
			}
		}
	}
	return err
}

// DeleteBucket deletes a bucket. The bucket must be empty or an error is returned.
func (s S3Storage) DeleteBucket(ctx context.Context, bucketName string) error {
	_, err := s.Client.DeleteBucket(ctx, &s3.DeleteBucketInput{
		Bucket: aws.String(bucketName)})
	if err != nil {
		var noBucket *types.NoSuchBucket
		if errors.As(err, &noBucket) {
			logging.Warn(ctx, "bucket does not exist", slog.String("bucket", bucketName))
			err = noBucket
		} else {
			logging.Error(ctx, "could not delete bucket", slog.String("bucket", bucketName), slog.Any(logging.KeyError, err))
		}
	} else {
		err = s3.NewBucketNotExistsWaiter(s.Client).Wait(
			ctx, &s3.HeadBucketInput{Bucket: aws.String(bucketName)}, time.Minute)
		if err != nil {
			logging.Error(ctx, "failed waiting for bucket deletion", slog.String("bucket", bucketName), slog.Any(logging.KeyError, err))
		} else {
			logging.Debug(ctx, "bucket deleted", slog.String("bucket", bucketName))
		}
	}
	return err
}
