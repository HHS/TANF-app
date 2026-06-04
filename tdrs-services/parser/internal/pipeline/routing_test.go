package pipeline

import (
	"context"
	"slices"
	"sync"
	"testing"

	"github.com/jackc/pgx/v5/pgtype"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/storage/writer"
	"go-parser/internal/testutil"
	"go-parser/internal/validation"
)

// --- ErrorStats tests ---

func TestErrorStats_Total_AllZero(t *testing.T) {
	s := &ErrorStats{}
	if got := s.Total(); got != 0 {
		t.Errorf("Total() = %d, want 0", got)
	}
}

func TestErrorStats_Total_SumsAllFields(t *testing.T) {
	s := &ErrorStats{
		RecordPreCheck:   3,
		FieldValue:       7,
		ValueConsistency: 2,
		CaseConsistency:  1,
	}
	if got := s.Total(); got != 13 {
		t.Errorf("Total() = %d, want 13", got)
	}
}

func TestErrorStats_Total_SingleField(t *testing.T) {
	tests := []struct {
		name  string
		stats ErrorStats
		want  int64
	}{
		{"RecordPreCheck only", ErrorStats{RecordPreCheck: 5}, 5},
		{"FieldValue only", ErrorStats{FieldValue: 10}, 10},
		{"ValueConsistency only", ErrorStats{ValueConsistency: 3}, 3},
		{"CaseConsistency only", ErrorStats{CaseConsistency: 8}, 8},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.stats.Total(); got != tt.want {
				t.Errorf("Total() = %d, want %d", got, tt.want)
			}
		})
	}
}

// --- RouteStats tests ---

func TestRouteStats_EmbeddedErrorStats(t *testing.T) {
	rs := RouteStats{
		ErrorStats: ErrorStats{
			RecordPreCheck:   1,
			FieldValue:       2,
			ValueConsistency: 3,
			CaseConsistency:  4,
		},
		BatchCount: 5,
		GroupCount: 10,
	}

	if rs.Total() != 10 {
		t.Errorf("Total() = %d, want 10", rs.Total())
	}
	if rs.BatchCount != 5 {
		t.Errorf("BatchCount = %d, want 5", rs.BatchCount)
	}
	if rs.GroupCount != 10 {
		t.Errorf("GroupCount = %d, want 10", rs.GroupCount)
	}
}

// --- countErrors tests ---

func TestCountErrors_EmptyBatch(t *testing.T) {
	vb := &validatedBatch{
		BatchID: 1,
		Groups:  nil,
	}
	rpc, fv, vc, cc := countErrors(vb)
	if rpc != 0 || fv != 0 || vc != 0 || cc != 0 {
		t.Errorf("countErrors(empty) = (%d, %d, %d, %d), want all zeros", rpc, fv, vc, cc)
	}
}

func TestCountErrors_GroupErrors(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	group := testutil.NewTestGroup(testutil.NewTestRecord(t1Schema, 1, nil))

	vb := &validatedBatch{
		BatchID: 1,
		Groups: []*validatedGroup{
			{
				Group: group,
				Result: &validation.GroupValidationResult{
					Group: group,
					GroupErrors: []*validation.ValidationResult{
						{Valid: false, ErrorType: validation.ErrorTypeCaseConsistency, ValidatorID: "v1"},
						{Valid: false, ErrorType: validation.ErrorTypeValueConsistency, ValidatorID: "v2"},
					},
					RecordResults: []*validation.RecordValidationResult{
						{Record: group.Records[0]},
					},
				},
			},
		},
	}

	rpc, fv, vc, cc := countErrors(vb)
	if rpc != 0 {
		t.Errorf("RecordPreCheck = %d, want 0", rpc)
	}
	if fv != 0 {
		t.Errorf("FieldValue = %d, want 0", fv)
	}
	if vc != 1 {
		t.Errorf("ValueConsistency = %d, want 1", vc)
	}
	if cc != 1 {
		t.Errorf("CaseConsistency = %d, want 1", cc)
	}
}

