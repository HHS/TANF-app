package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/decoder"
	"go-parser/internal/filespec"
	"go-parser/internal/parser"
	"go-parser/internal/processor"
	"go-parser/internal/registry"
	"go-parser/internal/testutil"
	"go-parser/internal/worker"
	"go-parser/internal/writer"
)

func main() {
	ctx := context.Background()

	// Connect to database
	pool, err := pgxpool.New(ctx, "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable")//os.Getenv("DATABASE_URL"))
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
	// program := "TANF"
	// program := "TRIBAL"
	program := "SSP"
	// program := "FRA"
	// section := 1
	// section := 2
	// section := 3
	section := 4

	// TANF test files
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.FTP1.TS06"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.FTP2.TS06"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.FTP3.TS06"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.FTP4.TS06"

	// Tribal TANF test files
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.FTP1.TS142"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.FTP2.TS142.txt"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.FTP3.TS142"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/tribal_section_4_fake.txt"

	// SSP test files
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/small_ssp_section1.txt"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ssp_section2_rec_oadsi_file.txt"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.NDM3.MS24"
	filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.NDM4.MS24"


	// FRA test files (Note: these files will fail on CopyFrom because they have malformed SSNs which rolls back the transaction. But they parse correctly.)
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/fra_ofa_test.csv"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/fra_ofa_test.xlsx"

	// Create a test datafile record to satisfy foreign key constraints
	datafileParams := testutil.DefaultDatafileParams()
	datafileParams.ProgramType = program
	datafileParams.Section = "Active Case Data"
	datafileID, err := testutil.CreateTestDatafile(ctx, pool, datafileParams)
	if err != nil {
		log.Fatalf("Failed to create test datafile: %v", err)
	}
	log.Printf("Created test datafile with ID: %d", datafileID)
	defer func() {
		// Optionally clean up the test datafile after processing
		// Uncomment to enable cleanup:
		// This technically doesn't work right now since the relations can't be deleted
		testutil.DeleteTestDatafile(ctx, pool, datafileID)
	}()

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

	// Step 3: Read and parse header (for positional files)
	headerRow, err := dec.ReadFirst()
	if err != nil {
		return fmt.Errorf("failed to read header: %w", err)
	}

	headerSchema := reg.GetSchema(parser.HeaderSchemaPath)
	parseCtx, err := parser.ParseHeader(headerRow, headerSchema)
	if err != nil {
		return fmt.Errorf("failed to parse header: %w", err)
	}

	if parseCtx != nil {
		log.Printf("Header: Year=%d, Quarter=%s, Encrypted=%v",
			parseCtx.Year, parseCtx.Quarter, parseCtx.IsEncrypted)
		log.Printf("Header fields: %v", parseCtx.Header.Fields)
	}

	// Step 4: Create record type detector
	detector := parser.NewRecordTypeDetector(spec, reg)

	// Step 5: Create worker pool
	poolConfig := worker.DefaultPoolConfig()
	workerPool := worker.NewPool(spec.Format, poolConfig)
	workerPool.SetParseContext(parseCtx) // Set context before starting workers
	workerPool.Start(ctx)

	// Step 6: Create database writer (dynamically from FileSpec)
	writerMgr := writer.NewWriterManager(pool, datafileID, spec, reg)

	// Step 7: Start result collector
	var collectorErr error
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		collectorErr = collectResults(ctx, workerPool, writerMgr)
	}()

	// Step 8: Process rows through the unified Accumulator
	err = processRows(dec, spec, detector, workerPool)

	if err != nil {
		workerPool.CloseInputs()
		workerPool.Wait()
		return err
	}

	// Step 9: Wait for everything to complete
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
		buf := make([]byte, 512)
		_, err := file.Read(buf)
		if err != nil && err != io.EOF {
			return nil, err
		}

		// Rewind the file pointer for later reading if necessary
		file.Seek(0, io.SeekStart)

		contentType := http.DetectContentType(buf)
		switch contentType {
		case "application/zip":
			// XLSX files are detected as application/zip because they are Open XML formats wrapped in a zip container.
			fmt.Printf("%s is likely an XLSX file (MIME type: %s)\n", file.Name(), contentType)
			// Let the XLSX decoder handle opening the file in the format it needs
			defer file.Close()
			return decoder.NewXLSXDecoder(file.Name(), spec.RecordTypeDetection.Schema)
		case "text/plain; charset=utf-8", "text/csv; charset=utf-8":
			fmt.Printf("%s is likely a CSV file (MIME type: %s)\n", file.Name(), contentType)
			return decoder.NewCSVDecoder(file, spec.RecordTypeDetection.Schema), nil
		default:
			return nil, fmt.Errorf("%s has an unknown or unexpected content type: %s\n", file.Name(), contentType)
		}
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
	writerMgr *writer.WriterManager,
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
