# Validation Architecture Diagrams (Mermaid)

## 1. High-Level System Architecture

```mermaid
flowchart TB
    subgraph CONFIG["Configuration Layer"]
        SCHEMA[Schema YAML]
        FILESPEC[FileSpec YAML]
        VALCONFIG[Validation YAML]
    end

    subgraph REGISTRY["Registry Layer"]
        SCHEMAREG[Schema Registry]
        VALIDATORREG[Validator Registry]
        MESSAGEREG[Message Registry]
    end

    subgraph PIPELINE["Pipeline Layer"]
        FILE[File Input]
        DECODER[Decoder]
        ACCUM[Accumulator]

        subgraph VALIDATION["Validation Pipeline"]
            ORCH[Category Orchestrator]
            ENGINE[Category Engines]
            ERROR[Error Engine]
        end
    end

    subgraph OUTPUT["Output Layer"]
        RECORDWRITER[Record Writer]
        ERRORWRITER[Error Writer]
        STATS[Stats/Metrics]
    end

    CONFIG --> REGISTRY
    REGISTRY --> PIPELINE
    FILE --> DECODER --> ACCUM --> VALIDATION
    VALIDATION --> OUTPUT
```

## 2. Validation Pipeline Detail

```mermaid
flowchart TB
    subgraph ORCHESTRATOR["Category Orchestrator"]
        direction TB
        ORDER["Execution Order: 4 → 1 → 2 → 3"]
        SHORT["Short-Circuit Rules"]
    end

    subgraph ENGINES["Category Engines"]
        CAT4["Cat 4: Group-Level<br/>Scope: RecordGroup"]
        CAT1["Cat 1: Pre-Parsing<br/>Scope: Record"]
        CAT2["Cat 2: Field-Level<br/>Scope: Field"]
        CAT3["Cat 3: Cross-Field<br/>Scope: Record"]
    end

    subgraph ERROR_ENGINE["Error Engine"]
        TEMPLATE["Message Templates"]
        CONTEXT["Context Builder"]
        GENERATOR["Error Generator"]
    end

    ORCHESTRATOR --> CAT4
    CAT4 -->|pass| CAT1
    CAT4 -->|fail| REJECT_GROUP["Reject Group"]
    CAT1 -->|pass| CAT2
    CAT1 -->|fail| REJECT_RECORD["Reject Record"]
    CAT2 --> CAT3

    CAT4 & CAT1 & CAT2 & CAT3 --> ERROR_ENGINE
```

## 3. Concurrency Model

```mermaid
flowchart TB
    subgraph INPUT["Input Stage"]
        FILE[File]
        DECODER[Decoder]
        ACCUM[Accumulator]
    end

    subgraph PARALLEL["Parallel Processing"]
        QUEUE["Work Queue<br/>(channel)"]

        subgraph WORKERS["Worker Pool"]
            W1[Worker 1]
            W2[Worker 2]
            W3[Worker 3]
            WN[Worker N]
        end

        RESULTS["Result Queue<br/>(channel)"]
    end

    subgraph OUTPUT["Output Stage"]
        AGG[Result Aggregator]
        RW[Record Writer]
        EW[Error Writer]
    end

    FILE --> DECODER --> ACCUM
    ACCUM -->|RecordGroups| QUEUE
    QUEUE --> W1 & W2 & W3 & WN
    W1 & W2 & W3 & WN --> RESULTS
    RESULTS --> AGG
    AGG --> RW & EW
```

## 4. Within-Worker Validation Flow

