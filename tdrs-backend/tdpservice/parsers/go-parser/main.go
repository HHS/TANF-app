package main

import (
	"context"
	"flag"
	"log"
	"os"
	"runtime/pprof"

	"go-parser/internal/config"
	"go-parser/internal/db"
	"go-parser/internal/pipeline"
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

	configDir := "config"

	// Load pipeline configuration (workers, buffers, DB pool, etc.)
	pipelineCfg, err := config.LoadPipelineConfig(configDir)
	if err != nil {
		log.Fatalf("Failed to load pipeline config: %v", err)
	}

	// Connect to database using config
	dbUrl := "postgres://tdpuser:something_secure@localhost:5432/tdrs_test?sslmode=disable"
	dbPool, err := db.NewPool(ctx, dbUrl, pipelineCfg.Database)
	if err != nil {
		log.Fatalf("Failed to connect to database: %v", err)
	}
	defer dbPool.Close()

	// Load schemas, filespecs, and validators
	// TODO: Need to revisit storing the object pools on the schemas. Since the registry will exist for as long as the
	// celery worker does, the object pools could grow to an enormous size since there isn't a way to clear them after a
	// parsing run. We should consider implementing/importing a better solution that allows clearing. Or, we could reload
	// the registry each time a new parsing request comes in (simpler).
	reg, err := config.Load(configDir)
	if err != nil {
		log.Fatalf("Failed to load configuration: %v", err)
	}

	// Load content types from database for error linking
	// This is done once at startup and reused across parsing runs
	contentTypes, err := db.LoadContentTypes(ctx, dbPool)
	if err != nil {
		log.Fatalf("Failed to load content types: %v", err)
	}
	reg.LoadContentTypes(contentTypes)
	log.Printf("Loaded %d content types from database", len(contentTypes))

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
	// filePath := "/Users/ericlipe/work/repos/tdrs/TANF-app/tdrs-backend/tdpservice/parsers/test/data/cat_4_edge_case.txt"
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
	datafileID, err := testutil.CreateTestDatafile(ctx, dbPool, datafileParams)
	if err != nil {
		log.Fatalf("Failed to create test datafile: %v", err)
	}
	log.Printf("Created test datafile with ID: %d", datafileID)
	defer func() {
		testutil.DeleteTestDatafile(ctx, dbPool, datafileID)
	}()

	// Create and run pipeline
	pipeln := pipeline.NewPipline(dbPool, reg, pipeline.NewConfig(pipelineCfg))
	result, err := pipeln.ProcessFile(ctx, pipeline.ProcessParams{
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
}
