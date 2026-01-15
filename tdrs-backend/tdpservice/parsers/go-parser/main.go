package main

import (
	"context"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"runtime/pprof"
	"sync"
	"time"

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

var cpuprofile = flag.String("cpuprofile", "", "write cpu profile to file")
var memprofile = flag.String("memprofile", "", "write memory profile to this file")

func main() {
	flag.Parse()
    if *cpuprofile != "" {
        f, err := os.Create(*cpuprofile)
        if err != nil {
            log.Fatal(err)
        }
        pprof.StartCPUProfile(f)
        defer pprof.StopCPUProfile()
    }

	ctx := context.Background()

	// Connect to database
	databaseUrl := "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable"
	// pool, err := pgxpool.New(ctx, "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable")//os.Getenv("DATABASE_URL"))
	// if err != nil {
	// 	log.Fatalf("Failed to connect to database: %v", err)
	// }
	config, err := pgxpool.ParseConfig(databaseUrl)
	if err != nil {
		log.Fatalf("Failed to parse database URL: %v", err)
	}
	config.MinConns = 4
	config.MinIdleConns = 1
	config.MaxConns = 4

	pool, err := pgxpool.NewWithConfig(ctx, config)
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
	// program := "TRIBAL"
	// program := "SSP"
	// program := "FRA"
	section := 1
	// section := 2
	// section := 3
	// section := 4

	// TANF test files
	filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.FTP1.TS06"
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.NDM1.TS53_fake.txt"
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
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/ADS.E2J.NDM4.MS24"


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

	// Start timing here for fair comparison to python patch to measure parsing time
	startTime := time.Now()

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
	// TODO: introduce toplevel config to specify pool config and other top level things (e.g. router config)
	poolConfig := worker.DefaultPoolConfig()
	workerPool := worker.NewPool(spec.Format, poolConfig)
	workerPool.SetParseContext(parseCtx) // Set context before starting workers
	workerPool.Start(ctx)

	// Step 6: Create database writer (dynamically from FileSpec)
	// Pre-warm object pools with 2x worker count to handle records in flight
	// TODO: should we introduce a router config?
	poolPrewarmSize := 10000
	router := writer.NewRouter(pool, datafileID, spec, reg, poolPrewarmSize)

	// Step 7: Start all writer goroutines before result collection
	router.Start(ctx)

	// Step 8: Start result collector with parallel dispatchers
	var collectorErr error
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		// TODO: make numDispatchers configurable via config file
		numDispatchers := 4 // Tune based on CPU cores / connection pool size
		collectorErr = routeResults(ctx, workerPool, router, numDispatchers)
	}()

	// Step 9: Process rows through the unified Accumulator
	err = processRows(dec, spec, detector, workerPool)

	if err != nil {
		workerPool.CloseInputs()
		workerPool.Wait()
		return err
	}

	// Step 10: Wait for everything to complete
	workerPool.CloseInputs()
	workerPool.Wait()
	wg.Wait()

	if collectorErr != nil {
		return collectorErr
	}

	// Stop timing here for fair comparison to python patch to measure parsing time
	endTime := time.Now()
	log.Printf("Time to parse: %s", endTime.Sub(startTime))

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

// routeResults receives parsed batches from the worker pool and routes them to the database writers.
// Multiple dispatcher goroutines compete on the Results channel for parallel processing.
func routeResults(
	ctx context.Context,
	pool *worker.Pool,
	router *writer.Router,
	numDispatchers int,
) error {
	var wg sync.WaitGroup
	errChan := make(chan error, numDispatchers)

	// Spawn multiple dispatchers reading from the same channel
	for range numDispatchers {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for pb := range pool.Results() {
				// Log any parsing errors
				for _, group := range pb.Groups {
					for _, e := range group.Errors {
						log.Printf("Dispatcher: Parse error at line %d (%s): %s",
							e.LineNumber, e.RecordType, e.Message)
					}
				}

				// Route the batch to writers (no conversion here)
				if err := router.RouteBatch(ctx, pb); err != nil {
					log.Printf("Dispatcher: batch %d error: %v", pb.BatchID, err)
					errChan <- err
					return
				}
			}
		}()
	}

	// Wait for all dispatchers to finish
	wg.Wait()
	close(errChan)
	if *memprofile != "" {
		f, err := os.Create(*memprofile)
		if err != nil {
			log.Fatal(err)
		}
		pprof.WriteHeapProfile(f)
		f.Close()
	}

	// Collect any errors from dispatchers
	var errs []error
	for err := range errChan {
		errs = append(errs, err)
	}

	// Stop writers (flushes remaining) and collect errors
	if err := router.Stop(); err != nil {
		errs = append(errs, err)
	}

	// Report stats
	records, errorCount := router.Stats()
	for table, count := range records {
		log.Printf("Written to %s: %d records", table, count)
	}
	log.Printf("Total errors: %d", errorCount)

	if len(errs) > 0 {
		return errors.Join(errs...)
	}
	return nil
}
