# Object Pooling Design for ParsedRecord

## Problem Statement

Profiling reveals that ~70% of CPU time is spent in garbage collection operations:

| Function | CPU % | Description |
|----------|-------|-------------|
| `runtime.madvise` | 22.85% | GC memory management |
| `runtime.scanobject` | 23.60% | GC object scanning |
| `runtime.(*mspan).typePointersOfUnchecked` | 17.42% | GC pointer scanning |
| `runtime.memclrNoHeapPointers` | 7.30% | Memory clearing |

Memory allocation hotspots:

| Location | Memory | % of Total |
|----------|--------|------------|
| `worker.(*Pool).parseRow` | 16.4MB | 52.88% |
| `writer.NewTableWriter` | 5.4MB | 17.33% |
| `processor.(*Accumulator).addWithKeySorted` | 1MB | 3.29% |

The root cause is that `parseRow` allocates new objects for every row:
- `map[string]any` for shared fields
- `[]*ParsedRecord` slice
- `ParsedRecord` struct with another `map[string]any` per segment

With 100K+ rows per file, this creates massive GC pressure.

## Goals

1. **Reduce allocations** - Reuse `ParsedRecord` objects via `sync.Pool`
2. **Eliminate map overhead** - Replace `map[string]any` with indexed `[]any`
3. **Minimize object lifetime** - Return objects to pool as early as possible
4. **Support future validation** - Design must allow validators to access `ParsedRecord` before writing

## Current Pipeline

```
┌─────────┐     ┌─────────────┐     ┌─────────────────────────────────┐
│ Workers │────▶│ Dispatchers │────▶│ Writers (convert + flush)       │
│ (parse) │     │ (route)     │     │                                 │
└─────────┘     └─────────────┘     └─────────────────────────────────┘
     │                                            │
     └── allocate ParsedRecord                    └── ParsedRecord finally consumed

     ════════════════════ Long lifetime ════════════════════
```

## Future Pipeline (with Validation)

```
┌─────────┐     ┌────────────┐     ┌───────────────────────────────┐     ┌─────────────────┐
│ Workers │────▶│ Validators │────▶│ Routers                       │────▶│ Writers         │
│ (parse) │     │ (validate) │     │ (convert + return to pool)    │     │ (buffer + flush)│
└─────────┘     └────────────┘     └───────────────────────────────┘     └─────────────────┘
     │                │                       │                                │
     │                │                       └── Release to pool              └── Receives []any only
     │                └── needs field access
     └── Acquire from pool

     ════════ Short lifetime ════════
```

Validation needs full `ParsedRecord` access. The router converts `ParsedRecord` to `[]any` for the database, then immediately releases to pool. Writers receive `[]any` directly - no `ParsedRecord` access needed.

## Design

### 1. Replace `map[string]any` with Indexed `[]any`

The current `ParsedRecord.Fields` uses a map, which allocates:
- Hash table buckets
- String keys (though often interned)
- Individual entries

An indexed slice is much cheaper:

```go
// Current - expensive
type ParsedRecord struct {
    Schema       *CompiledSchema
    LineNumber   int
    SegmentIndex int
    Fields       map[string]any  // allocates buckets, entries
}

// Proposed - cheap
type ParsedRecord struct {
    Schema       *CompiledSchema
    LineNumber   int
    SegmentIndex int
    Fields       []any  // single allocation, indexed by schema
}
```

### 2. Schema Owns Field Index Mapping

Each `CompiledSchema` knows its field structure. We build a name→index mapping at schema load time:

```go
type CompiledSchema struct {
    *SchemaDef
    Path string

    // Existing
    SharedFieldsByName map[string]*FieldDef

    // New: field indexing for pooled records
    FieldIndex map[string]int  // field name → index in []any
    FieldCount int             // total field slots needed

    // New: object pool for this schema's records
    recordPool sync.Pool
}
```

Field index assignment at schema compile time:

