package parser

import (
	"log"

	"go-parser/internal/config/filespec"
)

// ParsingOrchestrator coordinates parsing logic for decoded batches.
// It handles field extraction and record construction
type ParsingOrchestrator struct {
	extractor FieldExtractor
	parseCtx  *ParseContext // Runtime context from header
}

// NewParsingOrchestrator creates a parsing orchestrator.
func NewParsingOrchestrator(format filespec.Format, ctx *ParseContext) *ParsingOrchestrator {
	return &ParsingOrchestrator{
		extractor: GetExtractor(format),
		parseCtx:  ctx,
	}
}

// ParseBatch parses all records in a DecodedBatch.
// Called by pipeline.WorkerPool which owns the goroutines and adds validation.
func (o *ParsingOrchestrator) ParseBatch(batch *DecodedBatch) *ParsedBatch {
	result := &ParsedBatch{
		BatchID: batch.BatchID,
		Groups:  make([]*ParsedGroup, 0, len(batch.DecodedGroups)),
	}

	for _, group := range batch.DecodedGroups {
		result.Groups = append(result.Groups, o.processGroup(group))
	}

	return result
}

// processGroup parses all records in a single group.
func (o *ParsingOrchestrator) processGroup(decodedGroup *DecodedGroup) *ParsedGroup {
	result := &ParsedGroup{
		Key:     decodedGroup.Key,
		Records: make([]*ParsedRecord, 0, len(decodedGroup.DecodedRecords)),
	}

	for _, line := range decodedGroup.DecodedRecords {
		records, err := o.parseRow(line)
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
func (o *ParsingOrchestrator) parseRow(decodedRecord DecodedRecord) ([]*ParsedRecord, error) {
	schema := decodedRecord.Schema
	numSegments := len(schema.Segments)
	if numSegments == 0 {
		// Schema has no segments - this shouldn't happen with the new structure
		return nil, nil
	}

	// Parse shared fields once into a cache (one small allocation per row).
	// We store both FieldDef and Value, even when the value is nil, so validation
	// can still see required/missing fields.
	sharedCache := make(ParsedFieldCache, len(schema.Shared))
	for i := range schema.Shared {
		field := &schema.Shared[i]
		value, err := o.extractor.Extract(decodedRecord.Row, field, o.parseCtx, sharedCache)
		if err != nil {
			log.Printf("Failed to extract shared field %s: %v", field.Name, err)
			continue
		}
		sharedCache[field.Name] = ParsedField{Def: field, Value: value}
	}

	// Parse each segment into a separate record acquired from the pool
	records := make([]*ParsedRecord, 0, numSegments)
	for segIdx, segment := range schema.Segments {
		// Acquire record from pool (reuses memory, reduces GC pressure)
		record := schema.AcquireRecord().(*ParsedRecord)
		record.LineNumber = decodedRecord.Row.LineNum()
		record.SegmentIndex = segIdx
		record.DecodedSize = decodedRecord.Row.DecodedLength()

		// Copy cached shared fields into record using SetField() to preserve FieldDef
		for _, pf := range sharedCache {
			record.SetField(pf.Def, pf.Value)
		}

		// Parse segment-specific fields directly into record using SetField().
		// We keep segment 0 records even when required fields are nil so validation
		// can emit parser errors. Secondary segments are still suppressed when
		// they have no source data of their own. Computed/source_field values do
		// not count as segment data for this check because they can be populated
		// even when the segment's real columns are blank (for example T7 month rows).
		hasSegmentData := false
		for i := range segment.Fields {
			field := &segment.Fields[i]
			// The extractor expects a FieldGetter for lookups (e.g., source_field resolution)
			value, err := o.extractor.Extract(decodedRecord.Row, field, o.parseCtx, record)
			if err != nil {
				log.Printf("Failed to extract field %s: %v", field.Name, err)
				continue
			}
			record.SetField(field, value)
			if field.SourceField == "" && value != nil {
				hasSegmentData = true
			}
		}

		if segIdx >= 1 && !hasSegmentData {
			// Blank secondary segment - release record back to pool immediately.
			schema.ReleaseRecord(record)
			continue
		}

		records = append(records, record)
	}

	return records, nil
}
