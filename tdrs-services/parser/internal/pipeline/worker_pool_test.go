package pipeline

import (
	"context"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
	"go-parser/internal/metrics"
	"go-parser/internal/parser"
	"go-parser/internal/storage/writer"
	"go-parser/internal/validation"
)

// buildTestSchemaWithPool creates a CompiledSchema with an initialized object pool.
func buildTestSchemaWithPool(recordType string, shared []schema.FieldDef, segments []schema.SegmentDef) *schema.CompiledSchema {
	sdef := &schema.SchemaDef{
		RecordType: recordType,
		Shared:     shared,
		Segments:   segments,
	}
	cs := sdef.Compile()
	cs.InitPool(func() any {
		return &parser.ParsedRecord{
			Schema: cs,
			Fields: make([]parser.ParsedField, cs.FieldCount),
		}
	})
	return cs
}

func TestNewWorkerPool_Construction(t *testing.T) {
	parseCtx := &parser.ParseContext{}
	parsingOrch := parser.NewParsingOrchestrator(filespec.FormatPositional, parseCtx)
	valOrch := validation.NewValidationOrchestrator(&validation.ValidatorRegistry{}, false)

	ctx := context.Background()
	sink := &stubSink{}
	spec := &filespec.FileSpec{
		Program: "TEST",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{},
	}
	reg := config.NewTestRegistry(map[string]*schema.CompiledSchema{})
	router := writer.NewRouter(sink, 42, spec, reg, writer.RouterConfig{
		IncludeRecords: false,
		IncludeErrors:  true,
	})
	router.Start(ctx)

	wp := NewWorkerPool(parsingOrch, valOrch, &validation.DataFileContext{}, "TEST:1", router, 42, WorkerPoolConfig{
		NumWorkers:     4,
		WorkBufferSize: 8,
	})

	if wp == nil {
		t.Fatal("NewWorkerPool returned nil")
	}
	if wp.numWorkers != 4 {
		t.Errorf("numWorkers = %d, want 4", wp.numWorkers)
	}
	if wp.filespecKey != "TEST:1" {
		t.Errorf("filespecKey = %q, want TEST:1", wp.filespecKey)
	}
	if wp.datafileID != 42 {
		t.Errorf("datafileID = %d, want 42", wp.datafileID)
	}
	if len(wp.workerStats) != 4 {
		t.Errorf("workerStats len = %d, want 4", len(wp.workerStats))
	}

	_ = router.Stop()
}

func TestWorkerPool_StartAndStop_NoWork(t *testing.T) {
	parseCtx := &parser.ParseContext{}
	parsingOrch := parser.NewParsingOrchestrator(filespec.FormatPositional, parseCtx)
	valOrch := validation.NewValidationOrchestrator(&validation.ValidatorRegistry{}, false)

	ctx := context.Background()
	sink := &stubSink{}
	spec := &filespec.FileSpec{
		Program: "TEST",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{},
	}
	reg := config.NewTestRegistry(map[string]*schema.CompiledSchema{})
	router := writer.NewRouter(sink, 42, spec, reg, writer.RouterConfig{
		IncludeRecords: false,
		IncludeErrors:  true,
	})
	router.Start(ctx)

	wp := NewWorkerPool(parsingOrch, valOrch, &validation.DataFileContext{}, "TEST:1", router, 42, WorkerPoolConfig{
		NumWorkers:     2,
		WorkBufferSize: 4,
	})
	wp.Start(ctx)

	// Close immediately with no work submitted
	wp.CloseInputs()
	wp.Wait()

	if err := wp.Err(); err != nil {
		t.Errorf("Err() = %v, want nil", err)
	}

	stats := wp.AggregateStats()
	if stats.BatchCount != 0 {
		t.Errorf("BatchCount = %d, want 0", stats.BatchCount)
	}
	if stats.GroupCount != 0 {
		t.Errorf("GroupCount = %d, want 0", stats.GroupCount)
	}
	if stats.Total() != 0 {
		t.Errorf("Total errors = %d, want 0", stats.Total())
	}

	_ = router.Stop()
}

