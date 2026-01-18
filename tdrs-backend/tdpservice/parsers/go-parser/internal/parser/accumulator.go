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
// When sorted=true and key_fields are set, groups are flushed immediately when
// a new key is encountered, preventing memory buildup for large sorted files.
type Accumulator struct {
	spec     *filespec.FileSpec
	detector *RecordTypeDetector

	// Configuration derived from spec
	hasKeyFields   bool
	batchSize      int
	groupedSchemas map[string]bool
	sorted         bool

	// State for key-based grouping (unsorted mode)
	groups map[string]*RecordGroup

	// State for sorted streaming mode
	currentGroup *RecordGroup

	// State for batching
	pendingGroups []*RecordGroup
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
		sorted:         spec.Accumulator.Sorted,
		groups:         make(map[string]*RecordGroup),
		currentGroup:   nil,
		pendingGroups:  make([]*RecordGroup, 0),
		batchCounter:   0,
	}
}

// Add processes a row from the file.
//
// Returns:
//   - batch: A complete Batch if one is ready (only in non-keyed or per-record mode)
//   - schema: The detected schema for this row
//   - isAccumulated: true if the row was added to a group (not HEADER/TRAILER)
//   - err: Any error encountered
//
// For key-based grouping, batches are only returned from Drain() after all rows are processed.
// For non-keyed mode with batch_size > 0, batches are returned as they fill up.
// For per-record mode (no keys, batch_size=0), each row returns its own batch.
func (a *Accumulator) Add(row decoder.Row) (batch *Batch, sch *schema.CompiledSchema, isAccumulated bool, err error) {
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

	line := RawLine{Row: row, Schema: sch}

	if a.hasKeyFields {
		// Key-based grouping mode
		return a.addWithKey(line, sch)
	}

	// Non-keyed mode: each record is its own group
	return a.addWithoutKey(line, sch)
}

// addWithKey handles rows when key_fields is configured.
// In unsorted mode, groups are accumulated in memory and only returned via Drain().
// In sorted mode, groups are flushed as soon as a new key is encountered.
func (a *Accumulator) addWithKey(line RawLine, sch *schema.CompiledSchema) (*Batch, *schema.CompiledSchema, bool, error) {
	// Extract the grouping key
	key, rptMonth, caseNum, err := a.extractKey(line.Row)
	if err != nil {
		return nil, nil, false, fmt.Errorf("line %d: failed to extract key: %w", line.Row.LineNum(), err)
	}

	if a.sorted {
		return a.addWithKeySorted(line, sch, key, rptMonth, caseNum)
	}
	return a.addWithKeyUnsorted(line, sch, key, rptMonth, caseNum)
}

// addWithKeySorted handles sorted mode where groups are flushed when a new key appears.
func (a *Accumulator) addWithKeySorted(line RawLine, sch *schema.CompiledSchema, key, rptMonth, caseNum string) (*Batch, *schema.CompiledSchema, bool, error) {
	var completedBatch *Batch

	// Check if this is a new group
	if a.currentGroup == nil {
		// First record - start a new group
		a.currentGroup = &RecordGroup{
			Key:          key,
			RptMonthYear: rptMonth,
			CaseNumber:   caseNum,
			Lines:        make([]RawLine, 0, 8),
		}
	} else if a.currentGroup.Key != key {
		// Key changed - current group is complete
		completedBatch = a.flushCurrentGroup()

		// Start new group
		a.currentGroup = &RecordGroup{
			Key:          key,
			RptMonthYear: rptMonth,
			CaseNumber:   caseNum,
			Lines:        make([]RawLine, 0, 8),
		}
	}

	// Add line to current group
	a.currentGroup.Lines = append(a.currentGroup.Lines, line)

	return completedBatch, sch, true, nil
}

// flushCurrentGroup handles the completed group based on batch_size configuration.
// Returns a Batch if one is ready, nil otherwise.
func (a *Accumulator) flushCurrentGroup() *Batch {
	if a.currentGroup == nil {
		return nil
	}

	if a.batchSize == 0 {
		// Each group is its own batch
		batch := &Batch{
			BatchID: a.batchCounter,
			Groups:  []*RecordGroup{a.currentGroup},
		}
		a.batchCounter++
		return batch
	}

	// Batching mode: collect groups until batch is full
	a.pendingGroups = append(a.pendingGroups, a.currentGroup)

	if len(a.pendingGroups) >= a.batchSize {
		batch := &Batch{
			BatchID: a.batchCounter,
			Groups:  a.pendingGroups,
		}
		a.batchCounter++
		a.pendingGroups = make([]*RecordGroup, 0, a.batchSize)
		return batch
	}

	return nil
}