func TestCountErrors_RecordErrors(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, nil)
	group := testutil.NewTestGroup(rec)

	vb := &validatedBatch{
		BatchID: 1,
		Groups: []*validatedGroup{
			{
				Group: group,
				Result: &validation.GroupValidationResult{
					Group: group,
					RecordResults: []*validation.RecordValidationResult{
						{
							Record: rec,
							RecordErrors: []*validation.ValidationResult{
								{Valid: false, ErrorType: validation.ErrorTypeRecordPreCheck, ValidatorID: "rpc1"},
								{Valid: false, ErrorType: validation.ErrorTypeValueConsistency, ValidatorID: "vc1"},
								{Valid: false, ErrorType: validation.ErrorTypeCaseConsistency, ValidatorID: "cc1"},
							},
						},
					},
				},
			},
		},
	}

	rpc, fv, vc, cc := countErrors(vb)
	if rpc != 1 {
		t.Errorf("RecordPreCheck = %d, want 1", rpc)
	}
	if fv != 0 {
		t.Errorf("FieldValue = %d, want 0", fv)
	}
	if vc != 1 {
		t.Errorf("ValueConsistency = %d, want 1", vc)
	}
	if cc != 1 {
		t.Errorf("CaseConsistency = %d, want 1", cc)
	}
}