```mermaid
flowchart TB
    GROUP["RecordGroup<br/>{Key, Records[]}"]

    subgraph CAT4_BLOCK["Category 4 Validation"]
        CAT4_CHECK{"Group<br/>Valid?"}
    end

    subgraph RECORD_LOOP["Per-Record Loop"]
        subgraph CAT1_BLOCK["Category 1"]
            CAT1_CHECK{"Record<br/>Valid?"}
        end

        subgraph CAT2_BLOCK["Category 2"]
            FIELD1["Field 1"]
            FIELD2["Field 2"]
            FIELDN["Field N"]
        end

        subgraph CAT3_BLOCK["Category 3"]
            CROSS["Cross-Field<br/>Rules"]
        end
    end

    RESULT["Validation Result"]

    GROUP --> CAT4_CHECK
    CAT4_CHECK -->|Yes| CAT1_CHECK
    CAT4_CHECK -->|No| REJECT_GROUP["Reject Group<br/>Skip All Records"]

    CAT1_CHECK -->|Yes| CAT2_BLOCK
    CAT1_CHECK -->|No| REJECT_RECORD["Reject Record<br/>Skip Cat 2/3"]

    FIELD1 & FIELD2 & FIELDN --> CROSS
    CROSS --> RESULT
    REJECT_GROUP & REJECT_RECORD --> RESULT
```

## 5. Data Flow Sequence

```mermaid
sequenceDiagram
    participant File
    participant Decoder
    participant Accumulator
    participant WorkerPool
    participant Orchestrator
    participant Cat4Engine
    participant Cat1Engine
    participant Cat2Engine
    participant Cat3Engine
    participant ErrorEngine
    participant Writer

    File->>Decoder: Raw bytes
    Decoder->>Accumulator: Rows
    Accumulator->>WorkerPool: RecordGroup batch

    WorkerPool->>Orchestrator: ValidateGroup(group)

    Orchestrator->>Cat4Engine: Validate(records)
    Cat4Engine-->>Orchestrator: GroupResult

    alt Cat4 Failed
        Orchestrator-->>WorkerPool: GroupRejected + Errors
    else Cat4 Passed
        loop For each record
            Orchestrator->>Cat1Engine: Validate(record)
            Cat1Engine-->>Orchestrator: Result

            alt Cat1 Failed
                Orchestrator->>ErrorEngine: Generate error
            else Cat1 Passed
                Orchestrator->>Cat2Engine: Validate(fields)
                Cat2Engine-->>Orchestrator: Results
                Orchestrator->>Cat3Engine: Validate(record)
                Cat3Engine-->>Orchestrator: Results
            end
        end
        Orchestrator-->>WorkerPool: GroupResult
    end

    WorkerPool->>ErrorEngine: Failed validations
    ErrorEngine-->>WorkerPool: ParserErrors

    WorkerPool->>Writer: Valid records + Errors
```

## 6. Configuration Loading

```mermaid
flowchart LR
    subgraph YAML["YAML Files"]
        SCHEMA["schemas/<br/>tanf/t1.yaml"]
        RULES["validation/rules/<br/>tanf/t1.yaml"]
        MESSAGES["validation/messages/<br/>category2.yaml"]
        ORCH_CFG["validation/<br/>orchestrator.yaml"]
    end

    subgraph LOADER["Config Loader"]
        PARSE["YAML Parser"]
        COMPILE["Rule Compiler"]
        LINK["Schema Linker"]
    end

    subgraph REGISTRY["Registries"]
        SREG["Schema Registry<br/>(CompiledSchema)"]
        VREG["Validator Registry<br/>(ValidatorFunc)"]
        MREG["Message Registry<br/>(Templates)"]
    end

    SCHEMA --> PARSE --> SREG
    RULES --> COMPILE --> VREG
    MESSAGES --> LINK --> MREG
    ORCH_CFG --> LINK

    SREG -.->|field metadata| MREG
    VREG -.->|validator IDs| MREG
```

## 7. Error Generation Flow

