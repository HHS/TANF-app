package parser

import (
	"context"
	"log"
	"sync"

	"go-parser/internal/filespec"
	"go-parser/internal/schema"
)

// ParsedGroup contains parsing results for a single RecordGroup.
type ParsedGroup struct {
	// Key is the grouping key (empty for non-keyed records)
	Key          string
	RptMonthYear string
	CaseNumber   string

	// Records contains all successfully parsed records in this group
	Records []*schema.ParsedRecord
}

// ParsedBatch contains parsing results for a Batch (one or more groups).
type ParsedBatch struct {
	BatchID int
	Groups  []*ParsedGroup
}

// TotalRecords returns the total number of successfully parsed records.
func (pb *ParsedBatch) TotalRecords() int {
	total := 0
	for _, g := range pb.Groups {
		total += len(g.Records)
	}
	return total
}

// Pool manages worker goroutines for parallel parsing.
type Pool struct {
	numWorkers int
	extractor  FieldExtractor
	parseCtx   *schema.ParseContext // Runtime context from header

	// Single work input channel for all Batches
	work chan *Batch

	// Single result output channel
	results chan *ParsedBatch

	wg sync.WaitGroup
}

// SetParseContext sets the runtime context after header parsing.
// Must be called before processing data records.
func (p *Pool) SetParseContext(ctx *schema.ParseContext) {
	p.parseCtx = ctx
}

// PoolConfig configures the worker pool.
type PoolConfig struct {
	NumWorkers       int
	WorkBufferSize   int
	ResultBufferSize int
}

// DefaultPoolConfig returns sensible defaults.
func DefaultPoolConfig() PoolConfig {
	return PoolConfig{
		NumWorkers:       4,
		WorkBufferSize:   256,
		ResultBufferSize: 256,
	}
}

// NewPool creates a worker pool.
func NewPool(format filespec.Format, config PoolConfig) *Pool {
	return &Pool{
		numWorkers: config.NumWorkers,
		extractor:  GetExtractor(format),
		work:       make(chan *Batch, config.WorkBufferSize),
		results:    make(chan *ParsedBatch, config.ResultBufferSize),
	}
}

// Start launches the worker goroutines.
func (p *Pool) Start(ctx context.Context) {
	for i := 0; i < p.numWorkers; i++ {
		p.wg.Add(1)
		go p.worker(ctx)
	}
}

// Submit submits a Batch for processing.
// Blocks if the work channel is full (backpressure).
func (p *Pool) Submit(batch *Batch) {
	p.work <- batch
}

// CloseInputs signals that no more work will be submitted.
func (p *Pool) CloseInputs() {
	close(p.work)
}

// Wait blocks until all workers finish, then closes result channels.
func (p *Pool) Wait() {
	p.wg.Wait()
	close(p.results)
	log.Print("All lines in file have been parsed into records and queued for writing.")
}

// Results returns the channel for receiving parsed batch results.
func (p *Pool) Results() <-chan *ParsedBatch {
	return p.results
}

// worker is the main worker goroutine.
func (p *Pool) worker(ctx context.Context) {
	defer p.wg.Done()

	for {
		select {
		case <-ctx.Done():
			return

		case batch, ok := <-p.work:
			if !ok {
				return // Channel closed, exit
			}
			p.results <- p.processBatch(batch)
		}
	}
}

// processBatch parses all records in all groups within a batch.
func (p *Pool) processBatch(batch *Batch) *ParsedBatch {
	result := &ParsedBatch{
		BatchID: batch.BatchID,
		Groups:  make([]*ParsedGroup, 0, len(batch.Groups)),
	}

	for _, group := range batch.Groups {
		parsedGroup := p.processGroup(group)
		result.Groups = append(result.Groups, parsedGroup)
	}

	return result
}

// processGroup parses all records in a single group.
func (p *Pool) processGroup(group *RecordGroup) *ParsedGroup {
	result := &ParsedGroup{
		Key:          group.Key,
		RptMonthYear: group.RptMonthYear,
		CaseNumber:   group.CaseNumber,
		Records:      make([]*schema.ParsedRecord, 0, len(group.Lines)),
	}

	for _, line := range group.Lines {
		records, err := p.parseRow(line)
		if err != nil {
			log.Printf("Failed to parse line %d: %v", line.Row.LineNum(), err)
			continue
		}
		result.Records = append(result.Records, records...)
	}

	return result
}

// parseRow parses a single row into one or more ParsedRecords.
// For multi-segment schemas, one input line produces multiple records (one per segment).
// Records are acquired from the schema's object pool and must be released after use.
func (p *Pool) parseRow(line RawLine) ([]*schema.ParsedRecord, error) {
	numSegments := len(line.Schema.Segments)
	if numSegments == 0 {
		// Schema has no segments - this shouldn't happen with the new structure
		return nil, nil
	}

	// Parse shared fields once into a cache (one small allocation per row).
	// We use a map here temporarily to collect shared values, then copy them
	// into each record's indexed slice.
	sharedCache := make(MapFieldGetter, len(line.Schema.Shared))
	for i := range line.Schema.Shared {
		field := &line.Schema.Shared[i]
		value, err := p.extractor.Extract(line.Row, field, p.parseCtx, sharedCache)
		if err != nil {
			log.Printf("Failed to extract shared field %s: %v", field.Name, err)
			continue
		}
		if value != nil {
			sharedCache[field.Name] = value
		}
	}

	// Parse each segment into a separate record acquired from the pool
	records := make([]*schema.ParsedRecord, 0, numSegments)
	for segIdx, segment := range line.Schema.Segments {
		// Acquire record from pool (reuses memory, reduces GC pressure)
		record := line.Schema.AcquireRecord()
		record.LineNumber = line.Row.LineNum()
		record.SegmentIndex = segIdx

		// Copy cached shared fields into record using Set()
		for name, value := range sharedCache {
			record.Set(name, value)
		}

		// Parse segment-specific fields directly into record using Set()
		missingRequired := false
		for i := range segment.Fields {
			field := &segment.Fields[i]
			// Create a temporary map-like interface for the extractor
			// The extractor expects a map for lookups (e.g., source_field resolution)
			value, err := p.extractor.Extract(line.Row, field, p.parseCtx, record)
			if err != nil {
				log.Printf("Failed to extract field %s: %v", field.Name, err)
				continue
			}
			if value != nil {
				record.Set(field.Name, value)
			} else if field.Required || segIdx >= 1 {
				// TODO: do we generate an error here?
				// Most multi record schemas don't have the 2 through N segment's field's marked as required.
				// Therefore if the value is nil and the field is required or the segment index is greater than 0
				// we skip creating the record since it is invalid.
				// log.Printf("Skipping record for segment %d, type %s, line %d, field %s is nil", segIdx, record.Schema.RecordType, record.LineNumber, field.Name)
				missingRequired = true
				break
			}
		}

		if missingRequired {
			// Invalid segment - release record back to pool immediately
			line.Schema.ReleaseRecord(record)
			continue
		}

		records = append(records, record)
	}

	return records, nil
}