func TestCountErrors_FieldErrors(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER", "AMOUNT")
	rec := testutil.NewTestRecord(t1Schema, 1, nil)
	group := testutil.NewTestGroup(rec)

	vb := &validatedBatch{
		BatchID: 1,
		Groups: []*validatedGroup{
			{
				Group: group,
				Result: &validation.GroupValidationResult{
					Group: group,
					RecordResults: []*validation.RecordValidationResult{
						{
							Record: rec,
							FieldErrors: []*validation.ValidationResult{
								{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1", FieldName: "CASE_NUMBER"},
								{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv2", FieldName: "AMOUNT"},
							},
						},
					},
				},
			},
		},
	}

	rpc, fv, vc, cc := countErrors(vb)
	if rpc != 0 {
		t.Errorf("RecordPreCheck = %d, want 0", rpc)
	}
	if fv != 2 {
		t.Errorf("FieldValue = %d, want 2", fv)
	}
	if vc != 0 {
		t.Errorf("ValueConsistency = %d, want 0", vc)
	}
	if cc != 0 {
		t.Errorf("CaseConsistency = %d, want 0", cc)
	}
}

func TestCountErrors_MixedErrorTypes(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	t2Schema := testutil.NewTestSchema("T2", "SSN")
	rec1 := testutil.NewTestRecord(t1Schema, 1, nil)
	rec2 := testutil.NewTestRecord(t2Schema, 2, nil)
	group := testutil.NewTestGroup(rec1, rec2)

	vb := &validatedBatch{
		BatchID: 1,
		Groups: []*validatedGroup{
			{
				Group: group,
				Result: &validation.GroupValidationResult{
					Group: group,
					GroupErrors: []*validation.ValidationResult{
						{Valid: false, ErrorType: validation.ErrorTypeCaseConsistency, ValidatorID: "gc1"},
					},
					RecordResults: []*validation.RecordValidationResult{
						{
							Record: rec1,
							RecordErrors: []*validation.ValidationResult{
								{Valid: false, ErrorType: validation.ErrorTypeRecordPreCheck, ValidatorID: "rpc1"},
							},
							FieldErrors: []*validation.ValidationResult{
								{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1"},
							},
						},
						{
							Record: rec2,
							RecordErrors: []*validation.ValidationResult{
								{Valid: false, ErrorType: validation.ErrorTypeValueConsistency, ValidatorID: "vc1"},
							},
							FieldErrors: []*validation.ValidationResult{
								{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv2"},
								{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv3"},
							},
						},
					},
				},
			},
		},
	}

	rpc, fv, vc, cc := countErrors(vb)
	if rpc != 1 {
		t.Errorf("RecordPreCheck = %d, want 1", rpc)
	}
	if fv != 3 {
		t.Errorf("FieldValue = %d, want 3", fv)
	}
	if vc != 1 {
		t.Errorf("ValueConsistency = %d, want 1", vc)
	}
	if cc != 1 {
		t.Errorf("CaseConsistency = %d, want 1", cc)
	}
}

func TestCountErrors_MultipleGroups(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec1 := testutil.NewTestRecord(t1Schema, 1, nil)
	rec2 := testutil.NewTestRecord(t1Schema, 2, nil)
	group1 := testutil.NewTestGroup(rec1)
	group2 := testutil.NewTestGroup(rec2)

	vb := &validatedBatch{
		BatchID: 1,
		Groups: []*validatedGroup{
			{
				Group: group1,
				Result: &validation.GroupValidationResult{
					Group: group1,
					RecordResults: []*validation.RecordValidationResult{
						{
							Record: rec1,
							RecordErrors: []*validation.ValidationResult{
								{Valid: false, ErrorType: validation.ErrorTypeRecordPreCheck, ValidatorID: "rpc1"},
							},
						},
					},
				},
			},
			{
				Group: group2,
				Result: &validation.GroupValidationResult{
					Group: group2,
					RecordResults: []*validation.RecordValidationResult{
						{
							Record: rec2,
							FieldErrors: []*validation.ValidationResult{
								{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1"},
							},
						},
					},
				},
			},
		},
	}

	rpc, fv, vc, cc := countErrors(vb)
	if rpc != 1 {
		t.Errorf("RecordPreCheck = %d, want 1", rpc)
	}
	if fv != 1 {
		t.Errorf("FieldValue = %d, want 1", fv)
	}
	if vc != 0 {
		t.Errorf("ValueConsistency = %d, want 0", vc)
	}
	if cc != 0 {
		t.Errorf("CaseConsistency = %d, want 0", cc)
	}
}

// --- appendRecordErrors tests ---

func TestAppendRecordErrors_NoErrors(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	recResult := &validation.RecordValidationResult{Record: rec}

	var buf [][]any
	appendRecordErrors(&buf, recResult, rec, nil, 42, nil)

	if len(buf) != 0 {
		t.Errorf("buf length = %d, want 0", len(buf))
	}
}

func TestAppendRecordErrors_WithFieldError(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	recResult := &validation.RecordValidationResult{
		Record: rec,
		FieldErrors: []*validation.ValidationResult{
			{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1", FieldName: "CASE_NUMBER"},
		},
	}

	var buf [][]any
	appendRecordErrors(&buf, recResult, rec, nil, 42, nil)

	if len(buf) != 1 {
		t.Fatalf("buf length = %d, want 1", len(buf))
	}
	// Verify the error row is a valid slice (matches parserErrorColumns format)
	row := buf[0]
	if len(row) != 15 {
		t.Errorf("row length = %d, want 15 (parserErrorColumns)", len(row))
	}
}

func TestAppendRecordErrors_WithRecordUUID_SetsContentTypeForFieldErrors(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	recResult := &validation.RecordValidationResult{
		Record: rec,
		FieldErrors: []*validation.ValidationResult{
			{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1", FieldName: "CASE_NUMBER"},
		},
	}

	uuid := &pgtype.UUID{Bytes: [16]byte{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}, Valid: true}
	ctID := int32(99)

	var buf [][]any
	appendRecordErrors(&buf, recResult, rec, uuid, 42, &ctID)

	if len(buf) != 1 {
		t.Fatalf("buf length = %d, want 1", len(buf))
	}
	// content_type_id is at index 10 in parserErrorColumns
	row := buf[0]
	if ct, ok := row[10].(int32); !ok || ct != 99 {
		t.Errorf("content_type_id = %v, want 99", row[10])
	}
}

func TestAppendRecordErrors_WithRecordUUID_NoContentTypeForRecordPreCheck(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	recResult := &validation.RecordValidationResult{
		Record: rec,
		RecordErrors: []*validation.ValidationResult{
			{Valid: false, ErrorType: validation.ErrorTypeRecordPreCheck, ValidatorID: "rpc1"},
		},
	}

	uuid := &pgtype.UUID{Bytes: [16]byte{1}, Valid: true}
	ctID := int32(99)

	var buf [][]any
	appendRecordErrors(&buf, recResult, rec, uuid, 42, &ctID)

	if len(buf) != 1 {
		t.Fatalf("buf length = %d, want 1", len(buf))
	}
	// RECORD_PRE_CHECK errors should NOT get content_type_id even when UUID is set
	row := buf[0]
	if row[10] != nil {
		t.Errorf("content_type_id = %v, want nil for RECORD_PRE_CHECK", row[10])
	}
}

func TestAppendRecordErrors_MultipleErrors(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER", "AMOUNT")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	recResult := &validation.RecordValidationResult{
		Record: rec,
		RecordErrors: []*validation.ValidationResult{
			{Valid: false, ErrorType: validation.ErrorTypeValueConsistency, ValidatorID: "vc1"},
		},
		FieldErrors: []*validation.ValidationResult{
			{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1", FieldName: "CASE_NUMBER"},
			{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv2", FieldName: "AMOUNT"},
		},
	}

	var buf [][]any
	appendRecordErrors(&buf, recResult, rec, nil, 42, nil)

	if len(buf) != 3 {
		t.Errorf("buf length = %d, want 3", len(buf))
	}
}

func TestAppendRecordErrors_BufferReuse(t *testing.T) {
	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})

	// Pre-populate buffer with existing data
	buf := make([][]any, 0, 10)
	buf = append(buf, []any{"existing row"})

	recResult := &validation.RecordValidationResult{
		Record: rec,
		FieldErrors: []*validation.ValidationResult{
			{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1", FieldName: "CASE_NUMBER"},
		},
	}
	appendRecordErrors(&buf, recResult, rec, nil, 42, nil)

	if len(buf) != 2 {
		t.Errorf("buf length = %d, want 2 (1 existing + 1 new)", len(buf))
	}
}

// --- routeValidatedBatch tests ---

// buildTestRouter creates a real Router backed by a recording sink for testing.
// The router is set up with an error writer but no record writers (since we don't
// have real serializers for test schemas).
func buildTestRouter(t *testing.T, ctx context.Context) (*writer.Router, *recordingSink) {
	t.Helper()
	sink := newRecordingSink()

	// Build a minimal filespec and registry for the router
	spec := &filespec.FileSpec{
		Program: "TEST",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{}, // No record writers - just error writer
	}

	schemas := map[string]*schema.CompiledSchema{}
	reg := config.NewTestRegistry(schemas)

	router := writer.NewRouter(sink, 42, spec, reg, writer.RouterConfig{
		FlushThreshold:      100,
		ErrorFlushThreshold: 100,
		IncludeRecords:      false, // No record writers needed
		IncludeErrors:       true,
	})
	router.Start(ctx)
	return router, sink
}

// recordingSink captures all flushed rows for assertion.
type recordingSink struct {
	mu      sync.Mutex
	flushed map[string][][]any
}

func newRecordingSink() *recordingSink {
	return &recordingSink{flushed: make(map[string][][]any)}
}

func (s *recordingSink) Flush(_ context.Context, tableName string, _ []string, rows [][]any) (int64, error) {
	copied := make([][]any, len(rows))
	copy(copied, rows)
	s.mu.Lock()
	defer s.mu.Unlock()
	s.flushed[tableName] = append(s.flushed[tableName], copied...)
	return int64(len(rows)), nil
}

func (s *recordingSink) RollbackDatafile(_ context.Context, _ int32, _ []string, _ string) error {
	return nil
}
func (s *recordingSink) Close() error { return nil }

func (s *recordingSink) errorRows() [][]any {
	s.mu.Lock()
	defer s.mu.Unlock()
	if rows := s.flushed["shadow_parser_error"]; len(rows) > 0 {
		return slices.Clone(rows)
	}
	return slices.Clone(s.flushed["parser_error"])
}

func TestRouteValidatedBatch_NoErrors_NoWriters(t *testing.T) {
	ctx := context.Background()
	router, sink := buildTestRouter(t, ctx)

	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	group := testutil.NewTestGroup(rec)

	groups := []*validatedGroup{
		{
			Group: group,
			Result: &validation.GroupValidationResult{
				Group: group,
				RecordResults: []*validation.RecordValidationResult{
					{Record: rec},
				},
			},
		},
	}

	var errorRows [][]any
	err := routeValidatedBatch(ctx, router, groups, 42, &errorRows)
	if err != nil {
		t.Fatalf("routeValidatedBatch error: %v", err)
	}

	if err := router.Stop(); err != nil {
		t.Fatalf("router.Stop error: %v", err)
	}

	// No errors should have been written
	if len(sink.errorRows()) != 0 {
		t.Errorf("error rows = %d, want 0", len(sink.errorRows()))
	}
}

func TestRouteValidatedBatch_GroupErrors_WrittenToSink(t *testing.T) {
	ctx := context.Background()
	router, sink := buildTestRouter(t, ctx)

	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	group := testutil.NewTestGroup(rec)

	groups := []*validatedGroup{
		{
			Group: group,
			Result: &validation.GroupValidationResult{
				Group: group,
				GroupErrors: []*validation.ValidationResult{
					{Valid: false, ErrorType: validation.ErrorTypeValueConsistency, ValidatorID: "vc1"},
				},
				RecordResults: []*validation.RecordValidationResult{
					{Record: rec},
				},
			},
		},
	}

	var errorRows [][]any
	err := routeValidatedBatch(ctx, router, groups, 42, &errorRows)
	if err != nil {
		t.Fatalf("routeValidatedBatch error: %v", err)
	}

	if err := router.Stop(); err != nil {
		t.Fatalf("router.Stop error: %v", err)
	}

	// Group error should have been written
	if len(sink.errorRows()) != 1 {
		t.Errorf("error rows = %d, want 1", len(sink.errorRows()))
	}
}

func TestRouteValidatedBatch_BlockingGroupError_SkipsRecords(t *testing.T) {
	ctx := context.Background()
	router, sink := buildTestRouter(t, ctx)

	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	group := testutil.NewTestGroup(rec)

	groups := []*validatedGroup{
		{
			Group: group,
			Result: &validation.GroupValidationResult{
				Group: group,
				GroupErrors: []*validation.ValidationResult{
					{Valid: false, ErrorType: validation.ErrorTypeCaseConsistency, ValidatorID: "cc1"},
				},
				RecordResults: []*validation.RecordValidationResult{
					{
						Record: rec,
						FieldErrors: []*validation.ValidationResult{
							{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1", FieldName: "CASE_NUMBER"},
						},
					},
				},
			},
		},
	}

	var errorRows [][]any
	err := routeValidatedBatch(ctx, router, groups, 42, &errorRows)
	if err != nil {
		t.Fatalf("routeValidatedBatch error: %v", err)
	}

	if err := router.Stop(); err != nil {
		t.Fatalf("router.Stop error: %v", err)
	}

	// Group error + field error should both be written
	if len(sink.errorRows()) != 2 {
		t.Errorf("error rows = %d, want 2 (1 group + 1 field)", len(sink.errorRows()))
	}
}

func TestRouteValidatedBatch_EmptyGroups(t *testing.T) {
	ctx := context.Background()
	router, _ := buildTestRouter(t, ctx)

	var errorRows [][]any
	err := routeValidatedBatch(ctx, router, nil, 42, &errorRows)
	if err != nil {
		t.Fatalf("routeValidatedBatch error: %v", err)
	}

	if err := router.Stop(); err != nil {
		t.Fatalf("router.Stop error: %v", err)
	}
}

func TestRouteValidatedBatch_RecordWithBlockingError_SkipsRecord(t *testing.T) {
	ctx := context.Background()
	router, sink := buildTestRouter(t, ctx)

	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "12345"})
	group := testutil.NewTestGroup(rec)

	groups := []*validatedGroup{
		{
			Group: group,
			Result: &validation.GroupValidationResult{
				Group: group,
				RecordResults: []*validation.RecordValidationResult{
					{
						Record: rec,
						RecordErrors: []*validation.ValidationResult{
							{Valid: false, ErrorType: validation.ErrorTypeRecordPreCheck, ValidatorID: "rpc1"},
						},
					},
				},
			},
		},
	}

	var errorRows [][]any
	err := routeValidatedBatch(ctx, router, groups, 42, &errorRows)
	if err != nil {
		t.Fatalf("routeValidatedBatch error: %v", err)
	}

	if err := router.Stop(); err != nil {
		t.Fatalf("router.Stop error: %v", err)
	}

	// RECORD_PRE_CHECK error should be written
	if len(sink.errorRows()) != 1 {
		t.Errorf("error rows = %d, want 1", len(sink.errorRows()))
	}
}

func TestRouteValidatedBatch_MultipleGroupsAndRecords(t *testing.T) {
	ctx := context.Background()
	router, sink := buildTestRouter(t, ctx)

	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec1 := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "11111"})
	rec2 := testutil.NewTestRecord(t1Schema, 2, map[string]any{"CASE_NUMBER": "22222"})
	group1 := testutil.NewTestGroup(rec1)
	group2 := testutil.NewTestGroup(rec2)

	groups := []*validatedGroup{
		{
			Group: group1,
			Result: &validation.GroupValidationResult{
				Group: group1,
				RecordResults: []*validation.RecordValidationResult{
					{
						Record: rec1,
						FieldErrors: []*validation.ValidationResult{
							{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1", FieldName: "CASE_NUMBER"},
						},
					},
				},
			},
		},
		{
			Group: group2,
			Result: &validation.GroupValidationResult{
				Group: group2,
				RecordResults: []*validation.RecordValidationResult{
					{
						Record: rec2,
						RecordErrors: []*validation.ValidationResult{
							{Valid: false, ErrorType: validation.ErrorTypeRecordPreCheck, ValidatorID: "rpc1"},
						},
					},
				},
			},
		},
	}

	var errorRows [][]any
	err := routeValidatedBatch(ctx, router, groups, 42, &errorRows)
	if err != nil {
		t.Fatalf("routeValidatedBatch error: %v", err)
	}

	if err := router.Stop(); err != nil {
		t.Fatalf("router.Stop error: %v", err)
	}

	// Group1's field error is NOT written because the record has no writer
	// (HasWriter returns false, so the record is silently skipped including its errors).
	// Only group2's RECORD_PRE_CHECK error is written (blocking errors always write).
	if len(sink.errorRows()) != 1 {
		t.Errorf("error rows = %d, want 1 (only group2's blocking error)", len(sink.errorRows()))
	}
}

func TestRouteValidatedBatch_ErrorRowBufferReused(t *testing.T) {
	ctx := context.Background()
	router, _ := buildTestRouter(t, ctx)

	t1Schema := testutil.NewTestSchema("T1", "CASE_NUMBER")
	rec1 := testutil.NewTestRecord(t1Schema, 1, map[string]any{"CASE_NUMBER": "11111"})
	rec2 := testutil.NewTestRecord(t1Schema, 2, map[string]any{"CASE_NUMBER": "22222"})
	group1 := testutil.NewTestGroup(rec1)
	group2 := testutil.NewTestGroup(rec2)

	groups := []*validatedGroup{
		{
			Group: group1,
			Result: &validation.GroupValidationResult{
				Group: group1,
				RecordResults: []*validation.RecordValidationResult{
					{
						Record: rec1,
						FieldErrors: []*validation.ValidationResult{
							{Valid: false, ErrorType: validation.ErrorTypeFieldValue, ValidatorID: "fv1", FieldName: "CASE_NUMBER"},
						},
					},
				},
			},
		},
		{
			Group: group2,
			Result: &validation.GroupValidationResult{
				Group: group2,
				RecordResults: []*validation.RecordValidationResult{
					{Record: rec2},
				},
			},
		},
	}

	// Pre-allocate buffer to test reuse
	errorRows := make([][]any, 0, 16)
	err := routeValidatedBatch(ctx, router, groups, 42, &errorRows)
	if err != nil {
		t.Fatalf("routeValidatedBatch error: %v", err)
	}

	if err := router.Stop(); err != nil {
		t.Fatalf("router.Stop error: %v", err)
	}

	// Buffer should have been reset between groups - verify capacity was reused
	if cap(errorRows) < 16 {
		t.Errorf("errorRows cap = %d, expected >= 16 (buffer reuse)", cap(errorRows))
	}
}