func TestWorkerPool_ProcessesBatches(t *testing.T) {
	// Create a real schema with a pool
	t1Schema := buildTestSchemaWithPool("T1",
		[]schema.FieldDef{
			{Name: "RECORD_TYPE", Type: "string", Start: 0, End: 2},
			{Name: "RPT_MONTH_YEAR", Type: "string", Start: 2, End: 8},
			{Name: "CASE_NUMBER", Type: "string", Start: 8, End: 19},
		},
		[]schema.SegmentDef{
			{Fields: []schema.FieldDef{
				{Name: "COUNTY_FIPS_CODE", Type: "string", Start: 19, End: 22},
			}},
		},
	)
	t1Schema.Path = "tanf/t1"

	parseCtx := &parser.ParseContext{}
	parsingOrch := parser.NewParsingOrchestrator(filespec.FormatPositional, parseCtx)
	valOrch := validation.NewValidationOrchestrator(&validation.ValidatorRegistry{}, false)

	ctx := context.Background()
	sink := &stubSink{}
	spec := &filespec.FileSpec{
		Program: "TEST",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{},
	}
	reg := config.NewTestRegistry(map[string]*schema.CompiledSchema{"tanf/t1": t1Schema})
	router := writer.NewRouter(sink, 42, spec, reg, writer.RouterConfig{
		IncludeRecords: false,
		IncludeErrors:  true,
	})
	router.Start(ctx)

	wp := NewWorkerPool(parsingOrch, valOrch, &validation.DataFileContext{}, "TEST:1", router, 42, WorkerPoolConfig{
		NumWorkers:     2,
		WorkBufferSize: 4,
	})
	wp.Start(ctx)

	// Build a DecodedBatch with real decoded data
	row := decoder.NewPositionalRow(2, "T1", 156, "T1202401   12345  100")
	batch := &parser.DecodedBatch{
		BatchID: 1,
		DecodedGroups: []*parser.DecodedGroup{
			{
				Key: "202401|12345",
				DecodedRecords: []parser.DecodedRecord{
					{Row: row, Schema: t1Schema},
				},
			},
		},
	}

	wp.Submit(batch)
	wp.CloseInputs()
	wp.Wait()

	if err := wp.Err(); err != nil {
		t.Errorf("Err() = %v, want nil", err)
	}

	stats := wp.AggregateStats()
	if stats.BatchCount != 1 {
		t.Errorf("BatchCount = %d, want 1", stats.BatchCount)
	}
	if stats.GroupCount != 1 {
		t.Errorf("GroupCount = %d, want 1", stats.GroupCount)
	}

	_ = router.Stop()
}

func TestWorkerPool_MultipleBatches(t *testing.T) {
	t1Schema := buildTestSchemaWithPool("T1",
		[]schema.FieldDef{
			{Name: "RECORD_TYPE", Type: "string", Start: 0, End: 2},
			{Name: "RPT_MONTH_YEAR", Type: "string", Start: 2, End: 8},
			{Name: "CASE_NUMBER", Type: "string", Start: 8, End: 19},
		},
		[]schema.SegmentDef{
			{Fields: []schema.FieldDef{
				{Name: "COUNTY_FIPS_CODE", Type: "string", Start: 19, End: 22},
			}},
		},
	)
	t1Schema.Path = "tanf/t1"

	parseCtx := &parser.ParseContext{}
	parsingOrch := parser.NewParsingOrchestrator(filespec.FormatPositional, parseCtx)
	valOrch := validation.NewValidationOrchestrator(&validation.ValidatorRegistry{}, false)

	ctx := context.Background()
	sink := &stubSink{}
	spec := &filespec.FileSpec{
		Program: "TEST",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{},
	}
	reg := config.NewTestRegistry(map[string]*schema.CompiledSchema{"tanf/t1": t1Schema})
	router := writer.NewRouter(sink, 42, spec, reg, writer.RouterConfig{
		IncludeRecords: false,
		IncludeErrors:  true,
	})
	router.Start(ctx)

	wp := NewWorkerPool(parsingOrch, valOrch, &validation.DataFileContext{}, "TEST:1", router, 42, WorkerPoolConfig{
		NumWorkers:     2,
		WorkBufferSize: 8,
	})
	wp.Start(ctx)

	// Submit multiple batches
	for i := range 5 {
		row := decoder.NewPositionalRow(i+2, "T1", 156, "T1202401   12345  100")
		batch := &parser.DecodedBatch{
			BatchID: i + 1,
			DecodedGroups: []*parser.DecodedGroup{
				{
					Key: "202401|12345",
					DecodedRecords: []parser.DecodedRecord{
						{Row: row, Schema: t1Schema},
					},
				},
			},
		}
		wp.Submit(batch)
	}

	wp.CloseInputs()
	wp.Wait()

	if err := wp.Err(); err != nil {
		t.Errorf("Err() = %v, want nil", err)
	}

	stats := wp.AggregateStats()
	if stats.BatchCount != 5 {
		t.Errorf("BatchCount = %d, want 5", stats.BatchCount)
	}
	if stats.GroupCount != 5 {
		t.Errorf("GroupCount = %d, want 5", stats.GroupCount)
	}

	_ = router.Stop()
}

