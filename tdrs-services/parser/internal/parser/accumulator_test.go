package parser

import (
	"testing"

	"go-parser/internal/config"
	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
)

// buildNonKeyedSpec creates a FRA-style spec with no key_fields.
func buildNonKeyedSpec() *filespec.FileSpec {
	batchSize := 1
	return &filespec.FileSpec{
		Program: "FRA",
		Section: 1,
		Format:  filespec.FormatColumnar,
		Schemas: []string{"fra/te1"},
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "fixed",
			Schema: "fra/te1",
		},
		Accumulator: filespec.AccumulatorConfig{
			BatchSize:      &batchSize,
			GroupedSchemas: []string{"fra/te1"},
		},
	}
}

func buildKeyedColumnarSpec() *filespec.FileSpec {
	batchSize := 1
	return &filespec.FileSpec{
		Program: "FRA",
		Section: 1,
		Format:  filespec.FormatColumnar,
		Schemas: []string{"fra/te1"},
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "fixed",
			Schema: "fra/te1",
		},
		Accumulator: filespec.AccumulatorConfig{
			KeyFields: &filespec.KeyFieldsConfig{
				Fields: []filespec.KeyFieldDef{
					{Name: "exit_date", PositionDef: filespec.PositionDef{Start: 0, End: 1}},
					{Name: "ssn", PositionDef: filespec.PositionDef{Start: 1, End: 2}},
				},
			},
			BatchSize:      &batchSize,
			GroupedSchemas: []string{"fra/te1"},
		},
	}
}

// buildNonKeyedSchemas creates schemas for the non-keyed spec.
func buildNonKeyedSchemas() map[string]*schema.CompiledSchema {
	return map[string]*schema.CompiledSchema{
		"fra/te1": {
			SchemaDef: &schema.SchemaDef{RecordType: "TE1"},
			Path:      "fra/te1",
		},
	}
}

// buildBatchSize0Spec creates a TANF spec with batch_size=0 (all accumulated until Drain).
func buildBatchSize0Spec() *filespec.FileSpec {
	batchSize := 0
	return &filespec.FileSpec{
		Program: "TAN",
		Section: 1,
		Format:  filespec.FormatPositional,
		Schemas: []string{"common/header", "common/trailer", "tanf/t1", "tanf/t2", "tanf/t3"},
		RecordTypeDetection: filespec.RecordTypeDetection{
			Method: "prefix",
			Prefixes: []filespec.PrefixMapping{
				{Prefix: "HEADER", Schema: "common/header"},
				{Prefix: "TRAILER", Schema: "common/trailer"},
				{Prefix: "T1", Schema: "tanf/t1"},
				{Prefix: "T2", Schema: "tanf/t2"},
				{Prefix: "T3", Schema: "tanf/t3"},
			},
		},
		Accumulator: filespec.AccumulatorConfig{
			KeyFields: &filespec.KeyFieldsConfig{
				Fields: []filespec.KeyFieldDef{
					{Name: "rpt_month_year", PositionDef: filespec.PositionDef{Start: 2, End: 8}},
					{Name: "case_number", PositionDef: filespec.PositionDef{Start: 8, End: 19}},
				},
			},
			BatchSize:      &batchSize,
			GroupedSchemas: []string{"tanf/t1", "tanf/t2", "tanf/t3"},
		},
	}
}

func TestNewAccumulator(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)

	acc := NewAccumulator(spec, detector)
	if acc == nil {
		t.Fatal("expected non-nil accumulator")
	}
	if !acc.hasKeyFields {
		t.Error("expected hasKeyFields=true for TANF spec")
	}
	if acc.batchSize != 1 {
		t.Errorf("expected batchSize=1, got %d", acc.batchSize)
	}
	if len(acc.groupedSchemas) != 3 {
		t.Errorf("expected 3 grouped schemas, got %d", len(acc.groupedSchemas))
	}
	if !acc.groupedSchemas["tanf/t1"] {
		t.Error("expected tanf/t1 in grouped schemas")
	}
}

func TestAccumulator_AddGroupedSchema_ReturnsBatchOnKeyChange(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	// First row: key "202401|CASE0000001    "
	row1 := makeRow(1, "T1202401CASE0000001")
	batch1, sch1, isAcc1, err := acc.Add(row1)
	if err != nil {
		t.Fatalf("Add row1: %v", err)
	}
	if !isAcc1 {
		t.Error("expected isAccumulated=true for T1")
	}
	if sch1 == nil {
		t.Error("expected non-nil schema for T1")
	}
	if batch1 != nil {
		t.Error("expected no batch after first row")
	}

	// Second row: different key "202401|CASE0000002    " triggers flush of first group
	row2 := makeRow(2, "T1202401CASE0000002")
	batch2, _, isAcc2, err := acc.Add(row2)
	if err != nil {
		t.Fatalf("Add row2: %v", err)
	}
	if !isAcc2 {
		t.Error("expected isAccumulated=true for second T1")
	}
	if batch2 == nil {
		t.Fatal("expected batch when key changes with batch_size=1")
	}
	if batch2.TotalGroups() != 1 {
		t.Errorf("expected 1 group in batch, got %d", batch2.TotalGroups())
	}
	if batch2.TotalRecords() != 1 {
		t.Errorf("expected 1 record in batch, got %d", batch2.TotalRecords())
	}
}

