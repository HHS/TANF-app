package worker

import (
	"context"
	"sync"

	"go-parser/internal/filespec"
	"go-parser/internal/parser"
	"go-parser/internal/processor"
	"go-parser/internal/schema"
)

// ParsedRecord represents a successfully parsed record.
type ParsedRecord struct {
    Schema     *schema.CompiledSchema
    LineNumber int
    Fields     map[string]any
}

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
    Records []*ParsedRecord

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

    // Single work input channel for all Batches
    work chan *processor.Batch

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
        NumWorkers:       8,
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
        Records:      make([]*ParsedRecord, 0, len(group.Lines)),
        Errors:       make([]ParseError, 0),
    }

    for _, line := range group.Lines {
        record, err := p.parseRow(line)
        if err != nil {
            result.Errors = append(result.Errors, ParseError{
                LineNumber: line.Row.LineNum(),
                RecordType: line.Schema.RecordType,
                Message:    err.Error(),
            })
            continue
        }
        result.Records = append(result.Records, record)
    }

    return result
}

// parseRow parses a single row into a ParsedRecord.
func (p *Pool) parseRow(line processor.RawLine) (*ParsedRecord, error) {
    record := &ParsedRecord{
        Schema:     line.Schema,
        LineNumber: line.Row.LineNum(),
        Fields:     make(map[string]any, len(line.Schema.Fields)),
    }

    for i := range line.Schema.Fields {
        field := &line.Schema.Fields[i]

        value, err := p.extractor.Extract(line.Row, field)
        if err != nil {
            // Log but continue - validation will catch missing required fields
            continue
        }

        if value != nil {
            record.Fields[field.Name] = value
        }
    }

    return record, nil
}
