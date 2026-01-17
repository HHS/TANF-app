# Go Parser System Architecture Diagrams

Visual reference showing goroutine parallelism, channel communication, and the validation pipeline.

> **Code references** (e.g., `internal/pipeline/pipeline.go`) show where each component lives.

---

## 1. High-Level Goroutine Architecture

```mermaid
flowchart TB
    subgraph MAIN["<b>Main Goroutine</b><br/><code>internal/pipeline/pipeline.go:ProcessFile()</code>"]
        INIT["Initialize pipeline"]
        STREAM["Stream rows via Accumulator"]
        WAIT["Wait & collect stats"]
    end

    subgraph WORKERS["<b>Worker Pool</b> (default: 4)<br/><code>internal/worker/pool.go:worker()</code>"]
        W1["Worker 1"]
        W2["Worker 2"]
        W3["Worker 3"]
        WN["Worker N"]

        subgraph VAL["Validation<br/><code>internal/validation/</code>"]
            ORCH["Orchestrator"]
            subgraph CATS["Category Engines"]
                C4["Cat 4: Group"]
                C1["Cat 1: Row"]
                C2["Cat 2: Field"]
                C3["Cat 3: Cross-field"]
            end
        end
    end

    subgraph DISPATCHERS["<b>Dispatchers</b> (default: 4)<br/><code>internal/pipeline/result_router.go</code>"]
        D1["Dispatcher 1"]
        D2["Dispatcher 2"]
        D3["Dispatcher 3"]
        DN["Dispatcher N"]

        subgraph ERR_GEN["Lazy Error Generation<br/><code>internal/validation/errors/</code>"]
            RENDER["ErrorEngine.GenerateError()"]
        end
    end

    subgraph WRITERS["<b>TableWriter Pool</b> (1 per table)<br/><code>internal/writer/writer.go:run()</code>"]
        TW1["Writer: tanf_t1"]
        TW2["Writer: tanf_t2"]
        TW3["Writer: tanf_t3"]
        TWN["Writer: ..."]
        TWE["Writer: parser_errors"]
    end

    INIT --> STREAM
    STREAM -->|"*Batch<br/>(groups of records)"| WORKERS
    W1 & W2 & W3 & WN --> VAL
    VAL --> C4 -->|"pass"| C1 -->|"pass"| C2 --> C3
    C4 -->|"fail"| REJECT_G["Reject Group"]
    C1 -->|"fail"| REJECT_R["Reject Record"]

    WORKERS -->|"*ParsedBatch<br/>+ []*ValidationResult"| DISPATCHERS
    D1 & D2 & D3 & DN --> ERR_GEN
    ERR_GEN -->|"*ParserError"| TWE

    DISPATCHERS -->|"[]any rows"| WRITERS
    WRITERS -->|"COPY"| DB[(PostgreSQL)]
    STREAM --> WAIT
```

**Goroutine Count:** 1 (main) + N (workers) + N (dispatchers) + M (writers) = ~13+ total

**Key Points:**
- Workers parse AND validate (validation runs inside worker goroutines)
- Validation executes in order: Cat 4 → 1 → 2 → 3 with short-circuit on failure
- Error messages are rendered lazily by dispatchers (not during validation hot path)
- Each TableWriter runs in its own goroutine, including the error writer

---

## 2. Detailed Channel Flow