func TestAccumulator_AddColumnarGroupedSchema_ReturnsBatchOnKeyChange(t *testing.T) {
	spec := buildKeyedColumnarSpec()
	schemas := buildNonKeyedSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	row1 := decoder.NewColumnarRow(1, "TE1", 2, []any{"202401", "111111111"})
	batch1, _, isAcc1, err := acc.Add(row1)
	if err != nil {
		t.Fatalf("Add row1: %v", err)
	}
	if !isAcc1 {
		t.Error("expected isAccumulated=true for TE1")
	}
	if batch1 != nil {
		t.Error("expected no batch after first row")
	}

	row2 := decoder.NewColumnarRow(2, "TE1", 2, []any{"202401", "222222222"})
	batch2, _, isAcc2, err := acc.Add(row2)
	if err != nil {
		t.Fatalf("Add row2: %v", err)
	}
	if !isAcc2 {
		t.Error("expected isAccumulated=true for second TE1")
	}
	if batch2 == nil {
		t.Fatal("expected batch when columnar key changes with batch_size=1")
	}
	if got := batch2.DecodedGroups[0].Key; got != "202401|111111111" {
		t.Errorf("completed group key = %q, want %q", got, "202401|111111111")
	}
}

func TestAccumulator_AddNonGroupedSchema(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	// HEADER is not in grouped_schemas
	row := makeRow(1, "HEADER2024 1E                                      ")
	batch, sch, isAcc, err := acc.Add(row)
	if err != nil {
		t.Fatalf("Add HEADER: %v", err)
	}
	if isAcc {
		t.Error("expected isAccumulated=false for HEADER")
	}
	if sch == nil {
		t.Error("expected non-nil schema for HEADER")
	}
	if batch != nil {
		t.Error("expected no batch for non-grouped schema")
	}
}

func TestAccumulator_MultipleRecordsSameKey(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	// Add T1 and T2 for same case
	row1 := makeRow(1, "T1202401CASE0000001")
	batch1, _, _, err := acc.Add(row1)
	if err != nil {
		t.Fatalf("Add row1: %v", err)
	}
	if batch1 != nil {
		t.Error("expected no batch after first row of same key")
	}

	row2 := makeRow(2, "T2202401CASE0000001")
	batch2, _, _, err := acc.Add(row2)
	if err != nil {
		t.Fatalf("Add row2: %v", err)
	}
	if batch2 != nil {
		t.Error("expected no batch after second row of same key")
	}

	// Verify via Stats that we have 1 group with 2 lines
	numGroups, totalLines, pending := acc.Stats()
	if numGroups != 1 {
		t.Errorf("expected 1 group, got %d", numGroups)
	}
	if totalLines != 2 {
		t.Errorf("expected 2 total lines, got %d", totalLines)
	}
	if pending != 0 {
		t.Errorf("expected 0 pending groups, got %d", pending)
	}
}

func TestAccumulator_DifferentKeysFlushPreviousGroup(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	// Two rows for CASE0000001
	row1 := makeRow(1, "T1202401CASE0000001")
	row2 := makeRow(2, "T2202401CASE0000001")
	acc.Add(row1)
	acc.Add(row2)

	// Row for CASE0000002 should flush CASE0000001 group
	row3 := makeRow(3, "T1202401CASE0000002")
	batch, _, _, err := acc.Add(row3)
	if err != nil {
		t.Fatalf("Add row3: %v", err)
	}
	if batch == nil {
		t.Fatal("expected batch when key changes")
	}
	if batch.TotalGroups() != 1 {
		t.Errorf("expected 1 group in flushed batch, got %d", batch.TotalGroups())
	}
	if batch.TotalRecords() != 2 {
		t.Errorf("expected 2 records in flushed batch (CASE0000001 T1+T2), got %d", batch.TotalRecords())
	}

	// Verify the flushed group has the right key
	group := batch.DecodedGroups[0]
	if group.Key != "202401|CASE0000001" {
		t.Errorf("expected Key=%q, got %q", "202401|CASE0000001", group.Key)
	}
}