```go
func (s *SchemaDef) Compile() *CompiledSchema {
    cs := &CompiledSchema{
        SchemaDef:          s,
        SharedFieldsByName: make(map[string]*FieldDef, len(s.Shared)),
        FieldIndex:         make(map[string]int),
    }

    idx := 0

    // Index shared fields first (present in all segments)
    for i := range s.Shared {
        field := &s.Shared[i]
        cs.SharedFieldsByName[field.Name] = field
        cs.FieldIndex[field.Name] = idx
        idx++
    }

    // Index segment fields from first segment
    // All segments have the same field names (e.g., T3's two child segments
    // both have FAMILY_AFFILIATION, SSN, etc.)
    if len(s.Segments) > 0 {
        for _, field := range s.Segments[0].Fields {
            cs.FieldIndex[field.Name] = idx
            idx++
        }
    }

    cs.FieldCount = idx
    return cs
}
```

### 3. Schema Provides Acquire/Release Methods

Each schema has its own `sync.Pool` that produces correctly-sized records:

```go
// AcquireRecord gets a record from the pool or creates a new one.
// The returned record has Fields slice allocated but all values nil.
func (cs *CompiledSchema) AcquireRecord() *ParsedRecord {
    if r := cs.recordPool.Get(); r != nil {
        rec := r.(*ParsedRecord)
        // Reset fields but keep the backing array
        rec.LineNumber = 0
        rec.SegmentIndex = 0
        for i := range rec.Fields {
            rec.Fields[i] = nil
        }
        return rec
    }
    // Pool empty - allocate new record with correct capacity
    return &ParsedRecord{
        Schema: cs,
        Fields: make([]any, cs.FieldCount),
    }
}

// ReleaseRecord returns a record to the pool for reuse.
// The record must not be used after calling this method.
func (cs *CompiledSchema) ReleaseRecord(rec *ParsedRecord) {
    // Only pool records that belong to this schema
    if rec.Schema == cs {
        cs.recordPool.Put(rec)
    }
}
```

### 4. ParsedRecord Field Access Helpers

To maintain ergonomic field access for validators and converters:

```go
// Get retrieves a field value by name.
// Returns nil if the field doesn't exist or has no value.
func (pr *ParsedRecord) Get(fieldName string) any {
    idx, ok := pr.Schema.FieldIndex[fieldName]
    if !ok {
        return nil
    }
    return pr.Fields[idx]
}

// Set stores a field value by name.
// No-op if the field name is not in the schema.
func (pr *ParsedRecord) Set(fieldName string, value any) {
    idx, ok := pr.Schema.FieldIndex[fieldName]
    if ok {
        pr.Fields[idx] = value
    }
}

// GetString retrieves a field as a string.
// Returns empty string if field is nil or not a string.
func (pr *ParsedRecord) GetString(fieldName string) string {
    v := pr.Get(fieldName)
    if s, ok := v.(string); ok {
        return s
    }
    return ""
}

// GetInt retrieves a field as an int.
// Returns 0 if field is nil or not an int.
func (pr *ParsedRecord) GetInt(fieldName string) int {
    v := pr.Get(fieldName)
    if i, ok := v.(int); ok {
        return i
    }
    return 0
}
```

### 5. Worker Acquires from Pool

Update `parseRow` to acquire records from the schema's pool and parse directly into the record's `Fields []any`.

- **Shared fields**: Parsed once into a small cache (one allocation per row)
- **Segment fields**: Parsed directly into the leased record (no temp allocation)
- **Invalid segments**: Record is released back to pool immediately

