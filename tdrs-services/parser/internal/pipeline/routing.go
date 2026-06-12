package pipeline

import (
	"context"
	"log/slog"

	"github.com/jackc/pgx/v5/pgtype"

	"go-parser/internal/parser"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// ErrorStats tracks validation error counts by scope and type.
type ErrorStats struct {
	RecordPreCheck   int64 // Blocking record errors
	FieldValue       int64 // Field validation errors
	ValueConsistency int64 // Non-blocking record/group consistency errors
	CaseConsistency  int64 // Blocking group errors
}

// Total returns the total number of errors across all scopes.
func (s *ErrorStats) Total() int64 {
	return s.RecordPreCheck + s.FieldValue + s.ValueConsistency + s.CaseConsistency
}

// LogAttrs returns structured error count fields.
func (s ErrorStats) LogAttrs() []slog.Attr {
	return []slog.Attr{
		slog.Int64("record_pre_check_error_count", s.RecordPreCheck),
		slog.Int64("field_value_error_count", s.FieldValue),
		slog.Int64("value_consistency_error_count", s.ValueConsistency),
		slog.Int64("case_consistency_error_count", s.CaseConsistency),
		slog.Int64("total_validation_error_count", s.Total()),
	}
}

// RouteStats holds batch/group counts collected during result routing.
type RouteStats struct {
	ErrorStats
	BatchCount int64
	GroupCount int64
}

// countErrors tallies validation errors from a validated batch.
func countErrors(vb *validatedBatch) (recordPreCheck, fieldValue, valueConsistency, caseConsistency int64) {
	for _, vg := range vb.Groups {
		for _, err := range vg.Result.GroupErrors {
			switch err.ErrorType {
			case validation.ErrorTypeCaseConsistency:
				caseConsistency++
			case validation.ErrorTypeValueConsistency:
				valueConsistency++
			}
		}

		for _, recResult := range vg.Result.RecordResults {
			for _, err := range recResult.RecordErrors {
				switch err.ErrorType {
				case validation.ErrorTypeRecordPreCheck:
					recordPreCheck++
				case validation.ErrorTypeValueConsistency:
					valueConsistency++
				case validation.ErrorTypeCaseConsistency:
					caseConsistency++
				}
			}
			for range recResult.FieldErrors {
				fieldValue++
			}
		}
	}
	return
}

// routeValidatedBatch routes valid records and all errors to the database.
// Groups with blocking errors (CASE_CONSISTENCY) have errors written but records rejected.
// Records with blocking errors (RECORD_PRE_CHECK) have errors written but record rejected.
// Valid records are written with their non-blocking errors linked via ObjectID.
//
// Error rows are batched per group and sent in a single RouteErrorRows call to reduce
// channel send overhead (250K errors = 250K channel sends without batching).
//
// The errorRows buffer is owned by the caller and reused across calls to avoid allocation.
func routeValidatedBatch(ctx context.Context, router *writer.Router, groups []*validatedGroup, datafileID int32, errorRows *[][]any) error {
	for _, vg := range groups {
		// Reset buffer for this group (reuse backing array)
		*errorRows = (*errorRows)[:0]

		// Collect group-level error rows (use first record for context)
		if len(vg.Result.GroupErrors) > 0 && len(vg.Group.Records) > 0 {
			firstRec := vg.Group.Records[0]
			for _, groupErr := range vg.Result.GroupErrors {
				*errorRows = append(*errorRows, writer.SerializeError(groupErr, firstRec, nil, datafileID, nil))
			}
		}

		// Handle blocked groups: serialize all errors, release records, skip record writing
		if vg.Result.HasBlockingGroupErrors() {
			for i, recResult := range vg.Result.RecordResults {
				record := vg.Group.Records[i]
				appendRecordErrors(errorRows, recResult, record, nil, datafileID, nil)
				record.Schema.ReleaseRecord(record)
			}
			if err := router.RouteErrorRows(ctx, *errorRows); err != nil {
				return err
			}
			continue
		}

		// Process each record in the group
		for i, recResult := range vg.Result.RecordResults {
			record := vg.Group.Records[i]

			if recResult.HasBlockingErrors() {
				appendRecordErrors(errorRows, recResult, record, nil, datafileID, nil)
				record.Schema.ReleaseRecord(record)
				continue
			}

			// Record will be written - check if it has a writer
			if !router.HasWriter(record.Schema.Path) {
				record.Schema.ReleaseRecord(record)
				continue
			}

			// Serialize record to get UUID, then serialize errors with UUID linking
			rows, recordUUID, err := router.SerializeRecord(record)
			if err != nil {
				record.Schema.ReleaseRecord(record)
				return err
			}

			// Get content type ID for error linking (record will be written)
			contentTypeID := router.GetContentTypeID(record.Schema.Path)

			// Serialize non-blocking errors with ObjectID linking (while record still available)
			appendRecordErrors(errorRows, recResult, record, recordUUID, datafileID, contentTypeID)

			// Capture schema path before releasing record
			schemaPath := record.Schema.Path

			// Release record back to pool - no longer needed after conversion
			record.Schema.ReleaseRecord(record)

			// Send serialized record rows to writer
			if err := router.SendRecordRowsByPath(ctx, schemaPath, rows); err != nil {
				return err
			}
		}

		// Flush all error rows for this group in one batched send
		if err := router.RouteErrorRows(ctx, *errorRows); err != nil {
			return err
		}
	}
	return nil
}

// appendRecordErrors serializes all errors for a record to rows and appends them to the buffer.
// Must be called BEFORE record is released to pool.
// recordUUID is set for records that will be written (for error linking), nil otherwise.
// contentTypeID is set only when recordUUID is set (for FIELD_VALUE and VALUE_CONSISTENCY errors).
func appendRecordErrors(
	buf *[][]any,
	recResult *validation.RecordValidationResult,
	record *parser.ParsedRecord,
	recordUUID *pgtype.UUID,
	datafileID int32,
	contentTypeID *int32,
) {
	allErrors := recResult.AllErrors()
	if len(allErrors) == 0 {
		return
	}

	for _, vr := range allErrors {
		// Only set content type ID for non-blocking errors (when record is written)
		// Per Python parser: FIELD_VALUE and VALUE_CONSISTENCY get content_type when record exists
		var ctID *int32
		if recordUUID != nil && (vr.ErrorType == validation.ErrorTypeFieldValue ||
			vr.ErrorType == validation.ErrorTypeValueConsistency) {
			ctID = contentTypeID
		}
		*buf = append(*buf, writer.SerializeError(vr, record, recordUUID, datafileID, ctID))
	}
}