func TestWorkerPool_AggregateStats_CombinesWorkers(t *testing.T) {
	parseCtx := &parser.ParseContext{}
	parsingOrch := parser.NewParsingOrchestrator(filespec.FormatPositional, parseCtx)
	valOrch := validation.NewValidationOrchestrator(&validation.ValidatorRegistry{}, false)

	ctx := context.Background()
	sink := &stubSink{}
	spec := &filespec.FileSpec{
		Program: "TEST",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{},
	}
	reg := config.NewTestRegistry(map[string]*schema.CompiledSchema{})
	router := writer.NewRouter(sink, 42, spec, reg, writer.RouterConfig{
		IncludeRecords: false,
		IncludeErrors:  true,
	})
	router.Start(ctx)

	wp := NewWorkerPool(parsingOrch, valOrch, &validation.DataFileContext{}, "TEST:1", router, 42, WorkerPoolConfig{
		NumWorkers:     3,
		WorkBufferSize: 4,
	})

	// Manually set worker stats to test aggregation
	wp.workerStats[0] = RouteStats{
		ErrorStats:      ErrorStats{RecordPreCheck: 1, FieldValue: 2},
		BatchCount:      3,
		GroupCount:      4,
		ParsingDuration: 100 * time.Millisecond,
		RoutingDuration: 10 * time.Millisecond,
		ActiveDuration:  150 * time.Millisecond,
		ValidationDurations: validation.PhaseDurations{
			GroupValidation:  20 * time.Millisecond,
			RecordValidation: 30 * time.Millisecond,
			FieldValidation:  40 * time.Millisecond,
		},
	}
	wp.workerStats[1] = RouteStats{
		ErrorStats:      ErrorStats{ValueConsistency: 5, CaseConsistency: 6},
		BatchCount:      7,
		GroupCount:      8,
		ParsingDuration: 200 * time.Millisecond,
		RoutingDuration: 20 * time.Millisecond,
		ActiveDuration:  250 * time.Millisecond,
		ValidationDurations: validation.PhaseDurations{
			GroupValidation:  30 * time.Millisecond,
			RecordValidation: 40 * time.Millisecond,
			FieldValidation:  50 * time.Millisecond,
		},
	}
	wp.workerStats[2] = RouteStats{
		ErrorStats:      ErrorStats{RecordPreCheck: 10, FieldValue: 20, ValueConsistency: 30, CaseConsistency: 40},
		BatchCount:      50,
		GroupCount:      60,
		ParsingDuration: 300 * time.Millisecond,
		RoutingDuration: 30 * time.Millisecond,
		ActiveDuration:  350 * time.Millisecond,
		ValidationDurations: validation.PhaseDurations{
			GroupValidation:  40 * time.Millisecond,
			RecordValidation: 50 * time.Millisecond,
			FieldValidation:  60 * time.Millisecond,
		},
	}

	stats := wp.AggregateStats()

	if stats.RecordPreCheck != 11 {
		t.Errorf("RecordPreCheck = %d, want 11", stats.RecordPreCheck)
	}
	if stats.FieldValue != 22 {
		t.Errorf("FieldValue = %d, want 22", stats.FieldValue)
	}
	if stats.ValueConsistency != 35 {
		t.Errorf("ValueConsistency = %d, want 35", stats.ValueConsistency)
	}
	if stats.CaseConsistency != 46 {
		t.Errorf("CaseConsistency = %d, want 46", stats.CaseConsistency)
	}
	if stats.BatchCount != 60 {
		t.Errorf("BatchCount = %d, want 60", stats.BatchCount)
	}
	if stats.GroupCount != 72 {
		t.Errorf("GroupCount = %d, want 72", stats.GroupCount)
	}
	if stats.ParsingDuration != 600*time.Millisecond {
		t.Errorf("ParsingDuration = %s, want 600ms", stats.ParsingDuration)
	}
	if stats.RoutingDuration != 60*time.Millisecond {
		t.Errorf("RoutingDuration = %s, want 60ms", stats.RoutingDuration)
	}
	if stats.ActiveDuration != 750*time.Millisecond {
		t.Errorf("ActiveDuration = %s, want 750ms", stats.ActiveDuration)
	}
	if stats.ValidationDurations.GroupValidation != 90*time.Millisecond {
		t.Errorf("GroupValidation = %s, want 90ms", stats.ValidationDurations.GroupValidation)
	}
	if stats.ValidationDurations.RecordValidation != 120*time.Millisecond {
		t.Errorf("RecordValidation = %s, want 120ms", stats.ValidationDurations.RecordValidation)
	}
	if stats.ValidationDurations.FieldValidation != 150*time.Millisecond {
		t.Errorf("FieldValidation = %s, want 150ms", stats.ValidationDurations.FieldValidation)
	}

	_ = router.Stop()
}

