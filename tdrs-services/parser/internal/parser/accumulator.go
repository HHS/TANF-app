package parser

import (
	"fmt"
	"strconv"

	"go-parser/internal/config/filespec"
	"go-parser/internal/config/schema"
	"go-parser/internal/decoder"
)

// Accumulator collects records into Batches based on the AccumulatorConfig.
//
// The accumulator handles modes based on key_fields and batch_size:
//   - batch_size=0:  All groups accumulated into a single batch (emitted on Drain)
//   - batch_size=1:  Each group emitted as its own Batch
//   - batch_size=N:  N groups batched together
//
// When key_fields are set, records are grouped by composite key.
// When key_fields are empty, each record is its own group.
//
// All modes use key-change as the single mechanism for group completion.
// Files are assumed sorted at the group level, so groups are flushed immediately
// when a new key is encountered.
type Accumulator struct {
	spec     *filespec.FileSpec
	detector *decoder.RecordTypeDetector

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
func NewAccumulator(spec *filespec.FileSpec, detector *decoder.RecordTypeDetector) *Accumulator {
	// Build set of grouped schemas for quick lookup
	groupedSchemas := make(map[string]bool)
	for _, name := range spec.Accumulator.GroupedSchemas {
		groupedSchemas[name] = true
	}

	return &Accumulator{
		spec:           spec,
		detector:       detector,
		hasKeyFields:   spec.Accumulator.HasKeyFields(),
		batchSize:      spec.Accumulator.EffectiveBatchSize(),
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
	groupingKey, err := a.generateKey(row)
	if err != nil {
		return nil, nil, false, fmt.Errorf("line %d: failed to generate key: %w", row.LineNum(), err)
	}

	return a.addRecord(line, sch, groupingKey)
}

// generateKey creates a grouping key for the row.
// When key_fields configured: extracts composite key from row data.
// When no key_fields: uses line number as unique key (every record is its own group).
func (a *Accumulator) generateKey(row decoder.Row) (groupingKey, error) {
	if !a.hasKeyFields {
		// Each record is its own group - unique key guarantees immediate flush
		return groupingKey{Value: "line:" + strconv.Itoa(row.LineNum())}, nil
	}
	return a.extractKey(row)
}

// addRecord handles all records using key-change detection.
// If the key changes from the current group, the current group is flushed.
func (a *Accumulator) addRecord(line DecodedRecord, sch *schema.CompiledSchema, key groupingKey) (*DecodedBatch, *schema.CompiledSchema, bool, error) {
	var completedBatch *DecodedBatch

	// Check if this is a new group
	if a.currentGroup == nil {
		// First record - start a new group
		a.currentGroup = newDecodedGroup(key)
	} else if a.currentGroup.Key != key.Value {
		// Key changed - current group is complete
		completedBatch = a.flushCurrentGroup()

		// Start new group
		a.currentGroup = newDecodedGroup(key)
	}

	// Add line to current group
	a.currentGroup.DecodedRecords = append(a.currentGroup.DecodedRecords, line)

	return completedBatch, sch, true, nil
}

type groupingKey struct {
	Value string
}

func newDecodedGroup(key groupingKey) *DecodedGroup {
	return &DecodedGroup{
		Key:            key.Value,
		DecodedRecords: make([]DecodedRecord, 0, 8),
	}
}

// flushCurrentGroup handles the completed group based on batch_size configuration.
// Returns a Batch if one is ready, nil otherwise.
func (a *Accumulator) flushCurrentGroup() *DecodedBatch {
	if a.currentGroup == nil {
		return nil
	}

	// Always add the completed group to pending
	a.pendingGroups = append(a.pendingGroups, a.currentGroup)

	if a.batchSize == 0 {
		// Accumulate all groups into a single batch, emitted on Drain
		return nil
	}

	// Batching mode: emit when batch is full
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
func (a *Accumulator) extractKey(row decoder.Row) (groupingKey, error) {
	key, err := row.ExtractKey(a.spec.Accumulator.KeyFields.OrderedFields())
	if err != nil {
		return groupingKey{}, err
	}
	return groupingKey{Value: key}, nil
}

// Drain returns all accumulated groups as Batches and resets the accumulator.
// Call this after all rows have been processed.
//
// Any in-progress group is added to pending, then all pending groups are
// flushed as a single final batch.
func (a *Accumulator) Drain() []*DecodedBatch {
	var batches []*DecodedBatch

	// Flush the current group being built into pending
	if a.currentGroup != nil {
		a.pendingGroups = append(a.pendingGroups, a.currentGroup)
		a.currentGroup = nil
	}

	// Flush any remaining pending groups as a final batch
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