```go
func (p *Pool) parseRow(line processor.RawLine) ([]*schema.ParsedRecord, error) {
    numSegments := len(line.Schema.Segments)
    if numSegments == 0 {
        return nil, nil
    }

    // Parse shared fields once into cache (one small allocation per row)
    sharedCache := make(map[string]any, len(line.Schema.Shared))
    for i := range line.Schema.Shared {
        field := &line.Schema.Shared[i]
        value, err := p.extractor.Extract(line.Row, field, p.parseCtx, sharedCache)
        if err != nil {
            continue
        }
        if value != nil {
            sharedCache[field.Name] = value
        }
    }

    // Parse each segment directly into a pooled record
    records := make([]*schema.ParsedRecord, 0, numSegments)
    for segIdx, segment := range line.Schema.Segments {
        // Acquire record from pool
        record := line.Schema.AcquireRecord()
        record.LineNumber = line.Row.LineNum()
        record.SegmentIndex = segIdx

        // Copy cached shared fields into record
        for name, value := range sharedCache {
            record.Set(name, value)
        }

        // Parse segment fields DIRECTLY into record (no temp allocation)
        missingRequired := false
        for i := range segment.Fields {
            field := &segment.Fields[i]
            value, err := p.extractor.Extract(line.Row, field, p.parseCtx, record)
            if err != nil {
                continue
            }
            if value != nil {
                record.Set(field.Name, value)
            } else if field.Required || segIdx >= 1 {
                missingRequired = true
                break
            }
        }

        if missingRequired {
            // Invalid segment - release record back to pool
            line.Schema.ReleaseRecord(record)
            continue
        }

        records = append(records, record)
    }

    return records, nil
}
```

**Release points:**
- **Worker**: Releases only when segment is invalid (abort case)
- **Router**: Releases after successful conversion (normal flow)

### 6. Router Converts and Releases to Pool

**This is where valid `ParsedRecord` objects are released back to the pool.**

The router is the boundary between the `ParsedRecord` world and the `[]any` database row world. After conversion, the `ParsedRecord` is no longer needed and can be immediately recycled.

(Workers may also release records in the abort case when a segment is invalid - see section 5.)

```go
// In WriterManager - release point for valid records in normal flow
func (wm *WriterManager) WriteRecord(ctx context.Context, record *schema.ParsedRecord) error {
    tw, ok := wm.writers[record.Schema.Path]
    if !ok {
        return fmt.Errorf("no writer for schema: %s", record.Schema.Path)
    }

    // Get converter for this schema
    conv := wm.converters[record.Schema.Path]

    // Convert ParsedRecord → []any rows
    rows := conv(record, wm.datafileID)

    // ┌─────────────────────────────────────────────────────────────┐
    // │ RELEASE TO POOL - Normal flow release point                │
    // │ Workers may also release invalid segments during parsing.  │
    // └─────────────────────────────────────────────────────────────┘
    record.Schema.ReleaseRecord(record)

    // Send converted rows to writer ([]any, not ParsedRecord)
    for _, row := range rows {
        if err := tw.SendRow(ctx, row); err != nil {
            return err
        }
    }
    return nil
}
```

**Why release here?**
- Validators have already accessed the record (upstream)
- Conversion extracts all needed data into `[]any`
- Writers only need `[]any` - they never see `ParsedRecord`
- Releasing immediately minimizes object lifetime

### 7. TableWriter Receives []any Directly

The `TableWriter` no longer needs a converter - it just receives and buffers `[]any` rows:

```go
type TableWriter struct {
    tableName string
    columns   []string
    threshold int

    // Channel now carries []any rows, not ParsedRecords
    rowChan chan []any
    pool    *pgxpool.Pool
    wg      sync.WaitGroup

    // Internal buffer
    rows [][]any

    // Stats
    totalWritten atomic.Int64

    // Error handling
    err   error
    errMu sync.RWMutex
}

func NewTableWriter(tableName string, columns []string, threshold int) *TableWriter {
    if threshold <= 0 {
        threshold = DefaultFlushThreshold
    }
    return &TableWriter{
        tableName: tableName,
        columns:   columns,
        threshold: threshold,
        rowChan:   make(chan []any, threshold),
        rows:      make([][]any, 0, threshold),
    }
}

func (tw *TableWriter) run(ctx context.Context) {
    defer tw.wg.Done()

    for {
        select {
        case row, ok := <-tw.rowChan:
            if !ok {
                tw.flush(ctx)
                return
            }

            // Just buffer - no conversion needed
            tw.rows = append(tw.rows, row)
            if len(tw.rows) >= tw.threshold {
                if err := tw.flush(ctx); err != nil {
                    tw.setError(err)
                    tw.drain()
                    return
                }
            }

        case <-ctx.Done():
            tw.flush(context.Background())
            tw.drain()
            return
        }
    }
}

// SendRow queues a converted row for writing
func (tw *TableWriter) SendRow(ctx context.Context, row []any) error {
    if err := tw.getError(); err != nil {
        return err
    }

    select {
    case tw.rowChan <- row:
        return nil
    case <-ctx.Done():
        return ctx.Err()
    }
}

func (tw *TableWriter) drain() {
    for range tw.rowChan {
        // Just discard - no pool release needed for []any
    }
}
```