```mermaid
flowchart LR
    subgraph INPUT["<b>Input Stage</b><br/>(Main Goroutine)"]
        FILE["File"]
        DEC["Decoder<br/><code>internal/decoder/</code>"]
        ACC["Accumulator<br/><code>internal/processor/<br/>accumulator.go</code>"]
    end

    subgraph WORK_CHAN["<b>Work Channel</b><br/><code>chan *processor.Batch</code><br/>buffer: 256"]
        WC[["Buffered"]]
    end

    subgraph WORKERS["<b>Worker Pool</b><br/><code>internal/worker/pool.go</code>"]
        subgraph W1["Worker goroutine"]
            PARSE1["Parse"]
            VAL1["Validate<br/>(4→1→2→3)"]
        end
        subgraph W2["Worker goroutine"]
            PARSE2["Parse"]
            VAL2["Validate"]
        end
        subgraph WN["Worker goroutine"]
            PARSEN["Parse"]
            VALN["Validate"]
        end
    end

    subgraph RESULT_CHAN["<b>Results Channel</b><br/><code>chan *worker.ParsedBatch</code><br/>buffer: 256"]
        RC[["Buffered"]]
    end

    subgraph DISPATCHERS["<b>Dispatchers</b><br/><code>internal/pipeline/<br/>result_router.go</code>"]
        subgraph D1["Dispatcher goroutine"]
            ROUTE1["Route records"]
            ERR1["Render errors<br/>(lazy)"]
        end
        subgraph D2["Dispatcher goroutine"]
            ROUTE2["Route"]
            ERR2["Render"]
        end
        subgraph DN["Dispatcher goroutine"]
            ROUTEN["Route"]
            ERRN["Render"]
        end
    end

    subgraph ROUTER["Router<br/><code>internal/writer/router.go</code>"]
        CONVERT["Convert<br/>ParsedRecord → []any"]
        RELEASE["Release to pool"]
    end

    subgraph WRITER_CHANS["<b>Writer Channels</b><br/><code>chan []any</code><br/>buffer: 50000"]
        WCH1[["t1 chan"]]
        WCH2[["t2 chan"]]
        WCHN[["tN chan"]]
        WCHE[["errors chan"]]
    end

    subgraph WRITERS["<b>TableWriters</b><br/><code>internal/writer/writer.go</code>"]
        TW1["goroutine"]
        TW2["goroutine"]
        TWN["goroutine"]
        TWE["goroutine"]
    end

    FILE -->|"iter.Seq2[Row]"| DEC
    DEC -->|"Row"| ACC
    ACC -->|"*Batch"| WC

    WC --> W1 & W2 & WN
    PARSE1 --> VAL1
    PARSE2 --> VAL2
    PARSEN --> VALN
    W1 & W2 & WN -->|"*ParsedBatch<br/>+ []*ValidationResult"| RC

    RC --> D1 & D2 & DN
    ROUTE1 --> ERR1
    ROUTE2 --> ERR2
    ROUTEN --> ERRN
    D1 & D2 & DN --> CONVERT --> RELEASE
    CONVERT --> WCH1 & WCH2 & WCHN
    ERR1 & ERR2 & ERRN -->|"*ParserError"| WCHE

    WCH1 --> TW1
    WCH2 --> TW2
    WCHN --> TWN
    WCHE --> TWE

    TW1 & TW2 & TWN & TWE -->|"COPY"| DB[(PostgreSQL)]
```

**Channel Buffer Sizes:**
| Channel | Type | Buffer | Purpose |
|---------|------|--------|---------|
| Work | `chan *Batch` | 256 | Backpressure on accumulator |
| Results | `chan *ParsedBatch` | 256 | Backpressure on workers |
| Writer | `chan []any` | 50000 | Batch before COPY |

**Data Flow:**
1. **Main goroutine** streams rows through Decoder → Accumulator
2. **Accumulator** groups by `key_fields`, emits `*Batch` to work channel
3. **Workers** (competing) parse fields, run validation (Cat 4→1→2→3), emit `*ParsedBatch` + `[]*ValidationResult`
4. **Dispatchers** (competing) route valid records to table writers, render errors lazily
5. **TableWriters** buffer rows, flush via PostgreSQL COPY at threshold

**Validation Integration:**
- Validation runs inside workers (same goroutine as parsing)
- `ValidationResult` stores pointers (not rendered messages) — ~80 bytes each
- Error rendering happens in dispatchers via `ErrorEngine.GenerateError(result)`
- Rendered `*ParserError` sent to dedicated error writer channel