// addWithKeyUnsorted handles unsorted mode where all groups are held in memory.
func (a *Accumulator) addWithKeyUnsorted(line RawLine, sch *schema.CompiledSchema, key, rptMonth, caseNum string) (*Batch, *schema.CompiledSchema, bool, error) {
	// Get or create the group
	group, exists := a.groups[key]
	if !exists {
		group = &RecordGroup{
			Key:          key,
			RptMonthYear: rptMonth,
			CaseNumber:   caseNum,
			Lines:        make([]RawLine, 0, 8), // Pre-allocate for typical case size
		}
		a.groups[key] = group
	}

	// Add the row to the group
	group.Lines = append(group.Lines, line)

	// For unsorted key-based grouping, batches are only returned from Drain()
	return nil, sch, true, nil
}

// addWithoutKey handles rows when key_fields is empty.
// Each record is its own group. Batches may be returned immediately.
func (a *Accumulator) addWithoutKey(line RawLine, sch *schema.CompiledSchema) (*Batch, *schema.CompiledSchema, bool, error) {
	// Create a single-record group
	group := &RecordGroup{
		Key:   "", // No key for non-grouped records
		Lines: []RawLine{line},
	}

	// Per-record mode: batch_size = 0 means emit immediately
	if a.batchSize == 0 {
		batch := &Batch{
			BatchID: a.batchCounter,
			Groups:  []*RecordGroup{group},
		}
		a.batchCounter++
		return batch, sch, true, nil
	}

	// Batching mode: collect groups until batch is full
	a.pendingGroups = append(a.pendingGroups, group)

	if len(a.pendingGroups) >= a.batchSize {
		batch := &Batch{
			BatchID: a.batchCounter,
			Groups:  a.pendingGroups,
		}
		a.batchCounter++
		a.pendingGroups = make([]*RecordGroup, 0, a.batchSize)
		return batch, sch, true, nil
	}

	return nil, sch, true, nil
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
//
// For sorted mode:
//   - Returns the final in-progress group plus any pending batch
func (a *Accumulator) Drain() []*Batch {
	var batches []*Batch

	if a.hasKeyFields {
		if a.sorted {
			// Sorted mode: flush currentGroup and any pending groups
			batches = a.drainSorted()
		} else {
			// Unsorted mode: collect all groups from the map
			batches = a.drainUnsorted()
		}
	} else {
		// Non-keyed mode: return any remaining pending groups
		if len(a.pendingGroups) > 0 {
			batches = append(batches, &Batch{
				BatchID: a.batchCounter,
				Groups:  a.pendingGroups,
			})
			a.batchCounter++
			a.pendingGroups = make([]*RecordGroup, 0)
		}
	}

	return batches
}

// drainSorted handles Drain() for sorted mode.
func (a *Accumulator) drainSorted() []*Batch {
	var batches []*Batch

	// Flush the current group being built
	if a.currentGroup != nil {
		if a.batchSize == 0 {
			// Each group is its own batch
			batches = append(batches, &Batch{
				BatchID: a.batchCounter,
				Groups:  []*RecordGroup{a.currentGroup},
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
		batches = append(batches, &Batch{
			BatchID: a.batchCounter,
			Groups:  a.pendingGroups,
		})
		a.batchCounter++
		a.pendingGroups = make([]*RecordGroup, 0, a.batchSize)
	}

	return batches
}

// drainUnsorted handles Drain() for unsorted mode.
func (a *Accumulator) drainUnsorted() []*Batch {
	var batches []*Batch

	// Collect all groups from the map
	allGroups := make([]*RecordGroup, 0, len(a.groups))
	for _, group := range a.groups {
		allGroups = append(allGroups, group)
	}

	if a.batchSize == 0 {
		// Each group is its own batch
		for _, group := range allGroups {
			batches = append(batches, &Batch{
				BatchID: a.batchCounter,
				Groups:  []*RecordGroup{group},
			})
			a.batchCounter++
		}
	} else {
		// Batch groups together
		for i := 0; i < len(allGroups); i += a.batchSize {
			end := i + a.batchSize
			if end > len(allGroups) {
				end = len(allGroups)
			}
			batches = append(batches, &Batch{
				BatchID: a.batchCounter,
				Groups:  allGroups[i:end],
			})
			a.batchCounter++
		}
	}

	// Clear accumulated groups
	a.groups = make(map[string]*RecordGroup)

	return batches
}

// Stats returns statistics about accumulated state.
func (a *Accumulator) Stats() (numGroups, totalLines, pendingGroups int) {
	// Count groups in map (unsorted mode)
	for _, g := range a.groups {
		numGroups++
		totalLines += len(g.Lines)
	}

	// Count current group (sorted mode)
	if a.currentGroup != nil {
		numGroups++
		totalLines += len(a.currentGroup.Lines)
	}

	pendingGroups = len(a.pendingGroups)
	return
}
