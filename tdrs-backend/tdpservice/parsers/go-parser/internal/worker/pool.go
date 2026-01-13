package worker

import (
	"context"
	"maps"
	"sync"

	"go-parser/internal/filespec"
	"go-parser/internal/parser"
	"go-parser/internal/processor"
	"go-parser/internal/schema"
)

// ParseError represents a parsing error for a single row.
type ParseError struct {
	LineNumber int
	RecordType string
	Message    string
}

// ParsedGroup contains parsing results for a single RecordGroup.
type ParsedGroup struct {
	// Key is the grouping key (empty for non-keyed records)
	Key          string
	RptMonthYear string
	CaseNumber   string

	// Records contains all successfully parsed records in this group
	Records []*schema.ParsedRecord

	// Errors contains any parsing errors encountered
	Errors []ParseError
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

// TotalErrors returns the total number of parsing errors.
func (pb *ParsedBatch) TotalErrors() int {
	total := 0
	for _, g := range pb.Groups {
		total += len(g.Errors)
	}
	return total
}

// Pool manages worker goroutines for parallel parsing.
type Pool struct {
	numWorkers int
	extractor  parser.FieldExtractor
	parseCtx   *schema.ParseContext // Runtime context from header

	// Single work input channel for all Batches
	work chan *processor.Batch

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
		NumWorkers:       1,
		WorkBufferSize:   256,
		ResultBufferSize: 256,
	}
}

// NewPool creates a worker pool.
func NewPool(format filespec.Format, config PoolConfig) *Pool {
	return &Pool{
		numWorkers: config.NumWorkers,
		extractor:  parser.GetExtractor(format),
		work:       make(chan *processor.Batch, config.WorkBufferSize),
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
func (p *Pool) Submit(batch *processor.Batch) {
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
func (p *Pool) processBatch(batch *processor.Batch) *ParsedBatch {
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
func (p *Pool) processGroup(group *processor.RecordGroup) *ParsedGroup {
	result := &ParsedGroup{
		Key:          group.Key,
		RptMonthYear: group.RptMonthYear,
		CaseNumber:   group.CaseNumber,
		Records:      make([]*schema.ParsedRecord, 0, len(group.Lines)),
		Errors:       make([]ParseError, 0),
	}

	for _, line := range group.Lines {
		records, err := p.parseRow(line)
		if err != nil {
			result.Errors = append(result.Errors, ParseError{
				LineNumber: line.Row.LineNum(),
				RecordType: line.Schema.RecordType,
				Message:    err.Error(),
			})
			continue
		}
		result.Records = append(result.Records, records...)
	}

	return result
}

// parseRow parses a single row into one or more ParsedRecords.
// For multi-segment schemas, one input line produces multiple records (one per segment).
func (p *Pool) parseRow(line processor.RawLine) ([]*schema.ParsedRecord, error) {
	numSegments := len(line.Schema.Segments)
	if numSegments == 0 {
		// Schema has no segments - this shouldn't happen with the new structure
		return nil, nil
	}

	// Parse shared fields once (they're the same for all segments)
	sharedFields := make(map[string]any, len(line.Schema.Shared))
	for i := range line.Schema.Shared {
		field := &line.Schema.Shared[i]
		value, err := p.extractor.Extract(line.Row, field, p.parseCtx, sharedFields)
		if err != nil {
			continue
		}
		if value != nil {
			sharedFields[field.Name] = value
		}
	}

	// Parse each segment into a separate record
	records := make([]*schema.ParsedRecord, 0, numSegments)
	for segIdx, segment := range line.Schema.Segments {
		// Calculate field capacity: shared + segment fields
		fieldCount := len(sharedFields) + len(segment.Fields)

		record := &schema.ParsedRecord{
			Schema:       line.Schema,
			LineNumber:   line.Row.LineNum(),
			SegmentIndex: segIdx,
			Fields:       make(map[string]any, fieldCount),
		}

		// Copy shared fields into this record
		maps.Copy(record.Fields, sharedFields)

		// Parse segment-specific fields and track required fields
		missingRequired := false
		for i := range segment.Fields {
			field := &segment.Fields[i]
			value, err := p.extractor.Extract(line.Row, field, p.parseCtx, record.Fields)
			if err != nil {
				continue
			}
			if value != nil {
				record.Fields[field.Name] = value
			} else if field.Required || segIdx >= 1 {
				// TODO: do we generate an error here?
				// Most multi record schemas don't have the 2 through N segment's field's marked as required.
				// Therefore if the value is nil and the field is required or the segment index is greater than 0
				// we skip creating the record since it is invalid.
				missingRequired = true
				break
			}
		}

		// Only include records where all required segment-specific fields have data.
		// This matches Python behavior where empty segments (e.g., missing second child
		// in T3 records) are not parsed.
		if !missingRequired {
			records = append(records, record)
		}
	}

	return records, nil
}