func TestWorkerPool_RecordWorkerMetrics_EmitsAggregatedMetricsOnce(t *testing.T) {
	registry := metrics.NewRegistry("celery")
	metrics.UseDefault(registry)
	defer metrics.ResetDefault()

	wp := &WorkerPool{
		metricsProgram: "TAN",
		metricsSection: 1,
		numWorkers:     2,
		workerStats: []RouteStats{
			{
				ParsingDuration: 1 * time.Second,
				RoutingDuration: 2 * time.Second,
				ActiveDuration:  3 * time.Second,
				ValidationDurations: validation.PhaseDurations{
					GroupValidation:  4 * time.Second,
					RecordValidation: 5 * time.Second,
					FieldValidation:  6 * time.Second,
				},
			},
			{
				ParsingDuration: 2 * time.Second,
				RoutingDuration: 3 * time.Second,
				ActiveDuration:  4 * time.Second,
				ValidationDurations: validation.PhaseDurations{
					GroupValidation:  6 * time.Second,
					RecordValidation: 7 * time.Second,
					FieldValidation:  8 * time.Second,
				},
			},
		},
	}

	body := scrapeWorkerPoolMetrics(registry)
	assertMetricsMissing(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_parsing"}`)
	assertMetricsMissing(t, body, `go_parser_worker_pool_active_duration_seconds_total{program="TAN",section="1",server_mode="celery"}`)

	wp.recordWorkerMetrics()
	wp.recordWorkerMetrics()

	body = scrapeWorkerPoolMetrics(registry)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_parsing"} 1`)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_sum{program="TAN",section="1",server_mode="celery",stage="worker_parsing"} 3`)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_group_validation"} 1`)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_sum{program="TAN",section="1",server_mode="celery",stage="worker_group_validation"} 10`)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_record_validation"} 1`)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_sum{program="TAN",section="1",server_mode="celery",stage="worker_record_validation"} 12`)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_field_validation"} 1`)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_sum{program="TAN",section="1",server_mode="celery",stage="worker_field_validation"} 14`)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_routing"} 1`)
	assertMetricsContains(t, body, `go_parser_pipeline_stage_duration_seconds_sum{program="TAN",section="1",server_mode="celery",stage="worker_routing"} 5`)
	assertMetricsContains(t, body, `go_parser_worker_pool_active_duration_seconds_total{program="TAN",section="1",server_mode="celery"} 7`)
	assertMetricsMissing(t, body, `go_parser_worker_pool_active_workers{program="TAN",section="1",server_mode="celery"}`)
	assertMetricsMissing(t, body, `go_parser_worker_pool_utilization{program="TAN",section="1",server_mode="celery"}`)
}

