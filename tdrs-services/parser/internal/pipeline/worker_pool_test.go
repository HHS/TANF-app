package pipeline

import (
	"context"
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
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
		ErrorStats: ErrorStats{RecordPreCheck: 1, FieldValue: 2},
		BatchCount: 3, GroupCount: 4,
	}
	wp.workerStats[1] = RouteStats{
		ErrorStats: ErrorStats{ValueConsistency: 5, CaseConsistency: 6},
		BatchCount: 7, GroupCount: 8,
	}
	wp.workerStats[2] = RouteStats{
		ErrorStats: ErrorStats{RecordPreCheck: 10, FieldValue: 20, ValueConsistency: 30, CaseConsistency: 40},
		BatchCount: 50, GroupCount: 60,
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

	_ = router.Stop()
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