### 8. Update Converters for Indexed Access

Converters currently use map access. Update to use the `Get()` helper or direct index:

```go
// Before
func convertT1(record *schema.ParsedRecord, datafileID int32) [][]any {
    return [][]any{{
        record.Fields["record_type"],
        record.Fields["rpt_month_year"],
        record.Fields["case_number"],
        // ...
    }}
}

// After - using Get() helper (cleaner)
func convertT1(record *schema.ParsedRecord, datafileID int32) [][]any {
    return [][]any{{
        record.Get("record_type"),
        record.Get("rpt_month_year"),
        record.Get("case_number"),
        // ...
    }}
}

// After - using direct index (faster, but couples to schema)
func convertT1(record *schema.ParsedRecord, datafileID int32) [][]any {
    f := record.Fields
    return [][]any{{
        f[0],  // record_type
        f[1],  // rpt_month_year
        f[2],  // case_number
        // ...
    }}
}
```

Recommendation: Use `Get()` helper for maintainability. The map lookup overhead is minimal compared to the allocation savings.

## Object Lifecycle Diagram

```
                      sync.Pool (per schema)
                      ┌─────────────────────┐
                      │  recycled records   │
                      └──────────┬──────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │ AcquireRecord()  │                  │ ReleaseRecord()
              ▼                  │                  │
      ┌───────────────┐          │                  │
      │    Worker     │          │                  │
      │  parseRow()   │          │                  │
      │               │          │                  │
      │  record.Set() │          │                  │
      │               │──────────┘                  │
      │  (invalid     │  abort: release             │
      │   segment)    │                             │
      └───────┬───────┘                             │
              │ valid records                       │
              ▼                                     │
      ┌───────────────┐                             │
      │   Validator   │  (future)                   │
      │               │                             │
      │  record.Get() │                             │
      └───────┬───────┘                             │
              │                                     │
              ▼                                     │
      ┌───────────────┐                             │
      │    Router     │                             │
      │               │                             │
      │  convert()    │─────────────────────────────┘
      │  send []any   │  normal flow: release
      └───────┬───────┘
              │ []any (not ParsedRecord)
              ▼
      ┌───────────────┐
      │ TableWriter   │
      │               │
      │  buffer rows  │
      │  COPY to DB   │
      └───────────────┘
```

## Memory Comparison

### Before (per row with 20 fields)

| Allocation | Size | Count per Row |
|------------|------|---------------|
| `map[string]any` buckets | ~200 bytes | 1-2 (shared + record) |
| `ParsedRecord` struct | 40 bytes | 1-3 (per segment) |
| Map entries | ~50 bytes each | 20+ |

**Total: ~1-2KB per row**

### After (per row with 20 fields)

| Allocation | Size | Count per Row |
|------------|------|---------------|
| `[]any` slice | 160 bytes (20 × 8) | 0 (reused from pool) |
| `ParsedRecord` struct | 32 bytes | 0 (reused from pool) |

**Total: ~0 bytes per row** (after pool warmup)

### Expected Impact

For a 100K row file:
- Before: ~100-200MB allocations, heavy GC pressure
- After: ~1MB allocations (initial pool fill), minimal GC

## Implementation Steps

