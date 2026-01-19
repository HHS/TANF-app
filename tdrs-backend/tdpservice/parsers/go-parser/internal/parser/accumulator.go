package parser

import (
	"fmt"

	"go-parser/internal/decoder"
	"go-parser/internal/filespec"
	"go-parser/internal/schema"
)

// Accumulator collects records into Batches based on the AccumulatorConfig.
//
// The accumulator handles four modes based on key_fields and batch_size:
//   - key_fields set, batch_size=0:  Group by key, emit each group as its own Batch
//   - key_fields set, batch_size=N:  Group by key, batch N groups together
//   - key_fields empty, batch_size=N: Each record is a group, batch N groups together
//   - key_fields empty, batch_size=0: Each record is its own Batch (per-record mode)
//
// All modes use key-change as the single mechanism for group completion.
// Files are assumed sorted at the group level, so groups are flushed immediately
// when a new key is encountered.
type Accumulator struct {
	spec     *filespec.FileSpec
	detector *RecordTypeDetector

	// Configuration derived from spec
	hasKeyFields   bool
	batchSize      int
	groupedSchemas map[string]bool

	// State for streaming mode
	currentGroup *DecodedGroup

	// State for batching
	pendingGroups []*DecodedGroup
	batchCounter  int
}

// NewAccumulator creates an accumulator for the given file specification.
func NewAccumulator(spec *filespec.FileSpec, detector *RecordTypeDetector) *Accumulator {
	// Build set of grouped schemas for quick lookup
	groupedSchemas := make(map[string]bool)
	for _, name := range spec.Accumulator.GroupedSchemas {
		groupedSchemas[name] = true
	}

	return &Accumulator{
		spec:           spec,
		detector:       detector,
		hasKeyFields:   spec.Accumulator.HasKeyFields(),
		batchSize:      spec.Accumulator.BatchSize,
		groupedSchemas: groupedSchemas,
		currentGroup:   nil,
		pendingGroups:  make([]*DecodedGroup, 0),
		batchCounter:   0,
	}
}

// Add processes a row from the file.
//
// Returns:
//   - batch: A complete Batch if one is ready
//   - schema: The detected schema for this row
//   - isAccumulated: true if the row was added to a group (not HEADER/TRAILER)
//   - err: Any error encountered
//
// Groups are flushed when a new key is encountered.
// For key-based grouping, batches are returned when groups complete.
// For non-keyed mode, each record has a unique key so batches are returned immediately.
func (a *Accumulator) Add(row decoder.Row) (batch *DecodedBatch, sch *schema.CompiledSchema, isAccumulated bool, err error) {
	// Detect which schema this row belongs to
	sch, err = a.detector.Detect(row)
	if err != nil {
		return nil, nil, false, err
	}

	// Check if this schema participates in accumulation
	// groupedSchemas uses schema paths (e.g., "tanf/t1"), not record types
	if len(a.groupedSchemas) > 0 && !a.groupedSchemas[sch.Path] {
		// Not accumulated (e.g., HEADER, TRAILER) - return for immediate processing
		return nil, sch, false, nil
	}

	line := DecodedRecord{Row: row, Schema: sch}

	// Generate the grouping key
	key, rptMonth, caseNum, err := a.generateKey(row)
	if err != nil {
		return nil, nil, false, fmt.Errorf("line %d: failed to generate key: %w", row.LineNum(), err)
	}

	return a.addRecord(line, sch, key, rptMonth, caseNum)
}

// generateKey creates a grouping key for the row.
// When key_fields configured: extracts composite key from row data.
// When no key_fields: uses line number as unique key (every record is its own group).
func (a *Accumulator) generateKey(row decoder.Row) (key, rptMonth, caseNum string, err error) {
	if !a.hasKeyFields {
		// Each record is its own group - unique key guarantees immediate flush
		return fmt.Sprintf("line:%d", row.LineNum()), "", "", nil
	}
	return a.extractKey(row)
}