func TestWorkerPool_ProcessBatch_AccumulatesTimingWithoutMetrics(t *testing.T) {
	registry := metrics.NewRegistry("celery")
	metrics.UseDefault(registry)
	defer metrics.ResetDefault()

	t1Schema := buildTestSchemaWithPool("T1",
		[]schema.FieldDef{
			{Name: "RECORD_TYPE", Type: "string", Start: 0, End: 2},
			{Name: "RPT_MONTH_YEAR", Type: "string", Start: 2, End: 8},
			{Name: "CASE_NUMBER", Type: "string", Start: 8, End: 19},
		},
		[]schema.SegmentDef{
			{Fields: []schema.FieldDef{
				{Name: "COUNTY_FIPS_CODE", Type: "string", Start: 19, End: 22},
			}},
		},
	)
	t1Schema.Path = "tanf/t1"

	parseCtx := &parser.ParseContext{}
	parsingOrch := parser.NewParsingOrchestrator(filespec.FormatPositional, parseCtx)
	valOrch := validation.NewValidationOrchestrator(&validation.ValidatorRegistry{}, false)
	wp := NewWorkerPool(parsingOrch, valOrch, &validation.DataFileContext{}, "TAN:1", nil, 42, WorkerPoolConfig{
		NumWorkers:     1,
		WorkBufferSize: 1,
	})

	decodedRecords := make([]parser.DecodedRecord, 100)
	for i := range decodedRecords {
		row := decoder.NewPositionalRow(i+2, "T1", 156, "T1202401   12345  100")
		decodedRecords[i] = parser.DecodedRecord{Row: row, Schema: t1Schema}
	}
	batch := &parser.DecodedBatch{
		BatchID: 1,
		DecodedGroups: []*parser.DecodedGroup{
			{
				Key:            "202401|12345",
				DecodedRecords: decodedRecords,
			},
		},
	}

	vb := wp.processBatch(batch)
	if vb.ParsingDuration <= 0 {
		t.Errorf("ParsingDuration = %s, want positive duration", vb.ParsingDuration)
	}
	if len(vb.Groups) != 1 {
		t.Fatalf("Groups len = %d, want 1", len(vb.Groups))
	}

	body := scrapeWorkerPoolMetrics(registry)
	assertMetricsMissing(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_parsing"}`)
	assertMetricsMissing(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_group_validation"}`)
	assertMetricsMissing(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_record_validation"}`)
	assertMetricsMissing(t, body, `go_parser_pipeline_stage_duration_seconds_count{program="TAN",section="1",server_mode="celery",stage="worker_field_validation"}`)
}

func TestWorkerPool_ContextCancellation(t *testing.T) {
	parseCtx := &parser.ParseContext{}
	parsingOrch := parser.NewParsingOrchestrator(filespec.FormatPositional, parseCtx)
	valOrch := validation.NewValidationOrchestrator(&validation.ValidatorRegistry{}, false)

	ctx, cancel := context.WithCancel(context.Background())
	sink := &stubSink{}
	spec := &filespec.FileSpec{
		Program: "TEST",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{},
	}
	reg := config.NewTestRegistry(map[string]*schema.CompiledSchema{})
	router := writer.NewRouter(sink, 42, spec, reg, writer.RouterConfig{
		IncludeRecords: false,
		IncludeErrors:  true,
	})
	router.Start(ctx)

	wp := NewWorkerPool(parsingOrch, valOrch, &validation.DataFileContext{}, "TEST:1", router, 42, WorkerPoolConfig{
		NumWorkers:     2,
		WorkBufferSize: 4,
	})
	wp.Start(ctx)

	// Cancel the context - workers should exit
	cancel()
	wp.CloseInputs()
	wp.Wait()

	// No error expected from cancellation (workers just return)
	_ = router.Stop()
}

func TestWorkerPool_ProcessBatch_WithMultipleGroups(t *testing.T) {
	t1Schema := buildTestSchemaWithPool("T1",
		[]schema.FieldDef{
			{Name: "RECORD_TYPE", Type: "string", Start: 0, End: 2},
			{Name: "RPT_MONTH_YEAR", Type: "string", Start: 2, End: 8},
			{Name: "CASE_NUMBER", Type: "string", Start: 8, End: 19},
		},
		[]schema.SegmentDef{
			{Fields: []schema.FieldDef{
				{Name: "COUNTY_FIPS_CODE", Type: "string", Start: 19, End: 22},
			}},
		},
	)
	t1Schema.Path = "tanf/t1"

	parseCtx := &parser.ParseContext{}
	parsingOrch := parser.NewParsingOrchestrator(filespec.FormatPositional, parseCtx)
	valOrch := validation.NewValidationOrchestrator(&validation.ValidatorRegistry{}, false)

	ctx := context.Background()
	sink := &stubSink{}
	spec := &filespec.FileSpec{
		Program: "TEST",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{},
	}
	reg := config.NewTestRegistry(map[string]*schema.CompiledSchema{"tanf/t1": t1Schema})
	router := writer.NewRouter(sink, 42, spec, reg, writer.RouterConfig{
		IncludeRecords: false,
		IncludeErrors:  true,
	})
	router.Start(ctx)

	wp := NewWorkerPool(parsingOrch, valOrch, &validation.DataFileContext{}, "TEST:1", router, 42, WorkerPoolConfig{
		NumWorkers:     1,
		WorkBufferSize: 4,
	})
	wp.Start(ctx)

	// Batch with 2 groups
	row1 := decoder.NewPositionalRow(2, "T1", 156, "T1202401   11111  100")
	row2 := decoder.NewPositionalRow(3, "T1", 156, "T1202401   22222  200")
	batch := &parser.DecodedBatch{
		BatchID: 1,
		DecodedGroups: []*parser.DecodedGroup{
			{
				Key:            "202401|11111",
				DecodedRecords: []parser.DecodedRecord{{Row: row1, Schema: t1Schema}},
			},
			{
				Key:            "202401|22222",
				DecodedRecords: []parser.DecodedRecord{{Row: row2, Schema: t1Schema}},
			},
		},
	}

	wp.Submit(batch)
	wp.CloseInputs()
	wp.Wait()

	if err := wp.Err(); err != nil {
		t.Errorf("Err() = %v, want nil", err)
	}

	stats := wp.AggregateStats()
	if stats.BatchCount != 1 {
		t.Errorf("BatchCount = %d, want 1", stats.BatchCount)
	}
	if stats.GroupCount != 2 {
		t.Errorf("GroupCount = %d, want 2", stats.GroupCount)
	}

	_ = router.Stop()
}

func TestWorkerPool_Err_NilWhenNoError(t *testing.T) {
	wp := &WorkerPool{
		workerStats: make([]RouteStats, 2),
	}
	if wp.Err() != nil {
		t.Errorf("Err() = %v, want nil", wp.Err())
	}
}

func scrapeWorkerPoolMetrics(registry *metrics.Registry) string {
	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rec := httptest.NewRecorder()
	registry.ServeHTTP(rec, req)
	return rec.Body.String()
}

func assertMetricsContains(t *testing.T, body string, want string) {
	t.Helper()
	if !strings.Contains(body, want) {
		t.Fatalf("metrics body missing %q\nbody:\n%s", want, body)
	}
}

func assertMetricsMissing(t *testing.T, body string, want string) {
	t.Helper()
	if strings.Contains(body, want) {
		t.Fatalf("metrics body unexpectedly contained %q\nbody:\n%s", want, body)
	}
}
