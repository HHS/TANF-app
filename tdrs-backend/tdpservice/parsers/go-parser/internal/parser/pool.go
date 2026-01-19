package parser

import (
	"context"
	"log"
	"sync"

	"go-parser/internal/filespec"
)

// ParserPool manages worker goroutines for parallel parsing.
type ParserPool struct {
	numWorkers int
	extractor  FieldExtractor
	parseCtx   *ParseContext // Runtime context from header

	// Single work input channel for all Batches
	work chan *Batch

	// Single result output channel
	results chan *ParsedBatch

	wg sync.WaitGroup
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

// NewParserPool creates a worker pool.
func NewParserPool(format filespec.Format, config PoolConfig, ctx *ParseContext) *ParserPool {
	return &ParserPool{
		numWorkers: config.NumWorkers,
		extractor:  GetExtractor(format),
		parseCtx:   ctx,
		work:       make(chan *Batch, config.WorkBufferSize),
		results:    make(chan *ParsedBatch, config.ResultBufferSize),
	}
}

// Start launches the worker goroutines.
func (p *ParserPool) Start(ctx context.Context) {
	for i := 0; i < p.numWorkers; i++ {
		p.wg.Add(1)
		go p.worker(ctx)
	}
}

// Submit submits a Batch for processing.
// Blocks if the work channel is full (backpressure).
func (p *ParserPool) Submit(batch *Batch) {
	p.work <- batch
}

// CloseInputs signals that no more work will be submitted.
func (p *ParserPool) CloseInputs() {
	close(p.work)
}

// Wait blocks until all workers finish, then closes result channels.
func (p *ParserPool) Wait() {
	p.wg.Wait()
	close(p.results)
	log.Print("All lines in file have been parsed into records and queued for writing.")
}

// Results returns the channel for receiving parsed batch results.
func (p *ParserPool) Results() <-chan *ParsedBatch {
	return p.results
}

// worker is the main worker goroutine.
func (p *ParserPool) worker(ctx context.Context) {
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
func (p *ParserPool) processBatch(batch *Batch) *ParsedBatch {
	result := &ParsedBatch{
		BatchID: batch.BatchID,
		Groups:  make([]*ParsedGroup, 0, len(batch.DecodedGroups)),
	}

	for _, group := range batch.DecodedGroups {
		parsedGroup := p.processGroup(group)
		result.Groups = append(result.Groups, parsedGroup)
	}

	return result
}

// processGroup parses all records in a single group.
func (p *ParserPool) processGroup(decodedGroup *DecodedGroup) *ParsedGroup {
	result := &ParsedGroup{
		Key:          decodedGroup.Key,
		RptMonthYear: decodedGroup.RptMonthYear,
		CaseNumber:   decodedGroup.CaseNumber,
		Records:      make([]*ParsedRecord, 0, len(decodedGroup.DecodedRecords)),
	}

	for _, line := range decodedGroup.DecodedRecords {
		records, err := p.parseRow(line)
		if err != nil {
			log.Printf("Failed to parse line %d: %v", line.Row.LineNum(), err)
			continue
		}
		result.Records = append(result.Records, records...)
	}

	return result
}

// parseRow parses a single DecodedRecord into one or more ParsedRecords.
// For multi-segment schemas, one input line produces multiple records (one per segment).
// Records are acquired from the schema's object pool and must be released after use.
func (p *ParserPool) parseRow(decodedRecord DecodedRecord) ([]*ParsedRecord, error) {
	schema := decodedRecord.Schema
	numSegments := len(schema.Segments)
	if numSegments == 0 {
		// Schema has no segments - this shouldn't happen with the new structure
		return nil, nil
	}

	// Parse shared fields once into a cache (one small allocation per row).
	// We use a map here temporarily to collect shared values, then copy them
	// into each record's indexed slice.
	sharedCache := make(MapFieldGetter, len(schema.Shared))
	for i := range schema.Shared {
		field := &schema.Shared[i]
		value, err := p.extractor.Extract(decodedRecord.Row, field, p.parseCtx, sharedCache)
		if err != nil {
			log.Printf("Failed to extract shared field %s: %v", field.Name, err)
			continue
		}
		if value != nil {
			sharedCache[field.Name] = value
		}
	}

	// Parse each segment into a separate record acquired from the pool
	records := make([]*ParsedRecord, 0, numSegments)
	for segIdx, segment := range schema.Segments {
		// Acquire record from pool (reuses memory, reduces GC pressure)
		record := schema.AcquireRecord().(*ParsedRecord)
		record.LineNumber = decodedRecord.Row.LineNum()
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
			value, err := p.extractor.Extract(decodedRecord.Row, field, p.parseCtx, record)
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
			schema.ReleaseRecord(record)
			continue
		}

		records = append(records, record)
	}

	return records, nil
}