```mermaid
flowchart TB
    FAILURE["Validation Failure<br/>{ValidatorID, Params, FieldValue}"]

    subgraph LOOKUP["Template Lookup"]
        CHECK1{"Schema-specific<br/>override?"}
        CHECK2{"Field-specific<br/>override?"}
        DEFAULT["Default template"]
    end

    subgraph BUILD["Context Building"]
        RECORD_CTX["Record Context<br/>(type, line#)"]
        FIELD_CTX["Field Context<br/>(name, item#, value)"]
        GROUP_CTX["Group Context<br/>(case#, RPT_MONTH_YEAR)"]
        PARAMS_CTX["Validator Params<br/>(min, max, etc.)"]
    end

    subgraph RENDER["Message Rendering"]
        TEMPLATE["Go Template<br/>text/template"]
        MESSAGE["Error Message"]
    end

    PARSER_ERROR["ParserError<br/>{all fields populated}"]

    FAILURE --> CHECK1
    CHECK1 -->|Yes| BUILD
    CHECK1 -->|No| CHECK2
    CHECK2 -->|Yes| BUILD
    CHECK2 -->|No| DEFAULT --> BUILD

    RECORD_CTX & FIELD_CTX & GROUP_CTX & PARAMS_CTX --> TEMPLATE
    TEMPLATE --> MESSAGE --> PARSER_ERROR
```

## 8. Package Structure

```mermaid
flowchart TB
    subgraph INTERNAL["internal/"]
        subgraph VALIDATION["validation/"]
            ORCH["orchestrator.go"]
            ENGINE["engine.go"]
            RESULT["result.go"]
            CONTEXT["context.go"]
            POOL["pool.go"]

            subgraph REGISTRY_PKG["registry/"]
                VREG["validators.go"]
                MREG["messages.go"]
                LOADER["loader.go"]
            end

            subgraph VALIDATORS["validators/"]
                COMMON["common.go"]
                COMPARISON["comparison.go"]
                STRING["string.go"]
                NUMERIC["numeric.go"]
                DATE["date.go"]
                C1["category1.go"]
                C3["category3.go"]
                C4["category4.go"]
            end

            subgraph ERRORS["errors/"]
                ERR_ENGINE["engine.go"]
                TEMPLATES["templates.go"]
                TYPES["types.go"]
            end
        end

        EXISTING_PIPELINE["pipeline/<br/>(existing, modified)"]
        EXISTING_WORKER["worker/<br/>(existing, modified)"]
        EXISTING_WRITER["writer/<br/>(existing + error_writer.go)"]
    end

    VALIDATION --> EXISTING_PIPELINE
    VALIDATION --> EXISTING_WORKER
    ERRORS --> EXISTING_WRITER
```

## 9. Adding a New Category

```mermaid
flowchart TB
    subgraph STEP1["Step 1: Config"]
        ADD_CAT["Add to orchestrator.yaml<br/>categories: [{id: 5, scope: file}]"]
        ADD_ORDER["Add to execution_order"]
        ADD_SHORT["Add short_circuit_rules"]
    end

    subgraph STEP2["Step 2: Engine (if new scope)"]
        NEW_ENGINE["Implement CategoryEngine<br/>for new scope"]
        REGISTER["Register with orchestrator"]
    end

    subgraph STEP3["Step 3: Validators"]
        ADD_VALIDATORS["Add validator functions"]
        ADD_FACTORY["Register factories"]
    end

    subgraph STEP4["Step 4: Messages"]
        ADD_TEMPLATES["Add message templates<br/>category5.yaml"]
    end

    subgraph STEP5["Step 5: Rules"]
        ADD_RULES["Add rules to schemas<br/>category5: [...]"]
    end

    STEP1 --> STEP2 --> STEP3 --> STEP4 --> STEP5

    NOTE["Most new categories<br/>only need Steps 1, 3-5<br/>(reuse existing scopes)"]
```

## 10. Validator Composition

```mermaid
flowchart LR
    subgraph BASE["Base Validators"]
        IS_EQUAL["isEqual"]
        IS_GREATER["isGreaterThan"]
        IS_BETWEEN["isBetween"]
    end

    subgraph COMPOSED["Composed Validators"]
        IF_THEN["ifThenAlso<br/>(uses base validators)"]
        SUM_GT["sumIsGreaterThan<br/>(uses isGreaterThan)"]
    end

    subgraph YAML["YAML Config"]
        RULE["validator: ifThenAlso<br/>params:<br/>  condition: isGreaterThan<br/>  result: isEqual"]
    end

    IS_EQUAL & IS_GREATER --> IF_THEN
    IS_GREATER --> SUM_GT
    YAML --> IF_THEN
```
