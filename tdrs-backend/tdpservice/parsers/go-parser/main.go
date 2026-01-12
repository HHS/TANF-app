package main

import (
	"context"
	"fmt"
	"log"
	"os"
	"sync"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/db"
	"go-parser/internal/decoder"
	"go-parser/internal/filespec"
	"go-parser/internal/parser"
	"go-parser/internal/processor"
	"go-parser/internal/registry"
	"go-parser/internal/worker"
)

func main() {
	ctx := context.Background()

	// Connect to database
	pool, err := pgxpool.New(ctx, os.Getenv("DATABASE_URL"))
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer pool.Close()

	// Load configuration
	reg, err := registry.Load("config")
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Get file parameters (in real code, these come from the job queue)
	program := "TANF"
	section := 1
	filePath := os.Args[1]
	datafileID := int32(123) // From database

	// Process the file
	if err := processFile(ctx, pool, reg, program, section, filePath, datafileID); err != nil {
		log.Fatalf("Failed to process file: %v", err)
	}

	log.Println("File processed successfully")
}

func processFile(
	ctx context.Context,
	pool *pgxpool.Pool,
	reg *registry.Registry,
	program string,
	section int,
	filePath string,
	datafileID int32,
) error {
	// Step 1: Get the file specification
	spec := reg.GetFileSpec(program, section)
	if spec == nil {
		return fmt.Errorf("no file spec for %s section %d", program, section)
	}

	log.Printf("Processing %s Section %d file: %s", program, section, filePath)
	log.Printf("Format: %s, KeyFields: %v, BatchSize: %d",
		spec.Format, spec.Accumulator.HasKeyFields(), spec.Accumulator.BatchSize)

	// Step 2: Open the file and create decoder
	file, err := os.Open(filePath)
	if err != nil {
		return fmt.Errorf("failed to open file: %w", err)
	}
	defer file.Close()

	dec, err := createDecoder(file, spec)
	if err != nil {
		return fmt.Errorf("failed to create decoder: %w", err)
	}
	defer dec.Close()

	// Step 3: Create record type detector
	detector := parser.NewRecordTypeDetector(spec, reg)

	// Step 4: Create worker pool
	poolConfig := worker.DefaultPoolConfig()
	workerPool := worker.NewPool(spec.Format, poolConfig)
	workerPool.Start(ctx)

	// Step 5: Create database writer (dynamically from FileSpec)
	writerMgr := db.NewWriterManager(pool, datafileID, spec, reg)

	// Step 6: Start result collector
	var collectorErr error
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		collectorErr = collectResults(ctx, workerPool, writerMgr)
	}()

	// Step 7: Process rows through the unified Accumulator
	err = processRows(dec, spec, detector, workerPool)

	if err != nil {
		workerPool.CloseInputs()
		workerPool.Wait()
		return err
	}

	// Step 8: Wait for everything to complete
	workerPool.CloseInputs()
	workerPool.Wait()
	wg.Wait()

	if collectorErr != nil {
		return collectorErr
	}

	return nil
}

func createDecoder(file *os.File, spec *filespec.FileSpec) (decoder.Decoder, error) {
	switch spec.Format {
	case filespec.FormatPositional:
		return decoder.NewPostitionalDecoder(file), nil
	case filespec.FormatColumnar:
		// Determine if CSV or XLSX based on file extension
		// For now, assume CSV
		recordType := spec.RecordTypeDetection.Schema // Fixed schema for FRA
		return decoder.NewCSVDecoder(file, recordType), nil
	default:
		return nil, fmt.Errorf("unknown format: %s", spec.Format)
	}
}

// processRows uses the unified Accumulator to process all rows.
// The Accumulator handles all four modes (keyed, batched, both, neither)
// based on the AccumulatorConfig in the FileSpec.
func processRows(
	dec decoder.Decoder,
	spec *filespec.FileSpec,
	detector *parser.RecordTypeDetector,
	pool *worker.Pool,
) error {
	acc := processor.NewAccumulator(spec, detector)

	for row, err := range dec.Rows() {
		if err != nil {
			return err
		}

		batch, sch, isAccumulated, err := acc.Add(row)
		if err != nil {
			log.Printf("Line %d: %v", row.LineNum(), err)
			continue
		}

		// Non-accumulated rows (HEADER, TRAILER) could be processed here
		if !isAccumulated && sch != nil {
			log.Printf("Line %d: %s (not accumulated)", row.LineNum(), sch.RecordType)
		}

		// For non-keyed modes, batches may be returned during iteration
		if batch != nil {
			pool.Submit(batch)
		}
	}

	// Dispatch all remaining batches (for keyed modes, this is where groups are emitted)
	for _, batch := range acc.Drain() {
		pool.Submit(batch)
	}

	return nil
}

// collectResults receives parsed batches from the worker pool and writes to database.
func collectResults(
	ctx context.Context,
	pool *worker.Pool,
	writerMgr *db.WriterManager,
) error {
	for pb := range pool.Results() {
		// Log any parsing errors
		for _, group := range pb.Groups {
			for _, e := range group.Errors {
				log.Printf("Parse error at line %d (%s): %s",
					e.LineNumber, e.RecordType, e.Message)
			}
		}

		// Write the batch to the database
		if err := writerMgr.WriteBatch(ctx, pb); err != nil {
			log.Printf("Failed to write batch %d: %v", pb.BatchID, err)
		}
	}

	// Flush remaining records and report stats
	if err := writerMgr.FlushAll(ctx); err != nil {
		return fmt.Errorf("final flush: %w", err)
	}

	records, errors := writerMgr.Stats()
	for table, count := range records {
		log.Printf("Written to %s: %d records", table, count)
	}
	log.Printf("Total errors: %d", errors)

	return nil
}

