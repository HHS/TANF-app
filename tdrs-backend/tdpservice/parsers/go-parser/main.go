package main

import (
	"context"
	"flag"
	"log"
	"os"
	"runtime/pprof"

	"github.com/jackc/pgx/v5/pgxpool"

	"go-parser/internal/pipeline"
	"go-parser/internal/registry"
	"go-parser/internal/testutil"
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
		testutil.DeleteTestDatafile(ctx, pool, datafileID)
	}()

	// Create and run pipeline
	p := pipeline.New(pool, reg, pipeline.DefaultConfig())
	result, err := p.ProcessFile(ctx, pipeline.ProcessParams{
		Program:    program,
		Section:    section,
		FilePath:   filePath,
		DatafileID: datafileID,
	})
	if err != nil {
		log.Fatalf("Failed to process file: %v", err)
	}

	// Memory profiling (after pipeline completes)
	if *memprofile != "" {
		f, err := os.Create(*memprofile)
		if err != nil {
			log.Fatal(err)
		}
		pprof.WriteHeapProfile(f)
		f.Close()
	}

	// Report results
	log.Printf("File processed successfully in %s", result.Duration)
	for table, count := range result.RecordCounts {
		log.Printf("Written to %s: %d records", table, count)
	}
	log.Printf("Total errors: %d", result.ErrorCount)
}