// addRecord handles all records using key-change detection.
// If the key changes from the current group, the current group is flushed.
func (a *Accumulator) addRecord(line DecodedRecord, sch *schema.CompiledSchema, key, rptMonth, caseNum string) (*DecodedBatch, *schema.CompiledSchema, bool, error) {
	var completedBatch *DecodedBatch

	// Check if this is a new group
	if a.currentGroup == nil {
		// First record - start a new group
		a.currentGroup = &DecodedGroup{
			Key:            key,
			RptMonthYear:   rptMonth,
			CaseNumber:     caseNum,
			DecodedRecords: make([]DecodedRecord, 0, 8),
		}
	} else if a.currentGroup.Key != key {
		// Key changed - current group is complete
		completedBatch = a.flushCurrentGroup()

		// Start new group
		a.currentGroup = &DecodedGroup{
			Key:            key,
			RptMonthYear:   rptMonth,
			CaseNumber:     caseNum,
			DecodedRecords: make([]DecodedRecord, 0, 8),
		}
	}

	// Add line to current group
	a.currentGroup.DecodedRecords = append(a.currentGroup.DecodedRecords, line)

	return completedBatch, sch, true, nil
}

// flushCurrentGroup handles the completed group based on batch_size configuration.
// Returns a Batch if one is ready, nil otherwise.
func (a *Accumulator) flushCurrentGroup() *DecodedBatch {
	if a.currentGroup == nil {
		return nil
	}

	if a.batchSize == 0 {
		// Each group is its own batch
		batch := &DecodedBatch{
			BatchID:       a.batchCounter,
			DecodedGroups: []*DecodedGroup{a.currentGroup},
		}
		a.batchCounter++
		return batch
	}

	// Batching mode: collect groups until batch is full
	a.pendingGroups = append(a.pendingGroups, a.currentGroup)

	if len(a.pendingGroups) >= a.batchSize {
		batch := &DecodedBatch{
			BatchID:       a.batchCounter,
			DecodedGroups: a.pendingGroups,
		}
		a.batchCounter++
		a.pendingGroups = make([]*DecodedGroup, 0, a.batchSize)
		return batch
	}

	return nil
}

// extractKey extracts the grouping key from a row.
func (a *Accumulator) extractKey(row decoder.Row) (key, rptMonth, caseNum string, err error) {
	pr, ok := row.(*decoder.PositionalRow)
	if !ok {
		return "", "", "", fmt.Errorf("key-based grouping requires PositionalRow, got %T", row)
	}

	data := pr.Data()
	keyConfig := a.spec.Accumulator.KeyFields

	// Validate line length
	minLen := keyConfig.CaseNumber.End
	if len(data) < minLen {
		return "", "", "", fmt.Errorf("line too short: need %d bytes, got %d", minLen, len(data))
	}

	// Extract key components
	rptMonth = data[keyConfig.RptMonthYear.Start:keyConfig.RptMonthYear.End]
	caseNum = data[keyConfig.CaseNumber.Start:keyConfig.CaseNumber.End]

	// Composite key with separator
	key = rptMonth + "|" + caseNum

	return key, rptMonth, caseNum, nil
}

// Drain returns all accumulated groups as Batches and resets the accumulator.
// Call this after all rows have been processed.
//
// For key-based grouping:
//   - If batch_size=0: Each group becomes its own Batch
//   - If batch_size=N: Groups are batched together (N groups per Batch)
//
// For non-keyed mode:
//   - Returns any remaining partial batch
func (a *Accumulator) Drain() []*DecodedBatch {
	var batches []*DecodedBatch

	// Flush the current group being built
	if a.currentGroup != nil {
		if a.batchSize == 0 {
			// Each group is its own batch
			batches = append(batches, &DecodedBatch{
				BatchID:       a.batchCounter,
				DecodedGroups: []*DecodedGroup{a.currentGroup},
			})
			a.batchCounter++
		} else {
			// Add to pending groups
			a.pendingGroups = append(a.pendingGroups, a.currentGroup)
		}
		a.currentGroup = nil
	}

	// Flush any remaining pending groups
	if len(a.pendingGroups) > 0 {
		batches = append(batches, &DecodedBatch{
			BatchID:       a.batchCounter,
			DecodedGroups: a.pendingGroups,
		})
		a.batchCounter++
		a.pendingGroups = nil
	}

	return batches
}

// Stats returns statistics about accumulated state.
func (a *Accumulator) Stats() (numGroups, totalLines, pendingGroups int) {
	// Count current group
	if a.currentGroup != nil {
		numGroups++
		totalLines += len(a.currentGroup.DecodedRecords)
	}

	pendingGroups = len(a.pendingGroups)
	return
}