1. **Add `FieldIndex` and `FieldCount` to `CompiledSchema`**
   - Update `Compile()` to build the index
   - Add `AcquireRecord()` and `ReleaseRecord()` methods

2. **Add accessor methods to `ParsedRecord`**
   - `Get(name)`, `Set(name, value)`
   - `GetString(name)`, `GetInt(name)` convenience methods

3. **Update `parseRow` to use pool**
   - Acquire from schema's pool
   - Use `Set()` instead of map assignment

4. **Update `WriterManager` to convert and release**
   - Move converter ownership from `TableWriter` to `WriterManager`
   - `WriteRecord()` converts, releases to pool, sends `[]any` to writer

5. **Simplify `TableWriter` to receive `[]any`**
   - Remove converter from `TableWriter`
   - Change channel from `chan *ParsedRecord` to `chan []any`
   - Add `SendRow()` method

6. **Update converters to use `Get()` accessor**
   - Replace `record.Fields["name"]` with `record.Get("name")`

7. **Update tests**
   - Tests that create `ParsedRecord` directly need to use `AcquireRecord()`
   - Or create with properly-sized `Fields` slice

## Testing Strategy

### Unit Tests

```go
func TestRecordPooling(t *testing.T) {
    schema := createTestSchema() // has FieldCount = 5

    // Acquire should return record with correct capacity
    r1 := schema.AcquireRecord()
    assert.Equal(t, 5, len(r1.Fields))
    assert.Equal(t, schema, r1.Schema)

    // Set/Get should work
    r1.Set("field_a", "value")
    assert.Equal(t, "value", r1.Get("field_a"))

    // Release and re-acquire should return same object (usually)
    schema.ReleaseRecord(r1)
    r2 := schema.AcquireRecord()
    // Fields should be cleared
    assert.Nil(t, r2.Get("field_a"))
}
```

### Benchmark Tests

```go
func BenchmarkParseRowWithPool(b *testing.B) {
    // Setup schema, extractor, test data

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        records, _ := pool.parseRow(testLine)
        // Simulate writer releasing
        for _, r := range records {
            r.Schema.ReleaseRecord(r)
        }
    }
}

func BenchmarkParseRowWithoutPool(b *testing.B) {
    // Same setup but with old allocation-per-row code
}
```

### Integration Tests

Run full file parsing with pool enabled, verify:
- Correct record counts
- Correct field values in database
- Memory profile shows reduced allocations

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Use-after-release bugs | Data corruption | Clear fields on release; add debug mode that panics on use-after-release |
| Wrong schema pool | Silent bugs | Validate `rec.Schema == cs` in `ReleaseRecord()` |
| Pool contention | Performance regression | `sync.Pool` is already per-P (goroutine-local); unlikely to be a problem |
| Index mismatch | Wrong field values | Build index deterministically; add validation in debug builds |

## Future Optimizations

1. **Pool the `[]any` database rows** - Currently allocated per-record in converter. Could pool these too.

2. **Pool the temporary `sharedFields` map** - Small impact but could eliminate remaining allocations.

3. **Pre-warm pools** - Allocate N records at startup to avoid allocation during initial parsing.

4. **Pool `[]*ParsedRecord` slices** - The slice returned by `parseRow` is allocated per-row. Could pool these.

## Appendix: sync.Pool Behavior

Go's `sync.Pool` is designed for exactly this use case:

- **Per-P storage**: Each processor (P) has its own local pool, reducing contention
- **GC-aware**: Pool contents may be cleared on GC, but that's fine - we just allocate new records
- **Zero-value safe**: `Get()` returns `nil` if pool is empty; we handle this by allocating

```go
var pool sync.Pool

// Get returns nil or a previously-Put value
obj := pool.Get()
if obj == nil {
    obj = makeNew()
}

// Put returns object for potential reuse
pool.Put(obj)
```

The pool automatically scales based on usage patterns. High-throughput parsing will keep pools populated; idle parsers will have pools cleared by GC (which is fine - memory is freed).