func TestAccumulator_Drain(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	// Add rows without triggering a key change
	row1 := makeRow(1, "T1202401CASE0000001")
	row2 := makeRow(2, "T2202401CASE0000001")
	acc.Add(row1)
	acc.Add(row2)

	// Drain should return the remaining group
	batches := acc.Drain()
	if len(batches) != 1 {
		t.Fatalf("expected 1 batch from Drain, got %d", len(batches))
	}
	if batches[0].TotalGroups() != 1 {
		t.Errorf("expected 1 group in drained batch, got %d", batches[0].TotalGroups())
	}
	if batches[0].TotalRecords() != 2 {
		t.Errorf("expected 2 records in drained batch, got %d", batches[0].TotalRecords())
	}

	// Drain again should return nothing
	batches2 := acc.Drain()
	if len(batches2) != 0 {
		t.Errorf("expected 0 batches from second Drain, got %d", len(batches2))
	}
}

func TestAccumulator_Stats(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	// Empty accumulator
	numGroups, totalLines, pending := acc.Stats()
	if numGroups != 0 || totalLines != 0 || pending != 0 {
		t.Errorf("empty stats: expected (0,0,0), got (%d,%d,%d)", numGroups, totalLines, pending)
	}

	// Add one row
	row1 := makeRow(1, "T1202401CASE0000001")
	acc.Add(row1)

	numGroups, totalLines, pending = acc.Stats()
	if numGroups != 1 {
		t.Errorf("expected 1 group, got %d", numGroups)
	}
	if totalLines != 1 {
		t.Errorf("expected 1 total line, got %d", totalLines)
	}
	if pending != 0 {
		t.Errorf("expected 0 pending, got %d", pending)
	}
}

func TestAccumulator_NonKeyedMode(t *testing.T) {
	spec := buildNonKeyedSpec()
	schemas := buildNonKeyedSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	if acc.hasKeyFields {
		t.Error("expected hasKeyFields=false for non-keyed spec")
	}

	// In non-keyed mode with batch_size=1, each record gets a unique key.
	// The second Add triggers a flush of the first record's group.
	row1 := decoder.NewColumnarRow(1, "TE1", 5, []any{"a", "b", "c", "d", "e"})
	batch1, _, isAcc1, err := acc.Add(row1)
	if err != nil {
		t.Fatalf("Add row1: %v", err)
	}
	if !isAcc1 {
		t.Error("expected isAccumulated=true")
	}
	if batch1 != nil {
		t.Error("expected no batch from first row")
	}

	row2 := decoder.NewColumnarRow(2, "TE1", 5, []any{"f", "g", "h", "i", "j"})
	batch2, _, isAcc2, err := acc.Add(row2)
	if err != nil {
		t.Fatalf("Add row2: %v", err)
	}
	if !isAcc2 {
		t.Error("expected isAccumulated=true")
	}
	// Key changes on every record in non-keyed mode, so batch should be emitted
	if batch2 == nil {
		t.Fatal("expected batch when key changes in non-keyed mode")
	}
	if batch2.TotalGroups() != 1 {
		t.Errorf("expected 1 group in batch, got %d", batch2.TotalGroups())
	}
	if batch2.TotalRecords() != 1 {
		t.Errorf("expected 1 record in batch, got %d", batch2.TotalRecords())
	}
}

func TestAccumulator_BatchSize0(t *testing.T) {
	spec := buildBatchSize0Spec()
	schemas := buildTestSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	if acc.batchSize != 0 {
		t.Errorf("expected batchSize=0, got %d", acc.batchSize)
	}

	// Add rows for two different cases
	row1 := makeRow(1, "T1202401CASE0000001")
	batch1, _, _, err := acc.Add(row1)
	if err != nil {
		t.Fatalf("Add row1: %v", err)
	}
	if batch1 != nil {
		t.Error("expected no batch with batch_size=0")
	}

	row2 := makeRow(2, "T1202401CASE0000002")
	batch2, _, _, err := acc.Add(row2)
	if err != nil {
		t.Fatalf("Add row2: %v", err)
	}
	// Even though key changed, batch_size=0 means no batch emitted until Drain
	if batch2 != nil {
		t.Error("expected no batch with batch_size=0 even on key change")
	}

	// All groups should come out on Drain
	batches := acc.Drain()
	if len(batches) != 1 {
		t.Fatalf("expected 1 batch from Drain, got %d", len(batches))
	}
	if batches[0].TotalGroups() != 2 {
		t.Errorf("expected 2 groups in drained batch, got %d", batches[0].TotalGroups())
	}
}

func TestAccumulator_ExtractKeyTooShort(t *testing.T) {
	spec := buildTANFS1Spec()
	schemas := buildTestSchemas()
	registry := config.NewTestRegistry(schemas)
	detector := decoder.NewRecordTypeDetector(spec, registry)
	acc := NewAccumulator(spec, detector)

	// Row data is too short for key extraction (needs at least 19 bytes for configured key fields)
	row := makeRow(1, "T1short")
	_, _, _, err := acc.Add(row)
	if err == nil {
		t.Fatal("expected error for too-short row")
	}
}