// package main

// import (
// 	"fmt"

// 	"go-parser/parser/internal-Eric/parser"

// 	"github.com/xuri/excelize/v2"
// )

// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// // Required if using kwargs from Python Celery producer
// type parse struct {
// 	datafileId int
// 	reparseId int
// }

// func (p *parse) ParseKwargs(kwargs map[string]interface{}) error {
// 	fmt.Println("Parsing kwargs: ", kwargs)
// 	if len(kwargs) == 0 {
// 		return nil
// 	}
// 	datafileId, ok := kwargs["data_file_id"]
// 	if !ok {
// 		return fmt.Errorf("undefined kwarg data_file_id")
// 	}
// 	p.datafileId = datafileId.(int)

// 	reparseId, ok := kwargs["reparse_id"]
// 	if !ok {
// 		return fmt.Errorf("undefined kwarg reparse_id")
// 	}
// 	p.reparseId = reparseId.(int)
// 	return nil
// }

// func (p *parse) RunTask() (interface{}, error) {
// 	fmt.Println("Running task with datafileId:", p.datafileId, "and reparseId:", p.reparseId)
// 	return nil, nil
// }
// ////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// // Simple consumer since parse doesn't use kwargs. However, Go does not allow default values or a Python producer sending
// // a None. There is no conversion to Go's nil. Therefore, the Python consumer must always supply valid args for the Go
// // consumer. It CAN NOT use "None" as a value ever.
// func parseTask(datafileId, reparseId int) (interface{}, error) {
// 	fmt.Println("Running task with datafileId:", datafileId, "and reparseId:", reparseId)
// 	return nil, nil
// }

// func main() {

// 	// ctx := context.Background()

// 	// /////////////////// S3 Testing with aws-sdk-go ///////////////////////////
// 	// fmt.Println("S3 Testing with aws-sdk-go")
// 	// s3 := storage.NewS3Storage()
// 	// objs, err := s3.ListObjects(ctx, "tdp-datafiles-localstack")
// 	// if err != nil {
// 	// 	log.Fatal(err)
// 	// }
// 	// fmt.Println("Objects:", objs)

// 	// data, err := s3.DownloadLargeObject(ctx, "tdp-datafiles-localstack", "dev/data_files/2021/Q1/1/TAN/Active Case Data/ADS.E2J.FTP1.TS06")
// 	// if err != nil {
// 	// 	log.Fatal(err)
// 	// }
// 	// delimmiter := []byte("\n")
// 	// lines := bytes.Split(data, delimmiter)
// 	// for _, line := range lines {
// 	// 	fmt.Println(string(line), len(line))
// 	// }

// 	// /////////////////// Postgres Testing with sqlc ///////////////////////////
// 	// fmt.Println("Postgres Testing with sqlc")
// 	// conn, err := pgx.Connect(ctx, "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable")
// 	// if err != nil {
// 	// 	log.Fatal(err)
// 	// }
// 	// defer conn.Close(ctx)

// 	// q := db.New(conn)
// 	// _ = q

// 	// stts, err := q.GetSTTs(ctx)
// 	// if err != nil {
// 	// 	log.Fatal(err)
// 	// }
// 	// for _, stt := range stts {
// 	// 	fmt.Println(stt)
// 	// }

// 	/////////////////// Parser Testing ///////////////////////////
// 	fmt.Println("Parser Testing")
// 	f, err := excelize.OpenFile("/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/fra_ofa_test.xlsx")
//     if err != nil {
//         fmt.Println(err)
//         return
//     }
//     defer func() {
//         // Close the spreadsheet.
//         if err := f.Close(); err != nil {
//             fmt.Println(err)
//         }
//     }()

// 	sheet := f.GetSheetName(0)
// 	rows, err := f.GetRows(sheet)
//     if err != nil {
//         fmt.Println(err)
//         return
//     }
// 	// Cells are ALWAYS a string type
//     for _, row := range rows {
//         for _, colCell := range row {
//             fmt.Print(colCell, "\t")
//         }
//         fmt.Println()
//     }

// 	bp := parser.BaseParser{}
// 	err = bp.InitDecoder()
// 	if err != nil {
// 		fmt.Println(err)
// 		return
// 	}
// 	var row parser.RawRow
// 	for {
// 		row = bp.Decoder.Decode()
// 		if row == (parser.RawRow{}) {
// 			break
// 		}
// 		fmt.Println(row)
// 	}

//		/////////////////// Redis Testing with gocelery ///////////////////////////
//		// fmt.Println("Redis Testing with gocelery")
//		// w, err := worker.NewRedisWorker("redis://localhost:6379", map[string]interface{}{
//		// 	"tdpservice.scheduling.parser_task.parse": parseTask,
//		// })
//		// if err != nil {
//		// 	log.Fatal(err)
//		// }
//		// if err := w.Start(); err != nil {
//		// 	log.Fatal(err)
//		// }
//	}
